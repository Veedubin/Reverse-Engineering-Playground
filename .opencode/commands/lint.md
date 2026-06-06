---
name: /lint
description: Run linting across the MCP-Servers monorepo
argument:
  - name: project
    description: Project to lint (boomerang-v3, memini-ai-dev, boomerang-queue, boomerang-proxy, all)
    required: false
  - name: fix
    description: Auto-fix issues where possible
    required: false
---

## /lint — Run Linters

Run the appropriate linter for the specified project (or all projects).

### Usage

```
/lint --project=boomerang-v3
/lint --project=memini-ai-dev
/lint --project=all --fix
```

### Per-Project Commands

| Project | Linter | Fix Command |
|---------|--------|-------------|
| `boomerang-v3` | `npm run lint` (ESLint v9+ flat config) | `npm run lint -- --fix` |
| `memini-ai-dev` | `ruff check .` | `ruff check . --fix` |
| `boomerang-queue` | `ruff check .` | `ruff check . --fix` |
| `boomerang-proxy` | `ruff check .` | `ruff check . --fix` |
| `all` | Runs all linters in sequence | — |

### Examples

```
# Lint only TypeScript project
/lint --project=boomerang-v3

# Lint and auto-fix all Python projects
/lint --project=memini-ai-dev --fix
/lint --project=boomerang-queue --fix
/lint --project=boomerang-proxy --fix
```

### Notes

- TypeScript project uses ESLint flat config (`eslint.config.js`)
- Python projects use ruff for linting and formatting
- The `--fix` flag is passed through to the underlying linter
