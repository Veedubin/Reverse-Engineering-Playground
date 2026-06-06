# Provider Library

This directory contains reusable provider configuration blocks for
[OpenCode](https://opencode.ai/docs/config/#providers).

A user picks one or more of these, and the playground's `setup.py` tool
merges them into the active `opencode.json` automatically. **No vendor
binaries are shipped** — these JSON files only describe endpoints, API
key env-var names, and curated model lists.

## Supported providers

| File                       | Provider          | Env var(s)                            |
| -------------------------- | ----------------- | ------------------------------------- |
| `ollama-cloud.json`        | Ollama Cloud      | `OLLAMA_BASE_URL`, `OLLAMA_API_KEY`   |
| `openrouter.json`          | OpenRouter        | `OPENROUTER_API_KEY`                  |
| `anthropic.json`           | Anthropic direct  | `ANTHROPIC_API_KEY`                   |
| `openai.json`              | OpenAI direct     | `OPENAI_API_KEY`                      |
| `google.json`              | Google AI Studio  | `GOOGLE_API_KEY`                      |

## How multi-provider merge works

OpenCode's native schema supports multiple providers in one config:

```json
{
  "provider": {
    "ollama-cloud": { "...": "..." },
    "openrouter":   { "...": "..." }
  }
}
```

The `setup.py` CLI rewrites the `provider` block in `opencode.json` based
on which provider JSON files you select. The merge is **additive** — if
you select ollama-cloud and openrouter, both stay in the file. Models
with the same name across providers don't conflict (opencode namespaces
them as `<provider>/<model>`).

The `npm` field on each provider config determines which OpenCode
adapter handles the request. Most providers use
`@ai-sdk/openai-compatible` (Ollama Cloud, OpenRouter). Direct
providers use their own: `@ai-sdk/anthropic`, `@ai-sdk/openai`,
`@ai-sdk/google`.

## Why a curated list?

Model landscapes change weekly. The `models` block in each file is a
**curated snapshot** — not the full provider catalog. The `recommended`
block suggests picks for three tiers:

- `best`  — strongest reasoning, biggest context, premium price
- `fast`  — strong but cheap, good for most work
- `cheap` — minimum viable, for budget runs

The `boomerang-init` skill does a live web search against each
provider's docs at first run to refresh the `recommended` block. If
search fails, the curated list is used as-is.

## Per-model `options`

You can override temperature etc. on a per-model basis by extending
each model entry. Example:

```json
"claude-sonnet-4.5": {
  "name": "Claude Sonnet 4.5",
  "options": {
    "temperature": 0.2
  }
}
```

The `setup.py` tool can set per-agent temperatures globally based on
agent role (low for code/analysis, higher for creative brainstorming).

## Adding a new provider

1. Copy any existing file in this directory.
2. Change the `id`, `name`, `npm`, `baseURL`, `apiKeyEnv`, `models`,
   and `recommended` fields.
3. Add the new env var to `RE_Playground/.env.example`.
4. Update `setup.py`'s `PROVIDERS` list so the init flow can find it.

## Last reviewed

`2026-06-06` — model lists verified against provider docs. Refresh
quarterly or whenever a major model release lands.
