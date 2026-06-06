# RE_Playground Project Context

> **Project**: RE_Playground — AI-assisted reverse engineering with Ghidra MCP and radare2-mcp
> **Based on**: boomerang-v3 v0.5.0 agent framework with memini-ai semantic memory

---

## Project Overview

RE_Playground is a self-contained, AI-assisted reverse engineering laboratory. Drop it anywhere, install the toolchain with the included cross-platform installer, and you have a multi-agent RE workstation with 15 specialist personas, 265+ MCP tools, and a curated methodology wiki.

Core components:
- **Ghidra MCP** (245 tools) — Decompilation, disassembly, data flow analysis, debugger integration
- **radare2-mcp** — Native C implementation with r2 APIs, r2js scripting, readonly/sandbox modes
- **memini-ai** — Semantic memory with trust scoring, knowledge graph, tiered loading
- **Boomerang v3** — Multi-agent orchestration with specialized RE personas

---

## MCP Servers

### Ghidra MCP
- **Tools**: 245 MCP tools covering decompilation, function analysis, memory inspection, data types, cross-binary documentation, P-code emulation, live debugging
- **Headless mode**: Docker-ready for CI/CD and automated analysis
- **Script execution**: Disabled by default — enable with `GHIDRA_MCP_ALLOW_SCRIPTS=1`
- **Connection**: `python /opt/ghidra-mcp/bridge_mcp_ghidra.py` (stdio transport) or HTTP on port 8089
- **Repository**: [bethington/ghidra-mcp](https://github.com/bethington/ghidra-mcp) (Apache-2.0)

### radare2-mcp
- **Native C implementation** using r2 APIs
- **Modes**: Stdio MCP, HTTP server (`-H <port>`), r2 core plugin
- **Safety**: Readonly mode (`--readonly`), sandbox lock (`--sandbox`), restricted tools (`--restrict`)
- **Connection**: `r2pm -r r2mcp` (stdio transport)
- **Repository**: [radareorg/radare2-mcp](https://github.com/radareorg/radare2-mcp) (MIT)

### memini-ai-dev
- **Backend**: PostgreSQL with pgvector extension
- **Features**: Trust engine, knowledge graph, tiered loading, thought chains, dialectic, multi-peer
- **Connection**: `uv run --directory $MEMINI_AI_DIR memini-ai --stdio`
- **Repository**: [memini-ai-dev](https://github.com/Veedubin/memini-ai-dev) (MIT)

### Additional MCP Servers
- **searxng** — Web search (enabled by default, requires SearXNG instance)
- **github-mcp** — GitHub API for PRs, issues, repos (disabled by default)
- **markitdown** — Document→Markdown conversion (disabled by default)
- **playwright** — Browser automation (disabled by default)
- **super-memory-ts** — Legacy Qdrant snapshot (disabled, do not enable — replaced by memini-ai)

---

## Agent Roster (Reverse Engineering Focus)

| Agent | Skill | Role |
|-------|-------|------|
| **boomerang** | orchestrator | Task routing and delegation |
| **re-architect** | architect | Binary analysis, decompilation workflows, architecture research |
| **re-coder** | coder | Script/tool implementation |
| **re-explorer** | explorer | File/binary finding (glob-only, not research) |
| **re-tester** | tester | Test writing and execution |
| **re-linter** | linter | Quality enforcement |
| **re-git** | git | Version control |
| **re-writer** | writer | Documentation |
| **re-scraper** | scraper | Web research |
| **re-release** | release | Version automation (local only) |
| **re-agent-builder** | agent-builder | Skill/agent creation |
| **researcher** | researcher | Long-horizon research |
| **mcp-specialist** | mcp-specialist | MCP protocol design/debug |

See `AGENTS.md` for the full routing matrix and agent selection guide.

---

## Reverse Engineering Workflows

### Binary Analysis Workflow
1. Load binary into Ghidra or radare2
2. Run auto-analysis
3. Use `re-architect` to plan analysis strategy
4. Decompile key functions via Ghidra MCP
5. Cross-reference with radare2 for disassembly details
6. Document findings with memini-ai

### Function Documentation Workflow (Ghidra V5)
1. Select function for documentation
2. `ghidra_decompile_function` for C pseudocode
3. `ghidra_analyze_function_completeness` for scoring
4. Apply naming conventions (Hungarian notation)
5. `ghidra_batch_set_comments` for documentation
6. Save documentation to memini-ai with trust scoring

### Cross-Binary Matching
1. `ghidra_get_function_hash` for SHA-256 of normalized opcodes
2. `ghidra_build_function_hash_index` for persistent index
3. `ghidra_lookup_function_by_hash` to find matches
4. `ghidra_propagate_documentation` to apply docs across versions

### Dynamic Analysis (Ghidra)
1. Start debugger server (`python -m debugger`)
2. Attach to process via `ghidra_debugger_attach`
3. Set breakpoints, step through execution
4. `ghidra_read_memory` for runtime memory inspection
5. P-code emulation for isolated function execution

---

## Reverse Engineering Conventions

### Naming Conventions (Ghidra MCP v5)
- **Auto-fix**: `count` on `uint32` → auto-prefixed `dwCount` on save
- **Warn**: `processData` → "name should be PascalCase with a verb: `ProcessData`"
- **Reject**: `undefined → undefined` type change → "no-op rejected"
- **Disable enforcement**: Edit > Tool Options > GhidraMCP HTTP Server > Strict Naming Enforcement

### Comment Types
| Type | Location | Use For |
|------|----------|---------|
| **Plate** | Function header | High-level purpose, parameters, return value |
| **Pre** | Before instruction | Preconditions, setup notes |
| **EOL** | End of line | Specific line explanations |
| **Post** | After instruction | Postconditions, side effects |

### Data Type Prefixes (Hungarian)
| Prefix | Type | Example |
|--------|------|---------|
| `b` | `bool` | `bIsValid` |
| `c` | `char` | `cFlag` |
| `dw` | `uint32` | `dwCount` |
| `w` | `uint16` | `wFlags` |
| `qw` | `uint64` | `qwTimestamp` |
| `p` | pointer | `pBuffer` |
| `sz` | `char*` (string) | `szName` |
| `pfn` | function pointer | `pfnCallback` |

---

## Memory Saving Conventions

After completing reverse engineering work, save to memini-ai with these tags:

```json
{
  "metadata": {
    "project": "reverse_engineering",
    "type": "function_analysis",
    "binary": "program.exe",
    "function_address": "0x401000",
    "tools_used": ["ghidra", "radare2"]
  }
}
```

### Memory Types
| Type | When to Use |
|------|-------------|
| `binary_metadata` | Program info, entry points, segments, imports/exports |
| `function_analysis` | Decompilation, disassembly, control flow, calling conventions |
| `data_structure` | Struct layout, field analysis, enum values, type discovery |
| `string_analysis` | Extracted strings, regex matches, string-anchored function discovery |
| `cross_binary_match` | Function hashes, documentation propagation, version comparison |
| `debug_session` | Debugger output, register states, memory dumps, trace logs |
| `script_tool` | Custom Ghidra scripts, r2js scripts, automation tools |
| `cve_vulnerability` | CVE mappings, patch diffing, vulnerability analysis |

---

## Safety and Sandboxing

### Ghidra MCP Security
| Feature | Description |
|---|---|
| **localhost-only by default** | HTTP server bound to `127.0.0.1`; no remote access without explicit configuration |
| **Script endpoints off by default** | Set `GHIDRA_MCP_ALLOW_SCRIPTS=1` to enable |
| **Path traversal protection** | Set `GHIDRA_MCP_FILE_ROOT` to restrict filesystem access |
| **Auth for LAN exposure** | Set `GHIDRA_MCP_AUTH_TOKEN` before binding to `0.0.0.0` |

### radare2-mcp Security
| Feature | Flag |
|---|---|
| **Readonly mode** | `--readonly` — prevents all write operations |
| **Sandbox lock** | `--sandbox` — restricts dangerous commands |
| **Restrict tools** | `--restrict` — limits available tool set |
| **YOLO mode** | `--yolo` — disables approvals (use only in trusted environments) |

---

## 8-Step Protocol Quick Reference

All agents MUST follow this sequence for every task:

1. **MEMORY_QUERY** — `memini-ai-dev_query_memories` first
2. **THOUGHT_CHAIN** — `memini-ai-dev_add_thought` for complex tasks
3. **PLAN** — Create/refine plan (waived by: "skip planning", "just do it")
4. **DELEGATE** — OpenCode executes agent with Context Package
5. **GIT_CHECK** — `git status` before code changes (waived by: "git is fine")
6. **QUALITY_GATES** — Lint → Typecheck → Test (waived by: "skip tests")
7. **DOC_UPDATE** — Update TASKS.md / AGENTS.md / HANDOFF.md (waived by: "no docs needed")
8. **MEMORY_SAVE** — `memini-ai-dev_add_memory` with project tag

---

## Related Projects

| Project | URL | Purpose | License |
|---------|-----|---------|---------|
| Ghidra MCP | https://github.com/bethington/ghidra-mcp | 245-tool MCP bridge for Ghidra | Apache-2.0 |
| radare2-mcp | https://github.com/radareorg/radare2-mcp | radare2 MCP server | MIT |
| Ghidra | https://ghidra-sre.org/ | NSA's reverse engineering framework | Apache-2.0 |
| radare2 | https://radare.org/ | Open source reverse engineering framework | LGPL 3.0 |
| re-universe | https://github.com/bethington/re-universe | Ghidra BSim PostgreSQL platform for binary similarity | Apache-2.0 |
| Boomerang-v3 | https://github.com/Veedubin/Boomerang-v3 | Multi-agent orchestration framework | MIT |

### Resource Repositories

| Collection | URL | Highlights |
|------------|-----|------------|
| amilarajans/ghidra_scripts | https://github.com/amilarajans/ghidra_scripts | ARM/MIPS ROP finders, Call Chain, Codatify, Function Profiler, Leaf Blower, Rizzo, RC4 Decrypter, YARA search, Swift/Go renamers, stack strings, shellcode hashes |
| radare2 built-in scripts | https://github.com/radareorg/radare2/tree/master/scripts | english.r2.js, il2cpp.r2.js, ipsw-kernel-symbolicate.r2.js, vsmap.r2.js, unzip.r2.js, r2sptrace.py |
| WithSecureLabs/radare2-scripts | https://github.com/WithSecureLabs/radare2-scripts | r2_bin_carver.py, r2_hash_func_decoder.py |
| radareorg/awesome-radare2 | https://github.com/radareorg/awesome-radare2 | Curated list of 70+ r2 tools, scripts, articles, CTF writeups |
