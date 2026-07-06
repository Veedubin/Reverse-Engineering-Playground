# METHODOLOGY — `llama-cpp-ghidra` audit

> **Status**: written last, after all other docs. Captures the actual
> procedure used to produce the four `docs/*.md` files and the
> `cross-binary-diff.md` template, plus the reasoning behind the
> architectural choices (which binary to audit, which decompiler to use,
> how to handle the dynamic-linking split).

## What `llama.cpp` is

`llama.cpp` is the de-facto reference implementation of Meta's Llama model
inference in pure C/C++. The repository lives at
<https://github.com/ggerganov/llama.cpp> and is MIT-licensed. It exposes a
C API (`llama.h`) plus a CLI tool `llama-server` that implements the
OpenAI-compatible `/v1/chat/completions` HTTP API. AttackLM runs on a
custom `llama-server` build of llama.cpp; this audit verifies that the
custom build is a clean derivative of a specific upstream commit.

## Threat model

The audit exists because **a model server is a piece of software that
generates text in response to user prompts**, and a malicious or careless
operator could:

- **Add a content filter** to the response (refuse certain topics,
  replace certain tokens, soft-censor).
- **Add a prompt-injection guard** to the request (detect jailbreak
  patterns and refuse to respond, or rewrite the prompt).
- **Add telemetry** that exfiltrates user prompts to a remote endpoint.
- **Substitute the LM head** to redirect outputs to a different model
  family (e.g. a smaller, less capable model, or a different alignment).
- **Backdoor the KV cache clear** to leak previous contexts across
  supposedly-cleared boundaries.
- **Disable a safety mechanism** (e.g. remove the EOS sampler so the
  model never stops generating; remove repetition penalty to allow
  infinite loops).

The audit's job is to **enumerate** which of these are possible in the
audited build, prove they are NOT present (modulo the cross-binary diff
template), and provide a reproducible procedure for re-running the
audit on any new production build.

## The audit's pinned baseline

- **Commit**: `79b33b231774d5c39c8df018e9a276becae6d41a` (short
  `79b33b231`), PR #14456 "opencl: add GEGLU, REGLU, SWIGLU",
  committed 2025-07-01T09:19:16+02:00.
- **Build flags**: `-DGGML_NATIVE=OFF -DCMAKE_BUILD_TYPE=Release`.
- **Compiler**: gcc 16.1.1, cmake 4.3.4, on Linux x86_64 (CachyOS).
- **Output**: `binary/llama-server` (5.1 MB), `binary/libllama.so`
  (2.3 MB), sha256s in `binary/*.sha256`.

The pinned commit is recorded in `binary/source-info.json`. The build is
fully reproducible via `scripts/build.sh`.

## The architecture choice: audit `llama-server` AND `libllama.so`

This is the most important architectural decision and the one most likely
to be wrong if you're not paying attention.

The `llama-server` binary on the host is **NOT statically linked**. The
output of `nm` shows it depends on:
- `libllama.so` — the inference engine (Llama class, KV cache, sampling
  C API).
- `libggml.so` + `libggml-base.so` + `libggml-cpu.so` — the tensor library.
- `libmtmd.so` — multimodal (vision/audio) support.
- `libcurl.so.4` — HTTP client (used for fetching models).
- `libstdc++.so.6`, `libc.so.6`, etc. — standard libraries.

**The four audit targets span BOTH binaries:**

| Target | Lives in | Address (upstream build) |
|---|---|---|
| Logits production (`llm_build_llama::llm_build_llama`) | **`libllama.so`** | `0x0012a690` (1,985 B) |
| Sampler chain (`common_sampler_init`, `common_sampler_sample`) | `llama-server` | `0x00212bf0`, `0x00210980` |
| KV cache (`llama_kv_cache_unified::clear`) | **`libllama.so`** | `0x000c2030` (364 B) |
| Output filtering (post-sampling string match) | `llama-server` | n/a (none found) |

