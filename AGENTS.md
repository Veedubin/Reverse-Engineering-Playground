# Reverse Engineering Agent Roster

## ⚡ CRITICAL: memini-ai Memory Protocol (MUST FOLLOW)

All agents **MUST** interact with memini-ai at every step:
1. **Query FIRST** — Call `memini-ai-dev_query_memories` before starting work
2. **Save DURING** — Call `memini-ai-dev_add_memory` after every meaningful decision
3. **Preserve CONTEXT** — Save important context; query it back when continuing work

Failure to use memini-ai causes context loss, duplicate work, and wasted tokens.

## Core Agents

> **Note**: Models are configurable. Edit `.opencode/opencode.json` to customize.

| Agent | Skill | Recommended Ollama Cloud Model | Technical Justification |
|-------|-------|------------------------------|------------------------|
| **boomerang** | boomerang-orchestrator | kimi-k2.6:cloud | Specifically built for swarm-based task orchestration and proactive autonomous delegation. |
| **re-coder** | boomerang-coder | glm-5.1:cloud | Flagship for agentic engineering; achieves SOTA on SWE-Bench Pro for complex, multi-file generation. |
| **re-architect** | boomerang-architect | deepseek-v4-pro:cloud | Offers frontier reasoning with dedicated "thinking modes" for analyzing complex architectural trade-offs in binaries. |
| **re-explorer** | boomerang-explorer | devstral-2:123b-cloud | Explicitly designed to navigate codebases, trace dependencies, and map repository/binary structures. |
| **re-tester** | boomerang-tester | deepseek-v4-flash:cloud | Massive 1M context window for ingesting deep error logs and analysis context quickly and efficiently. |
| **re-linter** | boomerang-linter | qwen3-coder-next:cloud | Highly optimized for agentic coding workflows; blazing fast for syntax formatting and style checks. |
| **re-git** | boomerang-git | minimax-m2.7:cloud | Fast and highly reliable for standard professional productivity and executing structured terminal commands. |
| **re-writer** | boomerang-writer | gemma4:31b-cloud | Frontier-level instruction following; excels at translating technical logic into clean, readable Markdown. |
| **re-scraper** | boomerang-scraper | qwen3.5:cloud | Strong, lightweight generalist with excellent tool-use capabilities for reliable data extraction. |
| **re-release** | boomerang-release | devstral-small-2:24b-cloud | Fast 24B model perfect for targeted automation tasks like bumping versions and summarizing changelogs. |
| **re-agent-builder** | boomerang-agent-builder | glm-5.1:cloud | Excels at long-horizon tasks and ambiguous problems; ideal for writing and optimizing new agent logic. |
| **researcher** | researcher | kimi-k2.6:cloud | Advances practical capabilities in long-horizon research, data synthesis, and multi-step tool execution. |
| **mcp-specialist** | mcp-specialist | glm-5.1:cloud | SOTA on Terminal-Bench 2.0; the most capable model for debugging servers and designing complex tool protocols. |

| Skill | Purpose | Model |
|-------|---------|-------|
| **boomerang-init** | Initialize and personalize agents for a project | kimi-k2.6:cloud |
| **boomerang-handoff** | Wrap-up session. Updates docs, saves context | kimi-k2.6:cloud |
| **boomerang-agent-builder** | Build new skills and sub-agents from patterns | glm-5.1:cloud |

## Reverse Engineering Tools

This project uses **Ghidra MCP** (245 tools) and **radare2-mcp** for binary analysis.

### Ghidra MCP
- **245 MCP tools** — Decompilation, disassembly, function analysis, data flow, P-code emulation, debugger integration
- **Headless mode** — Docker-ready for CI/CD and automated analysis
- **Convention enforcement** — Auto-fix naming, warn on style violations, reject no-op changes
- **Cross-binary documentation** — SHA-256 hash matching propagates docs across binary versions
- **Server**: `python /opt/ghidra-mcp/bridge_mcp_ghidra.py` (stdio transport) or HTTP on port 8089

