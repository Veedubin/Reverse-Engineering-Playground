# Cross-Binary Diff — `llama-server` AttackLM audit

## Purpose

The cross-binary diff is the **central artifact** of the inversion audit. It
compares a production binary against the upstream llama.cpp build at the
pinned commit, and produces two tables:

1. **Custom additions in production** — functions present in the production
   binary that are NOT in the upstream build. These are the highest-priority
   findings: they may be backdoors, content filters, prompt-injection
   guards, or telemetry hooks.
2. **Upstream features missing from production** — upstream functions absent
   from the production binary. These may indicate a forked build that
   intentionally disabled a feature (e.g. repetition penalty, grammar).

## Strategy

The diff has two complementary paths:

### A. Function-hash diff (for `libllama.so`)

`libllama.so` is **not stripped** (binary header `stripped: false`), so the
full symbol table is available. The diff is a **set difference on
`(name, address, size)`** between the two builds:

```bash
python3 scripts/cross-binary-match.py \
    --upstream /tmp/llama.cpp-build/build/bin/libllama.so \
    --production <path-to-production-libllama.so> \
    --output docs/cross-binary-diff.md
```

### B. Byte-level diff (for `llama-server`)

`llama-server` is also not stripped. The diff uses a **function-by-function
bytewise comparison** (r2's `pdx` or `cmp`) on the four audit targets:

| Function | `llama-server` address |
|---|---|
| `common_sampler_sample` | `0x00210980` (2,747 B) |
| `common_sampler_init` | `0x00212bf0` (9,157 B) |
| `server_context::process_token` | `0x000c0080` (3,452 B) |
| `server_context::send_final_response` | `0x000c28e0` (3,824 B) |

```bash
# Function-by-function byte diff
diff <(r2 -q -c "pD 2747 @ 0x00210980" llama-server) \
     <(r2 -q -c "pD 2747 @ 0x00210980" production-llama-server)
```

### C. Symbol-presence check (cheap first pass)

Before doing byte-level diffs, a **symbol-presence check** is the cheapest
signal. Run:

```bash
# From the upstream binary
nm --defined-only /tmp/llama.cpp-build/build/bin/libllama.so | sort > /tmp/upstream.syms
nm --defined-only <production-libllama.so> | sort > /tmp/production.syms

# What's in production that's not in upstream?
comm -23 /tmp/production.syms /tmp/upstream.syms > docs/cross-binary-diff-additions.txt
# What's missing in production?
comm -13 /tmp/production.syms /tmp/upstream.syms > docs/cross-binary-diff-deletions.txt
```

**If a production binary's `libllama.so` has the exact same symbol set as
upstream (modulo address relocation), the binary is almost certainly
recompiled from upstream sources at the same commit, with no custom code.**

## Findings (this audit, 2026-07-06)

> **TODO** — no production binary was available for this initial audit.
> The script `scripts/cross-binary-match.py` is provided to run the diff
> when a production binary becomes available.

### Custom additions in production (TODO)

| Address (prod) | Symbol (demangled) | Size | Confidence | Notes |
|---:|---|---:|---|---|
| — | — | — | — | _No production binary available at audit time_ |

### Upstream features missing from production (TODO)

| Address (upstream) | Symbol | Size | Status | Notes |
|---:|---|---:|---|---|
| — | — | — | — | _No production binary available at audit time_ |

## Caveats

1. **Build flags matter.** A custom fork built with `-DGGML_CUDA=ON` instead
   of `-DGGML_NATIVE=OFF` will have different code in the GPU backends. The
   cross-binary diff must hold the build flag set constant (or filter by
   flag-controlled symbols). Always record the production build flags in
   `binary/source-info.json` before running the diff.

2. **Compiler version matters.** A build with gcc-13 vs gcc-16 will produce
   different code for the same source. Compare against an upstream build
   made with the **same compiler version** if at all possible.

3. **Address randomization.** Modern PIE binaries (`mode: DYN`, `bintype: elf`,
   `pic: true` — as our `llama-server` is) randomize the load address. Use
   **symbol names**, not raw addresses, as the diff key. The function-size
   column is a stable secondary key.

4. **Cold paths.** The `clone cold` variants of functions (e.g.
   `llama_kv_cache_unified::clear(...) [clone cold]`) may exist in one build
   and not the other depending on inlining decisions. These are NOT
   meaningful differences.

5. **C++ template instantiations.** Functions like
   `llm_graph_context::build_attn_inp_kv_iswa` exist as separate
   specializations. If a production build adds a new template parameter,
   every instantiation multiplies — leading to a large number of
   "additions" that are all the same template. Filter these by recognizing
   the template prefix and only counting the **base** function.

6. **Skipping non-determinism.** The audit is specifically about
   **behavioral differences** — what the binary does at runtime. Do not
   flag differences in:
   - `std::string::_M_dispose` and other stdlib details.
   - `method.std::ios_base_library_init__` (libstdc++ internals).
   - Any symbol with `std::` or `__cxx` prefix that isn't in the llama.cpp
     source tree.

## Re-running the audit

1. Get the production binary. If it's deployed as a Docker image, run
   `docker cp <container>:/usr/local/bin/llama-server ./production-llama-server`
   and similarly for `libllama.so`.
2. Compute its sha256: `sha256sum production-llama-server`.
3. Set the env var `PRODUCTION_BIN` and run:

   ```bash
   PRODUCTION_BIN=./production-llama-server \
   PRODUCTION_LIBLLAMA=./production-libllama.so \
   ./scripts/cross-binary-match.py
   ```

4. The script will:
   - Run `nm` on both binaries.
   - Produce `cross-binary-diff-additions.txt` and
     `cross-binary-diff-deletions.txt`.
   - For each of the four audit targets, run a byte-level diff.
   - Append results to this file.

5. **Manually review** any name in the additions list that contains
   `filter`, `censor`, `policy`, `telemetry`, `phone_home`,
   `validate_output`, `rewrite`, `inject`, `prompt_guard`, or
   `safety_check`. These are the highest-priority findings.
