---
name: boomerang-customize
description: Edit the customizable Persona section of any Boomerang agent. The Persona lives below a `<!-- PERSONA-MARKER -->` comment in each agent .md file. Everything above the marker (protocol, tools, routing) is locked; everything below is yours.
---

# Boomerang Customize

## Description

Tailor an individual agent's working personality to match your specific
workload. This is the right skill to call when you want a single agent to
focus on a particular kind of reverse engineering (Android APK, ARM
firmware, malware triage, protocol reversing, etc.) without rewriting
the whole agent file.

## The Rule

Every agent `.md` file in `.opencode/agents/` has a **Persona** section
appended at the bottom, marked by a `<!-- PERSONA-MARKER -->` HTML
comment. The convention is:

- **Above the marker** — protocol, tool permissions, routing rules, memory
  protocol. **Do not edit.**
- **Below the marker** — the agent's working personality. **This is yours.**

When this skill runs, it:

1. Locates the `<!-- PERSONA-MARKER -->` comment in the chosen agent.
2. Reads the text below it.
3. Replaces it with the new persona you provide.
4. **Never touches the text above the marker.**

A safety check at the end re-reads the file and verifies that everything
above the marker is byte-identical to the pre-edit version.

## Triggers

Use this skill when:
- You want a specific agent to focus on a particular type of RE work
- You want to revert an agent to its default persona
- You want to apply the same persona to multiple agents
- You're onboarding a new project and want to set the agents' focus

## Model

Use **Kimi K2.6** for the customization interview. The skill needs
mid-strength reasoning to translate your stated goals into a clean
persona block.

## Customization Workflow

### 1. Pick the agent

Ask the user (or default from context):
```
Which agent do you want to customize?
  1. boomerang          (orchestrator)
  2. boomerang-architect
  3. boomerang-coder
  4. boomerang-tester
  5. boomerang-writer
  6. boomerang-linter
  7. boomerang-git
  8. boomerang-explorer
  9. boomerang-scraper
 10. boomerang-researcher
 11. boomerang-handoff
 12. boomerang-init
 13. boomerang-agent-builder
 14. boomerang-release
 15. mcp-specialist
 16. researcher
```

The file is `.opencode/agents/<name>.md`.

### 2. Ask the focus questions

Collect from the user (one at a time, conversational):
- "What kind of RE work are you doing? (APK, firmware, malware, protocol, web, mixed?)"
- "Any specific target OS, architecture, or family? (ARM Cortex-M, x86_64, AArch64, MIPS, RISC-V?)"
- "Any languages/tools you want the agent to lean on? (Frida, Ghidra, radare2, jadx, binwalk, IDA?)"
- "Should the agent avoid any tools or approaches?"
- "Tone: terse and technical, or verbose and explanatory?"

### 3. Generate the persona

Translate the answers into a 3-6 sentence persona block. Example:

```markdown
## Persona

You are an Android APK reverse engineering specialist. You reach for
jadx first for static analysis, Frida for runtime instrumentation of
license checks or trust-all SSL bypass, and use Ghidra MCP only when
a target has interesting native libraries in `lib/arm64-v8a/`. Your
default targets are commercial automotive diagnostic APKs. You write
concise, technical reports — no preamble, no apologies, just the
finding and a recommendation.
```

### 4. Apply the edit

In the target file:
1. Find the line containing `<!-- PERSONA-MARKER -->`.
2. Find the next `## Persona` H2 (one of them may exist already, or you
   may need to add it).
3. Replace the body under `## Persona` with the new text.
4. Stop at the next `## ` H2 (if any) or EOF.

### 5. Safety check

Read the file back and confirm:
- The character offset of the `<!-- PERSONA-MARKER -->` is unchanged
- Everything above it is byte-identical
- The new persona text is present below it

If the safety check fails, abort the edit and report which check failed.

### 6. Confirm

Show the user the new persona and the diff. Ask if they want to
customize another agent or apply the same persona to a group of
agents (e.g. "all the re-* agents should focus on APK analysis").

## CLI Equivalent

The same workflow is available from a terminal via `setup.py persona`:

```bash
# Interactive: pick agent, answer questions, write persona
./setup.py persona

# Non-interactive: pipe in a description
./setup.py persona --agent re-architect --description "APK static analysis with jadx"

# Apply same persona to many agents
./setup.py persona --apply-group re --description "APK analysis"

# Revert an agent to default
./setup.py persona --agent re-architect --reset
```

## Reverting to Default

The default persona for every agent is preserved in the file just below
the marker comment. To revert, simply restore that text:

```markdown
## Persona

_Default: General-purpose reverse engineering assistant. Replace this with a
description of the specific work you want this agent to focus on — for example
"Android APK analysis with Frida", "ARM firmware RE on Cortex-M", "network
protocol reversing with Wireshark", or "malware triage and IOC extraction".

Delete this paragraph and write your own below._
```

## Output Format (Return to Orchestrator)

```markdown
## Persona Updated: <agent-name>

### Focus
- Domain: <APK / firmware / protocol / etc.>
- Tools preferred: <jadx / Frida / Ghidra / etc.>
- Avoid: <if any>

### Persona Written
<the new persona text>

### Safety
- Pre-edit byte-identical above marker: PASS
- Marker offset unchanged: PASS
- Persona block replaced cleanly: PASS
```

## memini-ai Protocol

### Save after every persona change
- `sourceType: "boomerang"`
- `metadata.project: "re-playground"`
- `metadata.type: "persona-update"`
- `metadata.agent: "<agent-name>"`

Include the new persona text as the memory content so we can replay it
later if the agent file is reset or the playground is reinstalled.