### radare2-mcp
- **Native C implementation** using r2 APIs
- **CLI, plugin, and MCP server modes**
- **Connect to any local or remote r2/iaito session** via r2pipe
- **Readonly mode, sandbox lock, restrict tools** for safe analysis
- **Server**: `r2pm -r r2mcp` (stdio transport) or HTTP with `-H <port>`

### Tool Naming in MCP
- Ghidra tools are exposed as `ghidra_*` (e.g., `ghidra_decompile_function`, `ghidra_list_functions`)
- radare2 tools are exposed as `radare2_*` (e.g., `radare2_disassemble`, `radare2_analyze_functions`)

## Mandatory Routing Matrix (CODE-LEVEL ENFORCED)

The orchestrator MUST delegate based on these rules. No exceptions.

| Task Type | Primary Agent | When to Use | NEVER delegate to |
|-----------|--------------|-------------|-------------------|
| Binary analysis / decompilation | `re-architect` | Analyzing binary structure, function logic, data flow | `general`, `re-coder` |
| Code implementation | `re-coder` | Writing/editing scripts, tools, config | `general`, `re-explorer` |
| Architecture/design | `re-architect` | System design, trade-offs, research | `general`, `re-coder` |
| File finding | `re-explorer` | ONLY glob/find operations | Everything else |
| Testing | `re-tester` | Test writing, test execution | `general`, `re-coder` |
| Linting/formatting | `re-linter` | Code style enforcement | Everything else |
| Git operations | `re-git` | Commits, branches, tags | Everything else |
| Documentation | `re-writer` | Markdown, README, docs | `general` |
| Web scraping | `re-scraper` | URL fetching, data extraction | `general` |
| MCP/server debug | `mcp-specialist` | MCP protocol, server issues | `general` |
| Release automation | `re-release` | Version bumps, changelogs | Everything else |

### Enforcement Rules
1. **NEVER use `general` agent for code** — `general` is ONLY for research/info tasks
2. **NEVER delegate research to `re-explorer`** — explorer is file-finding only
3. **ALWAYS prefer specialist over generalist** — coder > general for code
4. **If unsure, query memini-ai** — Ask memory for which agent handled similar tasks

### Consequences of Wrong Routing

| Violation | Consequence | Severity |
|-----------|-------------|----------|
| Code to `general` | Context loss, no memory integration, suboptimal code | HIGH |
| Research to `explorer` | Superficial analysis, no knowledge graph, wasted tokens | HIGH |
| Tests to `coder` | Missing coverage, no test infrastructure awareness | MEDIUM |
| Style to `coder` | Inconsistent formatting, linter config ignored | LOW |
| File finding to `architect` | Wasted reasoning cycles on trivial glob operations | LOW |

> **Routing errors compound** — wrong agent → wrong context → wrong output → retry loop. Correct routing on first dispatch saves 2-5x tokens and time.

## Agent Selection Guide

| Task Type | → Primary Agent | Model | Never Delegate To |
|-----------|------------------|-------|-------------------|
| Complex planning / orchestration | `boomerang` | kimi-k2.6:cloud | `general` |
| Binary analysis / decompilation workflow | `re-architect` | deepseek-v4-pro:cloud | `general`, `re-coder` |
| Architecture / design decisions | `re-architect` | deepseek-v4-pro:cloud | `general`, `re-coder` |
| Documentation writing | `re-writer` | gemma4:31b-cloud | `general` |
| Session initialization | `boomerang-init` | kimi-k2.6:cloud | Everything else |
| Session wrap-up / handoff | `boomerang-handoff` | kimi-k2.6:cloud | Everything else |
| Skill/agent creation | `re-agent-builder` | glm-5.1:cloud | `general` |
| Fast code generation / bug fixes | `re-coder` | glm-5.1:cloud | `general`, `re-explorer` |
| Code exploration / finding files | `re-explorer` | devstral-2:123b-cloud | Everything else |
| Writing / running tests | `re-tester` | deepseek-v4-flash:cloud | `general`, `re-coder` |
| Linting / formatting | `re-linter` | qwen3-coder-next:cloud | Everything else |
| Git operations | `re-git` | minimax-m2.7:cloud | Everything else |
| Web research / scraping | `re-scraper` | qwen3.5:cloud | `general` |
| MCP tool design / server debug | `mcp-specialist` | glm-5.1:cloud | `general` |
| Release automation | `re-release` | devstral-small-2:24b-cloud | Everything else |

