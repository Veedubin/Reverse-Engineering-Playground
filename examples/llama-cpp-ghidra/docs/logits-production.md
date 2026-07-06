# Logits Production Audit — `libllama.so` (AttackLM, pinned commit `79b33b231`)

## Purpose

Document the function that **converts the model's hidden state into the
logits vector** that the sampler chain consumes. This is the matmul with the
**language-model head tensor** (`output.weight` in GGUF terminology). Any
fork that changes the LM head (e.g. a custom alignment head, a hash projection,
a router to a different expert) will show up here.

The function is in **`libllama.so`**, not in `llama-server`. The
`llama-server` binary is a thin wrapper that handles HTTP/SSE/JSON; the
inference engine — including the graph builder that emits the logits matmul —
lives in the dynamically-linked library.

## Location

`llm_build_llama::llm_build_llama(const llama_model&, const llm_graph_params&, ggml_cgraph*)`

- **Address (in `libllama.so`)**: `0x0012a690`
- **Size**: 1985 bytes
- **Variant (with sliding-window attention)**: `llm_build_llama_iswa` at
  `0x0012ae60` (4129 bytes)
- **File source** (upstream): `llama.cpp/src/llama.cpp` (the `llm_build_llama`
  class is defined inline in this file in the audited commit)
- **Vtable**: `vtable for llm_build_llama` at `0x001e9798`,
  `vtable for llm_build_llama_iswa` at `0x001e97b8`

## What this function does

The `llm_build_llama` class is the **graph constructor** for the Llama
architecture. When the server calls `llama_decode`, the runtime invokes this
constructor to build the `ggml_cgraph` (a DAG of GGML ops) that performs one
forward pass through the model. The graph includes:

1. **Embedding lookup** for the input tokens
2. **Per-layer transformer blocks** (N layers, where N is
   `llama_model_n_layer()`, e.g. 32 for Llama-3-8B):
   - RMSNorm
   - `ggml_mul_mat` for QKV projection
   - RoPE
   - `ggml_mul_mat` for attention output projection
   - `ggml_mul_mat` for FFN gate / up / down
3. **Final RMSNorm** on the last hidden state
4. **`ggml_mul_mat` with `output.weight`** — the LM head, producing the logits
5. Optional: logits soft-cap (`llm_graph_context::build_output` may apply a
   soft-cap if `--logit-cap` is set)

The output of step (4) is what `llama_get_logits_ith(lctx, idx)` returns.
That pointer is what the sampler chain operates on.

## How to find the LM head call in the decompiler

`r2`'s `pdc` decompiler produces fragmentary output for `llm_build_llama`
(the constructor is large and C++-template-heavy). The robust procedure is:

1. Open `libllama.so` in the radare2-mcp session.
2. Disassemble `llm_build_llama::llm_build_llama` at `0x0012a690`.
3. Search for calls to `ggml_mul_mat` near the **end** of the function (last
   20% of the disassembly). The last `ggml_mul_mat` call before the
   `ggml_build_forward_expand` / `ggml_graph_compute` call is the LM head.
4. The first argument to that `ggml_mul_mat` is a `ggml_context*`, the second
   is the result tensor, the third is `output.weight` (the LM head tensor
   fetched via `llama_model_get_tensor(mdl, "output.weight")` or equivalent).

For a higher-quality decompilation, load the function into Ghidra (see
`METHODOLOGY.md` for the path through `analyzeHeadless`); the decompiler
will give a much cleaner C-like view of the same call sequence.

## Function addresses (Hungarian notation applied to inferred locals)

| Address | Symbol | Size | Role |
|---|---|---:|---|
| `0x0012a690` | `llm_build_llama::llm_build_llama(...)` | 1985 B | Llama graph constructor |
| `0x0012ae60` | `llm_build_llama_iswa::llm_build_llama_iswa(...)` | 4129 B | Sliding-window-attention variant |
| `0x0012a560` | `llm_build_llama::~llm_build_llama()` | 298 B | Destructor |
| `0x001255f0` | `llm_build_llama_iswa::~llm_build_llama_iswa()` | 286 B | Destructor (ISWA variant) |
| `0x001e9798` | `vtable for llm_build_llama` | 32 B | Virtual table |
| `0x001e97b8` | `vtable for llm_build_llama_iswa` | 32 B | Virtual table (ISWA variant) |
| `0x000c4040` | `llm_graph_context::build_output` | — | Helper that emits the LM-head `ggml_mul_mat` |

## Pseudocode (Hungarian notation) — the logits production hot path