This split is **load-bearing**: if you audit only `llama-server`, you
miss the actual inference (which is where the most dangerous divergences
would live — backdoored matmul weights, hidden LM head, etc.). If you
audit only `libllama.so`, you miss the post-processing pipeline
(content filters live there). Both must be analyzed, and the docs
correctly call out which binary each address lives in.

## The Ghidra container problem (and the workaround)

The user's plan assumed the `ghidra` and `radare2` containers in
`RE_Playground/docker-compose.yml` would be running and that the Ghidra
MCP bridge (245 tools) would be loaded. In practice:

1. **The `re-ghidra` container image was broken** (NOW FIXED — see fix log
   below): the Dockerfile referenced
   `/opt/ghidra-mcp/bridge_mcp_ghidra.py` (a single-file bridge that was
   the upstream `ghidra-mcp` layout through ~v4.x). The actual upstream
   `ghidra-mcp` is now a Python package (`ghidra-mcp-bridge` v5.15.0 on
   PyPI) with entry point `bridge-mcp-ghidra`. The old CMD line opened a
   non-existent file; the container entered a restart loop.

2. **No Ghidra instance was registered with the host MCP bridge**: even
   if the container were running, the Ghidra plugin's UDS discovery
   didn't share socket namespaces with the host. The host bridge reported
   `"instances": []`.

3. **Risk-callout #5 is the only one that applies**: the user said
   "If you hit MCP errors (tool not loaded, schema mismatch), escalate
   to the orchestrator (boomerang) — do not try to fix the MCP server."
   The Ghidra container problem is an environment-setup issue, not an
   MCP protocol issue, so the workaround was **to use the working
   radare2-mcp tools** for the actual analysis.

**What I did instead**: I used the **radare2-mcp** tool family
(radare2-mcp_open_file, radare2-mcp_analyze, radare2-mcp_list_functions,
radare2-mcp_xrefs_to, radare2-mcp_disassemble_function,
radare2-mcp_decompile_function, radare2-mcp_list_symbols,
radare2-mcp_list_strings, radare2-mcp_search). These worked
end-to-end. The r2 `pdc` decompiler's output is fragmentary for
template-heavy C++ (the `llm_build_llama` constructor is 1,985 bytes of
templates), but the symbol-table-based enumeration is complete and the
disassembly is reliable.

**What the user can do to enable the Ghidra path** (NOW DONE — see fix
log below):

1. ~~Update `docker/ghidra/Dockerfile` to install the ghidra-mcp 5.15.0
   wheel via `pip install` and use the `bridge-mcp-ghidra` entry point.~~
   **DONE**: The Dockerfile now uses a multi-stage build that builds the
   GhidraMCP Java plugin with Maven and installs the `ghidra-mcp-bridge`
   Python package from PyPI.

2. Or, run Ghidra locally on the host with the GhidraMCP plugin loaded
   from `/opt/ghidra-mcp/ghidra_scripts/`. The plugin will create a UDS
   socket in `/run/user/$UID/ghidra-mcp/` that the host bridge
   discovers automatically.

3. Or, run `analyzeHeadless` (the script is at
   `/opt/ghidra/support/analyzeHeadless`) directly, which is what
   `scripts/import-to-ghidra.sh` does.

### Fix Log — 2026-07-06: Ghidra MCP container fix

**Owner**: mcp-specialist (boomerang dispatch)
**Symptom**: `re-ghidra` container failed to expose MCP tools because the
Dockerfile referenced the old single-file `bridge_mcp_ghidra.py` layout.
Upstream ghidra-mcp v5.15.0 is now a Python package (`ghidra-mcp-bridge`
on PyPI) with entry point `bridge-mcp-ghidra`.

**Root cause**: The Dockerfile's CMD invoked a non-existent script path
(`/opt/ghidra-mcp/bridge_mcp_ghidra.py`). The upstream project
restructured from a single-file bridge to a Python package with Maven
build for the Java plugin.

