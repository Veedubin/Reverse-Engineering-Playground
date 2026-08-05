# Changelog

All notable changes to RE_Playground will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.6] — 2026-08-05

### Fixed

- **Ghidra MCP container rewritten for ghidra-mcp 5.15.0** — the bridge is now a proper Python package (`ghidra-mcp-bridge==5.15.0`); `docker/ghidra/Dockerfile` rebuilt as a multi-stage build and new `docker/ghidra/entrypoint.sh` launches the headless Java server (internal :8090) alongside the bridge (:8089). The old single-file bridge invocation no longer worked, so the container exposed no MCP tools.
- **Transport switched to streamable-http** — `.opencode/opencode.json` ghidra-mcp server now uses `streamable-http` on port 8089 with `GHIDRA_MCP_AUTH_TOKEN` bearer auth (the headless server refuses to bind `0.0.0.0` without it). Token lives in `.env.ghidra-mcp` (gitignored); see `.env.example`.
- `docker-compose.yml` / `podman-compose.yml` pass `GHIDRA_HEADLESS_PORT` and the auth-token env wiring.

### Added

- **`examples/llama-cpp-ghidra/`** — complete worked example: RE audit of the llama.cpp `llama-server`/`libllama` binaries with Ghidra MCP. Includes `METHODOLOGY.md` (448 lines), 7 deep-dive docs (sampling, KV-cache, logits production, output filtering, function index, cross-binary diff, production diff plan), and 3 reusable scripts (`build.sh`, `cross-binary-match.py`, `import-to-ghidra.sh`).

### Changed

- Agent model versions synced from workspace roster (boomerang-coder/writer/git/release/explorer/agent-builder, mcp-specialist).

## [0.2.0] — 2026-06-06

### Added

#### Windows / .NET RE Toolchain (6 new installer tools)
- **revula** — 116-tool all-in-one RE MCP server (PE/ELF/Mach-O, YARA, Capa, .NET IL, Frida, GDB, Android, exploit dev). Installed via `uv tool install 'revula[full]'`
- **ILSpyMcpServer** — .NET assembly decompiler (C#/VB.NET → source). Installed via `dotnet tool install -g ILSpyMcp.Server`
- **.NET SDK 9+** — runtime dependency for ilspycmd
- **diec (Detect It Easy CLI)** — packer / compiler / cryptor identification
- **YARA** — pattern-based malware identification (VirusTotal's rule engine)
- **pefile (Python)** — Python PE parser library
- New installer helpers: `_uv_tool_install`, `_pipx_or_pip_install`, `_dotnet_tool_install`
- Total tool count: 18 → 23 (RE Core group: 9 → 15)

#### MCP Server Expansion (3 new servers, all enabled by default)
- **revula** (stdio) — 116 RE tools under one roof
- **ilspy-mcp** (stdio) — .NET decompilation via natural language
- **die-mcp** (stdio) — Detect-It-Easy wrapper for packer/compiler ID
- Total MCP servers: 7 → 10, enabled: 4 → 7

#### Multi-Container Deployment
- `docker/core/Dockerfile` — OpenCode + 7 MCP servers + all RE tools (Ubuntu 24.04, tini entrypoint)
- `docker/ghidra/Dockerfile` — Ghidra 11.3.2 + ghidra-mcp bridge, JVM heap friendly, 4 GB mem_limit
- `docker/radare2/Dockerfile` — radare2 + rizin + r2mcp + Wine, with `SYS_PTRACE` capability for Win32 PE debug
- `docker/filebrowser/Dockerfile` — FileBrowser Quantum on `/samples` (the only `:rw` mount in the stack)
- `docker/radare2/entrypoint.sh` — health endpoint on :9090 + r2mcp launcher
- `docker-compose.yml` — 5-service stack: `core`, `ghidra`, `radare2`, `memini`, `files` on shared `re-net` bridge network
- `podman-compose.yml` — rootless variant with `userns_mode: keep-id`, `127.0.0.1:` port bindings, journald logging
- Shared volumes: `re-samples` (one-way ingress), `re-workspace`, `re-ghidra-projects`, `re-memini-data`, `re-memini-config`, `re-filebrowser-db`, `re-filebrowser-cfg`
- Healthchecks on every service; `depends_on` chains in correct order

#### Documentation
- `docs/learn-more.md` — curated reading list (419 lines) with GitHub links for 17 projects and 3-5 articles per tool
- `docs/container.md` — full multi-container deployment guide (413 lines) with file-ingress security model, LAN access patterns (Tailscale / nginx / 0.0.0.0), GPU passthrough, systemd unit, troubleshooting
- README "## Container Deployment" section added (66 lines, with ASCII architecture diagram)
- MCP server table in README expanded to 10 entries (7 enabled)
- Tool count and group totals corrected in README

### Security
- All new file paths in compose files are env-var driven or use named volumes
- No hardcoded API keys, paths, or secrets in any new file (validated: 0 hits for `github_pat_`, `gho_`, `sk-*`, `/home/jcharles`, `jayminwest`)
- 4 env-var references (`{env:OPENCODE_SERVER_PASSWORD}`, etc.) in `opencode.json` and compose files
- File ingress isolated to the `re-files` container; agent containers mount `/samples` read-only
- `SYS_PTRACE` capability scoped only to the `radare2` container

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
