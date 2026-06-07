# Examples

Worked walkthroughs showing RE_Playground in action. Each example includes
the prompt you'd type, what the agents do behind the scenes, and what the
output looks like.

| # | Title | Tools used | Time |
|---|-------|------------|------|
| [01](./01-suspicious-pe-triage.md) | Triage a suspicious Windows PE | diec, pefile, radare2, Ghidra, YARA | 15 min |

## Have an example to contribute?

Open a PR with a new `NN-short-name.md` file. The pattern is:

1. **The scenario** — what the user is trying to accomplish
2. **The setup** — bare metal vs. multi-container, what to drop in `/samples`
3. **The prompt** — exactly what to type into the OpenCode chat
4. **Behind the scenes** — which agents / MCP servers fire, in what order
5. **The output** — a representative report
6. **Follow-ups** — how to drill deeper if anything looks off

See [CONTRIBUTING.md](../CONTRIBUTING.md) for the full style guide.
