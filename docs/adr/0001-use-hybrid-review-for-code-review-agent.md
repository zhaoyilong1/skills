# Use Hybrid Review for the Code Review Agent

The Code Review Agent uses a Hybrid Review model rather than a purely defect-first review or Matt Pocock's strict two-axis Standards/Spec report. The agent should find or infer the Spec Source, check Standards Source material, and assess Risk separately, but aggregate the final output as senior-teammate findings ordered by merge risk. Subagents are reserved for Substantial Reviews so small reviews stay fast and coherent while larger or riskier changes still get isolated review passes.
