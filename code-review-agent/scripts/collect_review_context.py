#!/usr/bin/env python3
"""Collect lightweight git context for a code review."""

from __future__ import annotations

import argparse
import json
import os
import re
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

WALK_IGNORE_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".next",
    ".turbo",
    ".venv",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "target",
    "vendor",
}
TEXT_DOC_SUFFIXES = {".md", ".mdx", ".rst", ".txt", ".adoc"}
SPEC_DIR_PARTS = {"docs", "specs", ".scratch", "rfcs", "proposals", "designs"}
SPEC_NAME_HINTS = {"spec", "rfc", "proposal", "design", "ticket", "issue", "prd", "requirement"}
STANDARDS_SOURCE_NAMES = {
    "AGENTS.md",
    "CLAUDE.md",
    "CODING_STANDARDS.md",
    "CONTRIBUTING.md",
    "DEVELOPMENT.md",
    "STYLEGUIDE.md",
    "STYLE_GUIDE.md",
    "TESTING.md",
    "ARCHITECTURE.md",
    "copilot-instructions.md",
}
STANDARDS_DIR_PARTS = {"standards", "engineering", "architecture", "agents"}


def run_git(args: list[str], cwd: Path) -> tuple[int, str, str]:
    proc = subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return proc.returncode, proc.stdout.rstrip("\n"), proc.stderr.rstrip("\n")


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


def log_args(revs: list[str]) -> list[str]:
    if not revs:
        return []
    rev = revs[0]
    if "..." in rev:
        base, head = rev.split("...", 1)
        return [f"{base}..{head}"]
    return [f"{rev}..HEAD"]


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
    chunks = []
    if revs:
        chunks.append(git_stdout(["diff", "--stat", *revs], cwd))
    if not revs_include_worktree(revs):
        chunks.append(git_stdout(["diff", "--cached", "--stat"], cwd))
        chunks.append(git_stdout(["diff", "--stat"], cwd))
    return "\n".join(chunk for chunk in chunks if chunk)


def revs_include_worktree(revs: list[str]) -> bool:
    if not revs:
        return False
    rev = revs[0]
    return "..." not in rev and ".." not in rev


def parse_numstat(out: str) -> list[dict[str, str]]:
    rows = []
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) >= 3:
            rows.append({"additions": parts[0], "deletions": parts[1], "path": parts[2]})
    return rows


def count_text_lines(path: Path, max_bytes: int = 1_000_000) -> int | None:
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if len(data) > max_bytes or b"\0" in data:
        return None
    return data.count(b"\n") + (0 if data.endswith(b"\n") or not data else 1)


def untracked_numstat(cwd: Path, files: list[dict[str, str]]) -> list[dict[str, str]]:
    rows = []
    for item in files:
        if item["status"] != "??":
            continue
        count = count_text_lines(cwd / item["path"])
        if count is not None:
            rows.append({"additions": str(count), "deletions": "0", "path": item["path"]})
    return rows


def numstat(cwd: Path, revs: list[str], files: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    if revs:
        rows.extend(parse_numstat(git_stdout(["diff", "--numstat", *revs], cwd)))
    if not revs_include_worktree(revs):
        rows.extend(parse_numstat(git_stdout(["diff", "--cached", "--numstat"], cwd)))
        rows.extend(parse_numstat(git_stdout(["diff", "--numstat"], cwd)))
    rows.extend(untracked_numstat(cwd, files))
    return rows


def commit_log(cwd: Path, revs: list[str]) -> str:
    args = log_args(revs)
    if not args:
        return ""
    return git_stdout(["log", "--oneline", *args], cwd)


def classify(files: list[dict[str, str]]) -> Counter:
    counts: Counter = Counter()
    for item in files:
        path = item["path"]
        ext = Path(path).suffix
        counts[LANG_BY_EXT.get(ext, ext or "No extension")] += 1
    return counts


def path_parts(path: str) -> set[str]:
    return set(Path(path).parts)


def branch_tokens(branch: str) -> set[str]:
    tokens = {part.lower() for part in re.split(r"[^A-Za-z0-9]+", branch) if len(part) >= 3}
    noise = {"codex", "agent", "feature", "fix", "bugfix", "chore", "main", "master"}
    return tokens - noise


def iter_repo_files(root: Path, limit: int = 5000) -> list[Path]:
    files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in WALK_IGNORE_DIRS]
        for filename in filenames:
            path = Path(dirpath) / filename
            rel = path.relative_to(root)
            if should_ignore_path(str(rel)):
                continue
            files.append(rel)
            if len(files) >= limit:
                return files
    return files


def add_unique_candidate(candidates: list[dict[str, str]], seen: set[str], path: str, reason: str) -> None:
    if path in seen:
        return
    candidates.append({"path": path, "reason": reason})
    seen.add(path)


