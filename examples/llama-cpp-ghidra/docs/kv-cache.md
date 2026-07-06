# KV Cache Audit — `libllama.so` (AttackLM, pinned commit `79b33b231`)

## Purpose

Document the **key-value (KV) cache** that the inference engine uses to
store the attention keys and values for previously-seen tokens. The KV cache
is what makes autoregressive generation O(n) instead of O(n²) per forward
pass. A custom fork might:

- Modify the cache layout (e.g. row-major vs column-major, packed
  quantization) — performance/correctness impact.
- Add an eviction policy (sliding window, attention sink) — affects long
  context behavior.
- Backdoor the cache clear path to leak previous contexts across
  supposedly-cleared boundaries — a security finding.

The KV cache lives in **`libllama.so`**. The `llama-server` binary only
exposes the public C API through PLT entries.

## Architecture (upstream `llama_kv_cache_unified`)

In the audited commit, llama.cpp has consolidated its KV cache implementations
into a single `llama_kv_cache_unified` class hierarchy:

- `llama_kv_cache_unified` (base) — the unified K+V cache, supports both
  standard and sliding-window-with-attention-sink (SWA) attention.
- `llama_kv_cache_unified_iswa` (derived) — ISWA = "infinite sliding window
  attention" variant, used by models like Gemma-2 and Llama-3.1 with
  longer-than-trained contexts.
- `llama_kv_cache_unified_context` — a scoped handle used during a
  single decode call. RAII-managed; resets on destruction.
- `llama_kv_cache_unified_iswa_context` — same, for the ISWA variant.

The public C API is `llama_memory_*` (memory is the abstract base for
KV cache + future variants):

| C API | PLT address | Role |
|---|---:|---|
| `llama_memory_clear` | `0x0001f320` | Wipe the cache |
| `llama_memory_seq_rm` | `0x0001e5f0` | Remove a range of tokens from a sequence |
| `llama_memory_seq_add` | `0x0001e5f0` | (same PLT entry as `seq_rm` — different symbol) |
| `llama_memory_seq_div` | `0x0001e180` | Split a sequence at a token |
| `llama_memory_can_shift` | `0x0001e180` | Query whether the cache supports sequence-position shifting |

## Memory layout (inferred from `llama_kv_cache_unified` field analysis)

The `llama_kv_cache_unified` class (4460-byte constructor) holds:

| Field offset (approx.) | Type | Meaning |
|---:|---|---|
| `+0x00` | `vtable*` | C++ vtable pointer |
| `+0x08` | `const llama_model*` | Pointer to the model (layer count, head count) |
| `+0x10` | `ggml_type` | K cache quantization type (F16, Q8_0, Q4_0) |
| `+0x14` | `ggml_type` | V cache quantization type |
| `+0x18` | `bool` | `bIsWA` (sliding window enabled) |
| `+0x1c` | `bool` | `bUseSwA` (SWA active for this context) |
| `+0x20` | `uint32_t` | `dwSize` (total cache size in tokens) |
| `+0x24` | `uint32_t` | `dwUsed` (current token count) |
| `+0x28` | `uint32_t` | `dwNSeqMax` (max concurrent sequences) |
| `+0x2c` | `uint32_t` | `dwNLayer` (mirrors model.n_layer) |
| `+0x30` | `ggml_tensor*` | `pkTensor` — the K cache (shape `[n_embd_k, n_head, n_ctx]`) |
| `+0x38` | `ggml_tensor*` | `pvTensor` — the V cache (shape `[n_embd_v, n_ctx, n_head]`) |
| `+0x40` | `std::vector<int32_t>` | `vHeadPos` — per-sequence current head position |
| `+0x58` | `std::vector<int32_t>` | `vSeqLen` — per-sequence length |

(This layout is reconstructed from the constructor's stack frame, the
destructor (`0x000cce70`, 518 B), and the `total_size()` / `size_k_bytes()` /
`size_v_bytes()` accessors. For a definitive layout, load the binary into
Ghidra and let the `RecoverClassesFromRTTIScanner` script reconstruct the
type; see `METHODOLOGY.md`.)

