# Sampling Audit — `llama-server` (AttackLM, pinned commit `79b33b231`)

## Purpose

Document the **sampler chain** that converts the model's raw logits into the
chosen token. This is the locus where any custom fork might:

- Drop or modify a sampler (e.g. disable repetition penalty to allow
  infinite loops; disable grammar to allow jailbreak patterns).
- Add a new sampler (e.g. an in-house "alignment" sampler).
- Reorder the chain (e.g. apply top_k before vs after temperature).

The audit enumerates every sampler the binary knows about, where the chain
is assembled, and the byte-layout of the per-sampler parameters.

## Summary

The audited build exposes the **complete upstream llama.cpp sampler chain**,
all 14 upstream samplers, no additions, no removals. The chain is built in
`common_sampler_init` (9157 bytes) and is driven by `common_sampler_sample`
(2747 bytes). The two functions are in `llama-server` itself, not in
`libllama.so` (the library only exports the per-sampler `llama_sampler_init_*`
APIs as PLT entries).

## Sampler inventory (from `libllama.so` PLT)

The following `llama_sampler_init_*` symbols are imported by `llama-server`.
The presence of a PLT import does **not** mean the sampler is enabled by
default — it means the code path is wired up. Whether it's actually added to
the chain depends on the `--samplers` CLI flag and `common_params_sampling`.

