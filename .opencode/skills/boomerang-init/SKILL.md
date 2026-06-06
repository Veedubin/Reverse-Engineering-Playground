---
name: boomerang-init
description: First-run setup for RE_Playground. Picks LLM providers, configures agent→model mapping, runs a live web search to surface current best/cheap models, and triggers boomerang-customize to tailor each agent's Persona to the user's workload.
---

# Boomerang Init (RE_Playground)

## Description

Set up the playground for a specific user. This skill is invoked the
first time a user clones `RE_Playground/` and again whenever they want
to change providers, swap models, or refresh their customizations.

It does **not** ship any vendor binaries or proprietary config. It
just wires up the user's own API keys to the open-source agent
framework in `.opencode/agents/`.

## Triggers

Use this skill when:
- First run of `RE_Playground/`
- The user says "I want to use Claude / GPT / Gemini / Ollama"
- The user says "switch providers", "swap models", "use cheaper models"
- The user adds a new API key to `.env`

## Model

Use **Kimi K2.6** for the init interview. The init flow needs
mid-strength reasoning to translate the user's stated workload into
provider/model choices, but does not need frontier reasoning.

## Initialization Workflow

### Phase 1: Discovery

Read what's already in the playground:
- `RE_Playground/.env` (if it exists) — which keys does the user have?
- `RE_Playground/.opencode/opencode.json` — current provider config
- `.re-playground-state.json` (if it exists) — saved init choices from
  a prior run
- The agent `.md` files — see what Personas are already set

### Phase 2: User Interview

Ask the user these questions, one or two at a time. Don't dump them
all at once — keep it conversational.

**Q1. Workload**
> What kind of reverse engineering are you doing?
> - Android APK analysis
> - ARM/MIPS firmware (embedded, IoT)
> - x86/x86_64 native binaries
> - Network protocol reversing
> - Web/API security
> - Mixed / exploring
> - Other (describe)

**Q2. Provider keys**
> Which LLM providers do you have API keys for?
> - Ollama Cloud
> - OpenRouter
> - Anthropic (direct)
> - OpenAI (direct)
> - Google AI (Gemini)
> - Other (specify)

Multi-select. The user can pick one or several. **The more providers,
the more model options for the agent→model mapping.**

**Q3. Budget**
> How would you describe your budget?
> - Premium (best reasoning, cost is no object — Claude Opus, GPT-5, etc.)
> - Balanced (strong but cost-conscious — Claude Sonnet, Gemini Flash, MiniMax M3)
> - Budget (cheapest viable — Haiku, o4-mini, Gemma 3 4B, etc.)
> - Free-tier only (Gemini 2.5 Flash free tier)

**Q4. Forced picks**
> Any models you specifically want to use, or specifically want to avoid?
> (Free-form. e.g. "force Claude Sonnet for the architect" or
> "no Anthropic, please".)

**Q5. Long-context workloads**
> Will you be feeding any single document > 100K tokens to an agent?
> (e.g. inlining a whole APK source dump, a 500MB binary's strings,
> a long Wireshark capture.) If yes, prefer Gemini 2.5 Pro (1M ctx)
> or Claude Sonnet 4.5 (200K ctx).

**Q6. Customization scope**
> Do you want to set a Persona for each agent now, or later?
> - Now: I'll ask follow-up questions per agent
> - Later: skip Persona setup, run `boomerang-customize` ad-hoc

### Phase 3: Provider Research (Curated + Search Fallback)

For each provider the user picked, look up current model info.

**Step 1: Curated list (always).**
Each provider file in `.opencode/providers/<id>.json` has:
- `models` — full model catalog
- `recommended.best`, `recommended.fast`, `recommended.cheap` — tier picks
- `lastReviewed` — date stamp

Read these. If `lastReviewed` is more than 30 days old, **flag it** and
proceed to Step 2.

**Step 2: Live search (only if curated is stale or user asks).**
Use the `researcher` agent to query each provider's docs and pricing
page. Queries to run:
```
"<provider> latest frontier models 2026"
"<provider> best coding models 2026"
"<provider> pricing per million tokens"
```

If web search fails (rate limit, network, etc.), fall back to the
curated list and warn the user.

**Step 3: Build a unified "model universe".**
Combine all the user's providers into a single ranked list, normalized
to the same field names. Example:

| Tier   | Provider      | Model                          | Cost (1M tok) | Context  |
| ------ | ------------- | ------------------------------ | ------------- | -------- |
| best   | openrouter    | anthropic/claude-opus-4.5      | $$$           | 200K     |
| best   | openrouter    | openai/gpt-5                   | $$$           | 200K     |
| best   | google        | gemini-2.5-pro                 | $$            | 1M       |
| best   | ollama-cloud  | deepseek-v4-pro:cloud          | $             | 128K     |
| fast   | ollama-cloud  | minimax-m3-cloud               | $             | 200K     |
| fast   | openrouter    | google/gemini-2.5-flash        | $             | 1M       |
| cheap  | ollama-cloud  | gemma3:4b-cloud                | ¢             | 32K      |
| cheap  | openrouter    | meta-llama/llama-4-70b         | ¢             | 128K     |

### Phase 4: Agent → Model Mapping

