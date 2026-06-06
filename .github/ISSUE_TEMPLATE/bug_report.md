---
name: Bug Report
about: Report a problem with RE_Playground
title: "[Bug]: "
labels: ["bug"]
assignees: []
---

## Description

A clear and concise description of what the bug is.

## Steps to Reproduce

1. Run `...`
2. See error

## Expected Behavior

What you expected to happen.

## Actual Behavior

What actually happened. Include error messages, stack traces, or screenshots.

## Environment

- **OS**: [e.g., Arch Linux, Ubuntu 24.04, macOS 15]
- **Python version**: [e.g., 3.12.4]
- **OpenCode version**: [e.g., 1.14.20]
- **LLM provider**: [e.g., Ollama Cloud, OpenRouter]
- **Relevant tool versions**: [e.g., Ghidra 12.1, radare2 6.1.2]

## Install Script Output

If the issue is with `install.py`, paste the output of `./install.py --check`:

```
[output here]
```

## Memory / MCP Setup

If the issue is with memini-ai or MCP servers:

- Is memini-ai running? (`memini-ai-dev_get_status`)
- Is PostgreSQL + pgvector installed?
- Did you configure `.env` with `MEMINI_DB_URL`?

## Additional Context

Add any other context about the problem here.
