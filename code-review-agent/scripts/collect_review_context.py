#!/usr/bin/env python3
"""Collect lightweight git context for a code review."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


LANG_BY_EXT = {
    ".js": "JavaScript",
    ".jsx": "React/JavaScript",
    ".ts": "TypeScript",
    ".tsx": "React/TypeScript",
    ".py": "Python",
    ".go": "Go",
    ".rs": "Rust",
    ".java": "Java",
    ".kt": "Kotlin",
    ".kts": "Kotlin",
    ".sql": "SQL",
    ".rb": "Ruby",
    ".php": "PHP",
    ".cs": "C#",
    ".cpp": "C++",
    ".cc": "C++",
    ".c": "C",
    ".h": "C/C++ Header",
    ".swift": "Swift",
    ".sh": "Shell",
    ".yml": "YAML",
    ".yaml": "YAML",
    ".json": "JSON",
    ".toml": "TOML",
    ".tf": "Terraform",
    ".md": "Markdown",
}

MANIFEST_HINTS = {
    "package.json": "JavaScript/TypeScript package manifest",
    "pnpm-lock.yaml": "PNPM lockfile",
    "yarn.lock": "Yarn lockfile",
    "package-lock.json": "NPM lockfile",
    "pyproject.toml": "Python project manifest",
    "requirements.txt": "Python requirements",
    "poetry.lock": "Poetry lockfile",
    "go.mod": "Go module manifest",
    "go.sum": "Go checksum file",
    "Cargo.toml": "Rust package manifest",
    "Cargo.lock": "Rust lockfile",
    "pom.xml": "Maven manifest",
    "build.gradle": "Gradle build",
    "build.gradle.kts": "Gradle build",
    "Dockerfile": "Docker build",
}

IGNORED_PATH_PARTS = {"__pycache__", ".git", ".hg", ".svn"}
IGNORED_SUFFIXES = {".pyc", ".pyo"}


def run_git(args: list[str], cwd: Path) -> tuple[int, str, str]:
    proc = subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def git_stdout(args: list[str], cwd: Path) -> str:
    code, out, _ = run_git(args, cwd)
    return out if code == 0 else ""


def has_head(cwd: Path) -> bool:
    code, _, _ = run_git(["rev-parse", "--verify", "HEAD"], cwd)
    return code == 0


def repo_root() -> Path:
    code, out, err = run_git(["rev-parse", "--show-toplevel"], Path.cwd())
    if code != 0:
        print(f"Not inside a git repository: {err}", file=sys.stderr)
        sys.exit(2)
    return Path(out)


def default_upstream(cwd: Path) -> str:
    upstream = git_stdout(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"], cwd)
    return upstream


def diff_args(base: str | None, head: str | None, cwd: Path) -> list[str]:
    if base and head:
        return [f"{base}...{head}"]
    if base:
        return [base]
    upstream = default_upstream(cwd)
    if upstream:
        merge_base = git_stdout(["merge-base", "HEAD", upstream], cwd)
        if merge_base:
            return [f"{merge_base}...HEAD"]
    if has_head(cwd):
        return ["HEAD"]
    return []


def changed_files(cwd: Path, revs: list[str]) -> list[dict[str, str]]:
    if revs:
        code, out, _ = run_git(["diff", "--name-status", *revs], cwd)
        lines = out.splitlines() if code == 0 and out else []
    else:
        lines = []

    files: list[dict[str, str]] = []
    for line in lines:
        parts = line.split("\t")
        if not parts:
            continue
        status = parts[0]
        path = parts[-1]
        files.append({"status": status, "path": path})

    status_out = git_stdout(["status", "--short", "--untracked-files=all"], cwd)
    seen = {item["path"] for item in files}
    for line in status_out.splitlines():
        if not line:
            continue
        path = status_path(line)
        if path not in seen:
            files.append({"status": line[:2].strip() or "?", "path": path})
            seen.add(path)
    return files


def should_ignore_path(path: str) -> bool:
    parts = set(Path(path).parts)
    return bool(parts & IGNORED_PATH_PARTS) or Path(path).suffix in IGNORED_SUFFIXES


def status_path(line: str) -> str:
    path = line[3:]
    if " -> " in path:
        path = path.split(" -> ", 1)[1]
    return path


def filtered_status(cwd: Path) -> str:
    out = git_stdout(["status", "--short", "--untracked-files=all"], cwd)
    lines = [line for line in out.splitlines() if not should_ignore_path(status_path(line))]
    return "\n".join(lines)


def diff_stat(cwd: Path, revs: list[str]) -> str:
    if not revs:
        return ""
    return git_stdout(["diff", "--stat", *revs], cwd)


def numstat(cwd: Path, revs: list[str]) -> list[dict[str, str]]:
    if not revs:
        return []
    out = git_stdout(["diff", "--numstat", *revs], cwd)
    rows = []
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) >= 3:
            rows.append({"additions": parts[0], "deletions": parts[1], "path": parts[2]})
    return rows


def classify(files: list[dict[str, str]]) -> Counter:
    counts: Counter = Counter()
    for item in files:
        path = item["path"]
        ext = Path(path).suffix
        counts[LANG_BY_EXT.get(ext, ext or "No extension")] += 1
    return counts


def risk_hints(files: list[dict[str, str]]) -> list[str]:
    hints: list[str] = []
    paths = [item["path"] for item in files]
    basenames = {Path(path).name for path in paths}

    for name in sorted(basenames & set(MANIFEST_HINTS)):
        hints.append(f"{name}: {MANIFEST_HINTS[name]}")

    lowered = [path.lower() for path in paths]
    if any("migration" in path or path.endswith(".sql") for path in lowered):
        hints.append("Migration/schema surface: check backward compatibility, locking, idempotency, and rollback.")
    if any("auth" in path or "permission" in path or "policy" in path for path in lowered):
        hints.append("Authorization surface: check identity, ownership, tenant boundaries, and fail-closed behavior.")
    if any("payment" in path or "billing" in path or "invoice" in path for path in lowered):
        hints.append("Money surface: check idempotency, rounding, retries, auditability, and duplicate side effects.")
    if any("cache" in path or "redis" in path for path in lowered):
        hints.append("Cache surface: check keys, invalidation, tenant isolation, and stale data behavior.")
    if any("worker" in path or "job" in path or "queue" in path for path in lowered):
        hints.append("Async surface: check retries, ordering, duplicate delivery, cancellation, and poison-message handling.")
    if any(path.startswith(".github/") or "ci" in path for path in lowered):
        hints.append("CI/release surface: check required checks, secrets, branch conditions, and deploy behavior.")
    return hints


def package_scripts(root: Path) -> list[str]:
    package_json = root / "package.json"
    if not package_json.exists():
        return []
    try:
        data = json.loads(package_json.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    scripts = data.get("scripts", {})
    if not isinstance(scripts, dict):
        return []
    interesting = ["test", "lint", "typecheck", "check", "build"]
    return [f"npm run {name}" for name in interesting if name in scripts]


def validation_hints(root: Path) -> list[str]:
    hints: list[str] = []
    hints.extend(package_scripts(root))
    if (root / "pyproject.toml").exists() or (root / "pytest.ini").exists() or (root / "tests").exists():
        hints.append("python -m pytest")
    if (root / "go.mod").exists():
        hints.append("go test ./...")
    if (root / "Cargo.toml").exists():
        hints.append("cargo test")
    if (root / "pom.xml").exists():
        hints.append("mvn test")
    if (root / "gradlew").exists():
        hints.append("./gradlew test")
    if (root / "Makefile").exists():
        hints.append("make test or inspect Makefile targets")
    return hints


def build_context(base: str | None, head: str | None) -> dict:
    root = repo_root()
    revs = diff_args(base, head, root)
    files = changed_files(root, revs)
    files = [item for item in files if not should_ignore_path(item["path"])]
    return {
        "repo_root": str(root),
        "branch": git_stdout(["branch", "--show-current"], root),
        "upstream": default_upstream(root),
        "diff_range": " ".join(revs) if revs else "working tree/status only",
        "status": filtered_status(root),
        "diff_stat": diff_stat(root, revs),
        "files": files,
        "numstat": numstat(root, revs),
        "language_counts": dict(classify(files)),
        "risk_hints": risk_hints(files),
        "validation_hints": validation_hints(root),
    }


def print_markdown(context: dict, max_files: int) -> None:
    print("# Review Context")
    print()
    print(f"- Repo: `{context['repo_root']}`")
    print(f"- Branch: `{context['branch'] or '(detached or unknown)'}`")
    print(f"- Upstream: `{context['upstream'] or '(none)'}`")
    print(f"- Diff range: `{context['diff_range']}`")
    print()

    if context["language_counts"]:
        print("## Changed File Types")
        for lang, count in sorted(context["language_counts"].items()):
            print(f"- {lang}: {count}")
        print()

    if context["risk_hints"]:
        print("## Risk Hints")
        for hint in context["risk_hints"]:
            print(f"- {hint}")
        print()

    if context["validation_hints"]:
        print("## Validation Hints")
        for hint in context["validation_hints"]:
            print(f"- `{hint}`")
        print()

    if context["diff_stat"]:
        print("## Diff Stat")
        print("```text")
        print(context["diff_stat"])
        print("```")
        print()

    files = context["files"]
    print(f"## Changed Files ({len(files)})")
    for item in files[:max_files]:
        print(f"- `{item['status']}` `{item['path']}`")
    if len(files) > max_files:
        print(f"- ... {len(files) - max_files} more")
    print()

    if context["status"]:
        print("## Git Status")
        print("```text")
        print(context["status"])
        print("```")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", help="Base ref for a PR-style comparison.")
    parser.add_argument("--head", default="HEAD", help="Head ref for a PR-style comparison.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of Markdown.")
    parser.add_argument("--max-files", type=int, default=80, help="Maximum changed files to print in Markdown.")
    args = parser.parse_args()

    context = build_context(args.base, args.head if args.base else None)
    if args.json:
        print(json.dumps(context, indent=2, sort_keys=True))
    else:
        print_markdown(context, args.max_files)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
