# RE_Playground Session Handoff

> **For the next agent/session picking up RE_Playground**
> **Last updated**: 2026-06-07

---

## Current State (read this first)

**Last release**: v0.2.4 (commit `89c07d4`) — all 4 build-containers CI jobs green.
GitHub: https://github.com/Veedubin/Reverse-Engineering-Playground/releases/tag/v0.2.4

**Working tree has uncommitted changes, stashed in `stash@{0}`**:
- `wip-v0.2.5-revula-opt-in-distroless-additions`
- Contains: revula opt-in (install.py + opencode.json), 3 distroless Dockerfiles

**Restore with**: `git stash pop` (or `git stash show -p stash@{0}` to review first)

---

## What this session accomplished

### v0.2.3 (commit `9dc457b`, tag created)
1. Diagnosed why v0.2.2 build-containers CI failed: revula[full] needs
   `build-essential` + `python3-dev` + `libfuzzy-dev` AT THE SAME TIME as the
   pip install (ssdeep 3.4 has no Python 3.12 wheel; needs to compile)
2. Updated `docker/core/Dockerfile`: apt adds compile toolchain, revula install
   uses `git clone` + `pip install --ignore-installed '.[full]'`
3. Updated `docker/radare2/Dockerfile`: removed `rizin` (not in noble)
4. Added distroless `docker/filebrowser/Dockerfile` (39 MB, no shell)
5. Created `docs/v0.3.0-proposal.md` (295 lines): distroless + docker/mcp-gateway
   refactor plan, compose profiles, 11-PR implementation order

### v0.2.3 build was actually broken
- The v0.2.3 commit DID NOT include the core/radare2/install.py fixes (only the
  filebrowser + proposal doc). Build-containers CI failed on ilspycmd.
- **Lesson learned: always amend v0.2.x tag with the full set of fixes
  before retagging. Force-push the tag with `--force-with-lease`.**

### v0.2.4 (commit `89c07d4`, tag created) — **CURRENT RELEASE**
1. Diagnosed v0.2.3 ilspycmd failure: latest 10.1.0.8386 NuGet package is
   missing `DotnetToolSettings.xml` — won't install on .NET 9 SDK
2. Tested ilspycmd versions locally in `mcr.microsoft.com/dotnet/sdk:9.0`:
   - 10.1.0.8386: BROKEN (DotnetToolSettings.xml missing)
   - 8.2.0.7535: WORKS
3. Pinned ilspycmd to 8.2.0.7535 in `docker/core/Dockerfile`
4. Added `docker/revula/Dockerfile` as v0.3.0 distroless reference image
5. **All 4 build-containers CI jobs green** (6m 56s, run `27100361418`)

### v0.2.5 (in stash `stash@{0}`)
After v0.2.4 was released, investigated revula quality and found:
- GPL-3.0-or-later license (incompatible with our MIT)
- 116 tools claimed, but ~100 are thin wrappers
- Only the Exploit Development category (11 tools) has real depth
- Angr install is ~2 GB
- User's verdict: **make revula opt-in**

Implemented (all in stash):
- `install.py`: added `Tool.opt_in: bool = False` field
- `install.py`: TUI marks opt-in tools with `[opt-in]` suffix and leaves
  them unchecked by default
- `install.py`: revula flagged `opt_in=True`
- `.opencode/opencode.json`: revula `enabled: false` with `_comment`
- **Did not commit/tag v0.2.5 yet** — the distroless work is still
  untracked in working tree, needs to be combined into the commit

### Distroless work (validated end-to-end locally)
User asked to keep these Dockerfiles even though I tried to delete them:

1. `docker/core/Dockerfile.distroless` (3,293 bytes)
   - Multi-stage: `node:22-bookworm` build → `gcr.io/distroless/nodejs22-debian13:nonroot` runtime
   - 313 MB (vs 800 MB ubuntu-based re-core)
   - Validated: `opencode --version` returns 1.16.2, `opencode web` starts and serves :4096
   - Key finding: `node:22-slim` lacks curl/wget, must use `node:22-bookworm`
   - Key finding: distroless images have NO shell, so `RUN mkdir -p` must happen
     in the build stage and the dirs are then COPY'd