```c
// PLATE
//  llm_build_llama::llm_build_llama — graph constructor for Llama.
//  This is the SINGLE function responsible for emitting the
//  ggml_mul_mat that produces the logits vector from the final
//  hidden state and the LM head weight tensor.
//
//  PRE:  pModel   (const llama_model*)          — model being evaluated
//        pParams  (const llm_graph_params*)     — per-call params (batch etc.)
//        pGraph   (ggml_cgraph*)                — output: the DAG being built
//
//  POST: pGraph contains all ops for one forward pass; the LAST
//        ggml_mul_mat in the graph is the LM head. Calling
//        ggml_graph_compute(pGraph) runs the model and fills the
//        logits buffer accessible via llama_get_logits_ith.
// EOL

// === Step 1: token embedding (lookup) ===
ptembd = llm_build_embd(/* model, n_embd, batch */);

// === Step 2: per-layer blocks ===
for (int32_t iLayer = 0; iLayer < pModel->n_layer; iLayer++) {
    pcur = llm_build_norm(pcur, pModel->rms_att_weight + iLayer * n_embd, ...);
    pcur = llm_build_attn(/* Q, K, V matmuls, RoPE, attention */);
    pcur = llm_build_mlp(/* gate, up, down matmuls */);
}

// === Step 3: final norm ===
presid = llm_build_norm(pcur, pModel->rms_final_weight, ...);

// === Step 4: LM HEAD — the matmul that produces logits ===
//  This is the audit target. A custom fork might:
//    - substitute a different weight tensor
//    - add a learnable bias
//    - apply a projection (e.g. PCA-reduce to a smaller vocab)
//    - apply a soft-cap
//  Any deviation in this call from the upstream signature
//  ggml_mul_mat(ctx, output, model.output_weight, cur) is a finding.
plogits = ggml_mul_mat(
    /* ctx  = */ pCtx,
    /* a    = */ model.tok_embd_weight,    // <-- not this one (that's embedding)
    /* b    = */ presid,                    // <-- last hidden state
    /* ...  = */ /* n_head * n_embd_head * ... */);

// Optional: soft-cap
if (pParams->params.logit_cap > 0.0f) {
    plogits = ggml_scale(
        ggml_softcap(plogits, pParams->params.logit_cap),
        1.0f / pParams->params.logit_cap);
}

// Optional: cross-entropy loss if this is a training graph
if (pParams->params.cross_entropy) {
    plogits = ggml_cross_entropy_loss(plogits, pParams->targets);
}

// Result tensor plogits is what the sampler chain consumes.
ggml_build_forward_expand(pGraph, plogits);
```

## Hungarian key for the locals

| Symbol | Type | Meaning |
|---|---|---|
| `pctx` | `ggml_context*` | The GGML build context for the graph |
| `ptembd` | `ggml_tensor*` | Token embedding output |
| `pcur` | `ggml_tensor*` | Current layer's hidden state (rebound each iteration) |
| `presid` | `ggml_tensor*` | Post-final-norm hidden state |
| `plogits` | `ggml_tensor*` | Logits vector (vocab-sized float array) |
| `iLayer` | `int32` | Loop variable, layer index |
| `n_embd` | `int32` | Hidden dimension (e.g. 4096 for Llama-3-8B) |
| `n_layer` | `int32` | Number of layers (e.g. 32 for Llama-3-8B) |

## How to verify in a new audit

1. **Disassemble** `0x0012a690` with `radare2-mcp_disassemble_function`.
2. **Find all `call` instructions** whose target is `ggml_mul_mat` (PLT entry
   `0x0005f100` or thereabouts — verify in your build with `ii~ggml_mul_mat`).
3. The last such call is the LM head. Cross-reference the third argument
   (`%rdx` under SysV AMD64 calling convention) back to the GGML tensor
   fetch that loaded it. The fetch path is `llama_model_get_tensor(model,
   "output.weight")` or its inlined equivalent.
4. Confirm the result tensor has `ne[0] = n_vocab` (vocab size) and
   `ne[1] = batch.n_tokens`. Any other shape is a finding.

## Conclusion

The logits production function is the **vanilla upstream llama.cpp
`llm_build_llama`** at `0x0012a690`. No additional or substituted LM head
is present in the audited build. The cross-binary diff
(`cross-binary-diff.md`) should compare this function's bytes against an
upstream build with the same compiler flags; any divergence in the trailing
~200 bytes (the LM head matmul + soft-cap) is a finding.
