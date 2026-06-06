# Changelog

All notable changes to RE_Playground will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] — 2026-06-06

### Added

#### Core Infrastructure
- 15 specialist AI agents with reverse engineering personas (orchestrator, architect, coder, tester, linter, explorer, git, writer, scraper, release, agent-builder, init, handoff, researcher, MCP specialist)
- 8-step Boomerang Protocol enforcement (memory query → think → plan → delegate → git check → quality gates → doc update → memory save)
- Agent routing matrix with code-level enforcement (wrong-routing blocked)
- Parallel agent dispatch support (up to 10 concurrent on Ollama Cloud)
- LLM multi-provider support with 5 pre-configured providers: Ollama Cloud, OpenRouter, Anthropic, OpenAI, Google AI
- Persona customization system with `## Persona` H2 sections and `PERSONA-MARKER` structural delimiters

#### Reverse Engineering Tools (installer)
- Cross-distro TUI installer (`install.py`) supporting Arch/CachyOS, Debian/Ubuntu, macOS
- 18 tools in 5 groups: RE Core (9), Runtime (1), Android (1), Network (2), Build (4)
- Tools: JADX, Apktool, dex2jar, baksmali, smali, Frida, radare2, Binwalk, Ghidra, OpenJDK 17+, ADB, mitmproxy, Wireshark, Git, Python 3, Node.js, uv
- Interactive checkbox TUI (questionary) with `--check`, `--list`, `--yes` flags
- Venv bootstrap for PEP 668 compliance on Debian/Ubuntu

#### MCP Server Integration
- Ghidra MCP (245 tools): decompilation, disassembly, data flow, P-code emulation, live debugger, cross-binary matching
- radare2-mcp: native C server with readonly/sandbox/restrict modes
- memini-ai-dev: PostgreSQL + pgvector semantic memory with trust engine, knowledge graph, tiered loading
- searxng: web search (enabled); github-mcp, markitdown, playwright (disabled by default)

#### Semantic Memory (memini-ai)
- Trust engine with feedback signals (agent_used +0.05, user_confirmed +0.10, agent_ignored -0.05, user_corrected -0.10)
- Memory graph with relationships: SUPERSEDES, PARTIAL_UPDATE, RELATED_TO, CONTRADICTS, DERIVED_FROM
- Tiered loading: L0 (~100 tokens), L1 (~2K tokens), L2 (full context)
- Knowledge graph with entity extraction, inference chains, contradiction detection, dialectic engine
- Thought chains: structured multi-step reasoning stored and searchable
- Multi-peer support with peer-specific memory scopes
- Decay engine for automatic trust degradation

#### Configuration & CLI
- `setup.py` configuration orchestrator with subcommands: init, provider, persona, status, reset
- Provider management: add, set, remove with multi-provider merge
- Persona management: apply, reset, list, apply-group
- `boomerang-init` skill: 9-phase first-run setup (discovery → interview → research → mapping → temperature → reasoning → config → persona → state)
- `boomerang-customize` skill: guided walkthrough for writing agent personas
- Provider template library (`.opencode/providers/`) with curated model catalogs
- Env-var driven config with `.env.example` documenting all variables

#### v0.5.0 Permission Overhaul
- Replaced wildcard `memini-ai-dev_*: allow` with explicit per-agent allow-lists
- 57-73% reduction in tool description tokens per agent request
- Per-agent tool counts: orchestrator (11), architect (17), coder (8), explorer (3), tester (5), git (2), writer (3), release (4), init (5), handoff (6), linter (2), agent-builder (5), MCP specialist (4)

#### Documentation
- Comprehensive README.md (1,036 lines, 20 sections)
- RE-Playbook.md methodology wiki (curated tools, techniques, patterns, appendices)
- AGENTS.md: full agent roster, routing matrix, protocol specification
- CONTEXT.md: project context, workflows, conventions, MCP reference
- `.env.example`: annotated template for all environment variables

#### Security
- No hardcoded API keys in config (all `{env:VARIABLE_NAME}` references)
- No vendor binaries shipped (all tools pulled from package managers)
- No database dump (methodology in RE-Playbook.md)
- No vendor-specific content (sanitized from distributable files)
- `.gitignore` covers `.env`, secrets, node_modules, Python cache, build artifacts