def spec_candidates(root: Path, branch: str, files: list[dict[str, str]], max_results: int = 20) -> list[dict[str, str]]:
    candidates: list[dict[str, str]] = []
    seen: set[str] = set()
    tokens = branch_tokens(branch)

    for item in files:
        path = item["path"]
        p = Path(path)
        lowered = path.lower()
        parts = path_parts(path)
        if p.suffix.lower() in TEXT_DOC_SUFFIXES and (
            parts & SPEC_DIR_PARTS or any(hint in lowered for hint in SPEC_NAME_HINTS)
        ):
            add_unique_candidate(candidates, seen, path, "changed doc/spec-like file")

    for rel in iter_repo_files(root):
        if len(candidates) >= max_results:
            break
        path = str(rel)
        p = Path(path)
        lowered = path.lower()
        parts = path_parts(path)
        if p.suffix.lower() not in TEXT_DOC_SUFFIXES:
            continue
        has_spec_shape = bool(parts & SPEC_DIR_PARTS) or any(hint in lowered for hint in SPEC_NAME_HINTS)
        matches_branch = bool(tokens and any(token in lowered for token in tokens))
        if has_spec_shape and matches_branch:
            add_unique_candidate(candidates, seen, path, "matches branch tokens and spec-like location/name")

    return candidates


def standards_sources(root: Path, max_results: int = 30) -> list[dict[str, str]]:
    candidates: list[dict[str, str]] = []
    seen: set[str] = set()

    for rel in iter_repo_files(root):
        if len(candidates) >= max_results:
            break
        path = str(rel)
        p = Path(path)
        parts = path_parts(path)
        if p.name in STANDARDS_SOURCE_NAMES:
            add_unique_candidate(candidates, seen, path, "well-known standards source")
            continue
        if p.suffix.lower() in TEXT_DOC_SUFFIXES and parts & STANDARDS_DIR_PARTS:
            lowered = path.lower()
            if any(word in lowered for word in ["standard", "convention", "testing", "architecture", "agent"]):
                add_unique_candidate(candidates, seen, path, "standards-like documentation")

    return candidates


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


def changed_line_count(rows: list[dict[str, str]]) -> int:
    total = 0
    for row in rows:
        for key in ("additions", "deletions"):
            value = row[key]
            if value.isdigit():
                total += int(value)
    return total


def substantial_review_hints(
    files: list[dict[str, str]],
    rows: list[dict[str, str]],
    risks: list[str],
    specs: list[dict[str, str]],
) -> list[str]:
    hints: list[str] = []
    line_count = changed_line_count(rows)
    if len(files) > 12:
        hints.append(f"{len(files)} changed files: consider isolated Spec, Standards, Risk, and Tests passes.")
    if line_count > 500:
        hints.append(f"{line_count} changed lines: consider isolated passes or a pinned diff snapshot.")
    if risks:
        hints.append("High-risk surface detected: consider an isolated Risk pass.")
    if len(files) > 3 and not specs:
        hints.append("No likely Spec Source found for a non-trivial change: infer intent and note the limitation.")
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
    rows = numstat(root, revs, files)
    branch = git_stdout(["branch", "--show-current"], root)
    risks = risk_hints(files)
    specs = spec_candidates(root, branch, files)
    return {
        "repo_root": str(root),
        "branch": branch,
        "upstream": default_upstream(root),
        "diff_range": " ".join(revs) if revs else "working tree/status only",
        "commit_log": commit_log(root, revs),
        "status": filtered_status(root),
        "diff_stat": diff_stat(root, revs),
        "files": files,
        "numstat": rows,
        "language_counts": dict(classify(files)),
        "risk_hints": risks,
        "spec_candidates": specs,
        "standards_sources": standards_sources(root),
        "substantial_review_hints": substantial_review_hints(files, rows, risks, specs),
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

    if context["spec_candidates"]:
        print("## Spec Source Candidates")
        for item in context["spec_candidates"]:
            print(f"- `{item['path']}` - {item['reason']}")
        print()

    if context["standards_sources"]:
        print("## Standards Sources")
        for item in context["standards_sources"]:
            print(f"- `{item['path']}` - {item['reason']}")
        print()

    if context["substantial_review_hints"]:
        print("## Substantial Review Hints")
        for hint in context["substantial_review_hints"]:
            print(f"- {hint}")
        print()

    if context["validation_hints"]:
        print("## Validation Hints")
        for hint in context["validation_hints"]:
            print(f"- `{hint}`")
        print()

    if context["commit_log"]:
        print("## Commit Log")
        print("```text")
        print(context["commit_log"])
        print("```")
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
