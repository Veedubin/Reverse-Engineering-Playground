# Contributing to RE_Playground

Thanks for your interest in RE_Playground! Whether you're a first-time
contributor or a seasoned reverse engineer, this guide will help you get
your first PR merged.

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md).
By participating, you agree to its terms.

## How to report a bug

**Don't** open a public issue for suspected security vulnerabilities — see
[SECURITY.md](SECURITY.md) instead.

For everything else, open a [Bug Report](../../issues/new?template=bug_report.md).

## How to suggest a feature

Open a [Feature Request](../../issues/new?template=feature_request.md) and use
the **Motivation** section to explain *why*, not just *what*.

## Development setup

RE_Playground is a **distribution** — the project ships configuration, scripts,
documentation, and Dockerfiles. There is no compiled binary to build. To
develop locally:

```bash
# 1. Fork and clone
git clone https://github.com/YOUR_USERNAME/Reverse-Engineering-Playground.git
cd Reverse-Engineering-Playground

# 2. Install the platform OpenCode (>= 1.0)
curl -fsSL https://opencode.ai/install | bash

# 3. Run the TUI installer to install all RE tools
./install.py

# 4. (Optional) Install the multi-container stack
docker compose up -d

# 5. Try the agents
opencode
```

## What to work on

Issues tagged [`good first issue`](../../issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)
are pre-screened and friendly to new contributors. Look there first.

For larger work (new MCP server integration, new agent persona, major doc
restructuring), please open an issue **before** opening a PR. We want to align
on direction before you invest the time.

## Pull request process

1. **Branch off `master`** — `git checkout -b fix/short-description`
2. **Make focused commits** — one logical change per commit
3. **Run the validators locally before pushing:**
   ```bash
   python -m py_compile install.py        # syntax check
   python install.py --list               # 23 tools in 5 groups
   python install.py --check              # what's installed
   ruff check install.py                  # lint (warnings OK)
   ```
4. **CI must pass** — every PR triggers the [`validate`](.github/workflows/validate.yml)
   workflow which checks JSON/YAML syntax, secret patterns, hardcoded paths,
   and agent persona markers. CIs on tags additionally build + push 4
   container images to GHCR.
5. **Reference the issue** — "Fixes #123" in the PR body
6. **Squash before merge** — we use squash-merge to keep `master` linear

## Coding conventions

### Python (install.py, setup.py)
- Python 3.10+ syntax (no `from __future__ import annotations` needed)
- Type hints preferred
- Prefer stdlib + `questionary` (already a dep). Don't add new dependencies
  without discussion — TUI installers should stay bootable from a vanilla
  system.
- No emojis in print statements (the TUI banner is the only exception)

### JSON / YAML
- 2-space indent
- `opencode.json` MUST be valid OpenCode config — see https://opencode.ai/docs/config/
- Compose files MUST be valid against `docker compose config` (both Compose
  v2 schema) and `podman-compose validate`

### Markdown
- 80-column soft wrap for prose, hard-wrap for tables
- Use ATX headers (`##`, `###`)
- Code fences must declare a language (`bash`, `json`, `python`, `dockerfile`)

### Agent personas
Every file in `.opencode/agents/` MUST contain:
- A `## Persona` second-level heading
- A `<!-- PERSONA-MARKER -->` HTML comment immediately after the heading
- A closing `<!-- /PERSONA-MARKER -->` at the end of the persona block

The CI validator will fail the build if any agent file is missing these. Use
`./.opencode/agents/_append_persona.py` to repair a missing marker.

## Testing

There is no formal test suite. The "test" for `install.py` and `setup.py` is:
1. `python -m py_compile install.py` — syntax
2. `python install.py --list` — catalog renders correctly
3. `python install.py --check` — all 23 tools reported against your system
4. `python install.py --yes` — full install path on a fresh VM

These four commands are the manual QA. If your change breaks any of them, the
PR will not be merged.

For documentation changes, `markdownlint` is the closest thing to a test:
```bash
npx markdownlint-cli2 '**/*.md' '#node_modules' '#.git'
```

## What we won't accept

- **Vendor binaries** — never commit `.exe`, `.dll`, `.deb`, `.AppImage`,
  Ghidra `.zip`, or any closed-source binary. We link to official sources.
- **Hardcoded secrets** — all tokens, paths, and credentials go through
  `.env` / `{env:...}` placeholders. The CI secret-scanner enforces this.
- **Hardcoded user paths** — `/home/you/`, `/Users/you/`, `C:\Users\you\`.
  Same scanner enforces this.
- **License changes that are more restrictive than MIT** — every dependency
  we ship is MIT-compatible. Adding GPL/AGPL code is a deliberate policy
  decision; open an issue first.
- **Auto-generated tool catalogs** — if you add a new tool, edit the
  `add(...)` call in `install.py` directly. Don't write a generator.

## Questions?

Open a [Discussion](../../discussions) or tag `@Veedubin` in an issue.
