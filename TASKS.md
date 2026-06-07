# RE_Playground Tasks

> **Project**: RE_Playground — AI-assisted reverse engineering
> **Last updated**: 2026-06-07 (session wrap)

---

## ✅ Released

### v0.1.0 — Initial release (commit `35c57e0`)
- 56 files, full multi-agent RE workstation
- MIT license, 7 MCP servers, 15 specialist agents
- GitHub: https://github.com/Veedubin/Reverse-Engineering-Playground

### v0.2.0 — Feature release (commit `1b11743`)
- 6 new RE Core tools (revula, ILSpyMcpServer, .NET SDK 9+, diec, YARA, pefile)
- 3 new MCP servers (revula, ilspy-mcp, die-mcp — die-mcp later removed in v0.2.2)
- 4 Dockerfiles (core, ghidra, radare2, filebrowser) + multi-container stack
- docker-compose.yml + podman-compose.yml
- 2 new docs (learn-more.md, container.md)

### v0.2.1 — CI + governance (commit `a266469`, tag deleted)
- 15 files, 828 lines added
- .github/workflows/validate.yml + build-containers.yml
- CONTRIBUTING.md, SECURITY.md, CODE_OF_CONDUCT.md
- examples/01-suspicious-pe-triage.md
- 5 README shields.io badges
- **Build-containers CI failed — 3 of 4 images broken** (tag deleted)

### v0.2.2 — Build fixes (commit `dcd2ba8`, tag deleted)
- Removed die-mcp (no PyPI package, no Linux diec binary)
- Removed `detect-it-easy`, `wine-gecko`, `wine-mono` (not in Ubuntu 24.04 noble)
- Ghidra URL fix: 11.3.2 → 12.0.4 (URL pattern changed)
- Removed `ENV OPENCODE_SERVER_PASSWORD` (Buildx secret warning)
- **Build-containers CI still failed — 2 of 4 images broken** (tag deleted)

### v0.2.3 — Distroless filebrowser + revula install fix (commit `9dc457b`)
- `re-filebrowser` now distroless multi-stage (~39 MB, no shell)
- `re-core` revula install via `git clone` + `pip install --ignore-installed '.[full]'`
  (revula is not on PyPI; the `install_all.sh` script is broken on Ubuntu 24.04)
- apt adds `build-essential`, `python3-dev`, `libfuzzy-dev` (compile toolchain
  for ssdeep 3.4, python-tlsh, binary2strings C extensions)
- docs/v0.3.0-proposal.md (295 lines): distroless + docker/mcp-gateway refactor plan
- **Build-containers CI failed — ilspycmd 10.x broken on .NET 9 SDK** (tag still published)

### v0.2.4 — ilspycmd pin + distroless re-revula (commit `89c07d4`) — **CURRENT RELEASE**
- Pin ilspycmd 8.2.0.7535 (10.x NuGet missing DotnetToolSettings.xml)
- Add `docker/revula/Dockerfile` as v0.3.0 distroless reference (1.6 GB)
  - Multi-stage: `python:3.13-slim-trixie` → `gcr.io/distroless/python3-debian13:nonroot`
  - libfuzzy.so.2 vendored for ssdeep support
- **All 4 build-containers CI jobs green** (6m 56s)
- GitHub release: https://github.com/Veedubin/Reverse-Engineering-Playground/releases/tag/v0.2.4

---

## 🔄 In Progress (stashed)

### v0.2.5 — Revula opt-in (UNCOMMITTED, in stash)
- `install.py`: added `Tool.opt_in: bool = False` field
- TUI labels opt-in tools with `[opt-in]` suffix and leaves them unchecked
- revula flagged `opt_in=True` (GPL-3.0 incompatible with MIT; 100/116 tools
  are thin wrappers; 1.4 GB install footprint)
- `.opencode/opencode.json`: revula set to `enabled: false` with `_comment`
  explaining the rationale
- **All work stashed in `stash@{0}`** for clean handoff

---

## ⏳ Backlog (next session)

### v0.3.0 — Distroless + MCP Gateway refactor
See `docs/v0.3.0-proposal.md` for full plan. Implementation order:

1. **PR 1 (this session, partially done)** — Distroless filebrowser ✅
2. **PR 2** — `re-broker` service in compose (uses `docker/mcp-gateway` image)
3. **PR 3** — `catalogs/re-catalog.yaml` (OCI catalog of 9 MCP servers)
4. **PR 4** — `re-core` distroless conversion (file: `docker/core/Dockerfile.distroless`,
   313 MB, validated end-to-end locally — untracked in working tree)
5. **PR 5** — `re-revula` distroless conversion (file: `docker/revula/Dockerfile`,
   1.6 GB, validated end-to-end — untracked in working tree)
6. **PR 6** — `re-ilspy` distroless conversion (file: `docker/ilspy/Dockerfile`,
   738 MB, validated end-to-end — untracked in working tree)
7. **PR 7** — Update `.github/workflows/build-containers.yml` matrix: 4 → 6 services
8. **PR 8** — Compose profiles: `default` (files+core+broker), `re` (+revula+radare2),
   `ghidra` (+ghidra), `windows` (+ilspy)
9. **PR 9** — Update README.md (ilspycmd pin, v0.3.0 distroless plan, MCP Gateway)
10. **PR 10** — Update CHANGELOG.md with v0.2.3 + v0.2.4 + v0.2.5 lineage
11. **PR 11 (release)** — Tag v0.3.0, write CHANGELOG entry, publish GitHub release

### Other known issues

- **memini-ai vector index broken** (pre-existing): `add_memory` fails with
  `expected 384 dimensions, not 1024`. Out of scope for RE_Playground; affects
  boomerang-v3 development. Workaround: query_memories with `strategy="tiered"`
  still works.
- **GitHub PAT leaked earlier** (boomerang-v3 context, not RE_Playground):
  A `github_pat_` token was accidentally committed to the boomerang-v3 repo
  history. Must be revoked at https://github.com/settings/tokens (search history
  for the prefix; full token is intentionally not reproduced in this repo).
- **Node.js 20 deprecation warning** in CI: `actions/checkout@v4`, `docker/build-push-action@v6`,
  `docker/setup-buildx-action@v3`, `docker/setup-qemu-action@v3` need upgrading to
  Node.js 24. Forced default June 16, 2026; removed Sept 16, 2026. Should update
  in a maintenance release.

### Validation still needed

- [ ] `docker compose --profile default up -d` — start minimal stack, verify
      OpenCode web at :4096, FileBrowser at :8080
- [ ] `docker compose --profile re up -d` — add revula + radare2, verify MCP
      tools appear in OpenCode
- [ ] `docker compose --profile ghidra up -d` — add ghidra, verify decompile works
- [ ] `podman-compose up` — rootless mode, verify userns_mode: keep-id works
- [ ] `distroless` re-core smoke test against real binary (zadig-2.8.exe from
      examples/01-suspicious-pe-triage.md)
- [ ] `distroless` re-revula smoke test: `python -c "import revula"` + start
      MCP server, send 1 JSON-RPC ping, verify response

---

## 📋 Methodology

- Always query memini-ai first (it's broken — fall back to memory of context)
- Use 8-Step Boomerang Protocol for any non-trivial work
- Tag-driven releases only; never amend tags
- All commits should match this format: `v0.X.Y: short description`
- Build-containers CI is the source of truth for "image actually works"
- Validate CI before tagging next release