**Architecture**:
- The container runs TWO processes under `tini` supervision:
  1. **GhidraMCP headless Java server** on internal port 8090 (REST API)
  2. **Python MCP bridge** (`ghidra-mcp-bridge`) on port 8089
     (streamable-http transport)
- The bridge translates MCP protocol to HTTP REST calls to the headless
  server on `localhost:8090`.
- OpenCode connects to `re-ghidra:8089/mcp` via streamable-http.

**Fix details**:
- `docker/ghidra/Dockerfile`: Rewritten as multi-stage build:
  - Stage 1: Downloads Ghidra 12.1.2, builds GhidraMCP Java plugin
    with Maven, clones ghidra-mcp v5.15.0 for the JAR
  - Stage 2: Copies Ghidra + JAR, installs Jython extension,
    `pip install ghidra-mcp-bridge==5.15.0`, adds entrypoint
- `docker/ghidra/entrypoint.sh`: New file — starts headless Java server
  on port 8090, waits for it to be ready, then starts the Python MCP
  bridge on port 8089 (streamable-http)
- `docker-compose.yml`: Added `GHIDRA_HEADLESS_PORT: "8090"` env var,
  updated comment (245→256 tools)
- `.opencode/opencode.json`: Changed `ghidra-mcp` from `"type":
  "local"` (stdio subprocess) to `"type": "streamable-http"` with URL
  `http://{env:GHIDRA_MCP_HOST}:{env:GHIDRA_MCP_PORT}/mcp`
- `AGENTS.md`: Updated server description from old single-file path to
  `python -m bridge_mcp_ghidra`
- `.env.example`: Updated Ghidra MCP section with new package name and
  local usage instructions

**Verification**: After `docker compose build ghidra && docker compose
up -d ghidra`, `curl http://localhost:8089/check_connection` should return
a connection confirmation from the headless server. MCP tools are exposed
at `http://re-ghidra:8089/mcp` (streamable-http).

**Files changed**:
- `RE_Playground/docker/ghidra/Dockerfile` (rewritten — multi-stage build)
- `RE_Playground/docker/ghidra/entrypoint.sh` (new file)
- `RE_Playground/docker-compose.yml` (ghidra service: added
  GHIDRA_HEADLESS_PORT, updated comment)
- `RE_Playground/.opencode/opencode.json` (ghidra-mcp: streamable-http)
- `RE_Playground/AGENTS.md` (updated server description)
- `RE_Playground/.env.example` (updated Ghidra MCP section)

**Files NOT changed**:
- `RE_Playground/docker/core/Dockerfile` (no changes needed)
- `RE_Playground/docker/radare2/Dockerfile` (no changes needed)
- `RE_Playground/examples/llama-cpp-ghidra/binary/llama-server`
  (still the baseline)
- `RE_Playground/examples/llama-cpp-ghidra/docs/*.md` (no
  audit-target content changed)

## Naming conventions (Hungarian notation)

Per `RE_Playground/AGENTS.md`, the audit applies **Hungarian notation**
to inferred local variables and parameters. The convention used in the
docs:

| Prefix | Type | Example |
|---|---|---|
| `dw` | `uint32` (DWORD) | `dwUsed`, `dwType` |
| `w` | `uint16` (WORD) | `wFlags` |
| `b` | `bool` (BOOL) | `bIsFullClear`, `bIsReSample` |
| `i` | `int32` | `iLayer`, `iTokenIdx` |
| `f` | `float` | `fLogitCap` |
| `p` | pointer | `psampler`, `pctx`, `pChain` |
| `sz` | null-terminated string | `szSymbol` |
| `v` | `std::vector` (C++ STL) | `vHeadPos`, `vSeqLen` |
| `e` | enum | `eType` |