> **Note**: User has Ollama Cloud with **10 concurrent model limit**. Models are configured by editing `.opencode/opencode.json`.

### Orchestrator Permissions (v3.0.0)

The orchestrator provides **intelligent routing and context building** — it primarily delegates to sub-agents but CAN edit documentation files directly (TASKS.md, AGENTS.md, CONTEXT.md, HANDOFF.md).

**Orchestrator Does:**
- Analyze request and detect task type
- Query memini-ai for relevant context
- Select appropriate agent based on task
- Build rich Context Package with all necessary information
- Edit documentation and todo lists directly
- Return `{agent, systemPrompt, contextPackage, suggestions}` to OpenCode

**Orchestrator Delegates:**
- Agent execution → OpenCode (native)
- Code implementation → re-coder
- Testing → re-tester
- Linting → re-linter
- Git operations → re-git
- Multi-file changes → sub-agents
- Complex implementation → re-coder
- Architecture decisions → re-architect

**PARALLEL EXECUTION IS MANDATORY** — The orchestrator MUST launch multiple sub-agents simultaneously when tasks have no dependencies. Examples:
- Linter + Tester for independent validation
- Coder + Writer for code + documentation
- Multiple Coders for unrelated file changes

**Decision Threshold:**
```
Task Size ≤ 1 file AND ≤ 20 lines AND deterministic
    → Orchestrator handles directly

Task Size > 1 file OR > 20 lines OR needs analysis
    → Delegate to appropriate sub-agent
```

### Architect Reasoning Level

The `re-architect` agent uses **highest reasoning level** for Kimi K2.6 when creating implementation plans. The plan is handed back to the orchestrator as a "ready-to-run game plan" for dispatching coders, testers, etc.

## Protocol (MANDATORY)

All agents **MUST** follow the **8-Step Boomerang Protocol** — enforcement is **MANDATORY**.

### 8-Step Protocol (MANDATORY)

1. **Query Memory** — `memini-ai-dev_query_memories` FIRST
2. **Think** — `memini-ai-dev_add_thought` for complex tasks
3. **Plan** — Create/refine implementation plan (MANDATORY unless user explicitly waives)
4. **Delegate** — OpenCode executes selected agent with Context Package
5. **Git Check** — Verify working tree state before code changes
6. **Quality Gates** — Lint → Typecheck → Test
7. **Update Docs & Todos** — Update TASKS.md, todo list, AGENTS.md as needed
8. **Save Memory** — `memini-ai-dev_add_memory` with project tag

### Planning Enforcement

Planning is MANDATORY unless user explicitly waives with phrases like:
- "skip planning"
- "just do it"
- "/boomerang-handoff"
- "do a handoff"
- "no plan needed"

Simple tasks (handoff, status checks, single-file docs) may skip planning.
Build/create/implement tasks ALWAYS require planning.

### Context Passing

The orchestrator builds a complete Context Package with:
1. Original User Request (verbatim)
2. Task Background
3. Relevant Files
4. Code Snippets
5. Previous Decisions & Constraints
6. Expected Output Format
7. Scope Boundaries (IN vs OUT of scope)
8. Error Handling

