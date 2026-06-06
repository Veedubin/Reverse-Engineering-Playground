---
name: boomerang-handoff
description: Wrap-up function for ending a session cleanly. Updates all documentation files and saves context for the next session.
---

# RE Handoff

## Description
Wrap-up function for ending a session cleanly. Updates all documentation files and saves context for the next session.

## Instructions

You are the **RE Handoff** specialist. Your role is:

1. **Wrap Up**: End session cleanly with documentation updates
2. **Save Context**: Preserve session state for future work
3. **Update Docs**: Ensure TASKS.md, AGENTS.md, HANDOFF.md are current
4. **Summarize**: Create session summary for memory

## Triggers

Use this skill when:
- Ending a work session
- Context is approaching limit
- User requests `/handoff` or session wrap-up
- Significant milestones reached

## Model

Use **Kimi K2.6** for comprehensive session summarization.

## Handoff Workflow

### 1. Update TASKS.md
- Mark completed tasks as done
- Add any new tasks discovered
- Remove outdated tasks
- Update task statuses

### 2. Update Documentation
- Update AGENTS.md if agent changes occurred
- Update README.md if user-facing changes
- Document any new patterns established

### 3. Create HANDOFF.md
- Summarize current work state
- Note in-progress items
- List next steps and priorities
- Preserve context for resume

### 4. Save to Memory
Save session summary to memini-ai with:
- Work completed
- Key decisions made
- Patterns established
- Issues encountered
- Recommendations for next session

### 5. Self-Evolution Gate

After saving session summary, evaluate for skill/agent patterns:

#### Step 5.1: Check Waiver Flags
Respect these flags to skip evaluation:
- `--no-skills`: Skip skill evaluation
- `--no-agents`: Skip agent evaluation
- `--no-builder`: Skip both

If any flag present, skip to Documentation Checklist.

#### Step 5.2: Query Pattern Candidates
Query memini-ai for pattern candidates with:
```
pattern_type: "skill_candidate" OR "agent_candidate"
trigger_count >= 3
```

Example query:
```
memini-ai-dev_query_memories({
  query: "pattern candidate skill agent trigger_count >= 3",
  limit: 5
})
```

#### Step 5.3: Evaluate Candidates
For each candidate found:
1. **Repetition**: trigger_count >= 3 ✅
2. **Interface Clarity**: Clear input/output, not context-dependent ✅
3. **Independence**: Can run without full session context ✅
4. **Time Savings**: Saves more time than maintenance costs ✅

#### Step 5.4: Invoke Agent Builder
If candidate meets all criteria:
1. Invoke `re-agent-builder` skill with pattern candidate
2. Pass full context: pattern, metadata, session history
3. Builder creates SKILL.md and updates AGENTS.md as needed

```javascript
// Example: Invoke builder
re-agent-builder({
  pattern: "npm publish workflow",
  metadata: {
    pattern_type: "skill_candidate",
    trigger_count: 5,
    suggested_name: "npm-publisher"
  },
  session_history: ["session-id-1", "session-id-2", "session-id-3"]
})
```

#### Step 5.5: Track Results
- Log what was created (skill, agent, or none)
- Update TASKS.md if new capability added
- Save evolution result to memini-ai

## Documentation Checklist

- [ ] TASKS.md: All completed tasks marked, new tasks added
- [ ] AGENTS.md: Agent roster updated if changed
- [ ] README.md: User-facing changes documented
- [ ] HANDOFF.md: Session summary created
- [ ] Self-Evolution Gate: Pattern evaluation performed (if not waived)

## Self-Evolution Gate

After session save, check for skill/agent pattern candidates:
1. Check waiver flags (`--no-skills`, `--no-agents`, `--no-builder`)
2. Query memini-ai for candidates with trigger_count >= 3
3. Evaluate against criteria (repetition, interface, independence, time savings)
4. If qualified, invoke re-agent-builder
5. Track results in TASKS.md if changes made

## Output Format (Return to Orchestrator)

```markdown
## Handoff Complete: [Session Summary]

### Work Completed
- [item 1]
- [item 2]

### Key Decisions
- [decision 1]
- [decision 2]

### Documentation Updated
- `TASKS.md`: [changes]
- `AGENTS.md`: [changes]
- `HANDOFF.md`: [created/updated]

### Memory Saved
Session summary saved to memini-ai with project tag.

### Next Session
[what to do first]
```

## memini-ai Protocol

### Required Actions

1. **Query at start**: Query memini-ai for:
   - Previous session context
   - Ongoing tasks
   - User preferences

2. **Save at end**: Save to memini-ai:
   - Complete session summary (HIGH VALUE - always use project tag)
   - Work completed with outcomes
   - Key decisions and rationale
   - Patterns established
   - Issues encountered
   - Next steps for next session

### Trust Adjustment
After session summary:
```javascript
memini-ai-dev_adjust_trust({
  memory_id: "session-summary-id",
  signal: "user_confirmed"  // +0.10 - high-value session summary
})
```

## Session Summary Template

```markdown
# Session Summary: [Date]

## Work Completed
-

## Key Decisions
-

## Patterns Established
-

## Issues Encountered
-

## Next Steps
-

## Context for Resume
- [any critical context to preserve]
```