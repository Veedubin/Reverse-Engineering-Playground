---
name: /release
description: Bump version, create git tag, and push for release
argument:
  - name: project
    description: Project to release (boomerang-v3, memini-ai-dev, boomerang-queue, boomerang-proxy)
    required: true
  - name: version
    description: Version to bump to (e.g., 0.3.3, 0.2.9)
    required: true
  - name: dry-run
    description: Show what would be done without executing
    required: false
---

## /release — Create a Release

Bump the version, create a git tag, and push for continuous deployment.

### Usage

```
/release --project=boomerang-v3 --version=0.3.3
/release --project=memini-ai-dev --version=0.2.9 --dry-run
```

### Per-Project Release Steps

| Project | Language | Release Steps |
|---------|----------|---------------|
| `boomerang-v3` | TypeScript | 1. Update `package.json` version<br>2. `npm run build`<br>3. `git tag v{version}`<br>4. `git push origin v{version}`<br>5. GitHub Actions publishes to NPM |
| `memini-ai-dev` | Python | 1. Update `pyproject.toml` version<br>2. `uv build`<br>3. `git tag v{version}`<br>4. `git push origin v{version}`<br>5. GitHub Actions publishes to PyPI |
| `boomerang-queue` | Python | 1. Update `pyproject.toml` version<br>2. `uv build`<br>3. `git tag queue-v{version}`<br>4. `git push origin queue-v{version}` |
| `boomerang-proxy` | Python | 1. Update `pyproject.toml` version<br>2. `uv build`<br>3. `git tag proxy-v{version}`<br>4. `git push origin proxy-v{version}` |

### Examples

```
# Release boomerang-v3 v0.3.3
/release --project=boomerang-v3 --version=0.3.3

# Dry-run memini-ai-dev release
/release --project=memini-ai-dev --version=0.2.9 --dry-run
```

### Notes

- Requires git remote configured for the project
- NPM packages use `@veedubin/` scope
- PyPI packages use `memini-ai-dev` name
- GitHub Actions handles actual publishing on tag push (see `.github/workflows/`)
- Use `--dry-run` to preview changes before executing