### memini-ai Hub
- Query memini-ai BEFORE answering user
- Save to memini-ai AFTER answering user
- Pass context DIRECTLY to sub-agents (don't tell them to query memory)
- Sub-agents save detailed work to memory, return thin summaries

## Documentation Maintenance (Encouraged)

After EVERY session interaction, consider updating:

1. **TASKS.md** — Mark done, add new, remove outdated
2. **Todo List** — Mark completed, remove old, add new
3. **AGENTS.md** — Update if agent changes made
4. **README.md** — Update if user-facing changes
5. **HANDOFF.md** — Update at session end

> **Note**: Unlike previous versions, documentation updates are **MANDATORY** at handoff.

### memini-ai Integration Architecture (v3.0.0)

Boomerang v3 uses **memini-ai** for memory — a Python-based semantic memory server with trust scoring, knowledge graph, and tiered loading.

| Integration | Description |
|-------------|-------------|
| **Built-in** | Direct memini-ai integration via Python subprocess |
| **MCP (External)** | Standalone MCP server for non-boomerang users |

#### How memini-ai Memory Works

- memini-ai is a Python FastMCP server with PostgreSQL/pgvector backend
- Boomerang communicates via MCP protocol to memini-ai-dev tools
- All memory operations are async via MCP tool calls
- Trust scoring, knowledge graph, and tiered loading are built-in features

### Memory Operations (via MCP)

All agents SHOULD:
1. **Query memory FIRST** — `memini-ai-dev_query_memories` before work
2. **Use thought chains** — `memini-ai-dev_add_thought` for complex tasks
3. **Save results** — `memini-ai-dev_add_memory` when complete

### Trust-Weighted Memory

memini-ai uses a trust engine where every memory starts at trust=0.5 and is adjusted based on agent feedback:

| Signal | Trust Adjustment |
|--------|------------------|
| `agent_used` | +0.05 |
| `user_confirmed` | +0.10 |
| `agent_ignored` | -0.05 |
| `user_corrected` | -0.10 |

### Memory Graph

memini-ai tracks relationships between memories:

| Relationship | Description |
|-------------|-------------|
| `SUPERSEDES` | New memory replaces old one |
| `RELATED_TO` | Memories are semantically related |
| `CONTRADICTS` | Memories conflict |
| `DERIVED_FROM` | Memory was derived from another |

### Tiered Memory Architecture

memini-ai supports tiered memory loading for efficient context use:

| Tier | Description | Use Case |
|------|-------------|----------|
| **L0 Summary** | ~100 tokens, high-trust memories only | Session start |
| **L1 Key Decisions** | ~2K tokens, trust ≥ 0.8 | Planning |
| **L2 Full Context** | All memories | Deep research |

#### When Saving:
- **Routine work** (logs, quick fixes, explorations): Use standard `memini-ai-dev_add_memory`
- **High-value work** (architectural decisions, session summaries, verified successes): Use `memini-ai-dev_add_memory` with a descriptive `project` tag in metadata

#### When Searching:
- Default searches use the configured strategy automatically
- For explicit control: `memini-ai-dev_query_memories` with `strategy` parameter (`tiered`, `vector_only`, or `text_only`)

### Knowledge Graph Integration

memini-ai includes a knowledge graph for tracking entities and relationships:

| Tool | Purpose |
|------|---------|
| `memini-ai-dev_query_kg` | Execute formal KG queries |
| `memini-ai-dev_extract_entities` | Extract entities from a memory |
| `memini-ai-dev_get_entity_graph` | Get all connections for an entity |
| `memini-ai-dev_get_inference_chain` | Find inference paths between entities |
| `memini-ai-dev_search_entities` | Search for entities by name |

## Project-Specific Context

This is **reverse_engineering** — an AI-assisted reverse engineering project using Ghidra MCP (245 tools) and radare2-mcp for binary analysis, decompilation, and automated documentation.

## Agent Governance Rules (v3.0.0)

> **⚠️ CODE-LEVEL ENFORCED** — These rules are not optional guidelines.

### Research Ownership
- **re-architect** owns ALL research tasks (web searches, code analysis, documentation review)
- re-explorer is **file-finding only** - no pattern analysis or code research
- **memini-ai-dev_search_project** is the primary research tool for codebase investigation

### Orchestrator Delegation Rules
1. Research tasks → `re-architect` (NOT explorer)
2. File finding → `re-explorer` (only for glob/find operations)
3. Code implementation → `re-coder`
4. Never delegate research to explorer - architect handles it

### Agent Scope Boundaries

| Agent | Scope |
|-------|-------|
| re-explorer | Find files by name/glob ONLY |
| re-architect | Design + Research + Code analysis |
| re-coder | Code implementation |
| re-tester | Test writing |
| re-linter | Quality enforcement |

### Why This Matters
- Prevents duplicate work (explorer finds file, architect analyzes)
- Ensures proper context for design decisions
- Uses memini-ai search for efficient research

## Protocol Advisor v3.0.0

> **BREAKING CHANGE**: The Boomerang Protocol is now **MANDATORY** — it enforces all 8 steps and blocks execution if required steps are missing.

### Architecture: Mandatory State Machine

The protocol is implemented as a **mandatory state machine with enforcement at each step**:

```
IDLE → MEMORY_QUERY → SEQUENTIAL_THINK → PLAN → DELEGATE → GIT_CHECK → QUALITY_GATES → DOC_UPDATE → MEMORY_SAVE → COMPLETE
```

| Component | Purpose |
|-----------|---------|
| **ProtocolStateMachine** | Tracks state transitions for logging |
| **ProtocolAdvisor** | Enforces steps and blocks execution if required steps are missing |
| **TaskRunner** | Prompt builder only (no subprocess execution) |
| **DocTracker** | Tracks documentation changes via SHA-256 hash comparison |

### Strictness Levels (Enforced)

| Level | Behavior |
|-------|----------|
| **lenient** | Log suggestions, auto-fix logged |
| **standard** | Log warnings and suggestions (default) |
| **strict** | BLOCK execution if required steps are missing |

**Important**: v3.0.0 **blocks execution** if mandatory steps are missing in strict mode.

### 8-Step Mandatory Protocol

1. **MEMORY_QUERY** — MUST call `memini-ai-dev_query_memories` first
2. **THOUGHT_CHAIN** — MUST call `memini-ai-dev_add_thought` for complex tasks
3. **PLAN** — MUST create plan or delegate to architect for build tasks
4. **DELEGATE** — OpenCode handles agent execution
5. **GIT_CHECK** — MUST verify working tree state before code changes
6. **QUALITY_GATES** — MUST run lint/typecheck/test before completion
7. **DOC_UPDATE** — Track via DocTracker, update at handoff
8. **MEMORY_SAVE** — MUST save to memory when complete

### Enforcement Matrix

| Step | Requirement | Waiver Phrase |
|------|-------------|---------------|
| 1. Memory Query | MUST query memory first | None (always required) |
| 2. Thought Chains | MUST think for complex tasks | None (always required for complex) |
| 3. Planning | MUST plan or delegate to architect | "skip planning", "just do it", "no plan needed" |
| 4. Delegate | OpenCode executes | None |
| 5. Git Check | MUST verify working tree | "git is fine" |
| 6. Quality Gates | MUST run lint/typecheck/test | "skip tests", "skip gates" |
| 7. Doc Update | MUST update documentation | "no docs needed" |
| 8. Memory Save | MUST save to memory | None (always required) |

### Waiver Phrases (Escape Hatches)

| Phrase | Effect |
|--------|--------|
| `skip planning` | Skip planning for this turn |
| `just do it` | Skip planning and execute immediately |
| `no plan needed` | Skip planning for simple tasks |
| `skip tests` | Skip running tests |
| `skip gates` | Skip quality gates |
| `git is fine` | Skip git check |
| `--force` | Skip all checks (emergency) |
| `no docs needed` | Skip documentation update |

### memini-ai MCP Tools Available

| Tool | Purpose |
|------|---------|
| `memini-ai-dev_query_memories` | Semantic search over memories |
| `memini-ai-dev_add_memory` | Store a new memory entry |
| `memini-ai-dev_search_project` | Search indexed project files |
| `memini-ai-dev_index_project` | Trigger project indexing |
| `memini-ai-dev_get_file_contents` | Reconstruct file from indexed chunks |
| `memini-ai-dev_get_status` | Check memini-ai server status |
| `memini-ai-dev_query_kg` | Query knowledge graph |
| `memini-ai-dev_extract_entities` | Extract entities from memory |
| `memini-ai-dev_get_entity_graph` | Get entity connections |
| `memini-ai-dev_get_trust_score` | Get memory trust score |
| `memini-ai-dev_adjust_trust` | Adjust memory trust |
| `memini-ai-dev_find_contradictions` | Find contradictory memories |

---

### Ghidra MCP Tools (245 tools)

| Category | Example Tools |
|----------|---------------|
| **Function Analysis** | `decompile_function`, `disassemble_function`, `get_function_callers`, `get_function_callees`, `analyze_function_completeness` |
| **Memory & Data** | `read_memory`, `list_segments`, `search_byte_patterns`, `detect_array_bounds` |
| **Data Types** | `create_struct`, `add_struct_field`, `apply_data_type`, `list_data_types` |
| **Symbols & Labels** | `list_imports`, `list_exports`, `list_strings`, `create_label` |
| **Renaming & Docs** | `rename_function`, `set_decompiler_comment`, `batch_set_comments` |
| **Dynamic Analysis** | P-code emulation, live debugger integration (17 Java + 22 Python bridge tools) |
| **Cross-Binary** | `get_function_hash`, `propagate_documentation`, `bulk_fuzzy_match_functions` |

### radare2-mcp Tools

| Category | Capabilities |
|----------|--------------|
| **Binary Analysis** | Disassembly, function analysis, string extraction, section mapping |
| **Scripting** | r2js script execution, raw r2 command access |
| **Modes** | Stdio, HTTP server, r2 core plugin |
| **Safety** | Readonly mode, sandbox lock, restrict tools |

### Agent Permission Overhaul (v0.5.0 - In Progress)

**Problem**: Every agent uses `mode: subagent` with wildcard tool patterns (`"memini-ai-dev_*": allow`, `"searxng_*": allow`, etc.), exposing 100+ tools per request.

**Fix**: Replace wildcards with explicit allow-lists per agent role.

| Agent | Wildcards Removed | Memini Tools | GH MCP | Other |
|-------|-------------------|--------------|--------|-------|
| boomerang | memini-*, searxng*, markitdown*, github-mcp*, playwright*, webfetch, websearch | Core Memory (6) + Thought Chains (5) | No | No |
| re-coder | memini-*, searxng*, github-mcp*, playwright*, webfetch, websearch | Core (5) + Thought Chains (2) + search_project | No | No |
| re-architect | memini-* (most), searxng*, playwright*, webfetch, websearch | Full Memory + Full KG (7) + Thought Chains (2) + Project Index (3) | No | markitdown |
| re-explorer | memini-* | search_project, index_project, get_file_contents | No | No |
| re-tester | memini-*, searxng*, github-mcp*, playwright*, webfetch, websearch | query_memories, add_memory, adjust_trust, get_trust_score, search_project | No | No |
| re-git | memini-*, searxng*, markitdown*, playwright*, webfetch, websearch | query_memories, add_memory | Yes | git bash |
| re-writer | memini-* (most), searxng*, github-mcp*, playwright*, webfetch, websearch | query_memories, add_memory, get_tier0_summary | No | No |
| re-release | memini-* (most), github-mcp*, searxng*, markitdown*, playwright*, webfetch, websearch | query_memories, add_memory, adjust_trust, get_trust_score | No | npm version/publish bash, git tag bash |
| boomerang-init | memini-* (most), searxng*, github-mcp*, playwright*, webfetch, websearch | query_memories, get_tier0_summary, get_tier1_summary, list_peers, get_user_profile | No | No |
| boomerang-handoff | memini-* (most), searxng*, github-mcp*, playwright*, webfetch, websearch | query_memories, add_memory, get_tier0_summary, get_tier1_summary, adjust_trust, get_trust_score | No | No |
| re-linter | memini-* (most), searxng*, github-mcp*, playwright*, webfetch, websearch | query_memories, add_memory | No | No |
| re-agent-builder | memini-*, searxng*, github-mcp*, playwright*, webfetch, websearch | query_memories, add_memory, search_project, query_kg, extract_entities | No | skill tool, task to coder/writer |
| mcp-specialist | memini-* (most), searxng*, github-mcp*, playwright*, webfetch, websearch | query_memories, add_memory, query_kg, extract_entities | No | No |
| researcher | Unchanged | searxng, webfetch, websearch + core memini | No | — |
| re-scraper | Unchanged | searxng, webfetch + core memini | No | — |

**Corrections Applied**:
1. `re-release`: NO github-mcp tools, NO push to remote. Only local version bumps and git tags.
2. `re-git`: DOES get github-mcp tools for remote GH operations (PRs, branches, file updates).
3. `re-explorer`: NO memini-ai-dev except search_project, NO edit, NO bash, NO task.

## Review Notes

- **2026-05-30**: **reverse_engineering project initialized** — Copied boomerang-v3 agent framework, added Ghidra MCP and radare2-mcp MCP servers, retargeted all personas for reverse engineering, updated model list to full Ollama Cloud catalog.
- **2026-05-21**: **boomerang-v3 v0.5.0 RELEASED** — Agent permission overhaul: replaced wildcard tool patterns with explicit allow-lists per agent role. Security improvements: boomerang-release local-only (no github-mcp), boomerang-git gets remote github-mcp tools. ~57-73% token reduction per request.
- **2026-05-20**: **boomerang-v3 v0.4.3 RELEASED** — Fixed critical env var mismatch for thought chains: `MEMINI_THOUGHT_CHAINS_ENABLED` → `THOUGHT_CHAINS`. The memini-ai server uses `alias="THOUGHT_CHAINS"` (not `MEMINI_THOUGHT_CHAINS_ENABLED`). Requires OpenCode restart to load the corrected config.
- **2026-05-20**: **boomerang-v3 v0.4.2 RELEASED** — Removed deprecated `sequential-thinking` references from README, skills, and orchestrator SKILL.md. Added `MEMINI_THOUGHT_CHAINS_ENABLED: "true"` to root `opencode.json` (later corrected to `THOUGHT_CHAINS`).

- **2026-05-20**: **boomerang-v3 v0.4.1 TAG PUSHED** — Fixed git state: v0.4.1 tag was on commit c51bb6f (package.json showing 0.4.0). Committed working tree changes, deleted tag, recreated on correct commit 57e7c51 (package.json 0.4.1). Tag pushed. NPM publish workflow triggered after user renewed NPM_PUBLISH_TOKEN.
- **2026-05-20**: **boomerang-v3 v0.4.1 STAGED** — Git tag pushed, npm publish pending (user renewed token, workflow triggered).
- **2026-05-19**: **boomerang-v3 v0.4.1 STAGED** — Lint fixes (13 ESLint errors), context buffer, telemetry client. 127/127 tests, 0 lint errors. Git tag `v0.4.1` pushed. npm publish PENDING: awaiting token renewal in GitHub Actions secrets (v0.4.0 publish failure led to token discovery). Package exists on npm (v0.3.4).
- **2026-05-19**: **boomerang-v3 v0.3.1 RELEASED** — Added common bash commands (ls, head, tail, cat, grep, find, cd, echo) to 7 agent permission files. Tag `v0.3.1` pushed to GitHub.
- **2026-05-19**: **boomerang-v3 v0.3.0 RELEASED** — Agent permissions overhaul: `mode: subagent` + comprehensive tool permissions for all 30 agent files. SQL injection fix in boomerang-queue. Phase 3 Ollama Cloud Proxy design doc created. Tag `v0.3.0` pushed to GitHub.
- **2026-05-19**: **memini-ai-dev v0.2.8 RELEASED** — Ruff formatting pass (isort, whitespace, imports) across 30 files. No functional changes. Tag `v0.2.8` pushed to GitHub.
- **2026-05-19**: Updated to Ollama Cloud models — All agents reassigned to Ollama Cloud models with 10 concurrent limit. Created `.opencode/opencode.json` with `ollama-cloud` provider. Provider ID: `ollama`, baseURL: `https://ollama.com/v1`.
- **2026-05-18**: v3.0.0 RELEASED — memini-ai integration: Trust engine, knowledge graph, tiered loading. PostgreSQL with pgvector backend. 645 tests passing in memini-ai.
- **2026-05-06**: v4.1.0 (boomerang-v2) — Protocol enforcement: MANDATORY. Parallel agent launching.
- **2026-05-03**: v4.0.0 (boomerang-v2) — Orchestrator as pure decision layer, OpenCode handles execution.
