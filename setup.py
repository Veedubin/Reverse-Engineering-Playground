#!/usr/bin/env python3
"""
RE_Playground setup orchestrator.

A single CLI that drives the boomerang-init + boomerang-customize flows
from the terminal (no agent chat required). Subcommands:

  init         First-run interview: pick providers, set agent→model mapping,
               configure Personas. Writes opencode.json + .re-playground-state.json.
  provider     Add/remove providers without redoing the full interview.
  persona      Edit one agent's Persona, or apply a Persona to many agents.
  status       Show current config + last known state.
  reset        Restore defaults and clear saved state.

All subcommands work non-interactively with flags for scripting.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# --- Paths ------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent
OPENCODE_DIR = ROOT / ".opencode"
PROVIDERS_DIR = OPENCODE_DIR / "providers"
AGENTS_DIR = OPENCODE_DIR / "agents"
OPENCODE_JSON = OPENCODE_DIR / "opencode.json"
STATE_FILE = ROOT / ".re-playground-state.json"
ENV_FILE = ROOT / ".env"
ENV_EXAMPLE = ROOT / ".env.example"


# --- Pretty output ---------------------------------------------------------


def _color(text: str, c: str) -> str:
    if not sys.stdout.isatty():
        return text
    codes = {
        "g": "\033[1;32m",
        "r": "\033[1;31m",
        "y": "\033[1;33m",
        "c": "\033[1;36m",
        "b": "\033[1m",
        "d": "\033[2m",
        "x": "\033[0m",
    }
    return f"{codes.get(c, '')}{text}{codes['x']}"


def info(m):
    print(f"{_color('[*]', 'c')} {m}")


def ok(m):
    print(f"{_color('[+]', 'g')} {m}")


def warn(m):
    print(f"{_color('[!]', 'y')} {m}")


def err(m):
    print(f"{_color('[-]', 'r')} {m}", file=sys.stderr)


# --- Provider discovery ----------------------------------------------------


@dataclass
class Provider:
    id: str
    name: str
    path: Path
    raw: dict


def load_providers() -> dict[str, Provider]:
    providers: dict[str, Provider] = {}
    for f in sorted(PROVIDERS_DIR.glob("*.json")):
        try:
            data = json.loads(f.read_text())
        except json.JSONDecodeError as e:
            warn(f"Skipping {f.name}: invalid JSON ({e})")
            continue
        pid = data.get("_meta", {}).get("id") or f.stem
        providers[pid] = Provider(
            id=pid,
            name=data.get("_meta", {}).get("name", pid),
            path=f,
            raw=data,
        )
    return providers


# --- State -----------------------------------------------------------------


@dataclass
class InitState:
    created_at: str = ""
    updated_at: str = ""
    workload: str = ""
    budget_tier: str = "balanced"  # premium / balanced / budget / free
    providers: list[str] = field(default_factory=list)
    forced: list[str] = field(default_factory=list)
    avoided: list[str] = field(default_factory=list)
    long_context: bool = False
    agent_models: dict[str, str] = field(default_factory=dict)
    agent_temperatures: dict[str, float] = field(default_factory=dict)
    personas: dict[str, str] = field(default_factory=dict)

    def save(self, path: Path = STATE_FILE) -> None:
        self.updated_at = datetime.now(timezone.utc).isoformat()
        if not self.created_at:
            self.created_at = self.updated_at
        path.write_text(json.dumps(asdict(self), indent=2) + "\n")

    @classmethod
    def load(cls, path: Path = STATE_FILE) -> "InitState":
        if not path.exists():
            return cls()
        try:
            data = json.loads(path.read_text())
            return cls(
                **{k: v for k, v in data.items() if k in cls.__dataclass_fields__}
            )
        except (json.JSONDecodeError, TypeError) as e:
            warn(f"State file unreadable: {e}. Starting fresh.")
            return cls()


# --- opencode.json merge ---------------------------------------------------


def write_opencode_providers(
    selected: list[str], providers: dict[str, Provider]
) -> None:
    """Merge selected provider blocks into opencode.json.

    OpenCode supports multi-provider natively. We just write all selected
    provider blocks into the `provider` key. Other keys in opencode.json
    (mcp, tool_output, plugin, lsp, etc.) are preserved.
    """
    if not OPENCODE_JSON.exists():
        err(f"{OPENCODE_JSON} not found. Are you in RE_Playground/?")
        sys.exit(1)

    cfg = json.loads(OPENCODE_JSON.read_text())

    merged: dict[str, Any] = {}
    for pid in selected:
        if pid not in providers:
            warn(f"Unknown provider '{pid}', skipping")
            continue
        # Strip the _meta block — opencode doesn't recognize it
        block = {k: v for k, v in providers[pid].raw.items() if k != "_meta"}
        merged[pid] = block

    cfg["provider"] = merged
    OPENCODE_JSON.write_text(json.dumps(cfg, indent=2) + "\n")
    ok(f"Wrote {OPENCODE_JSON} with {len(merged)} provider(s): {', '.join(merged)}")


# --- Provider subcommand ---------------------------------------------------


def cmd_provider(args, providers: dict[str, Provider]) -> int:
    state = InitState.load()

    if args.action == "list":
        print()
        for pid, p in providers.items():
            meta = p.raw.get("_meta", {})
            n_models = len(p.raw.get("models", {}))
            mark = "  " if pid not in state.providers else _color("[*] ", "g")
            print(
                f"  {mark}{pid:<14} {p.name:<22} {n_models} models  "
                f"{_color(meta.get('lastReviewed', '?'), 'd')}"
            )
        print()
        print(f"  Legend: {_color('[*]', 'g')} = currently selected")
        return 0

    if args.action == "add":
        to_add = [a for a in args.ids if a in providers]
        if not to_add:
            err(f"No valid providers in: {args.ids}")
            err(f"Available: {', '.join(providers)}")
            return 1
        new = list(dict.fromkeys(state.providers + to_add))
        write_opencode_providers(new, providers)
        state.providers = new
        state.save()
        return 0

    if args.action == "remove":
        new = [p for p in state.providers if p not in args.ids]
        if not new:
            err("Can't remove all providers — playground needs at least one.")
            return 1
        write_opencode_providers(new, providers)
        state.providers = new
        state.save()
        return 0

    if args.action == "set":
        # Replace wholesale
        bad = [a for a in args.ids if a not in providers]
        if bad:
            err(f"Unknown providers: {bad}")
            return 1
        write_opencode_providers(args.ids, providers)
        state.providers = list(args.ids)
        state.save()
        return 0

    return 1


# --- Persona subcommand ----------------------------------------------------

PERSONA_MARKER = "<!-- PERSONA-MARKER"
DEFAULT_PERSONA = """\
## Persona