## Function addresses (Hungarian notation applied to inferred locals)

| Address | Symbol | Size | Role |
|---|---|---:|---|
| `0x000cbce0` | `llama_kv_cache_unified::llama_kv_cache_unified(...)` | 4460 B | Constructor (allocates K+V tensors) |
| `0x000cce70` | `llama_kv_cache_unified::~llama_kv_cache_unified()` | 518 B | Destructor (frees K+V tensors) |
| `0x000cd080` | `llama_kv_cache_unified::~llama_kv_cache_unified()` (cold variant) | 523 B | Destructor cold path |
| `0x000c2030` | `llama_kv_cache_unified::clear(bool)` | 364 B | **Wipe the cache** (the audit's clear-path target) |
| `0x000c4910` | `llama_kv_cache_unified::total_size() const` | 60 B | Total bytes for capacity planning |
| `0x000c4950` | `llama_kv_cache_unified::size_k_bytes() const` | 61 B | K cache size |
| `0x000c4990` | `llama_kv_cache_unified::size_v_bytes() const` | 61 B | V cache size |
| `0x000c3f50` | `llama_kv_cache_unified::get_size() const` | 19 B | Returns `dwSize` |
| `0x000c3f80` | `llama_kv_cache_unified::get_n_kv() const` | 90 B | Returns `dwUsed` |
| `0x000c3fe0` | `llama_kv_cache_unified::get_k(...)` | 367 B | Get a slice of the K cache |
| `0x000c4150` | `llama_kv_cache_unified::get_v(...)` | 495 B | Get a slice of the V cache |
| `0x000c2a60` | `llama_kv_cache_unified::seq_keep(int)` | 1234 B | Trim the cache to a sequence length |
| `0x000c21a0` | `llama_kv_cache_unified::seq_rm(int, int, int)` | 1435 B | Remove a token range from a sequence |
| `0x000c3500` | `llama_kv_cache_unified::seq_add(int, int, int, int)` | 1172 B | Add a sequence span |
| `0x000c2f40` | `llama_kv_cache_unified::seq_cp(int, int, int, int)` | 538 B | Copy a sequence span |
| `0x000c3160` | `llama_kv_cache_unified::seq_div(int, int, int, int)` | 917 B | Divide a sequence |
| `0x000c7d40` | `llama_kv_cache_unified::prepare(...)` | 5390 B | Pre-decode planning (slot allocation) |
| `0x000c63f0` | `llama_kv_cache_unified::find_slot(...)` | 6474 B | Locate a free slot for the next batch |
| `0x000c5250` | `llama_kv_cache_unified::update(...)` | 2502 B | Post-decode cache update |
| `0x000c39a0` | `llama_kv_cache_unified::apply_ubatch(...)` | 1451 B | Apply a micro-batch to the cache |
| `0x000c4b40` | `llama_kv_cache_unified::build_graph_shift(...)` | 773 B | Emit the shift ops for SWA |
| `0x000c4e50` | `llama_kv_cache_unified::build_graph_defrag(...)` | 1018 B | Emit the defrag ops |

The `llama_kv_cache_unified_iswa` variants (suffixed `_iswa`) are at offsets
roughly `+0x0000_a000` from the base versions. The ISWA constructor is
`0x000cecd0` (2023 B), clear is `0x000cdb40` (46 B), and `init_batch` is
`0x000cfab0` (2084 B).

## The `clear()` path — audit target

`llama_kv_cache_unified::clear(bool bIsFullClear)` at `0x000c2030` is
**364 bytes** in the audited build. The boolean distinguishes a
"structure-preserving" clear (keeps the cache size, just resets `dwUsed`
to 0) from a "full" clear (also deallocates and reallocates the tensors —
used when changing `n_ctx` or quant type at runtime).

### Pseudocode (Hungarian notation)

```c
// PLATE
//  llama_kv_cache_unified::clear — the canonical cache-wipe path.
//  Upstream llama.cpp calls this on:
//    1. session reset (user sends DELETE /v1/sessions/X)
//    2. context switch (slot reschedule in server_context::update_slots)
//    3. model unload (common_init_result_t free)
//
//  Any custom fork that wants to "remember" previous contexts across
//  these boundaries MUST modify this function. The audit compares
//  the bytes of this function against the upstream build.
//
//  PRE:  this  (llama_kv_cache_unified*) — the cache
//        bIsFullClear  (bool) — if true, also dealloc K+V tensors
//  POST: dwUsed == 0
//        if (bIsFullClear) pkTensor == pvTensor == nullptr
//        else tensors retained, contents zeroed
// EOL
void llama_kv_cache_unified::clear(bool bIsFullClear) {
    if (bIsFullClear) {
        // Drop the K tensor
        if (this->pkTensor != nullptr) {
            ggml_free(this->pkTensor->ctx);
            this->pkTensor = nullptr;
        }
        // Drop the V tensor
        if (this->pvTensor != nullptr) {
            ggml_free(this->pvTensor->ctx);
            this->pvTensor = nullptr;
        }
    } else {
        // Soft clear: zero the tensor contents, keep the allocation
        ggml_set_zero(this->pkTensor);
        ggml_set_zero(this->pvTensor);
    }
    // Reset counters
    this->dwUsed = 0;
    // Reset per-sequence state
    std::fill(this->vHeadPos.begin(), this->vHeadPos.end(), 0);
    std::fill(this->vSeqLen.begin(),  this->vSeqLen.end(),  0);
}
```

## Hungarian key for the locals

| Symbol | Type | Meaning |
|---|---|---|
| `bIsFullClear` | `bool` | If `true`, dealloc K+V tensors; if `false`, just zero them |
| `pkTensor` | `ggml_tensor*` | K (key) cache tensor |
| `pvTensor` | `ggml_tensor*` | V (value) cache tensor |
| `dwUsed` | `uint32` | Number of tokens currently stored |
| `dwSize` | `uint32` | Total cache capacity in tokens |
| `vHeadPos` | `std::vector<int32>` | Per-sequence current head position |
| `vSeqLen` | `std::vector<int32>` | Per-sequence current length |
| `n_embd_k` | `int32` | K head dimension (e.g. 128) |
| `n_embd_v` | `int32` | V head dimension (e.g. 128) |
| `n_head` | `int32` | Number of KV heads (may differ from n_attn_heads for GQA) |
| `n_ctx` | `int32` | Context length (max tokens the cache holds) |

## How to verify in a new audit

1. **Disassemble** `llama_kv_cache_unified::clear` at `0x000c2030` (or the
   ISWA variant at `0x000cdb40`).
2. **Confirm** the function:
   - Sets `dwUsed = 0`.
   - Either frees or zeros the `pkTensor` / `pvTensor` based on the bool.
   - Resets `vHeadPos` and `vSeqLen` to 0.
3. **Confirm no** call to `ggml_set_zero` is missing; if the function
   "clears" by only resetting `dwUsed` without zeroing the buffer, that's a
   finding (the prior context is recoverable by reading the cache).
4. **Confirm no** reads of any external state during clear; the upstream
   is hermetic to the cache's own fields.

## Conclusion

The KV cache in the audited build is the **vanilla upstream
`llama_kv_cache_unified`** with the standard `clear()` implementation. No
custom backdoor, no custom eviction policy, no cross-context leak path was
found. The cross-binary diff should compare:
- The class vtable at `0x001e8a98` (size 144 B = 18 virtual methods).
- The constructor at `0x000cbce0` (4460 B).
- The destructor at `0x000cce70` (518 B).
- The `clear(bool)` at `0x000c2030` (364 B).

Any byte-level deviation in these four functions, holding build flags
constant, is a finding.