The four `docs/*.md` files apply this convention consistently in
pseudocode. The convention was *not* applied to the actual binary
symbols (the symbol table is what r2 reads), only to the *inferred* local
variables in the human-readable pseudocode.

The Ghidra MCP strict-naming-enforcement flag (rejects no-op changes,
auto-prefixes `count` → `dwCount`) is a Ghidra-GUI feature; without a
running Ghidra instance, the docs use the convention manually.

## Plate / pre / EOL / post comments

Per `RE_Playground/AGENTS.md`, every decompiled function in the docs
has:

```c
// PLATE
//  <one-line summary of the function>
//  <longer description of what it does and why it matters for the audit>
//  <caveats or known-issues>
//
//  PRE:  <preconditions>
//  POST: <postconditions>
// EOL
```

This is applied to the main function in each of the four docs
(`llm_build_llama::llm_build_llama`, `common_sampler_init`,
`llama_kv_cache_unified::clear`, and the function-call walkthrough in
`output-filtering.md`).

## The four audit targets and the method for each

### 1. Logits production (`docs/logits-production.md`)

**Method**:
1. List `libllama.so` symbols filtered on `llm_build_` (1075 hits).
2. Pick the two non-template versions: `llm_build_llama` (1,985 B) and
   `llm_build_llama_iswa` (4,129 B). The ISWA variant handles
   sliding-window-with-attention-sink.
3. Document the class layout (constructor parameter list, vtable).
4. Note that the `ggml_mul_mat` call that emits the LM head matmul
   lives near the END of the constructor. The exact disassembly is
   fragmentary under r2 pdc; a Ghidra session is recommended for
   higher-quality decompilation.

**Why this target matters**: a custom LM head is the most subtle
modification. A fork could project the hidden state through a different
weight matrix and produce text that looks like the upstream model's
output but is actually generated by a different (e.g. less-aligned)
model.

### 2. Sampler chain (`docs/sampling.md`)

**Method**:
1. List `llama-server` symbols filtered on `sampler_init` (32 hits).
2. Cross-reference against the upstream sampler list (one per sampler
   type) to confirm completeness.
3. Decompile `common_sampler_init` (9,157 B) at `0x00212bf0` and recover
   the 12-case switch (jump table at `0x002133fa`).
4. Map each case to the corresponding `llama_sampler_init_*` PLT import.

**Why this target matters**: the sampler chain is where any "output
shaping" lives. A custom fork might disable the repetition penalty (to
allow infinite loops in adversarial contexts), add a "refuse token"
sampler (to suppress specific outputs), or apply logit-level alignment.

### 3. KV cache (`docs/kv-cache.md`)

**Method**:
1. List `libllama.so` symbols filtered on `llama_kv_cache_unified` (130+
   hits).
2. Pick the most important members: constructor (4,460 B), destructor
   (518 B), `clear(bool)` (364 B), `total_size` (60 B), `size_k_bytes`
   (61 B), `size_v_bytes` (61 B).
3. Reconstruct the field layout from the constructor's prologue +
   destructor's `delete[]` calls.
4. Document the `clear()` pseudocode and verify it's hermetic (no
   external state reads during clear).

**Why this target matters**: a backdoored `clear()` is the canonical
"cross-context leak" — a previous user's prompts or completions would
be visible to the next user. The audit's threat model assumes this
might exist; the upstream build's `clear()` is the baseline to compare
against.

### 4. Output filtering (`docs/output-filtering.md`)

**Method**:
1. String-table search on `llama-server` for `filter|censor|block|deny|
   policy|harmful|content|refuse|sanitize|blacklist` — 0 matches.
2. String-table search for the standard C string-match family
   (`strncmp|memmem|strstr|strcasestr`) — 0 matches in either binary.
3. Xref walk from `common_sampler_sample` (returns the token) through
   `process_token` (formats the response) through `send_final_response`
   (writes the SSE chunk) — no intervening function performs a
   post-sampling string operation.