2. `docker/revula/Dockerfile` (5,554 bytes)
   - Multi-stage: `python:3.13-slim-trixie` build → `gcr.io/distroless/python3-debian13:nonroot` runtime
   - 1.6 GB (heavy: angr 252MB + semgrep 230MB + frida 94MB + z3 111MB = 687MB just for revula's [full] deps)
   - Validated: revula 0.1.0 MCP server starts, all 14 heavy deps import OK
   - Key finding: **distroless python3-debian13 = Python 3.13**; build stage must
     use `python:3.13-slim-trixie` not `python:3.12-slim` (ABI mismatch on .so files)
   - Key finding: distroless python3 does NOT ship `libfuzzy.so.2`; must COPY
     it from the build stage for ssdeep to work

3. `docker/ilspy/Dockerfile` (3,515 bytes)
   - Multi-stage: `mcr.microsoft.com/dotnet/sdk:9.0` build → `mcr.microsoft.com/dotnet/runtime-deps:9.0-bookworm-slim` runtime
   - 738 MB
   - **Note**: gcr.io/distroless has NO dotnet variant. Microsoft's `runtime-deps`
     is the closest distroless-like option
   - Validated: `ilspycmd --help` works, `ilspycmd 8.2.0.7535` runs
   - Key findings:
     - `dotnet tool install` puts the .dll in `~/.dotnet/tools/.store/ilspycmd/<version>/`,
       must COPY the whole `.store/` directory
     - COPY to `/opt/ilspy/tools/` (not `/root/.dotnet/tools/`) with `--chown=app:app`
       so the nonroot user can execute
     - ilspycmd 8.x was built for `net6.0`; runtime image only has .NET 9.0.
       Set `ENV DOTNET_ROLL_FORWARD=Major` for ABI compatibility

### Revula quality assessment (during this session)
Per the official GitHub README, revula's tool count by category:

| Category              | Tools | Real depth?                          |
|-----------------------|-------|--------------------------------------|
| Static Analysis       | 8     | Thin LIEF/Capstone wrappers          |
| Dynamic Analysis      | 29    | Thin GDB-MI/LLDB/Frida wrappers      |
| Android RE            | 24    | Real APK/DEX, but tools shell out    |
| Cross-Platform RE     | 7     | r2/rizin/QEMU wrappers               |
| **Exploit Development** | **11** | **Deepest category — ROP, heap, libc DB, format strings** |
| Anti-Analysis         | 2     | Pattern detection only               |
| Malware Analysis      | 4     | Stubs                                |
| Firmware RE           | 3     | Very thin                            |
| Protocol RE           | 3     | tshark wrapper                       |
| Unpacking             | 4     | UPX + pattern detect                 |
| Deobfuscation         | 3     | XOR/ROT/Base64, very basic           |
| Symbolic Execution    | 4     | angr wrapper                         |
| Binary Formats        | 4     | .NET/Java/WASM, thin                 |
| Utilities             | 8     | Hex, crypto, basic                   |
| Admin                 | 2     | Server status                        |
| **TOTAL CLAIMED**     | **116** | **Real depth ≈ 30 tools**            |

---

## What the next session should do

1. **Run `git stash pop`** to restore the v0.2.5 working tree
2. **Commit v0.2.5** with: revula opt-in changes + 3 distroless Dockerfiles
3. **Tag v0.2.5 + create GH release** (don't amend — let CI run fresh)
4. **Verify v0.2.5 build-containers CI is green** (link: check after push)
5. **Continue v0.3.0 work** per `docs/v0.3.0-proposal.md`:
   - PR 2: Add `re-broker` service to compose (uses `docker/mcp-gateway` image)
   - PR 3: Write `catalogs/re-catalog.yaml` (OCI catalog of 9 MCP servers)
   - PR 7: Update build-containers.yml matrix 4 → 6 services
6. **Write `docs/distroless.md`** — reference doc for which distroless tag for
   which purpose (would have saved me hours today)

---

## Important technical findings to apply

### Distroless Python ABI
- `gcr.io/distroless/python3-debian13:nonroot` ships **Python 3.13** (not 3.12)
- Build stage MUST be `python:3.13-slim-trixie` (not 3.12-slim)
- ABI mismatch on .so files causes cryptic `ModuleNotFoundError: pydantic_core._pydantic_core`
  even though the .so is present
- Source: https://github.com/GoogleContainerTools/distroless/blob/main/python3/README.md

### Distroless constraints
- NO shell, NO apt, NO package manager
- `RUN` commands in the runtime stage fail with `executable file not found`
- Persistent directories must be created in the build stage and COPY'd
- Run as `nonroot:nonroot` (uid 65532) by default

### distroless Debian tags available (gcr.io/distroless)
- `static-debian13:nonroot` — 2 MiB, just glibc+ca-certs (use for Go binaries like FileBrowser)
- `base-debian13:nonroot` — minimal
- `python3-debian13:nonroot` — Python 3.13
- `nodejs22-debian13:nonroot` — Node.js 22
- `java21-debian13:nonroot` — Java 21
- `cc-debian13:nonroot` — gcc (use for Wine/glibc-heavy builds)
- **NO dotnet variant** — use `mcr.microsoft.com/dotnet/runtime-deps:9.0-bookworm-slim`

### ilspycmd pin
- 10.1.0.8386 (latest): BROKEN on .NET 9 SDK (missing DotnetToolSettings.xml)
- 8.2.0.7535: WORKS, install with `dotnet tool install -g ilspycmd --version 8.2.0.7535`
- ilspycmd 8.x was built for net6.0; set `ENV DOTNET_ROLL_FORWARD=Major` in runtime

### Revula install
- revula is NOT on PyPI; must `git clone https://github.com/president-xd/revula.git`
- Use `pip install --break-system-packages --ignore-installed '.[full]'`
- revula's own `scripts/install/install_all.sh` is broken on Ubuntu 24.04 (PEP 668)
- revula is **GPL-3.0-or-later** (incompatible with our MIT license)
- We don't ship revula; we just call into it. Document this clearly.

### Build size reality check (v0.3.0)
Decomposing the stack doesn't reduce total RAM:
- ubuntu-based re-core: 800 MB
- distroless re-core: 313 MB (only OpenCode, no revula)
- distroless re-revula: 1.6 GB (revula's [full] deps are the size)
- Total if decomposed: 313 + 1,600 = 1,913 MB (LARGER than 800 MB)
- **The win is isolation + cgroup limits + smaller blast radius, NOT size reduction**
- Document this in v0.3.0 docs so we don't over-promise

### CI quirks
- ilspycmd install adds 90 seconds to re-core build (the slowest step)
- ssdeep compile adds ~2 minutes the first time (caching helps)
- angr compile adds ~3 minutes the first time
- 4-service matrix takes ~7 minutes total when parallelized

### Known secrets that need cleanup
- `opencode-old.json` in `.gitignore` (leaked PAT incident from boomerang-v3)
- No secrets in RE_Playground shipping paths — validated by `.github/workflows/validate.yml`

### User preferences
- **TUI installer with all tools checked by default** — but opt-in fields override this
- **MIT license** — confirmed safe for our project
- **Multi-container over single fat image** — security + isolation win
- **Podman compatible** — rootless mode must work
- **No vendor binaries shipped** — install from distro PMs / Homebrew / pip / npm
- **Sanitize vendor-specific content** — no Launch Tech / CRP* / CyberSDK / etc.
- **Sanitize `mandela` / `x431` / `80166`** references
- **No hardcoded API keys/paths** — all `{env:...}` references
- **Do NOT ship a DB dump**

---

## Files to review at session start

- `TASKS.md` — current task state, in-progress items, backlog
- `docs/v0.3.0-proposal.md` — the v0.3.0 plan
- `docs/container.md` — current multi-container deployment
- `docs/learn-more.md` — curated 17 tool links
- `examples/01-suspicious-pe-triage.md` — zadig-2.8.exe walkthrough
- `CONTEXT.md` — architecture overview
- `install.py` — TUI installer, now with `Tool.opt_in` field
- `.opencode/opencode.json` — 9 MCP servers, 6 enabled, revula disabled
- `docker/` directory — 4 working + 3 distroless Dockerfiles

## Files to NOT touch without explicit user direction

- `LICENSE` (MIT)
- `AGENTS.md` (15-agent routing matrix)
- `CONTRIBUTING.md` (development guide)
- `SECURITY.md` (90-day disclosure)
- `CODE_OF_CONDUCT.md` (Contributor Covenant v2.1)
- `.github/ISSUE_TEMPLATE/` (bug + feature request templates)

---

## Memory state

memini-ai's vector index is broken (pre-existing, out of scope): `add_memory` fails
with `expected 384 dimensions, not 1024`. `query_memories` with `strategy="tiered"`
still works partially. This is a boomerang-v3 issue, not RE_Playground.

If you need to save important session state, do it in HANDOFF.md (this file)
and TASKS.md, not in memini-ai. Re-evaluate memini-ai at the start of next session.
