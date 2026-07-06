# Production Cross-Binary Diff — Implementation Plan

**Author:** re-architect (2026-07-06 boomerang dispatch)
**Status:** PLAN ONLY — not yet executed (no production binary supplied)
**Trigger:** 5th open-work item from the 2026-07-06 session-close (TASKS.md)

## What this plan does

Produces a function-level diff between a user-supplied production `llama-server`
and the upstream `llama.cpp` baseline pinned at commit `79b33b231`. Replaces
the symbol-only `cross-binary-match.py` with a Ghidra-MCP-driven workflow:

1. Exact-name match
2. Exact-hash match (catches recompiles)
3. Fuzzy structural match (catches renames + modifications)
4. Byte-level diff on attack-target functions
5. Classify every ADDED/MODIFIED/REMOVED as HARD / SOFT / NO-FINDING

## What it produces

- `binary/production-info.json` — SHA-256, format, size
- `docs/baseline-fingerprints.json` — function-level fingerprints of upstream
- `docs/production-fingerprints.json` — function-level fingerprints of prod
- `docs/match-table.json` — all 5 classifications (machine-readable)
- `docs/findings.json` — every finding with severity + rationale
- `docs/byte-diffs/<name>.diff` — one per MODIFIED attack-target function
- `docs/cross-binary-diff.md` — human-readable report

## Key tools

- `ghidra_mcp.import_file` — bring the production binary into the project
- `ghidra_mcp.list_functions_enhanced` — function list with thunk/external flags
- `ghidra_mcp.get_bulk_function_hashes` — BLAKE2b opcode hashes (100/batch)
- `ghidra_mcp.find_similar_functions_fuzzy` — cross-binary structural match
- `ghidra_mcp.diff_functions` — byte-level diff for attack-target MODIFIEDs
- `ghidra_mcp.merge_program_documentation` — bulk doc transfer (if needed)

## Hard-finding criteria (the "is this a finding?" answer)

A function is **HARD** if it:
- Has a name matching `HIGH_PRIORITY_KEYWORDS` (filter, censor, block, validate_output, redact, obfuscate, encrypt, etc.)
- Lives in attack-target area (logits, sampling, KV cache, output filtering)
- Is stripped + size > 200B
- Calls sensitive APIs (write, exec, ptrace, dlopen, mmap PROT_EXEC)
- References high-entropy rodata (XOR-encoded strings)

## Cost

20-90 min per audit run (without fuzzy); 1.5-3 h with full fuzzy pass.
Script-upgrade step (one-time): ~30 min + ~5K tokens for re-coder.

## Full plan

See the boomerang session transcript for the complete 10-section plan
with detailed step-by-step tool calls, pre-execution checklist (10 items),
output templates, classification rules, failure handling, and acceptance
criteria. The key sections:

- §1 Executive summary
- §2 Pre-execution checklist (10 items)
- §3 Step-by-step execution plan (8 steps)
- §4 Output format (`cross-binary-diff.md` template)
- §5 Classification rules (HARD / SOFT / NO-FINDING)
- §6 Failure handling (16 failure modes)
- §7 Estimated cost (20-90 min wall-clock)
- §8 Acceptance criteria (15 items)
- §9 What this plan deliberately does NOT do
- §10 Hand-off checklist

## When to run

Run when:
- The user supplies a production binary at `binary/llama-server-production`
  (or `binary/libllama.so-production`)
- The Ghidra MCP container is running (it is, as of 2026-07-06)

Do NOT run until both conditions hold.
