# Security Policy

## Supported versions

| Version | Supported           |
|---------|---------------------|
| v0.2.x  | :white_check_mark: Yes |
| v0.1.x  | :x: No (upgrade to v0.2.0) |
| < v0.1  | :x: No              |

## Reporting a vulnerability

**Please do not file a public issue.** RE_Playground is a reverse-engineering
toolkit — vulnerabilities in the *toolkit itself* (RCE in our installer, secret
leakage in the default config, container escape paths) deserve quiet
coordination.

Email **security reports** to: open a private security advisory on
[GitHub Security Advisories](../../security/advisories/new) for this repo
(recommended) or DM `Veedubin` on GitHub. We will respond within 72 hours.

For clearly-low-impact issues (typos, missing docs, version bumps), an
ordinary public issue is fine.

## What we consider in scope

Vulnerabilities **in RE_Playground itself** — the things we ship:

- **RCE in `install.py`** — arbitrary code execution through crafted
  tool-name, version, or distro parameters
- **Hardcoded secrets in shipped config** — if a future regression causes
  a token to land in `opencode.json` or a Dockerfile, we want to know fast
  (CI enforces this with regex scans, but humans are the last line)
- **Container escape** — paths through which an untrusted binary uploaded
  via FileBrowser could reach the host filesystem or other containers
- **Path traversal** in TUI prompts that accept user input
- **Supply-chain compromise** of a tool/MCP server we recommend in
  `install.py` or `setup.py`

## What is out of scope (use the upstream's process)

- Vulnerabilities **in the tools themselves** (Ghidra, radare2, YARA, ILSpy,
  revula, etc.). Report those to the upstream project.
- Vulnerabilities **in the OpenCode platform** itself
- Vulnerabilities in **Ollama Cloud / Anthropic / OpenAI / OpenRouter** APIs
- Your local model endpoint leaking your prompt
- Issues with the `memini-ai` server (report to that repo)

## Disclosure timeline

We follow a **90-day responsible disclosure** window:

1. **Day 0** — You report privately
2. **Day 1-7** — We acknowledge and triage
3. **Day 7-60** — We develop and ship a fix
4. **Day 60-90** — Coordinated disclosure
5. **Day 90** — Public disclosure (we'll credit you unless you prefer anonymity)

We will keep you in the loop at every step.

## Hardening recommendations for users

Even though RE_Playground is hardened, you are running an agent that can
decompile, debug, and execute binaries. Treat it like an untrusted-user
workstation:

1. **Run the multi-container stack in production** — `docker compose up -d`
   isolates the dangerous tools (Ghidra's JVM, Wine in the r2 container)
   from your host filesystem.
2. **Use a throwaway VM** for hostile binary analysis — the agent will run
   `wine target.exe` or `frida target.exe` without asking twice. The
   `re-samples` volume mount is `:ro` on the agent containers for a reason.
3. **Treat the `.env` file like a private key** — Ollama/GitHub tokens grant
   paid API access. Rotate if you suspect exposure.
4. **Watch the `validate` CI workflow** — every push to `master` runs a
   secret scan. If it ever fails, treat the repo as compromised until proven
   otherwise.
5. **Don't expose port 4096 to the public internet without a reverse proxy
   and a strong `OPENCODE_SERVER_PASSWORD`** — see `docs/container.md` for
   Tailscale / nginx + Let's Encrypt guides.
6. **Disable the MCP servers you don't need** — `github-mcp`, `markitdown`,
   and `playwright` are disabled by default for a reason. If you enable one,
   understand the data it exfiltrates.
