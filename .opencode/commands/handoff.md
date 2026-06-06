---
name: /handoff
description: Perform session handoff with documentation updates
argument:
  - name: no-skills
    description: Skip skill evaluation in self-evolution gate
    required: false
  - name: no-agents
    description: Skip agent evaluation in self-evolution gate
    required: false
  - name: no-builder
    description: Skip boomerang-agent-builder invocation
    required: false
---

## /handoff — Session Wrap-Up

End the current session cleanly by updating all documentation and saving context for the next session.

### Usage

```
/handoff
/handoff --no-skills
/handoff --no-builder
/handoff --no-skills --no-agents --no-builder
```

### Steps Performed

1. **Update TASKS.md** — Mark done tasks, add new ones, remove outdated
2. **Update HANDOFF.md** — Add session entry with what was accomplished
3. **Update CONTEXT.md** — Refresh architecture notes and next steps
4. **Run Quality Gates** — Lint → Typecheck → Test (if --run-tests flag)
5. **Self-Evolution Gate** — Evaluate session patterns for skill/agent candidates
6. **Save Memory** — Store session summary to memini-ai with project tag

### Waiver Flags

| Flag | Effect |
|------|--------|
| `--no-skills` | Skip skill candidate evaluation |
| `--no-agents` | Skip agent candidate evaluation |
| `--no-builder` | Skip boomerang-agent-builder invocation entirely |

### Self-Evolution Gate

If enabled (default), the handoff will:
1. Query memini-ai for recurring patterns (trigger_count >= 3)
2. Evaluate against 4 criteria: Repetition, Interface Clarity, Independence, Time Savings
3. If criteria met → invoke `boomerang-agent-builder` skill
4. Create `SKILL.md` or update `AGENTS.md` as needed

### Notes

- Handoff is the final step of the Boomerang Protocol (Step 8)
- Memory is saved with `sourceType: "boomerang"` and `metadata.project: "boomerang-v3"`
- Context preservation ensures the next agent has full project state