_Default: General-purpose reverse engineering assistant. Replace this with a
description of the specific work you want this agent to focus on — for example
"Android APK analysis with Frida", "ARM firmware RE on Cortex-M", "network
protocol reversing with Wireshark", or "malware triage and IOC extraction".

Delete this paragraph and write your own below._
"""


def apply_persona(agent_file: Path, new_body: str) -> tuple[bool, str]:
    """Replace the body under `## Persona` in agent_file. Returns (ok, message).

    File layout expected:
        ... locked content ...
        ## Persona

        <!-- PERSONA-MARKER ... -->
        <customizable body>

    The `## Persona` H2 is the start; the comment marker is a structural
    delimiter inside the persona block that we ALWAYS preserve. Everything
    from the H2 onward is replaceable; everything before the H2 is locked.
    """
    if not agent_file.exists():
        return False, f"file not found: {agent_file}"

    original = agent_file.read_text()

    if PERSONA_MARKER not in original:
        return False, "missing PERSONA-MARKER comment — run _append_persona.py first"

    # Find the `## Persona` H2 — it must be the LAST H2 in the file
    persona_h2 = list(re.finditer(r"^## Persona\s*$", original, re.MULTILINE))
    if not persona_h2:
        return False, "no `## Persona` H2 found"
    if len(persona_h2) > 1:
        return (
            False,
            f"multiple `## Persona` H2s found ({len(persona_h2)}) — file is malformed",
        )
    h2 = persona_h2[0]

    pre = original[: h2.start()]  # locked content above (and the H2 line itself)
    persona_section = original[h2.start() :]  # H2 + body

    # Find the end of the persona block: next `## ` H2 or EOF
    next_h2 = re.search(r"^## ", persona_section[len("## Persona") :], re.MULTILINE)
    if next_h2:
        # next_h2.start() is offset within persona_section[len("## Persona"):]
        # convert back to persona_section absolute offset
        end_of_persona = len("## Persona") + next_h2.start()
        tail = persona_section[end_of_persona:]
    else:
        tail = ""

    # ALWAYS re-emit the marker as a structural delimiter so future
    # edits can find it. Even after a persona rewrite.
    new_section = (
        f"## Persona\n\n"
        f"<!-- PERSONA-MARKER: STRUCTURAL DELIMITER — preserved across edits. -->\n\n"
        f"{new_body.rstrip()}\n"
    )
    if tail.strip():
        new_section += "\n" + tail

    new_text = pre + new_section

    # Safety: locked content above the H2 must be unchanged
    if new_text[: h2.start()] != pre:
        return False, "pre-H2 text would change — aborting"

    agent_file.write_text(new_text)
    return True, f"updated {agent_file.name}"


def list_agents() -> list[Path]:
    return sorted(AGENTS_DIR.glob("*.md"))


def cmd_persona(args) -> int:
    state = InitState.load()
    agents = [a for a in list_agents() if a.name != "_append_persona.py"]

    if args.list:
        print()
        for a in agents:
            has_custom = state.personas.get(a.stem)
            mark = _color("[custom]", "g") if has_custom else _color("[default]", "d")
            print(f"  {mark}  {a.stem}")
        print()
        return 0

    # Determine target agent(s)
    if args.agent:
        targets = [AGENTS_DIR / f"{args.agent}.md"]
    elif args.apply_group:
        prefix = args.apply_group
        targets = [
            a for a in agents if a.stem == prefix or a.stem.startswith(prefix + "-")
        ]
        if not targets:
            err(f"No agents match prefix '{prefix}'")
            return 1
    else:
        # Interactive
        if not sys.stdin.isatty():
            err("Either --agent, --apply-group, --list, or interactive TTY required.")
            return 1
        print("Which agent? (number or name)")
        for i, a in enumerate(agents, 1):
            print(f"  {i:2}. {a.stem}")
        choice = input("> ").strip()
        try:
            idx = int(choice) - 1
            targets = [agents[idx]]
        except (ValueError, IndexError):
            # try by name
            matches = [a for a in agents if a.stem == choice]
            if not matches:
                err("Invalid choice")
                return 1
            targets = matches

    if args.reset:
        body = DEFAULT_PERSONA.replace("## Persona\n\n", "").rstrip()
        for t in targets:
            ok_flag, msg = apply_persona(t, body)
            if ok_flag:
                ok(msg)
                state.personas.pop(t.stem, None)
            else:
                err(msg)
        state.save()
        return 0

    if not args.description:
        err("--description is required (or pass --reset)")
        return 1

    # Wrap the user's description in a small framing paragraph
    body = (
        f"You are a specialist focused on {args.description}. "
        f"Lean on the tools most appropriate to this work, follow the project's "
        f"protocol (memory query → thought chain → plan → delegate → git check → "
        f"quality gates → doc update → memory save), and produce concise, technical "
        f"output. Stay within your agent's scope — escalate to the orchestrator "
        f"(`boomerang`) or architect (`boomerang-architect`) when work crosses "
        f"role boundaries."
    )

    for t in targets:
        ok_flag, msg = apply_persona(t, body)
        if ok_flag:
            ok(msg)
            state.personas[t.stem] = args.description
        else:
            err(msg)

    state.save()
    return 0


# --- Status subcommand -----------------------------------------------------


def cmd_status(args) -> int:
    state = InitState.load()
    providers = load_providers()

    print()
    print(_color("RE_Playground Status", "b"))
    print("=" * 50)

    print(
        f"\n{_color('State file:', 'b')}    {STATE_FILE}  "
        f"({_color('present', 'g') if STATE_FILE.exists() else _color('absent', 'y')})"
    )
    if state.updated_at:
        print(f"{_color('Last init:', 'b')}      {state.updated_at}")
    if state.workload:
        print(f"{_color('Workload:', 'b')}       {state.workload}")
    if state.budget_tier:
        print(f"{_color('Budget:', 'b')}         {state.budget_tier}")
    print(f"{_color('Long-context:', 'b')}    {state.long_context}")

    print(f"\n{_color('Selected providers:', 'b')}")
    if state.providers:
        for p in state.providers:
            n = len(providers.get(p, Provider(p, p, Path(), {})).raw.get("models", {}))
            print(f"  - {p:<14} ({n} models)")
    else:
        print(
            f"  {_color('(none — run `./setup.py init` or `./setup.py provider add ...`', 'y')}"
        )

    if state.agent_models:
        print(f"\n{_color('Agent → Model mapping:', 'b')}")
        for agent, model in sorted(state.agent_models.items()):
            t = state.agent_temperatures.get(agent)
            t_str = f"  temp={t}" if t is not None else ""
            print(f"  - {agent:<32} {model}{t_str}")

    if state.personas:
        print(f"\n{_color('Custom Personas:', 'b')}")
        for agent, desc in sorted(state.personas.items()):
            print(f"  - {agent}: {desc[:80]}{'…' if len(desc) > 80 else ''}")
    else:
        n_defaults = len([a for a in list_agents() if a.name != "_append_persona.py"])
        print(
            f"\n{_color('Custom Personas:', 'b')}  {n_defaults} agents on default persona"
        )

    # Check opencode.json validity
    if OPENCODE_JSON.exists():
        try:
            cfg = json.loads(OPENCODE_JSON.read_text())
            n_providers = len(cfg.get("provider", {}))
            print(
                f"\n{_color('opencode.json:', 'b')}    {n_providers} provider(s) active, valid JSON"
            )
        except json.JSONDecodeError as e:
            err(f"opencode.json is INVALID: {e}")

    print()
    return 0


# --- Reset subcommand ------------------------------------------------------


def cmd_reset(args) -> int:
    if STATE_FILE.exists():
        if not args.yes:
            r = input("Delete .re-playground-state.json? [y/N] ").strip().lower()
            if r != "y":
                info("Cancelled.")
                return 0
        STATE_FILE.unlink()
        ok("Removed state file")
    else:
        info("No state file to remove")

    if args.full:
        warn("--full reset not implemented yet. Run `./setup.py init` to re-do setup.")
    return 0


# --- Init subcommand -------------------------------------------------------


def cmd_init(args) -> int:
    """Init flow: interview the user, then write opencode.json + state.

    This is the non-agent version. The `boomerang-init` skill is the
    agent-powered equivalent. They produce the same output state.
    """
    if not args.yes and not args.from_state:
        info("Init flow — non-interactive mode not yet implemented in setup.py.")
        info("Please run the `boomerang-init` skill from inside an opencode session,")
        info("or use `./setup.py provider add ...` and `./setup.py persona ...` to")
        info("configure providers and agents without the full interview.")
        return 0

    state = InitState.load()
    if args.from_state and state.created_at:
        info(f"Re-applying state from {state.updated_at}")
    else:
        warn("No saved state. Run `./setup.py provider add ...` to get started.")
        return 0

    providers = load_providers()
    if not state.providers:
        err("State has no providers. Add at least one:")
        err("    ./setup.py provider add ollama-cloud")
        return 1

    write_opencode_providers(state.providers, providers)
    ok("Init re-applied from saved state.")
    return 0


# --- Entrypoint ------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="setup.py",
        description="RE_Playground orchestrator: providers, models, personas.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # init
    p_init = sub.add_parser("init", help="first-run interview (full setup)")
    p_init.add_argument("--yes", action="store_true", help="non-interactive")
    p_init.add_argument(
        "--from-state", action="store_true", help="re-apply last known state"
    )
    p_init.add_argument("--no-persona", action="store_true", help="skip persona phase")

    # provider
    p_prov = sub.add_parser("provider", help="manage LLM providers")
    p_prov_sub = p_prov.add_subparsers(dest="action", required=True)
    p_prov_sub.add_parser("list", help="show available + selected providers")
    p_prov_add = p_prov_sub.add_parser("add", help="add providers to the active set")
    p_prov_add.add_argument(
        "ids", nargs="+", help="provider ids (e.g. ollama-cloud openrouter)"
    )
    p_prov_rm = p_prov_sub.add_parser(
        "remove", help="remove providers from the active set"
    )
    p_prov_rm.add_argument("ids", nargs="+")
    p_prov_set = p_prov_sub.add_parser("set", help="replace the active set")
    p_prov_set.add_argument("ids", nargs="+")

    # persona
    p_pers = sub.add_parser("persona", help="edit an agent's customizable Persona")
    p_pers.add_argument("--agent", help="agent name (without .md)")
    p_pers.add_argument(
        "--apply-group", help="apply to all agents starting with this prefix"
    )
    p_pers.add_argument("--description", help="workload description (focus)")
    p_pers.add_argument(
        "--reset", action="store_true", help="revert to default persona"
    )
    p_pers.add_argument(
        "--list", action="store_true", help="list all agents and their state"
    )

    # status
    sub.add_parser("status", help="show current state")

    # reset
    p_reset = sub.add_parser("reset", help="clear saved state")
    p_reset.add_argument(
        "--full", action="store_true", help="also revert opencode.json"
    )
    p_reset.add_argument("--yes", action="store_true", help="don't prompt")

    args = parser.parse_args()

    if args.cmd == "init":
        return cmd_init(args)
    if args.cmd == "provider":
        return cmd_provider(args, load_providers())
    if args.cmd == "persona":
        return cmd_persona(args)
    if args.cmd == "status":
        return cmd_status(args)
    if args.cmd == "reset":
        return cmd_reset(args)

    parser.print_help()
    return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        err("\nInterrupted.")
        sys.exit(130)