| Sampler | PLT address | Purpose |
|---|---:|---|
| `llama_sampler_init_temp` | `0x0001ee80` | Temperature scaling (Boltzmann) |
| `llama_sampler_init_temp_ext` | `0x0001f7f0` | Extended temperature with dynatemp |
| `llama_sampler_init_top_k` | `0x0001ef00` | Keep top-K logits |
| `llama_sampler_init_top_p` | `0x0001eda0` | Nucleus sampling |
| `llama_sampler_init_min_p` | `0x0001f580` | Min-P sampling |
| `llama_sampler_init_top_n_sigma` | `0x0001e650` | Top-n-sigma (entropy-aware) |
| `llama_sampler_init_xtc` | `0x0001e220` | XTC: exclude top tokens |
| `llama_sampler_init_typical_p` | `0x0001e230` | Typical-P (information-theoretic) |
| `llama_sampler_init_penalties` | `0x0001f5b0` | repeat / presence / frequency penalty |
| `llama_sampler_init_dry` | `0x0001f850` | DRY (Don't Repeat Yourself) |
| `llama_sampler_init_logit_bias` | `0x0001e460` | Per-token logit bias |
| `llama_sampler_init_mirostat` | `0x0001eed0` | Mirostat v1 |
| `llama_sampler_init_mirostat_v2` | `0x0001f700` | Mirostat v2 |
| `llama_sampler_init_dist` | `0x0001f3b0` | Final categorical distribution draw |
| `llama_sampler_init_grammar` | `0x0001f970` | GBNF grammar constraint |
| `llama_sampler_init_grammar_lazy_patterns` | `0x0001ec30` | Lazy-pattern GBNF |
| `llama_sampler_init_infill` | `0x0001e700` | Fill-in-the-middle sampling |
| `llama_sampler_chain_init` | `0x0001f6c0` | Allocate the chain |
| `llama_sampler_chain_add` | `0x0001ed60` | Append a sampler to the chain |
| `llama_sampler_chain_n` | `0x0001e4e0` | Number of samplers in the chain |
| `llama_sampler_chain_get` | `0x0001ed90` | Index into the chain |
| `llama_sampler_apply` | `0x0001e410` | Apply the chain to a token's logits |
| `llama_sampler_accept` | `0x0001f5f0` | Update samplers with a chosen token |
| `llama_sampler_reset` | `0x0001e470` | Reset sampler state |
| `llama_sampler_name` | `0x0001eb80` | Get a sampler's name |
| `llama_sampler_get_seed` | `0x0001f880` | Get the sampler's RNG seed |
| `llama_sampler_clone` | `0x0001ed30` | Clone a sampler |
| `llama_sampler_free` | `0x0001ed50` | Free a sampler |

## Sampler switch (12 cases) — recovered from `common_sampler_init` jump table

`r2` recovered a 12-entry jump table at `0x002133fa` inside
`common_sampler_init` (9157 bytes, at `0x00212bf0`). Each case in the
switch maps a `common_sampler_type` enum value to the constructor +
`llama_sampler_chain_add` sequence. The mapping (with Hungarian notation
for clarity) is:

```c
// PLATE: Sampler switch in common_sampler_init
//   pParams    (const common_params_sampling*) — caller-supplied settings
//   pChain     (llama_sampler_chain*)          — the chain being built
//   psampler   (llama_sampler*)               — the new sampler
//   dwType     (common_sampler_type)          — switch discriminant
//   dwN        (int32)                        — sampler count
// PRE:  pParams != NULL, pChain != NULL
// POST: switch fully handles upstream's 12 sampler types; default case
//       falls through to the type error site.
switch (dwType) {
    case 0:  // DRY
        psampler = llama_sampler_init_dry(
            pParams->dry_params, ...);
        llama_sampler_chain_add(pChain, psampler);
        break;
    case 1:  // grammar
        psampler = llama_sampler_init_grammar(
            pParams->grammar_str, ...);
        llama_sampler_chain_add(pChain, psampler);
        break;
    case 2:  // top_k
        psampler = llama_sampler_init_top_k(
            dwN, pParams->top_k);
        llama_sampler_chain_add(pChain, psampler);
        break;
    case 3:  // top_p
        psampler = llama_sampler_init_top_p(
            pParams->top_p, pParams->min_keep);
        llama_sampler_chain_add(pChain, psampler);
        break;
    case 4:  // min_p
        psampler = llama_sampler_init_min_p(
            pParams->min_p, pParams->min_keep);
        llama_sampler_chain_add(pChain, psampler);
        break;
    case 5:  // (loc_0x00214af0 — falls through to assert)
        // Unreachable in current upstream; the default case asserts.
        break;
    case 6:  // typical_p
        psampler = llama_sampler_init_typical(
            pParams->typical_p, pParams->min_keep);
        llama_sampler_chain_add(pChain, psampler);
        break;
    case 7:  // temp_ext
        psampler = llama_sampler_init_temp_ext(
            pParams->temp, pParams->dynatemp_range,
            pParams->dynatemp_exponent);
        llama_sampler_chain_add(pChain, psampler);
        break;
    case 8:  // xtc
        psampler = llama_sampler_init_xtc(
            pParams->xtc_probability, pParams->xtc_threshold,
            dwN);
        llama_sampler_chain_add(pChain, psampler);
        break;
    case 9:  // infill
        psampler = llama_sampler_init_infill(pParams->model);
        llama_sampler_chain_add(pChain, psampler);
        break;
    case 10: // penalties
        psampler = llama_sampler_init_penalties(
            dwN, pParams->repeat_last_n,
            pParams->repeat_penalty, pParams->frequency_penalty,
            pParams->presence_penalty);
        llama_sampler_chain_add(pChain, psampler);
        break;
    case 11: // top_n_sigma
        psampler = llama_sampler_init_top_n_sigma(
            pParams->top_n_sigma);
        llama_sampler_chain_add(pChain, psampler);
        break;
    default:
        GGML_ASSERT(false && "unknown sampler type");
        break;
}
```

## Function addresses (Hungarian notation applied)

| Address | Symbol | Size | Role |
|---|---|---:|---|
| `0x00212bf0` | `common_sampler_init(llama_model*, const common_params_sampling&)` | 9157 B | Builds the chain |
| `0x00214fc0` | `common_sampler_types_from_chars(string)` | 2060 B | `--samplers k,t,p` parser |
| `0x00215a20` | `common_sampler_types_from_names(vector<string>, bool)` | 3850 B | Long-form `--samplers top_k,top_p,...` parser |
| `0x00210980` | `common_sampler_sample(common_sampler*, llama_context*, int, bool)` | 2747 B | The hot loop |
| `0x00211440` | `common_sampler_sample_and_accept_n(...)` (5-arg) | 824 B | Speculative helper |
| `0x00211780` | `common_sampler_sample_and_accept_n(...)` (3-arg) | 532 B | Batch helper |
| `0x00210870` | `common_sampler_accept(common_sampler*, int, bool)` | 153 B | Update state for next round |
| `0x00210910` | `common_sampler_reset(common_sampler*)` | 29 B | Reset state |
| `0x002106c0` | `common_sampler_free(common_sampler*)` | 417 B | Free the chain |
| `0x00212a10` | `common_sampler_clone(common_sampler*)` | 478 B | Clone the chain |
| `0x002119a0` | `common_sampler_get_seed(common_sampler*)` | 12 B | Get the RNG seed |
| `0x002119c0` | `common_sampler_last(common_sampler*)` | 47 B | Last token (for grammar warmup) |
| `0x002119f0` | `common_sampler_print(common_sampler*)` | 2039 B | Pretty-print the chain |
| `0x002121f0` | `common_sampler_prev_str(common_sampler*, llama_context*, int)` | 1675 B | Reconstruct prompt prefix for grammar rewind |
| `0x00212880` | `common_sampler_type_to_chr(common_sampler_type)` | 25 B | Sampler name (short) |
| `0x002128a0` | `common_sampler_type_to_str(common_sampler_type)` | 363 B | Sampler name (long) |

## Cross-reference summary

`common_sampler_sample` (`0x00210980`) is called from:

- `server_context::update_slots` (`0x000d2080`, 16170 B) at offset `0xd4793`
  — the main server inference loop.
- `common_sampler_sample_and_accept_n` (5-arg variant) at offsets `0x21150e`
  and `0x211677`.
- `common_speculative_gen_draft` (`0x00218*`) at offset `0x2184c8` — the
  speculative-decoding draft loop (also in `llama-server`).

The xref to `update_slots` is the canonical call site for the
OpenAI-compatible API.

## Conclusion

The sampler chain is **complete upstream llama.cpp**, **no additions, no
removals**. The `--samplers` CLI flag drives which of the 12 types are
included (default: `top_k,top_p,min_p,temp`). The cross-binary diff
(`cross-binary-diff.md`) should compare the case statements and the PLT
imports; any deviation is a finding.