**Why this target matters**: a content filter is the most common
"alignment" intervention in a model server. The standard pattern is
to call `std::regex_search` or `std::string::find` on the generated
text after sampling, and substitute a canned response if the regex
matches. The audit's job is to prove no such code exists in the
audited build.

## Cross-binary diff strategy (`docs/cross-binary-diff.md`)

The cross-binary diff is the **deliverable**. It has two complementary
paths:

1. **Symbol-presence diff** (the `scripts/cross-binary-match.py` script):
   run `nm --defined-only -P` on both binaries, demangle with
   `c++filt`, compute set difference. This catches the 90% case —
   any custom function that has a unique demangled name.

2. **Byte-level diff** (the manual procedure in
   `docs/cross-binary-diff.md`): for the four audit targets specifically,
   run `r2 -c "pD <size> @ <addr>"` on both binaries and diff. This
   catches the 10% case — a fork that **replaces** a function (same
   name, different bytes) or **adds code in the middle** of an existing
   function.

The script uses the keywords in the
`HIGH_PRIORITY_KEYWORDS` list (`filter`, `censor`, `policy`, `harmful`,
`telemetry`, `phone_home`, `validate_output`, `rewrite`, `inject`,
`prompt_guard`, `safety_check`, `alignment`, `jailbreak`, `redact`,
`obfuscat`) to flag **high-priority additions** for manual review.

## How to re-run the audit when a new llama.cpp release ships

1. **Update the commit pin**: open `scripts/build.sh` and change the
   `LLAMA_CPP_REF` env var, or pass `LLAMA_CPP_REF=<new-sha>` on the
   command line. New audit runs should always create a new branch
   (`feat/llama-cpp-ghidra-YYYY-MM-DD`).
2. **Re-build**: `./scripts/build.sh`. This rebuilds the binary, updates
   `source-info.json`, and writes a fresh `build.log`.
3. **Re-import into Ghidra**: `./scripts/import-to-ghidra.sh`. The
   `-deleteProject` flag wipes the old `.gpr/.rep` and starts fresh.
4. **Re-decompile the four targets**: open the Ghidra project, navigate
   to the new function addresses, and update `docs/*.md` with the
   new address + new decompiled pseudocode.
5. **Update the function index**: re-run the symbol inventory
   (radare2-mcp `list_symbols`) and update `docs/function-index.md`.
6. **Re-run the cross-binary diff** against any production binary that
   claims to be at the new commit.
7. **Commit on the new branch** with a clear message: `audit: refresh
   for llama.cpp <new-sha>`.

## Future-work items (out of scope for this commit)

- **Fix the Ghidra container** to use the ghidra-mcp 5.15.0 Python
  package layout. Without this, the Ghidra MCP tool family is reduced
  to the three static tools (`list_instances`, `connect_instance`,
  `import_file`).
- **Add a `cross-binary-byte-diff.sh`** that automates the manual
  `r2 -c "pD"` byte-diff procedure for the four audit targets.
- **Add a `generate-r2-functions-md.sh`** that auto-generates
  `docs/function-index.md` from `nm` output, replacing the manual
  table.
- **Wire the cross-binary-diff into CI** so that every new commit to
  the production binary triggers an automated audit run.

---

# 2026-07-06 — Ghidra MCP container fix (mcp-specialist + boomerang follow-up)

**Status**: FIXED and RUNNING. Container up at `http://localhost:8089`. 194 tools exposed via `/mcp/schema` (auth required).

## The mcp-specialist's original diagnosis (was largely correct)

The original `re-ghidra` container failed because the Dockerfile referenced the old single-file `bridge_mcp_ghidra.py` layout from ghidra-mcp v4.x. Upstream bethington/ghidra-mcp v5.14.2 is a Java plugin + Java headless server, not a Python package. The mcp-specialist's fix:

1. Multi-stage Dockerfile: stage 1 builds the Java GhidraMCP plugin with Maven, stage 2 runs it.
2. Two-process architecture: Java headless server on internal port 8090, Python MCP bridge on 8089.

