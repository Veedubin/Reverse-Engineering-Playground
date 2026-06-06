---
name: /test
description: Run tests across the MCP-Servers monorepo
argument:
  - name: project
    description: Project to test (boomerang-v3, memini-ai-dev, boomerang-queue, boomerang-proxy, all)
    required: false
  - name: watch
    description: Run tests in watch mode (TypeScript only)
    required: false
---

## /test — Run Project Tests

Run the test suite for the specified project (or all projects).

### Usage

```
/test --project=boomerang-v3
/test --project=memini-ai-dev
/test --project=boomerang-queue
/test --project=boomerang-proxy
/test --project=all
```

### Per-Project Commands

| Project | Command | Notes |
|---------|---------|-------|
| `boomerang-v3` | `npx vitest run` | TypeScript ESM tests with vitest |
| `memini-ai-dev` | `pytest` | Python tests (requires PostgreSQL on 5434) |
| `boomerang-queue` | `pytest` | Python FastMCP tests |
| `boomerang-proxy` | `pytest` | Python FastAPI tests (needs FastAPI >=0.115.0) |
| `all` | Runs all of the above in sequence | Stops on first failure unless `--continue` |

### Examples

```
# Run boomerang-v3 tests
/test --project=boomerang-v3

# Run all Python tests
/test --project=memini-ai-dev
/test --project=boomerang-queue
/test --project=boomerang-proxy
```

### Notes

- memini-ai-dev and boomerang-queue tests require PostgreSQL running on `localhost:5434`
- boomerang-proxy tests require FastAPI >=0.115.0
- Use `npx vitest` with `--watch` flag for watch mode on TypeScript projects
