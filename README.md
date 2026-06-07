# Reverse Engineering Playground

<div align="center">

**A self-contained, AI-assisted reverse engineering laboratory for [OpenCode](https://opencode.ai).**

15 specialist agents &bull; Ghidra MCP (245 tools) &bull; radare2-mcp &bull; semantic memory &bull; cross-distro installer &bull; multi-provider LLM support

[![CI: validate](https://img.shields.io/github/actions/workflow/status/Veedubin/Reverse-Engineering-Playground/validate.yml?branch=master&label=validate&logo=github)](https://github.com/Veedubin/Reverse-Engineering-Playground/actions/workflows/validate.yml)
[![CI: build-containers](https://img.shields.io/github/actions/workflow/status/Veedubin/Reverse-Engineering-Playground/build-containers.yml?label=build-containers&logo=github)](https://github.com/Veedubin/Reverse-Engineering-Playground/actions/workflows/build-containers.yml)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/Veedubin/Reverse-Engineering-Playground?include_prereleases)](https://github.com/Veedubin/Reverse-Engineering-Playground/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/Veedubin/Reverse-Engineering-Playground?style=social)](https://github.com/Veedubin/Reverse-Engineering-Playground/stargazers)

</div>

---

## What is Reverse Engineering Playground?

Reverse Engineering Playground (tagline: `RE_Playground`) is a drop-in reverse engineering workspace for [OpenCode](https://opencode.ai) that combines **15 specialized AI agents** with **265+ MCP tools** for binary analysis, decompilation, dynamic instrumentation, and semantic documentation.

It ships as a pre-configured [OpenCode](https://opencode.ai) project built on the [Boomerang v3](https://github.com/Veedubin/Boomerang-v3) OpenCode plugin (multi-agent orchestration) and the [memini-ai](https://github.com/Veedubin/memini-ai-dev) semantic memory server. Clone it, run the installer, and you have a multi-agent RE workstation with a curated methodology wiki and trust-weighted memory — no vendor binaries shipped, everything pulled from your distro's package manager, Homebrew, pip, or npm.

**You bring a binary. The agents bring everything else.**

- Load an APK, ELF, or PE into Ghidra or radare2
- Ask the architect agent to plan an analysis strategy
- Watch agents decompile, annotate, cross-reference, and document — automatically
- All findings are saved to a trust-weighted semantic memory that improves with every session

### What can you do with it?

| Capability | How |
|---|---|
| **APK / DEX analysis** | Decompile to Java source (JADX), decode/rebuild (Apktool), DEX→JAR conversion, smali disassembly/reassembly |
| **Native binary reverse engineering** | ARM/x86/ELF/PE analysis via Ghidra (NSA's SRE framework) and radare2, with AI-guided navigation |
| **Dynamic instrumentation** | Frida for runtime hooking, tracing, and memory manipulation |
| **Network protocol analysis** | mitmproxy for HTTPS interception, Wireshark for packet capture |
| **Firmware extraction** | Binwalk for carving filesystems, kernels, and bootloaders from firmware images |
| **Cross-binary documentation** | SHA-256 function hashing propagates analysis across binary versions |
| **Live debugging** | Ghidra debugger with breakpoints, register inspection, memory watchpoints, function tracing |
| **P-code emulation** | Isolated function execution for understanding behavior without running the target |
| **Semantic search** | PostgreSQL + pgvector memory indexed by embedding, searchable by concept |
| **Trust-weighted knowledge** | Every finding has a trust score; used findings get promoted, wrong findings get corrected |
| **Knowledge graph** | Entities and relationships tracked across sessions — inference paths between concepts |
| **Multi-provider LLM** | 5 providers pre-configured (Ollama Cloud, OpenRouter, Anthropic, OpenAI, Google AI) |
| **Persona customization** | Every agent can be given a specific focus area via CLI or in-app skill |

---

## Table of Contents

- [Quick Start](#quick-start)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
  - [Supported Platforms](#supported-platforms)
  - [The Install Script](#the-install-script)
  - [Manual Installs](#manual-installs)
- [The Agent Roster](#the-agent-roster)
  - [Agent Routing Matrix](#agent-routing-matrix)
  - [Agent Selection Guide](#agent-selection-guide)
- [MCP Server Integration](#mcp-server-integration)
  - [Ghidra MCP (245 tools)](#ghidra-mcp-245-tools)
  - [radare2-mcp](#radare2-mcp)
  - [memini-ai (Semantic Memory)](#memini-ai-semantic-memory)
  - [Additional MCP Servers](#additional-mcp-servers)
- [LLM Providers](#llm-providers)
  - [Pre-configured Providers](#pre-configured-providers)
  - [Managing Providers via CLI](#managing-providers-via-cli)
  - [Adding a Custom Provider](#adding-a-custom-provider)
- [The Methodology Wiki](#the-methodology-wiki)
- [Persona Customization](#persona-customization)
  - [How the Persona System Works](#how-the-persona-system-works)
  - [Managing Personas via CLI](#managing-personas-via-cli)
  - [The boomerang-customize Skill](#the-boomerang-customize-skill)
- [The 8-Step Boomerang Protocol](#the-8-step-boomerang-protocol)
- [Reverse Engineering Workflows](#reverse-engineering-workflows)
  - [Binary Analysis Workflow](#binary-analysis-workflow)
  - [Function Documentation Workflow (Ghidra V5)](#function-documentation-workflow-ghidra-v5)
  - [Cross-Binary Matching](#cross-binary-matching)
  - [Dynamic Analysis (Live Debugging)](#dynamic-analysis-live-debugging)
- [Container Deployment](#container-deployment)
- [Safety and Sandboxing](#safety-and-sandboxing)
- [CLI Reference](#cli-reference)
  - [setup.py — Configuration Orchestrator](#setuppy--configuration-orchestrator)
  - [install.py — Toolchain Installer](#installpy--toolchain-installer)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

---

## Quick Start

```bash
# 1. Clone or drop RE_Playground/ anywhere on disk
cd RE_Playground

# 2. Install the RE toolchain (interactive TUI, all 18 tools checked by default)
python3 install.py
# Press <space> to toggle tools on/off, <enter> to confirm.

# 3. Configure your LLM provider secrets
cp .env.example .env
$EDITOR .env
# Set at minimum: OLLAMA_API_KEY (or the API key for whichever provider you prefer)

# 4. Pick your providers
./setup.py provider add ollama-cloud    # or openrouter, anthropic, openai, google
./setup.py provider add openrouter      # add multiple — multi-provider merge is native

# 5. Launch OpenCode with the bundled agent framework
cd .opencode
npm install
opencode                              # 15 agents, 265+ MCP tools, all ready
```

That's it. You now have a multi-agent RE workstation with a curated methodology wiki, trust-weighted memory, and AI-powered binary analysis.

**Want a guided first-run setup?** Run `./setup.py init` instead of steps 4-5. It will walk you through provider selection, model assignment, and persona customization interactively.

---

## Features

### Core Infrastructure

- **15 specialist AI agents** — architect, coder, tester, linter, explorer, git, writer, scraper, release, agent-builder, init, handoff, orchestrator, researcher, MCP specialist
- **8-step Boomerang Protocol** — disciplined, auditable workflow enforced per agent: memory query → think → plan → delegate → git check → quality gates → doc update → memory save
- **Agent routing matrix** — task types mapped to correct agent automatically; wrong routing blocked
- **Parallel agent dispatch** — orchestrator launches multiple agents simultaneously when tasks have no dependencies (up to 10 concurrent on Ollama Cloud)

### Reverse Engineering Tools (auto-installed)

- **Ghidra MCP** — 245 MCP tools bridging the full Ghidra API: decompilation, disassembly, data flow analysis, P-code emulation, live debugging, cross-binary matching
- **radare2-mcp** — Native C MCP server for fast binary triage, disassembly, string extraction, section mapping, r2js scripting
- **revula** — 116-tool RE MCP server: PE/ELF/Mach-O parsing, YARA, Capa ATT&CK mapping, .NET IL, Frida injection, GDB debugging, Android RE, ROP/heap exploit dev, deobfuscation ([president-xd/revula](https://github.com/president-xd/revula))
- **ILSpyMcpServer** — Decompile .NET assemblies (C#/VB.NET) to source via natural language
- **Detect-It-Easy (diec)** — Identify packer / compiler / cryptor on PE/ELF/Mach-O
- **YARA** — Pattern-based malware identification (VirusTotal's rule engine)
- **pefile** — Python PE parser used by revula and custom RE scripts
- **JADX** — APK/DEX → Java source decompiler
- **Apktool** — APK decode/rebuild with smali support
- **dex2jar / baksmali / smali** — DEX ↔ JAR conversion and smali assembly/disassembly
- **Frida** — Dynamic instrumentation toolkit (Python bindings via pip)
- **Binwalk** — Firmware analysis and filesystem extraction
- **mitmproxy** — Interactive HTTPS intercepting proxy
- **Wireshark** — Deep packet inspection and protocol analysis

### Semantic Memory (memini-ai)

- **PostgreSQL + pgvector** backend with 384-dim MiniLM embeddings
- **Trust engine** — every memory starts at 0.5, adjusted by usage signals (agent_used +0.05, user_confirmed +0.10, agent_ignored -0.05, user_corrected -0.10)
- **Knowledge graph** — entities, relationships, inference chains across sessions
- **Tiered loading** — L0 (~100 token summary for session start), L1 (~2K token key decisions for planning), L2 (full context for deep research)
- **Thought chains** — structured multi-step reasoning stored and searchable
- **Contradiction detection** — finds conflicting memories before decisions are made
- **Dialectic engine** — challenge memories, generate resolutions, track argument history
- **Multi-peer** — multiple users/projects can coexist with peer-specific memory scopes
- **Decay engine** — low-trust memories fade automatically; high-value findings are sticky

### LLM Multi-Provider

- **5 providers** pre-configured with curated model catalogs: Ollama Cloud, OpenRouter, Anthropic, OpenAI, Google AI
- **Multi-provider merge** — opencode natively supports all providers active simultaneously; agents pick the best model per task
- **Provider templates** in `.opencode/providers/<id>.json` — each with `_meta`, `models`, and `recommended` (best/fast/cheap) tiers, `lastReviewed` date for freshness
- **Env-var driven** — all API keys read from `.env`, never hardcoded in config
- **Add your own** — copy a template, fill in models, run `setup.py provider add`

### Customization

- **Persona system** — every agent file has a `## Persona` H2 section with a `PERSONA-MARKER` structural delimiter; edit to focus agents on your specific RE domain
- **CLI persona management** — `setup.py persona --agent ... --description "..."` applies a persona; `--reset` reverts to default; `--apply-group` does a whole category at once
- **boomerang-customize skill** — in-app guided walkthrough for writing agent personas
- **boomerang-init skill** — 9-phase first-run setup: discovers your environment, interviews you, researches current model availability, maps agents to models, sets temperatures, configures reasoning effort, writes config, offers persona customization, saves state

### Documentation

- **RE-Playbook.md** — curated, trust-weighted methodology wiki with tools, techniques, patterns, and appendices
- **AGENTS.md** — full agent roster, routing matrix, protocol specification, governance rules
- **CONTEXT.md** — project context, environment details, MCP server config, model selection guide, RE conventions, troubleshooting
- **docs/learn-more.md** — curated reading list (3-5 articles per tool) with GitHub links for every tool
- **docs/container.md** — multi-container deployment guide (Docker / Podman) with file ingress + LAN access patterns
- **docs/windows-re/tools-and-mcp-servers.md** — Windows PE / .NET RE research and recommendations
- **.env.example** — annotated template documenting every environment variable with descriptions and where to get the values

---

## Container Deployment

For a self-contained, browser-only RE workstation, RE_Playground ships with a multi-container deployment. The agents stay inside containers; you only touch it from the browser. Desktop files are uploaded through a dedicated FileBrowser container that has no other network access.

### Architecture (5 containers)

```
  Browser
     │
   :4096 HTTP       OpenCode web UI + 7 enabled MCP servers
   :8080 HTTP       FileBrowser (sample ingress — only one with :rw on /samples)
     │
   re-net (bridge) — shared network between all 5 containers
     │
   ┌────┴────┬────────┬──────────┐
   ▼         ▼        ▼          ▼
re-ghidra  re-radare2  re-memini  re-files
:8089 MCP  :9090 MCP   pgvector  filebrowser
Ghidra SRE  r2mcp+Wine  memory    (same /samples vol, :ro from others)
+ 245 tools
```

### Quick start

```bash
git clone https://github.com/Veedubin/Reverse-Engineering-Playground.git
cd Reverse-Engineering-Playground
export OPENCODE_SERVER_PASSWORD="$(openssl rand -hex 16)"
docker compose up -d --build        # or: podman-compose up -d --build
# Open http://localhost:4096 (OpenCode)
# Open http://localhost:8080 (FileBrowser — upload target.exe here)
```

### Why multi-container (not one fat image)?

- **Smaller images** — Ghidra's 400 MB JVM doesn't ship in the core image
- **Independent scaling** — `docker compose up --scale ghidra=2` if you need two Ghidra instances
- **Tighter isolation** — Wine's `SYS_PTRACE` is only on the r2 container; if r2 is pwned, core/ghidra/memini are untouched
- **Cleaner security model** — only `re-files` has write access to `/samples`; everything else mounts `:ro`
- **Runtime choice** — the same compose file works under Docker **and** rootless Podman

### File ingress (the security bit)

The desktop cannot reach the agents directly. The flow is:

1. You open `http://localhost:8080` (FileBrowser)
2. Upload `target.exe` to FileBrowser's web UI
3. FileBrowser writes it to the `re-samples` named volume
4. All 4 other containers see the file appear at their own `/samples` mount
5. You tell the agent: "analyze /samples/target.exe"
6. Agent runs `r2`, `ghidra`, `diec`, `yara` against the file — all inside the container network

The agents **cannot** read your home directory, `~/.ssh`, browser cookies, or anything else on your host. Even if a malicious PE exploits Frida and escapes its container, your filesystem is on a different Docker volume entirely.

### LAN access

Three options, in order of recommendation:

1. **Tailscale** (zero-config WireGuard mesh) — install on host + every client, reach the UI at `<host-tailscale-ip>:4096`
2. **nginx + Let's Encrypt** (public HTTPS with a real domain) — full reverse-proxy config in `docs/container.md`
3. **`0.0.0.0` bind** (trusted LAN only) — change `"127.0.0.1:4096:4096"` to `"4096:4096"` in `docker-compose.yml`

See **[`docs/container.md`](docs/container.md)** for the full guide: systemd integration, GPU passthrough, persistent volume backups, port troubleshooting, GPU/NVIDIA setup, and Podman rootless specifics.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                          OpenCode IDE                             │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    Boomerang v3 Orchestrator                  │ │
│  │  Routes tasks → dispatches agents → enforces 8-step protocol │ │
│  └─────────────────────────────────────────────────────────────┘ │
│           │                │                │                     │
│     ┌─────▼─────┐   ┌──────▼──────┐   ┌────▼────────┐           │
│     │ re-architect │   │  re-coder   │   │ re-tester   │  ...      │
│     │  (analysis)  │   │ (impl)      │   │  (quality)  │  (15 total)│
│     └─────┬─────┘   └──────┬──────┘   └────┬────────┘           │
│           │                │                │                     │
│  ┌────────▼────────────────▼────────────────▼────────────────┐  │
│  │                     MCP Protocol Layer                      │  │
│  │  ghidra-mcp (245) │ radare2-mcp │ memini-ai-dev │ searxng   │  │
│  │  markitdown │ playwright │ github-mcp (disabled)            │  │
│  └────────┬────────────────┬────────────────┬────────────────┘  │
│           │                │                │                     │
└───────────┼────────────────┼────────────────┼─────────────────────┘
            │                │                │
      ┌─────▼─────┐   ┌──────▼──────┐   ┌────▼────────────┐
      │   Ghidra  │   │   radare2   │   │  PostgreSQL      │
      │  (NSA SRE) │   │  (r2mcp)   │   │  + pgvector      │
      │  245 tools │   │  fast triage│   │  (memini-ai)     │
      └───────────┘   └─────────────┘   └─────────────────┘
```

**Flow**: User request → Orchestrator queries memory → Creates plan → Dispatches specialist agent(s) → Agents call MCP tools (Ghidra/radare2/memory) → Results saved to memory with trust score → Documentation updated

**Key design decisions**:
- The orchestrator is a **routing layer**, not an execution engine — it delegates all work to sub-agents
- Agents communicate **via the MCP protocol**, not direct function calls
- Memory is **async and persistent** — findings survive sessions
- Multi-provider LLM is **native to opencode** — no proxy or shim needed

---

## Installation

### Supported Platforms

`install.py` auto-detects your OS from `/etc/os-release` (Linux) or `platform.system()` (macOS) and uses the correct package manager.

| Platform | Package Manager | AUR Helper | Status |
|---|---|---|---|
| **Arch Linux / CachyOS** | `pacman` | `paru` (falls back to `yay`) | ✅ Full support |
| **Manjaro / EndeavourOS** | `pacman` | `paru` / `yay` | ✅ Full support |
| **Ubuntu 22.04+ / Debian 12+** | `apt` | n/a | ✅ Full support |
| **macOS (Apple Silicon / Intel)** | `brew` | n/a | ✅ Full support |

**Unsupported** (manual install only): openSUSE, Fedora/RHEL, Alpine, FreeBSD. PRs welcome.

**Prerequisites**: Python 3.8+ (already present on all supported platforms).

### The Install Script

`install.py` is the one-stop toolchain installer. It:

1. **Detects your OS** and selects the appropriate package manager
2. **Checks which tools are already installed** (18 items across 5 groups)
3. **Shows an interactive checkbox TUI** (powered by [questionary](https://github.com/tmbo/questionary)) with everything pre-checked — press `<space>` to toggle, `<enter>` to confirm
4. **Bootstraps a local venv** at `.opencode/.install-venv/` to satisfy PEP 668 restrictions on Debian/Ubuntu
5. **Installs selected tools** via the native package manager, pip, or npm
6. **Skips tools with no package** on your platform and reports them as `manual` — see [Manual Installs](#manual-installs)

```bash
./install.py              # Interactive TUI (all 18 tools checked by default)
./install.py --yes        # Non-interactive: install everything available
./install.py --check      # Dry-run: report which tools are already installed
./install.py --list       # Print the tool catalog with descriptions and exit
./install.py --help       # Show usage
```

#### Tool Groups

The catalog is organized into 5 groups. All 23 items are checked by default in the TUI.

| Group | Tools | Count |
|---|---|---|
| **RE Core** | JADX, Apktool, dex2jar, baksmali, smali, Frida tools, radare2, Binwalk, Ghidra, **revula, ILSpyMcpServer, .NET SDK 9+, diec, YARA, pefile** | 15 |
| **Runtime** | OpenJDK 17+ (required by Ghidra, JADX, apktool) | 1 |
| **Android** | Android Platform Tools (adb + fastboot) | 1 |
| **Network** | mitmproxy, Wireshark | 2 |
| **Build / Runtime** | Git, Python 3, Node.js + npm, uv (Python toolchain) | 4 |

#### What each tool does

| Tool | Purpose | Install Method |
|---|---|---|
| **JADX** | APK/DEX → Java source decompiler with GUI and CLI | Arch: AUR (`jadx`), Debian: manual (release tarball), macOS: `brew` |
| **Apktool** | APK decode/rebuild; produces smali from DEX | Arch: AUR, Debian: manual, macOS: `brew` |
| **dex2jar** | DEX → JAR bytecode converter | Arch: AUR, Debian: manual, macOS: `brew` |
| **baksmali** | DEX disassembler → smali format | Arch: AUR, Debian: manual, macOS: `brew` |
| **smali** | Smali → DEX assembler | Arch: AUR, Debian: manual, macOS: `brew` |
| **Frida tools** | Dynamic instrumentation framework (Python bindings) | `pip` (all platforms) |
| **radare2** | Native binary analysis framework | `pacman` / `apt` / `brew` |
| **Binwalk** | Firmware analysis + filesystem extraction | `pacman` / `apt` / `brew` |
| **Ghidra** | NSA's Software Reverse Engineering framework | Manual (tarball) on Linux; `brew --cask` on macOS |
| **revula (MCP server)** | 116-tool all-in-one RE backend (PE/ELF/Mach-O, YARA, Capa, .NET, Frida, GDB, Android) | `uv tool install 'revula[full]'` (all platforms) |
| **ILSpyMcpServer (.NET decompiler)** | Decompile .NET assemblies to C#/VB.NET | `dotnet tool install -g ILSpyMcp.Server` (needs .NET SDK 9+) |
| **.NET SDK 9+** | Runtime for ilspycmd | Arch: AUR; Debian: `dotnet-install.sh`; macOS: `brew --cask dotnet-sdk` |
| **diec (Detect It Easy)** | Identify packer/compiler/cryptor on PE/ELF/Mach-O | `pacman` / `apt` / `brew` (Kali has it packaged) |
| **YARA** | Pattern-based malware identification | `pacman` / `apt` / `brew` |
| **pefile (Python)** | Python PE parser library | `pipx install pefile` (or `pip install --user pefile`) |
| **OpenJDK 17+** | Java runtime required by Ghidra, JADX, apktool | `pacman` / `apt` / `brew` |
| **adb + fastboot** | Android Debug Bridge + fastboot | `pacman` / `apt` / `brew` |
| **mitmproxy** | Interactive HTTPS intercepting proxy | `pacman` / `apt` / `brew` / `pip` |
| **Wireshark** | Deep packet inspection + protocol analysis | `pacman` / `apt` / `brew` |
| **Git** | Version control | `pacman` / `apt` (built-in on macOS) |
| **Python 3** | Runtime for installer + tooling | Pre-installed on all supported platforms |
| **Node.js + npm** | Runtime for `.opencode/` plugin | `pacman` / `apt` / `brew` |
| **uv** | Fast Python package manager (drives memini-ai) | `pip` / `brew` / standalone installer |

### Manual Installs

Some tools have no native package on certain platforms. The installer flags these with `manual` and skips them. Here's how to install them yourself:

#### JADX on Ubuntu / Debian

No apt package exists. Install the release tarball:

```bash
sudo apt install -y default-jre
wget -qO /tmp/jadx.zip https://github.com/skylot/jadx/releases/download/v1.5.0/jadx-1.5.0.zip
sudo unzip -o /tmp/jadx.zip -d /opt/jadx
sudo ln -s /opt/jadx/bin/jadx /usr/local/bin/jadx
sudo ln -s /opt/jadx/bin/jadx-gui /usr/local/bin/jadx-gui
```

If you use a different version, replace the URL. Check [releases](https://github.com/skylot/jadx/releases) for the latest.

#### Ghidra on Linux

Ghidra is not in pacman or apt. Install the public release:

```bash
wget -qO /tmp/ghidra.zip https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_11.3.2_build/ghidra_11.3.2_PUBLIC_20250415.zip
sudo unzip -o /tmp/ghidra.zip -d /opt
sudo ln -s /opt/ghidra_11.3.2_PUBLIC/ghidraRun /usr/local/bin/ghidra
```

Ghidra requires OpenJDK 17+. The install script handles this as part of the "Runtime" group — if you skipped it, install it manually.

#### Ghidra on macOS

```bash
brew install --cask ghidra
```

#### AUR packages on Arch without paru/yay

The installer skips AUR installs if no AUR helper is found. Install one:

```bash
sudo pacman -S --needed base-devel git
git clone https://aur.archlinux.org/paru.git
cd paru && makepkg -si
```

---

## The Agent Roster

RE_Playground ships with 15 specialist agents, each assigned a model optimized for its role. The models are configurable — edit `.opencode/opencode.json` or use `./setup.py init` to reassign.

| Agent | Skill | Recommended Model | Role |
|---|---|---|---|
| **boomerang** | orchestrator | kimi-k2.6:cloud | Task routing, delegation, protocol enforcement |
| **re-architect** | architect | deepseek-v4-pro:cloud | Binary analysis strategy, decompilation workflows, architecture research |
| **re-coder** | coder | glm-5.1:cloud | Script and tool implementation, code generation |
| **re-explorer** | explorer | devstral-2:123b-cloud | File and binary discovery (glob-only, not research) |
| **re-tester** | tester | deepseek-v4-flash:cloud | Test writing, execution, and validation (1M context window) |
| **re-linter** | linter | qwen3-coder-next:cloud | Code quality, formatting, style enforcement |
| **re-git** | git | minimax-m2.7:cloud | Version control operations (commits, branches, PRs) |
| **re-writer** | writer | gemma4:31b-cloud | Documentation, markdown, README generation |
| **re-scraper** | scraper | qwen3.5:cloud | Web research and data extraction |
| **re-release** | release | devstral-small-2:24b-cloud | Version bumping, changelogs, local-only (no remote push) |
| **re-agent-builder** | agent-builder | glm-5.1:cloud | Creating new skills and sub-agents from detected patterns |
| **boomerang-init** | init | kimi-k2.6:cloud | First-run project setup and personalization |
| **boomerang-handoff** | handoff | kimi-k2.6:cloud | Session wrap-up, docs update, context save |
| **researcher** | researcher | kimi-k2.6:cloud | Long-horizon research, data synthesis, multi-step analysis |
| **mcp-specialist** | mcp-specialist | glm-5.1:cloud | MCP protocol design, server debugging, tool schema review |

### Agent Routing Matrix

**This is code-level enforced.** The orchestrator must delegate based on these rules. No exceptions.

| Task Type | Primary Agent | NEVER delegate to |
|---|---|---|
| Binary analysis / decompilation | `re-architect` | `general`, `re-coder` |
| Code implementation | `re-coder` | `general`, `re-explorer` |
| Architecture / design decisions | `re-architect` | `general`, `re-coder` |
| File finding | `re-explorer` | Everything else |
| Testing | `re-tester` | `general`, `re-coder` |
| Linting / formatting | `re-linter` | Everything else |
| Git operations | `re-git` | Everything else |
| Documentation | `re-writer` | `general` |
| Web research / scraping | `re-scraper` | `general` |
| MCP protocol / server debug | `mcp-specialist` | `general` |
| Release automation | `re-release` | Everything else |

**Enforcement rules**:
1. **NEVER delegate code to `general`** — `general` is only for research/info
2. **NEVER delegate research to `re-explorer`** — explorer is file-finding only
3. **ALWAYS prefer specialist over generalist** — coder > general for code
4. **If unsure, query memini-ai** — ask memory which agent handled similar tasks

### Agent Selection Guide

| Task Type | Primary Agent | Model | Why |
|---|---|---|---|
| Complex planning / orchestration | `boomerang` | kimi-k2.6:cloud | Purpose-built for swarm orchestration |
| Binary analysis / decompilation workflow | `re-architect` | deepseek-v4-pro:cloud | Frontier reasoning with dedicated thinking modes |
| Architecture / design decisions | `re-architect` | deepseek-v4-pro:cloud | Best for analyzing complex binary trade-offs |
| Documentation writing | `re-writer` | gemma4:31b-cloud | Frontier-level instruction following |
| Session initialization | `boomerang-init` | kimi-k2.6:cloud | Guided setup with provider/model research |
| Session wrap-up / handoff | `boomerang-handoff` | kimi-k2.6:cloud | Docs update + context preservation |
| Skill / agent creation | `re-agent-builder` | glm-5.1:cloud | Long-horizon, ambiguous problem solving |
| Fast code generation / bug fixes | `re-coder` | glm-5.1:cloud | SOTA on SWE-Bench Pro for multi-file generation |
| Code exploration / finding files | `re-explorer` | devstral-2:123b-cloud | Designed for codebase navigation |
| Writing / running tests | `re-tester` | deepseek-v4-flash:cloud | 1M context for ingesting deep error logs |
| Linting / formatting | `re-linter` | qwen3-coder-next:cloud | Optimized for agentic coding workflows |
| Git operations | `re-git` | minimax-m2.7:cloud | Fast, reliable structured terminal commands |
| Web research / scraping | `re-scraper` | qwen3.5:cloud | Strong generalist with excellent tool use |
| MCP tool design / server debug | `mcp-specialist` | glm-5.1:cloud | SOTA on Terminal-Bench 2.0 |
| Release automation | `re-release` | devstral-small-2:24b-cloud | Fast 24B for targeted automation |

---

## MCP Server Integration

RE_Playground comes pre-configured with **10 MCP servers** in `.opencode/opencode.json`. Seven are enabled by default; three are disabled but present.

| Server | Status | Purpose | Transport |
|---|---|---|---|
| **ghidra-mcp** | ✅ enabled | 245 tools for Ghidra headless RE | stdio (Python bridge) |
| **radare2-mcp** | ✅ enabled | Fast binary triage and analysis | stdio (r2pipe) |
| **revula** | ✅ enabled | 116-tool all-in-one RE server (PE/ELF/Mach-O, YARA, Capa, .NET, Frida, GDB, Android, exploit dev) | stdio (Python) |
| **ilspy-mcp** | ✅ enabled | Decompile .NET assemblies to C#/VB.NET | stdio (.NET global tool) |
| **die-mcp** | ✅ enabled | Detect packer / compiler / cryptor via Detect-It-Easy | stdio (Python) |
| **memini-ai-dev** | ✅ enabled | PostgreSQL + pgvector semantic memory | stdio (Python FastMCP) |
| **searxng** | ✅ enabled | Web search for research | HTTP |
| **github-mcp** | ❌ disabled | GitHub API (PRs, issues, repos) | HTTP |
| **markitdown** | ❌ disabled | Convert documents to Markdown | stdio |
| **playwright** | ❌ disabled | Browser automation | stdio |

All `apiKey`, `dbUrl`, and filesystem paths are **env-var driven** — set them in `.env`, never in `opencode.json` directly.

### Ghidra MCP (245 tools)

The Ghidra MCP bridge exposes the full Ghidra API through 245 MCP tools across these categories:

| Category | Example Tools | Count |
|---|---|---|
| **Function Analysis** | `decompile_function`, `disassemble_function`, `get_function_callers`, `get_function_callees`, `analyze_function_completeness` | ~40 |
| **Memory & Data** | `read_memory`, `list_segments`, `search_byte_patterns`, `detect_array_bounds` | ~15 |
| **Data Types** | `create_struct`, `add_struct_field`, `apply_data_type`, `list_data_types` | ~20 |
| **Symbols & Labels** | `list_imports`, `list_exports`, `list_strings`, `create_label` | ~15 |
| **Renaming & Docs** | `rename_function`, `set_decompiler_comment`, `batch_set_comments` | ~10 |
| **Cross-Binary** | `get_function_hash`, `propagate_documentation`, `bulk_fuzzy_match_functions` | ~10 |
| **Dynamic Analysis** | P-code emulation, live debugging (breakpoints, registers, memory, traces) | ~30 |
| **Tool Management** | `list_instances`, `connect_instance`, `list_tool_groups`, `load_tool_group` | ~10 |

**Key capabilities**:
- **Auto-analysis** of imported binaries with function boundary detection
- **Decompilation to C pseudocode** with type recovery
- **P-code emulation** for isolated function analysis without running the target
- **Live debugging** with breakpoints, step-over/into, register inspection, memory watchpoints, function tracing (non-breaking, logs every call with arguments at ~0.5ms overhead)
- **Cross-binary documentation** via SHA-256 function hashing (normalized opcodes, format-independent) — document a function once, propagate to all binary versions
- **Hungarian notation enforcement** — auto-prefix (e.g., `count` on `uint32` → `dwCount`), convention warnings, no-op rejection
- **Headless mode** — Docker-ready for CI/CD automated analysis pipelines

**Connection**: The bridge connects to a running Ghidra instance (GUI or headless). Start Ghidra, load a binary, and the MCP tools become available. See `CONTEXT.md` for detailed tool invocation examples.

### radare2-mcp

A native C MCP server using the radare2 API via r2pipe, providing:

| Category | Capabilities |
|---|---|
| **Binary Analysis** | Disassembly, function listing, string extraction, section/symbol/import/export mapping |
| **Decompilation** | Multiple backends (pdc default, r2ghidra, r2dec available) |
| **Scripting** | r2js script execution, raw r2 command pass-through |
| **Safety** | Readonly mode (`--readonly`), sandbox lock (`--sandbox`), restricted tools (`--restrict`) |
| **Modes** | Stdio MCP, HTTP server (`-H <port>`), r2 core plugin |

radare2-mcp is optimized for **fast binary triage** — quick disassembly, string extraction, and import/export review before deeper analysis in Ghidra.

### revula (116 tools)

[revula](https://github.com/president-xd/revula) is the single most powerful RE tool added to RE_Playground. One `pip install` and your agents have:

- **Static analysis** (8 tools): PE/ELF/Mach-O via LIEF+pefile, multi-backend disassembly (Capstone/r2/objdump), string extraction with 17 classifier patterns, Shannon entropy + sliding-window packing detection, symbol extraction (DWARF/PDB/LIEF), YARA scanning, **Capa** (ATT&CK/MBC mapping), Ghidra/RetDec decompilation
- **Dynamic analysis** (29 tools): GDB/MI debug, LLDB, Frida injection, DynamoRIO + Frida Stalker code coverage
- **Android RE** (24 tools): APK parsing, DEX analysis, jadx/apktool integration, ADB bridge, Frida for Android (root bypass, SSL pinning bypass), MobSF/Quark-Engine scanners
- **Cross-platform** (7 tools): Rizin, GDB enhanced (heap/ROP/checksec), QEMU user/system emulation
- **Exploit dev** (11 tools): ROP chain builder, heap exploitation (tcache/fastbin/safe-linking), libc database, ASLR defeat, one-gadget finder
- **Anti-analysis** (2 tools): anti-debug/VM detection + bypass script generation
- **Malware triage** (4 tools): hash + IoC extraction, sandbox queries (VT/Hybrid Analysis), YARA generation, C2 config extraction
- **Firmware** (3 tools): binwalk extraction, CVE scanning, base address recovery
- **Protocol** (3 tools): tshark PCAP analysis (8 actions), binary protocol dissection, mutation fuzzing
- **Unpacking** (4 tools): UPX/Themida/VMProtect detection, dynamic unpacking via Frida
- **Deobfuscation** (3 tools): XOR/ROT/Base64/RC4 string recovery, OLLVM CFF detection
- **Symbolic** (4 tools): angr, Triton DSE
- **Binary formats** (4 tools): APK/DEX, .NET IL, Java class, WebAssembly
- **Utilities** (8 tools): hex tools, crypto (MD5/SHA/TLSH/ssdeep), binary patching, PCAP analysis

After install, an agent can answer "analyze /samples/target.exe" with a single call sequence: `re_pe_elf` → `re_strings` → `re_entropy` → `re_yara_scan` → `re_capa_scan` → `re_gdb` for dynamic. See [docs/learn-more.md](docs/learn-more.md) for the full tool list and curated tutorials.

### ILSpyMcpServer (.NET decompiler)

For Windows binaries built on .NET (C#, VB.NET, F#), ILSpyMcpServer ([github](https://github.com/bivex/ILSpy-Mcp)) lets agents ask:

- *"Decompile the String class from System.Runtime.dll"*
- *"List all types in Calculator.dll"*
- *"Find the Authenticate method"*
- *"Show me the type hierarchy for ProductService"*

Backed by [ILSpy](https://github.com/icsharpcode/ILSpy), the standard open-source .NET decompiler. Install with `dotnet tool install -g ILSpyCmd` and `dotnet tool install -g ILSpyMcp.Server`. Requires .NET SDK 9+ (also in `install.py`).

### D.I.E-MCP (Detect It Easy wrapper)

[D.I.E-MCP](https://github.com/lazy-importer/D.I.E-MCP) wraps the `diec` CLI of [Detect-It-Easy](https://github.com/horsicq/Detect-It-Easy) — the most thorough packer/compiler/cryptor signature database in the world. Agents can ask "what packer was used on /samples/x.exe?" and get a structured answer (e.g. `UPX 3.96`, `Themida 3.x`, `MSVC 2022`). Useful as a quick first-pass triage before running revula's deeper static analysis.

### memini-ai (Semantic Memory)

memini-ai is the project's persistent memory layer — a Python FastMCP server backed by PostgreSQL with the pgvector extension. It stores every finding, decision, and pattern with embeddings for semantic search.

#### Trust Engine

Every memory starts at a **trust score of 0.5** and is adjusted by feedback:

| Signal | Adjustment | When |
|---|---|---|
| `agent_used` | **+0.05** | An agent found this memory useful and acted on it |
| `user_confirmed` | **+0.10** | You explicitly confirmed the memory is correct |
| `agent_ignored` | **-0.05** | An agent was offered this memory but chose not to use it |
| `user_corrected` | **-0.10** | You corrected the memory — it contained wrong information |

Trust decays over time. High-trust memories are "sticky" (slower decay). Low-trust memories eventually archive.

#### Memory Graph

memini-ai tracks relationships between memories:

| Relationship | Meaning |
|---|---|
| `SUPERSEDES` | New memory replaces an outdated one |
| `PARTIAL_UPDATE` | New memory partially updates an existing one |
| `RELATED_TO` | Two memories are semantically connected |
| `CONTRADICTS` | Two memories conflict — triggers dialectic resolution |
| `DERIVED_FROM` | Memory was inferred or generated from another |

#### Tiered Loading

Context is expensive (in tokens). memini-ai loads at three tiers:

| Tier | Size | Composition | When |
|---|---|---|---|
| **L0** | ~100 tokens | High-trust (≥0.5) summary only | Session start auto-injection |
| **L1** | ~2K tokens | Promoted (≥0.8 trust) key decisions + patterns | Planning tasks |
| **L2** | Full | All memories, all trust levels | Deep research, contradiction detection |

#### Key Tools for Agents

| Tool | Purpose |
|---|---|
| `query_memories` | Semantic search over all memories |
| `add_memory` | Store a new finding with metadata and source tracking |
| `adjust_trust` | Signal whether a memory was useful or wrong |
| `query_kg` | Search the knowledge graph for entities and relationships |
| `find_contradictions` | Detect conflicting memories before making decisions |
| `challenge_memory` | Submit a counter-argument to a memory |
| `resolve_contradiction` | Synthesize a resolution for two conflicting memories |
| `add_thought` / `start_thought_chain` | Structured multi-step reasoning, stored and searchable |
| `get_tier0_summary` / `get_tier1_summary` | Load context at the right granularity |
| `search_project` | Semantic search over indexed project files |
| `extract_entities` | Pull named entities from a memory into the knowledge graph |
| `get_inference_chain` | Find reasoning paths between two entities |

### Additional MCP Servers

| Server | When to enable |
|---|---|
| **searxng** | Enabled by default — provides web search for the `researcher` and `re-scraper` agents. Requires a running SearXNG instance (`SEARXNG_URL` in `.env`). |
| **github-mcp** | Enable if you want agents to create PRs, manage issues, or read/write files on GitHub. Requires `GITHUB_PERSONAL_ACCESS_TOKEN` in `.env`. |
| **markitdown** | Enable to convert web pages, PDFs, and Office documents to Markdown for analysis. |
| **playwright** | Enable for browser automation (e.g., scraping JS-heavy pages, form interaction). |

---

## LLM Providers

RE_Playground ships with **five pre-curated LLM providers**. opencode natively supports multi-provider configuration — you can have all five active simultaneously, and agents select the best model for each task.

### Pre-configured Providers

| Provider | Config ID | Best For | Models | API Key Env Var |
|---|---|---|---|---|
| **Ollama Cloud** | `ollama-cloud` | Default — broadest model selection | 15 models (Kimi K2.6, GLM 5.1, DeepSeek V4, Qwen…) | `OLLAMA_API_KEY` |
| **OpenRouter** | `openrouter` | 200+ models, single key, pay-per-token | 15 curated (Claude, GPT, Gemini, Llama…) | `OPENROUTER_API_KEY` |
| **Anthropic** | `anthropic` | Direct Claude access | Claude Opus 4.5, Sonnet 4.5, Haiku 4.5 | `ANTHROPIC_API_KEY` |
| **OpenAI** | `openai` | Direct GPT access | GPT-5, GPT-5-mini, GPT-4.1, o4-mini, o3 | `OPENAI_API_KEY` |
| **Google AI** | `google` | Direct Gemini access | Gemini 2.5 Pro, 2.5 Flash, 2.5 Flash-Lite | `GOOGLE_API_KEY` |

Each provider template is stored in `.opencode/providers/<id>.json` and contains:
- `_meta` — provider ID, npm package, base URL, auth method
- `models` — full model catalog with context windows, pricing, and capability flags
- `recommended` — curated `best`, `fast`, and `cheap` model selections
- `lastReviewed` — ISO date for staleness detection

### Managing Providers via CLI

```bash
./setup.py provider list              # Show all available providers with model counts
./setup.py provider add openrouter    # Merge openrouter into opencode.json
./setup.py provider add anthropic     # Add another — multi-provider merge is native
./setup.py provider add ollama-cloud  # You can have all 5 active simultaneously
./setup.py provider set anthropic     # Replace current selection with anthropic only
./setup.py provider remove openai     # Drop openai from the active set
```

When you add a provider, `setup.py` automatically writes the correct `apiKey` env-var reference into `opencode.json`. You just need to set the corresponding key in `.env`.

**Multi-provider example**: With all five providers added, opencode sees one `provider` block with five keys. Agents can route to Claude Opus for architecture, Gemini Flash for fast triage, and GPT-5 for code generation — all in the same session.

### Refreshing Provider Catalogs

The curated model lists in `.opencode/providers/*.json` include a `lastReviewed` date. When you run `./setup.py init` and a provider's catalog is more than **30 days old**, the agent offers to do a web search to refresh pricing, context lengths, and capability flags. This is optional — you can always skip it and keep the curated defaults.

The refresh workflow uses the `boomerang-init` skill, which employs a **curated + search fallback** strategy: it checks the `lastReviewed` date first, and only searches the web if the data is stale.

### Adding a Custom Provider

Want to add Mistral, Groq, Together AI, or any OpenAI-compatible endpoint? It's five steps:

1. **Copy a template**: `cp .opencode/providers/openrouter.json .opencode/providers/mistral.json`
2. **Edit the metadata**:
   - `_meta.id`: `"mistral"`
   - `_meta.npm`: `"@ai-sdk/mistral"` (or the correct npm package for the provider's AI SDK adapter)
   - `_meta.options.baseURL`: The provider's API endpoint (e.g., `"https://api.mistral.ai/v1"`)
   - `_meta.options.apiKey`: The env var reference (e.g., `"{env:MISTRAL_API_KEY}"`)
3. **Fill in models**: List each model with its `name`, `contextLength`, `description`, and `capabilities` (vision, reasoning, function calling, structured output). Include `recommended` tiers (`best`, `fast`, `cheap`).
4. **Add to `.env.example`**: Document `MISTRAL_API_KEY` with a link to where users get it.
5. **Register**: `./setup.py provider add mistral`

The provider file format looks like this:

```jsonc
{
  "_meta": {
    "id": "mistral",
    "npm": "@ai-sdk/mistral",
    "name": "Mistral AI",
    "options": {
      "baseURL": "https://api.mistral.ai/v1",
      "apiKey": "{env:MISTRAL_API_KEY}"
    },
    "lastReviewed": "2026-06-06"
  },
  "models": {
    "mistral-large-latest": {
      "name": "Mistral Large",
      "contextLength": 131072,
      "description": "Flagship model for complex reasoning",
      "capabilities": ["function_calling", "structured_output"]
    }
  },
  "recommended": {
    "best": "mistral-large-latest",
    "fast": "mistral-small-latest",
    "cheap": "mistral-small-latest"
  }
}
```

---

## The Methodology Wiki

`RE-Playbook.md` is a **curated, trust-weighted knowledge base** of reverse engineering tools, techniques, and patterns. Every entry has a status indicator (✅ Proven / 🧪 Experimental) and a trust score.

### What's in the Playbook

**Tools** — detailed entries for JADX, Frida, Ghidra MCP, radare2 MCP, Binwalk, Apktool, and more

**Techniques** — step-by-step workflows for:
- APK decompilation (DEX → smali → Java)
- Hardcoded secret extraction (API keys, tokens, certs)
- Native library ARM analysis (`.so` inspection in Ghidra)
- SharedPreferences feature unlock (boolean/config toggles)
- SQLite database license bypass
- Dynamic instrumentation with Frida (hooking, tracing, memory manipulation)

**Patterns** — recurring anti-patterns and bypasses:
- Anti-tamper trust-all SSL (pinning bypass)
- XOR-based license key derivation
- BroadcastReceiver ADB capture
- Serial-prefix device gating

**Appendices**:
- **Appendix A**: Complete tool catalog (50+ tools with status and descriptions)
- **Appendix B**: Blog post summaries (6 entries from security researchers)
- **Appendix C**: Romain Thomas blog index (12 entries — binary analysis, DEX, Frida, LLVM)

### Using the Playbook

The playbook is designed to be **expanded collaboratively** with AI agents:

1. Open a session with `opencode`
2. Tell the `re-architect` or `researcher` agent which section you want to expand
3. The agent researches, writes, and saves to `RE-Playbook.md` using the entry template
4. The agent also saves to memini-ai with appropriate trust scoring and metadata tags

**Entry template** (at the top of `RE-Playbook.md`):
```markdown
### [Tool/Technique Name]
- **Status**: ✅ Proven | 🧪 Experimental
- **Trust**: 0.0–1.0
- **Category**: <tool / technique / pattern>
- **Tags**: <comma-separated>
- **Description**: <what it is, what it does>
- **Installation**: <how to get it>
- **Usage**: <common workflows, gotchas>
- **Links**: <references>
```

---

## Persona Customization

Every agent file in `.opencode/agents/` is split into two parts:

1. **Locked body** — agent name, model assignment, tool permissions, protocol instructions (managed by the framework, **do not edit by hand**)
2. **`## Persona` section** — the customizable part at the bottom of the file

This separation means you can tailor each agent to your specific RE domain (automotive firmware, APK analysis, malware triage, protocol reversing) without breaking the agent's structure.

### How the Persona System Works

Each agent file ends with this structure:

```markdown
# boomerang-architect
<locked body — agent metadata, tool permissions, 8-step protocol, routing rules>

## Persona

<!-- PERSONA-MARKER: DO NOT REMOVE THIS COMMENT. STRUCTURAL DELIMITER. -->

You are a specialist focused on Android APK reverse engineering. Lean on
the tools most appropriate to this work, follow the project's protocol
(memory query → thought chain → plan → delegate → git check → quality
gates → doc update → memory save), and produce concise, technical output.
```

- The `## Persona` H2 is the **section anchor** — everything above it is locked
- The `<!-- PERSONA-MARKER -->` comment is a **structural delimiter** — `setup.py` uses it to find and edit the persona, and always re-emits it
- The text between them is **your custom persona description**

**Safety guarantee**: `setup.py` performs a byte-identical comparison of the locked content before and after every edit. If anything above the `## Persona` H2 would change, the edit is aborted. Your customizations never break the agent.

### Managing Personas via CLI

```bash
./setup.py persona --list                                    # List all 15 agents
./setup.py persona --agent boomerang-architect \
    --description "Android APK reverse engineering with jadx and Frida"
./setup.py persona --agent re-tester \
    --description "Embedded firmware validation on ARM Cortex-M with Ghidra P-code emulation"
./setup.py persona --agent re-coder \
    --description "Writing Ghidra Python scripts for batch function annotation"
./setup.py persona --agent boomerang-coder --reset           # Revert to default
./setup.py persona --group planning \
    --apply-group "Automotive ECU firmware analysis on Qualcomm SA8155P"
```

**Persona groups** let you apply one description to multiple related agents:

| Group | Agents |
|---|---|
| `planning` | boomerang, re-architect |
| `implementation` | re-coder, re-tester, re-linter |
| `documentation` | re-writer |
| `research` | re-scraper, researcher |
| `infrastructure` | re-git, re-release, re-agent-builder, mcp-specialist |

### The boomerang-customize Skill

For a guided walkthrough, load the `boomerang-customize` skill inside OpenCode:

1. Open an OpenCode session
2. Type: `/skills load boomerang-customize`
3. The skill asks: which agent? what kind of RE work do you focus on? what tools and workflows?
4. It writes a tailored persona to the agent file
5. The persona is immediately active in the next agent dispatch

You can also **edit persona files by hand** — just keep the `## Persona` H2 and the `<!-- PERSONA-MARKER -->` comment intact, and replace the text between them with your own.

---

## The 8-Step Boomerang Protocol

All 15 agents follow a **mandatory 8-step workflow** for every task. This ensures discipline, prevents context loss, and produces auditable results.

| Step | Action | Tool | Waiver Phrase |
|---|---|---|---|
| **1. Memory Query** | Search memini-ai for relevant context | `query_memories` | None (always required) |
| **2. Think** | Structure reasoning in a thought chain | `add_thought` | None (always required for complex tasks) |
| **3. Plan** | Create implementation plan or delegate to architect | — | `skip planning`, `just do it`, `no plan needed` |
| **4. Delegate** | Dispatch specialist agent(s) with full context | Task tool | None |
| **5. Git Check** | Verify working tree state before code changes | `git status` | `git is fine` |
| **6. Quality Gates** | Lint → Typecheck → Test | lint/typecheck/test tools | `skip tests`, `skip gates` |
| **7. Doc Update** | Update TASKS.md, AGENTS.md, HANDOFF.md | Write/Edit tools | `no docs needed` |
| **8. Memory Save** | Save findings to memini-ai with trust scoring | `add_memory` | None (always required) |

The protocol is enforced at **three strictness levels** (configured per agent):

| Level | Behavior |
|---|---|
| **lenient** | Logs suggestions; auto-fixes what it can |
| **standard** | Logs warnings and suggestions (default) |
| **strict** | **Blocks execution** if mandatory steps are missing |

### Protocol State Machine

```
IDLE → MEMORY_QUERY → THINK → PLAN → DELEGATE → GIT_CHECK → QUALITY_GATES → DOC_UPDATE → MEMORY_SAVE → COMPLETE
```

---

## Reverse Engineering Workflows

Here are the primary workflows supported by the agents and MCP tools. See `CONTEXT.md` for detailed step-by-step guides and example tool invocations.

### Binary Analysis Workflow

1. Load binary into Ghidra (File → Import File → Auto Analyze) or radare2 (`r2 -A /path/to/binary`)
2. Tell the `re-architect` agent: "Plan an analysis strategy for this binary"
3. Agent queries memini-ai for any prior analysis of similar binaries
4. Agent calls `ghidra_list_functions`, `ghidra_list_imports`, `ghidra_list_strings` for initial triage
5. Agent identifies key functions (entry points, crypto, networking, string parsing)
6. `ghidra_decompile_function` on each key function — C pseudocode returned
7. Agent annotates: renames functions, sets comments, applies data types
8. All findings saved to memini-ai with trust scores and binary-specific metadata
9. `radare2_disassemble` for detailed instruction-level review where needed
10. Documentation written to `RE-Playbook.md` or a task-specific analysis doc

### Function Documentation Workflow (Ghidra V5)

1. Select a function for documentation
2. `ghidra_decompile_function` → C pseudocode
3. `ghidra_analyze_function_completeness` → quality score (decompilation coverage, parameter recovery, type inference)
4. Apply naming conventions (Hungarian notation, PascalCase, verb prefixes)
5. `ghidra_batch_set_comments` → plate comment (purpose, parameters, return), pre/post comments for tricky sections
6. `ghidra_rename_function_by_address` → meaningful name based on analysis
7. Save documentation to memini-ai with `binary_metadata` and `function_analysis` types
8. Trust score adjusted based on analysis confidence

### Cross-Binary Matching

1. `ghidra_get_function_hash` on a well-documented function → SHA-256 of normalized opcodes (format-independent)
2. `ghidra_build_function_hash_index` → persistent index for cross-version matching
3. Open a different binary version
4. `ghidra_lookup_function_by_hash` → find all matches
5. `ghidra_propagate_documentation` → apply comments, names, and data types to the new binary
6. `ghidra_bulk_fuzzy_match_functions` for functions that changed slightly between versions

### Dynamic Analysis (Live Debugging)

1. Start the Ghidra debugger server: `python -m debugger`
2. `ghidra_debugger_attach` → connect to running process by name or PID
3. `ghidra_debugger_modules` → see loaded DLLs with runtime+Ghidra address mapping
4. `ghidra_debugger_set_breakpoint` → set INT3 or hardware breakpoints
5. `ghidra_debugger_continue` → run to breakpoint
6. `ghidra_debugger_registers` → inspect CPU state (EAX-EDI, ESP, EBP, EIP, EFLAGS on x86)
7. `ghidra_debugger_step_into` / `ghidra_debugger_step_over` → instruction-level stepping
8. `ghidra_debugger_read_memory` → dump memory regions at runtime
9. `ghidra_debugger_stack_trace` → backtrace with symbols mapped to Ghidra
10. `ghidra_debugger_trace_function` → **non-breaking function tracing**: logs every call with arguments at ~0.5ms overhead, invisible at 25fps game frame rates
11. `ghidra_debugger_watch_memory` → hardware watchpoints on memory reads/writes

**Debugger argument capture** works with calling conventions:
- `__stdcall`, `__fastcall`, `__thiscall`, `__cdecl`
- Reads from registers and stack automatically
- Named arguments for readability: `arg_names: "pUnit,nSkillId,nWeaponSpeed"`

---

## Safety and Sandboxing

### Ghidra MCP Security

| Feature | Description |
|---|---|
| **localhost-only by default** | HTTP server bound to `127.0.0.1`; no remote access without explicit configuration |
| **Script endpoints off by default** | Set `GHIDRA_MCP_ALLOW_SCRIPTS=1` to enable (v5.4.1+) |
| **Path traversal protection** | Set `GHIDRA_MCP_FILE_ROOT` to restrict filesystem access |
| **Auth for LAN exposure** | Set `GHIDRA_MCP_AUTH_TOKEN` before binding to `0.0.0.0` |

### radare2-mcp Security

| Feature | Flag |
|---|---|
| **Readonly mode** | `--readonly` — prevents all write operations |
| **Sandbox lock** | `--sandbox` — restricts dangerous commands |
| **Restrict tools** | `--restrict` — limits available tool set |
| **YOLO mode** | `--yolo` — disables approvals (use only in trusted environments) |

### General

- **No API keys in config**: `.opencode/opencode.json` uses `{env:VARIABLE_NAME}` references exclusively
- **`.env` is gitignored**: never commit real secrets
- **`.gitignore` covers**: `.env`, `node_modules/`, `__pycache__/`, `.install-venv/`, binaries directory, build artifacts, IDE files

---

## CLI Reference

RE_Playground ships with two CLI tools: `setup.py` (configuration) and `install.py` (toolchain).

### setup.py — Configuration Orchestrator

Run with no arguments for a summary of available subcommands.

| Subcommand | Purpose |
|---|---|
| **`init`** | Full interactive setup — provider selection, model research, agent→model mapping, persona customization, state save |
| **`provider list`** | Show all available providers with model counts and `lastReviewed` dates |
| **`provider add <id>`** | Merge a provider into `opencode.json` (preserves existing providers and non-provider config) |
| **`provider set <id>`** | Replace current provider set with a single provider |
| **`provider remove <id>`** | Drop one provider from the active set |
| **`persona --list`** | List all 15 agent names and their current persona description (first line) |
| **`persona --agent <id> --description "..."`** | Apply a persona description to one agent |
| **`persona --agent <id> --reset`** | Revert one agent to the default persona |
| **`persona --group <group> --apply-group "..."`** | Apply the same persona to all agents in a group (`planning`, `implementation`, `documentation`, `research`, `infrastructure`) |
| **`status`** | Show current configuration: active providers, model counts, agent personas, state file health, opencode.json validity |
| **`reset`** | Delete `.re-playground-state.json` and start over (does not touch agent files or `opencode.json`) |

**State persistence**: `setup.py` saves your choices to `.re-playground-state.json` (gitignored). This file tracks which providers you selected, which personas you applied, your budget preference, and other init choices. `./setup.py status` reads it; `./setup.py reset` deletes it.

### install.py — Toolchain Installer

```bash
./install.py              # Interactive TUI (all 18 tools checked by default)
./install.py --yes        # Non-interactive: install everything available
./install.py --check      # Dry-run: report currently installed/missing/manual status
./install.py --list       # Print the tool catalog with descriptions
./install.py --help       # Show usage
```

**Exit codes**: 0 on success (all requested tools installed or already present), 1 on any installation failure. `--check` always exits 0.

**Venv bootstrap**: On Debian/Ubuntu systems with PEP 668 restrictions, `install.py` creates a local venv at `.opencode/.install-venv/`, installs `questionary` into it, and re-execs itself inside that environment. This is transparent — you don't need to activate the venv manually.

---

## Troubleshooting

### The install script's TUI looks broken

`install.py` uses `questionary`, which requires a real TTY. Run from a real terminal, not over `script` recordings or unusual pipes. On SSH, ensure `TERM` is set to something reasonable:

```bash
export TERM=xterm-256color
```

### `questionary` won't install

The script auto-creates a local venv at `.opencode/.install-venv/`. If that fails:

```bash
pipx install questionary    # or: uv tool install questionary
```

### memini-ai won't connect to PostgreSQL

Check `.env`:
- `MEMINI_DB_URL` matches a running PostgreSQL + pgvector instance
- The database exists and the user has CREATE rights
- Port 5434 (memini default) is reachable:
  ```bash
  psql "$MEMINI_DB_URL" -c '\dt'
  ```
- If using Docker/Podman, ensure the container is running:
  ```bash
  podman ps | grep timescaledb   # or: docker ps | grep postgres
  ```
- If using the RE_Playground multi-container stack, override the bare-metal
  default (`localhost:5434`) to point at the bundled `re-memini` container
  (`postgresql://memini:memini@re-memini:5432/memini`) — this is set
  automatically by `docker-compose.yml`/`podman-compose.yml`.

### Ghidra says it needs Java

Ghidra requires OpenJDK 17+. The install script installs it as part of the "Runtime" group. If you skipped it:

```bash
# Arch
sudo pacman -S jdk17-openjdk
# Debian/Ubuntu
sudo apt install -y openjdk-17-jdk
# macOS
brew install openjdk@17
```

Verify: `javac --version` should report 17 or higher on PATH.

### "Server not responding / Connection refused" (Ghidra MCP)

1. Ensure the Ghidra CodeBrowser is open with a binary loaded
2. Check **Tools → GhidraMCP → Start MCP Server** was clicked
3. Verify the bridge can reach it: `curl http://127.0.0.1:8089/check_connection`
4. Expected response: `"Connected: GhidraMCP plugin running with program '<name>'"`

### "404 Not Found" from Ghidra MCP

- Verify a binary is loaded in CodeBrowser
- Run **Analysis → Auto Analyze** first
- Check that the tool name matches exactly (Ghidra MCP tools use lowercase with underscores)

### "No script provider found" (Ghidra Python scripts)

- Ghidra 12.1+: Jython is an optional extension
- Install via **File → Install Extensions → Jython**, then restart
- Alternative: use PyGhidra for new automation or Java scripts

### Sudo prompts during install

Arch and Debian package installs need root. The script uses `sudo` if you're not already running as root. macOS never needs sudo (Homebrew installs to `/opt/homebrew` or `~/.homebrew`).

To skip sudo on Arch (e.g., in a container where you're already root):
```bash
sudo ./install.py --yes    # runs pacman without additional sudo prompts
```

### Wireshark on Arch

The script tries `wireshark-qt` first, then falls back to `wireshark-cli`. If both fail:
```bash
sudo pacman -S wireshark-qt
```
You may need to add your user to the `wireshark` group to capture packets without root.

---

## Contributing

PRs are welcome, especially for:

- **Platform support**: Adding Fedora/RHEL, openSUSE, Alpine, or FreeBSD to `install.py`
- **Tool additions**: New RE tools with cross-platform install methods
- **Playbook entries**: New tools, techniques, or patterns in `RE-Playbook.md`
- **Provider templates**: Curated model catalogs for additional LLM providers
- **Persona presets**: Domain-specific agent personas (e.g., `automotive-ecu-re`, `malware-campaign-triage`, `iot-firmware-extraction`)
- **Workflow documentation**: Step-by-step guides for specific analysis scenarios

Before submitting:
1. Run `install.py --check` on your platform to verify tool detection
2. Verify `setup.py` commands still work (`provider list`, `persona --list`, `status`)
3. Keep provider templates' `lastReviewed` date current
4. Follow the existing code style (Python: PEP 8, Markdown: standard with code fences)

---

## License

**Code** (install.py, setup.py, opencode config, agent definitions): MIT License (see `LICENSE` file — TBD by the project owner).

**Documentation** (AGENTS.md, CONTEXT.md, RE-Playbook.md, README.md): [CC-BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).

**Third-party tools** (Ghidra, radare2, JADX, Frida, etc.) retain their own licenses.

---

## Acknowledgements

RE_Playground is built on several open-source projects:

| Project | Purpose | License |
|---|---|---|
| [Boomerang v3](https://github.com/Veedubin/Boomerang-v3) | Multi-agent orchestration framework | MIT |
| [memini-ai](https://github.com/Veedubin/memini-ai-dev) | Semantic memory server (PostgreSQL + pgvector) | MIT |
| [Ghidra MCP](https://github.com/bethington/ghidra-mcp) | 245-tool MCP bridge for Ghidra | Apache 2.0 |
| [radare2-mcp](https://github.com/radareorg/radare2-mcp) | radare2 MCP server | LGPL 3.0 |
| [revula](https://github.com/president-xd/revula) | 116-tool all-in-one RE MCP server | GPL |
| [ILSpyMcpServer](https://github.com/bivex/ILSpy-Mcp) | .NET decompiler MCP wrapper | MIT |
| [ILSpy](https://github.com/icsharpcode/ILSpy) | Underlying .NET decompiler engine | MIT |
| [D.I.E-MCP](https://github.com/lazy-importer/D.I.E-MCP) | Detect It Easy MCP wrapper | MIT |
| [Detect-It-Easy](https://github.com/horsicq/Detect-It-Easy) | Packer / compiler / cryptor identification | MIT |
| [YARA](https://github.com/VirusTotal/yara) | Pattern-based malware identification | Apache 2.0 (binding) / BSD (CLI) |
| [pefile](https://github.com/erocarrera/pefile) | Python PE parser | MIT |
| [Ghidra](https://ghidra-sre.org/) | NSA Software Reverse Engineering framework | Apache 2.0 |
| [radare2](https://radare.org/) | UNIX-like reverse engineering framework | LGPL 3.0 |
| [JADX](https://github.com/skylot/jadx) | DEX to Java decompiler | Apache 2.0 |
| [Frida](https://frida.re/) | Dynamic instrumentation toolkit | wxWindows Library Licence |
| [questionary](https://github.com/tmbo/questionary) | Python TUI library | MIT |
| [re-universe](https://github.com/bethington/re-universe) | Ghidra BSim PostgreSQL platform for binary similarity | Apache 2.0 |
| [FileBrowser Quantum](https://github.com/filebrowser/filebrowser) | Web file manager (Docker ingress) | Apache 2.0 |

**Resource repositories** (Ghidra and radare2 scripts worth checking before building your own):

| Collection | URL | Highlights |
|---|---|---|
| amilarajans/ghidra_scripts | [GitHub](https://github.com/amilarajans/ghidra_scripts) | ARM/MIPS ROP finders, Call Chain, Codatify, Function Profiler, Leaf Blower, Rizzo, RC4 Decrypter, YARA search, Swift/Go renamers, stack strings, shellcode hashes, Cyclomatic complexity, vulnerable sscanf search |
| radare2 built-in scripts | [GitHub](https://github.com/radareorg/radare2/tree/master/scripts) | english.r2.js, il2cpp.r2.js, ipsw-kernel-symbolicate.r2.js, vsmap.r2.js, unzip.r2.js, r2sptrace.py |
| WithSecureLabs/radare2-scripts | [GitHub](https://github.com/WithSecureLabs/radare2-scripts) | r2_bin_carver.py (carve files from memory dumps), r2_hash_func_decoder.py (decode hashed functions in shellcode) |
| radareorg/awesome-radare2 | [GitHub](https://github.com/radareorg/awesome-radare2) | Curated list of 70+ r2 tools, scripts, articles, CTF writeups |