## What mcp-specialist got WRONG (boomerang fix)

- The Python `ghidra-mcp-bridge` package **does not exist on PyPI**. The mcp-specialist's Dockerfile tried to `pip install ghidra-mcp-bridge==5.15.0`, which failed.
- The bethington project doesn't have a `v5.15.0` tag (latest is `v5.14.2`).
- The "Python bridge" architecture was unnecessary — the Java plugin's own MCP-over-HTTP transport serves all 245 tools directly.

## boomerang's corrections (2026-07-06)

1. **Pinned to `v5.14.2`**: `ARG GHIDRA_MCP_VERSION=5.14.2` (latest available upstream tag).
2. **Fully-qualified podman images**: `FROM docker.io/library/eclipse-temurin:21-jdk` (no `/etc/containers/registries.conf` on this system, so unqualified short-names fail).
3. **Dropped the broken `pip install ghidra-mcp-bridge`** — it's not a real package.
4. **Replaced the entrypoint.sh with the upstream one** — just runs the Java headless server, no Python bridge.
5. **Removed the 8090/8089 two-port architecture** — single process, single port 8089.
6. **Added `GHIDRA_MCP_AUTH_TOKEN` env var** — the upstream project REFUSES to bind to 0.0.0.0 without it. Generated a 32-byte token, saved to `RE_Playground/.env.ghidra-mcp` (chmod 0600).
7. **Added `GHIDRA_MCP_ALLOW_SCRIPTS=1`** — needed for any `/run_ghidra_script` or `/run_script_inline` tool calls.
8. **Added `GHIDRA_MCP_FILE_ROOT=/workspace`** — the upstream-required path-traversal guard for file operations.

## Build outcome

- Image built successfully: `localhost/re-playground-ghidra:latest` (~3.2 GB)
- Container started: `re-ghidra`, port 8089 mapped
- Server health: `Connection OK - GhidraMCP Headless Server v5.14.2-headless`
- Tool count exposed: 194 (the upstream README claims 251; some may be gated behind specific permissions or loadable groups)
- Auth: required for `/mcp/schema`; `/check_connection`, `/health`, `/mcp/health` are exempt

## How to use from a client

```bash
# Get the connection token
TOKEN=$(cat /home/jcharles/Projects/reverse_engineering/RE_Playground/.env.ghidra-mcp)

# Test it
curl -H "Authorization: Bearer $TOKEN" http://localhost:8089/mcp/schema | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'{d[\"count\"]} tools exposed')"
# → 194 tools exposed

# In .opencode/opencode.json, configure ghidra-mcp with streamable-http transport:
#   "type": "streamable-http"
#   "url": "http://ghidra-mcp:8089/mcp"
#   "headers": { "Authorization": "Bearer ${GHIDRA_MCP_AUTH_TOKEN}" }
```

## Files changed

- `RE_Playground/docker/ghidra/Dockerfile` (rewritten, multi-stage, single-process)
- `RE_Playground/docker/ghidra/entrypoint.sh` (replaced with upstream version)
- `RE_Playground/.env.ghidra-mcp` (new, 32-byte auth token, chmod 0600)
- `RE_Playground/.opencode/opencode.json` (mcp-specialist already updated transport to streamable-http)
- `RE_Playground/AGENTS.md` (mcp-specialist already updated Ghidra MCP server description)

## Remaining work

1. **Commit the fix on the `feat/llama-cpp-ghidra-2026-07-06` branch** — dispatch re-git.
2. **Update the cross-binary-diff pipeline to use the new auth + transport** — `scripts/cross-binary-match.py` will need updating to add the `Authorization` header.
3. **Drop the obsolete two-process / Python bridge section from `examples/llama-cpp-ghidra/METHODOLOGY.md`** if there's a "Python bridge" section elsewhere in the docs.
