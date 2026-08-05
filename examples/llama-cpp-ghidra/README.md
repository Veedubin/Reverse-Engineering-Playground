# `llama-cpp-ghidra` — AttackLM Binary RE Audit

> **What this is**: a binary-reverse-engineering audit of the
> `llama-server` (and its dynamically-linked `libllama.so`) that ships with
> AttackLM. The goal is to **prove the production binary is a known
> derivative of upstream `llama.cpp` at a pinned commit, and list every
> divergence** between it and the upstream build.

This is the binary-RE side of the **inversion-audit program**: the data
side (AttackLM v0.3.1, the 11 source/20 bucket/25,601 record dataset) is
audited in `AttackLM/`; the binary side (the model server) is audited here.

## Layout

```
examples/llama-cpp-ghidra/
├── README.md                          ← you are here
├── METHODOLOGY.md                     ← audit procedure (write LAST)
├── binary/
│   ├── llama-server                   ← the audited server binary (5.1 MB)
│   ├── llama-server.sha256            ← canonical hash
│   ├── libllama.so                    ← the inference engine (2.3 MB)
│   ├── libllama.so.sha256             ← canonical hash
│   ├── source-info.json               ← build provenance
│   └── build.log                      ← full cmake configure + build log
├── ghidra-project/                    ← .gpr + .rep (gitignored, rebuildable)
├── docs/
│   ├── function-index.md              ← auto-generated function inventory
│   ├── logits-production.md           ← llm_build_llama audit
│   ├── sampling.md                    ← common_sampler_init + chain audit
│   ├── kv-cache.md                    ← llama_kv_cache_unified audit
│   ├── output-filtering.md            ← post-sampling string-search audit
│   └── cross-binary-diff.md           ← upstream-vs-production diff
└── scripts/
    ├── build.sh                       ← reproducible llama.cpp build
    ├── import-to-ghidra.sh            ← analyzeHeadless import
    └── cross-binary-match.py          ← symbol-based production-vs-upstream diff
```

## Quick start

### 1. Build the audited binary

```bash
cd RE_Playground/examples/llama-cpp-ghidra
./scripts/build.sh
# Produces: binary/llama-server, binary/llama-server.sha256,
#           binary/source-info.json, binary/build.log
```

Override the pinned commit with `LLAMA_CPP_REF=<ref>`.

### 2. Import into Ghidra (optional but recommended)

```bash
./scripts/import-to-ghidra.sh
# or, with a production binary to diff:
./scripts/import-to-ghidra.sh --production /path/to/production-llama-server
```

This takes 5–15 minutes for auto-analysis.

### 3. Run the cross-binary diff (when a production binary is available)

```bash
./scripts/cross-binary-match.py \
    --upstream binary/llama-server \
    --production /path/to/production-llama-server \
    --output-dir docs/
# Produces: docs/cross-binary-diff-functions.md
#           docs/cross-binary-diff-additions.txt
#           docs/cross-binary-diff-deletions.txt
```

## Audit findings (2026-07-06 baseline)

| Target | Result |
|---|---|
| **Logits production** (`llm_build_llama::llm_build_llama`) | Vanilla upstream. No custom LM head, no soft-cap, no projection. |
| **Sampler chain** (`common_sampler_init`) | All 12 upstream sampler types present, no additions, no removals. |
| **KV cache** (`llama_kv_cache_unified::clear(bool)`) | Vanilla upstream. No backdoor, no custom eviction. |
| **Output filtering** | **No filter found.** String-table search and call-graph traversal confirm no post-sampling content filter, no string replacement, no policy enforcement. |
| **Cross-binary diff** | No production binary available yet — `cross-binary-diff.md` is in TODO state. |

## Pinned commit

`llama.cpp` commit `79b33b231774d5c39c8df018e9a276becae6d41a` (short
`79b33b231`), committed 2025-07-01T09:19:16+02:00, PR #14456
"opencl: add GEGLU, REGLU, SWIGLU".

The user's task description referenced commit `b5788`; `git` resolved the
short-SHA prefix to `79b33b231`. The full SHA is the canonical pin (the
short prefix is kept in `binary/source-info.json` for traceability).

## Re-running the audit when llama.cpp ships a new release

1. `git pull` or update the `LLAMA_CPP_REF` env var in `build.sh`.
2. Re-run `./scripts/build.sh`. The new binary overwrites
   `binary/llama-server`; the SHA256 is updated; `source-info.json` is
   rewritten.
3. Re-run `./scripts/import-to-ghidra.sh` to refresh the Ghidra project.
4. Diff the new upstream against any production binary with
   `./scripts/cross-binary-match.py`.
5. Update the four `docs/*.md` files with the new function addresses and
   any new findings.
6. Commit on a new branch (e.g. `feat/llama-cpp-ghidra-YYYY-MM-DD`).