Default mapping (the orchestrator's best guess for RE work):

| Agent                       | Default tier | Rationale                                    |
| --------------------------- | ------------ | -------------------------------------------- |
| `boomerang`                 | fast         | Mid-strength reasoning for routing decisions |
| `boomerang-architect`       | best         | Hardest reasoning: protocol design, ADRs     |
| `boomerang-coder`           | fast         | Code generation is well-served by mid-tier   |
| `boomerang-tester`          | cheap        | Repetitive, structured work                  |
| `boomerang-linter`          | cheap        | Same                                         |
| `boomerang-git`             | cheap        | Mechanical commands, summaries               |
| `boomerang-writer`          | fast         | Docs need nuance                             |
| `boomerang-explorer`        | cheap        | File finding                                 |
| `boomerang-scraper`         | cheap        | Web fetching                                 |
| `boomerang-handoff`         | cheap        | Templated                                    |
| `boomerang-init`            | fast         | Setup interviews                             |
| `boomerang-agent-builder`   | fast         | Skill design is mid-strength                 |
| `boomerang-release`         | cheap        | Mechanical                                   |
| `researcher`                | best         | Web research quality matters                 |
| `mcp-specialist`            | fast         | Protocol debugging, mid-tier                 |

Override this default based on:
- User's budget (Q3) — shift everyone down a tier on "Budget"
- User's forced picks (Q4) — honor them
- User's long-context (Q5) — prefer Gemini/Claude for agents likely to
  handle big inputs (`researcher`, `boomerang-architect`,
  `boomerang-coder`)

### Phase 5: Per-Agent Temperature

Temperature is set per-model in the provider block (not per-agent in
opencode's schema). Default temperatures:

| Agent class              | Default temp | Why                                          |
| ------------------------ | ------------ | -------------------------------------------- |
| Architecture/Planning    | 0.2          | Deterministic, structured output             |
| Code generation          | 0.2          | Same                                         |
| Code review / Lint       | 0.1          | Strict, consistent                           |
| Writing / Docs           | 0.4          | More varied phrasing                         |
| Web research             | 0.5          | Open-ended                                   |
| Brainstorming (rare)     | 0.7          | Higher creativity                            |

Apply these as `options.temperature` to the chosen model in the
provider block. **Some models ignore temperature** (most reasoning
models do) — skip if so.

### Phase 6: Reasoning Effort

Reasoning effort is **not** a native opencode.json field. The init
skill should append a "use max reasoning effort" hint to the
`prompt` of the relevant agents if the model supports it (e.g.
`o4-mini`, `deepseek-r1`, `gemini-2.5-pro-thinking`).

Pattern:
```markdown
<original agent prompt>

Reasoning effort: max. Spend tokens on thinking before responding.
```

### Phase 7: Write opencode.json

The `setup.py` tool actually performs the write. This skill produces
the diff and hands it to the tool. The tool:

1. Reads the current `opencode.json`
2. Replaces the `provider` block with the merged multi-provider config
3. Optionally sets `model` and `small_model` at the top level
4. Writes the file

### Phase 8: Persona Customization

If the user said "Now" to Q6, call `boomerang-customize` for each
agent. For each one, ask the focus questions and write the persona
block. Update `.re-playground-state.json` so the choices persist.

### Phase 9: Save State

Write `RE_Playground/.re-playground-state.json` with:
- Timestamp
- Workload description
- Selected providers
- Budget tier
- Forced picks / avoid list
- Long-context flag
- Agent → model mapping
- Per-model temperatures
- Per-agent persona hashes (so we can detect drift)

This file is what `setup.py status` reads to show the current config.

## memini-ai Protocol

### Query at start
- Previous init sessions for this project
- User preferences (model choices, budget tier, workload type)
- Any explicit "I don't want X" / "always use Y" signals from past
  sessions

### Save at end
- The full agent→model mapping
- The provider list
- The persona hashes
- Reasoning for non-obvious choices (e.g. "we picked gemini-2.5-pro for
  the architect because the user said they'd be inlining full APKs")

## CLI Equivalent

```bash
./setup.py init                 # full interview, then write
./setup.py init --no-persona    # skip persona phase
./setup.py init --from-state    # re-apply last known state without re-asking
./setup.py status               # show current state
./setup.py reset                # restore defaults, clear state
```

## Output Format (Return to Orchestrator)

```markdown
## Init Complete: RE_Playground

### Detected
- Workload: <user's answer>
- Providers: <list>
- Budget tier: <premium/balanced/budget/free>
- Long-context: <yes/no>

### Provider Block (written to opencode.json)
- ollama-cloud: <N> models
- openrouter: <N> models
- ...

### Agent → Model Mapping
| Agent           | Tier | Model                          | Temp |
| --------------- | ---- | ------------------------------ | ---- |
| boomerang       | fast | minimax-m3-cloud               | 0.4  |
| re-architect    | best | anthropic/claude-sonnet-4.5    | 0.2  |
| ...             | ...  | ...                            | ...  |

### Personas Set
- <agent>: <one-line summary>  (or "default" if not customized)

### State Saved
- `.re-playground-state.json`: yes
- memini-ai: yes

### Next Steps
- Run `cd .opencode && npm install` if you haven't
- Set API keys in `.env`
- Run `opencode` to start
```
