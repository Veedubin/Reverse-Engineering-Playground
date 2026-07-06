# Function Index — `llama-server` + `libllama.so` (AttackLM audit)

> **Auto-generated inventory** of the audit-target functions and their
> immediate call graph. Function addresses are valid for the binary built
> from llama.cpp commit `79b33b231` (sha256
> `f741a96bb573b6da6d926fbe0ba6b0ac6d7eb6b0f5bffcfa54b081f79166b93d` for
> `llama-server`, `bc149f112270fd2a50fd6bc2022d4e52206d5340ee2a4817424e80a7dda49e23`
> for `libllama.so`).

The inventory is split into two tables: **`llama-server`** (the server binary
the user runs; 5.1 MB) and **`libllama.so`** (the inference engine; 2.3 MB).
Function names are demangled; sizes are in bytes. Hungarian-notation names
are applied to inferred locals in the per-function docs.

## `llama-server` (5,158,232 bytes, 7,121 functions)

### Server loop

| Address | Symbol | Size |
|---:|---|---:|
| `0x000d2080` | `server_context::update_slots()` | 16,170 |
| `0x000ede50` | `server_context::init()` | 28,915 |
| `0x000a2260` | `server_context::load_model(const common_params&)` | 13,503 |
| `0x000f4f60` | `server_context::launch_slot_with_task(...)` | 4,234 |
| `0x000f6000` | `server_context::process_single_task(...)` | 5,263 |
| `0x000c0080` | `server_context::process_token(...)` | 3,452 |
| `0x000c28e0` | `server_context::send_final_response(...)` | 3,824 |
| `0x00099100` | `server_context::send_embedding(...)` | 3,169 |

### Sampling (in `llama-server`, not `libllama.so`)

| Address | Symbol | Size |
|---:|---|---:|
| `0x00212bf0` | `common_sampler_init(...)` | 9,157 |
| `0x00210980` | `common_sampler_sample(...)` | 2,747 |
| `0x00211440` | `common_sampler_sample_and_accept_n(...)` (5-arg) | 824 |
| `0x00211780` | `common_sampler_sample_and_accept_n(...)` (3-arg) | 532 |
| `0x00210870` | `common_sampler_accept(...)` | 153 |
| `0x00210910` | `common_sampler_reset(...)` | 29 |
| `0x002106c0` | `common_sampler_free(...)` | 417 |
| `0x00212a10` | `common_sampler_clone(...)` | 478 |
| `0x002119a0` | `common_sampler_get_seed(...)` | 12 |
| `0x002119c0` | `common_sampler_last(...)` | 47 |
| `0x002119f0` | `common_sampler_print(...)` | 2,039 |
| `0x002121f0` | `common_sampler_prev_str(...)` | 1,675 |
| `0x00212880` | `common_sampler_type_to_chr(...)` | 25 |
| `0x002128a0` | `common_sampler_type_to_str(...)` | 363 |
| `0x00215a20` | `common_sampler_types_from_names(...)` | 3,850 |
| `0x00214fc0` | `common_sampler_types_from_chars(...)` | 2,060 |

### Sampler chain PLT imports (constructors in `libllama.so`)

| Address | Symbol |
|---:|---|
| `0x0001e220` | `imp.llama_sampler_init_xtc` |
| `0x0001e230` | `imp.llama_sampler_init_typical` |
| `0x0001e410` | `imp.llama_sampler_apply` |
| `0x0001e460` | `imp.llama_sampler_init_logit_bias` |
| `0x0001e470` | `imp.llama_sampler_reset` |
| `0x0001e4e0` | `imp.llama_sampler_chain_n` |
| `0x0001e650` | `imp.llama_sampler_init_top_n_sigma` |
| `0x0001e700` | `imp.llama_sampler_init_infill` |
| `0x0001eb80` | `imp.llama_sampler_name` |
| `0x0001ec30` | `imp.llama_sampler_init_grammar_lazy_patterns` |
| `0x0001ed30` | `imp.llama_sampler_clone` |
| `0x0001ed50` | `imp.llama_sampler_free` |
| `0x0001ed60` | `imp.llama_sampler_chain_add` |
| `0x0001ed90` | `imp.llama_sampler_chain_get` |
| `0x0001eda0` | `imp.llama_sampler_init_top_p` |
| `0x0001ee80` | `imp.llama_sampler_init_temp` |
| `0x0001eed0` | `imp.llama_sampler_init_mirostat` |
| `0x0001ef00` | `imp.llama_sampler_init_top_k` |
| `0x0001ef30` | `imp.llama_sampler_chain_default_params` |
| `0x0001f3b0` | `imp.llama_sampler_init_dist` |
| `0x0001f580` | `imp.llama_sampler_init_min_p` |
| `0x0001f5b0` | `imp.llama_sampler_init_penalties` |
| `0x0001f5f0` | `imp.llama_sampler_accept` |
| `0x0001f6c0` | `imp.llama_sampler_chain_init` |
| `0x0001f700` | `imp.llama_sampler_init_mirostat_v2` |
| `0x0001f7f0` | `imp.llama_sampler_init_temp_ext` |
| `0x0001f840` | `imp.llama_perf_sampler_print` |
| `0x0001f850` | `imp.llama_sampler_init_dry` |
| `0x0001f880` | `imp.llama_sampler_get_seed` |
| `0x0001f970` | `imp.llama_sampler_init_grammar` |

### KV cache PLT imports (memory ops in `libllama.so`)

| Address | Symbol |
|---:|---|
| `0x0001e180` | `imp.llama_memory_can_shift` |
| `0x0001e1f0` | `imp.llama_encode` |
| `0x0001e760` | `imp.llama_decode` |
| `0x0001f320` | `imp.llama_memory_clear` |
| `0x0001f340` | `imp.llama_memory_seq_rm` |
| `0x0001f3a0` | `imp.llama_memory_seq_add` |
| `0x0001f3c0` | `imp.llama_memory_seq_div` |
| `0x0001f3c0` | `imp.llama_memory_seq_pos_min` |
| `0x0001f450` | `imp.llama_memory_seq_pos_max` |

## `libllama.so` (2,336,704 bytes, 11,544 functions)

### Graph constructor (logits production)

| Address | Symbol | Size |
|---:|---|---:|
| `0x0012a690` | `llm_build_llama::llm_build_llama(...)` | 1,985 |
| `0x0012ae60` | `llm_build_llama_iswa::llm_build_llama_iswa(...)` | 4,129 |
| `0x0012a560` | `llm_build_llama::~llm_build_llama()` | 298 |
| `0x001255f0` | `llm_build_llama_iswa::~llm_build_llama_iswa()` | 286 |
| `0x001e9798` | `vtable for llm_build_llama` | 32 |
| `0x001e97b8` | `vtable for llm_build_llama_iswa` | 32 |

### KV cache (unified)

| Address | Symbol | Size |
|---:|---|---:|
| `0x000cbce0` | `llama_kv_cache_unified::llama_kv_cache_unified(...)` | 4,460 |
| `0x000cce70` | `llama_kv_cache_unified::~llama_kv_cache_unified()` | 518 |
| `0x000cd080` | `llama_kv_cache_unified::~llama_kv_cache_unified()` (cold) | 523 |
| `0x000c2030` | `llama_kv_cache_unified::clear(bool)` | 364 |
| `0x000c4910` | `llama_kv_cache_unified::total_size() const` | 60 |
| `0x000c4950` | `llama_kv_cache_unified::size_k_bytes() const` | 61 |
| `0x000c4990` | `llama_kv_cache_unified::size_v_bytes() const` | 61 |
| `0x000c3f50` | `llama_kv_cache_unified::get_size() const` | 19 |
| `0x000c3f80` | `llama_kv_cache_unified::get_n_kv() const` | 90 |
| `0x000c3fe0` | `llama_kv_cache_unified::get_k(...)` | 367 |
| `0x000c4150` | `llama_kv_cache_unified::get_v(...)` | 495 |
| `0x000c21a0` | `llama_kv_cache_unified::seq_rm(int, int, int)` | 1,435 |
| `0x000c3500` | `llama_kv_cache_unified::seq_add(int, int, int, int)` | 1,172 |
| `0x000c2a60` | `llama_kv_cache_unified::seq_keep(int)` | 1,234 |
| `0x000c2f40` | `llama_kv_cache_unified::seq_cp(int, int, int, int)` | 538 |
| `0x000c3160` | `llama_kv_cache_unified::seq_div(int, int, int, int)` | 917 |
| `0x000c7d40` | `llama_kv_cache_unified::prepare(...)` | 5,390 |
| `0x000c63f0` | `llama_kv_cache_unified::find_slot(...)` | 6,474 |
| `0x000c5250` | `llama_kv_cache_unified::update(...)` | 2,502 |
| `0x000c39a0` | `llama_kv_cache_unified::apply_ubatch(...)` | 1,451 |
| `0x000c4b40` | `llama_kv_cache_unified::build_graph_shift(...)` | 773 |
| `0x000c4e50` | `llama_kv_cache_unified::build_graph_defrag(...)` | 1,018 |
| `0x000c9ee0` | `llama_kv_cache_unified::state_read_meta(...)` | 3,662 |
| `0x000cad30` | `llama_kv_cache_unified::state_read_data(...)` | 1,781 |
| `0x000c9970` | `llama_kv_cache_unified::state_write(...)` | 1,384 |
| `0x000c95c0` | `llama_kv_cache_unified::state_write_data(...)` | 942 |
| `0x000c9250` | `llama_kv_cache_unified::state_write_meta(...)` | 870 |
| `0x000cb430` | `llama_kv_cache_unified::state_read(...)` | 204 |

### KV cache (ISWA — sliding window with attention sink)

| Address | Symbol | Size |
|---:|---|---:|
| `0x000cecd0` | `llama_kv_cache_unified_iswa::llama_kv_cache_unified_iswa(...)` | 2,023 |
| `0x000d0300` | `llama_kv_cache_unified_iswa::~llama_kv_cache_unified_iswa()` | 1,190 |
| `0x000cdb40` | `llama_kv_cache_unified_iswa::clear(bool)` | 46 |
| `0x000cdb70` | `llama_kv_cache_unified_iswa::seq_rm(...)` | 64 |
| `0x000cdc30` | `llama_kv_cache_unified_iswa::seq_add(...)` | 68 |
| `0x000cf660` | `llama_kv_cache_unified_iswa_context::llama_kv_cache_unified_iswa_context(...)` | 271 |
| `0x000ce320` | `llama_kv_cache_unified_iswa_context::apply()` | 1,334 |
| `0x000ce860` | `llama_kv_cache_unified_iswa_context::next()` | 1,122 |
| `0x000cfab0` | `llama_kv_cache_unified_iswa::init_batch(...)` | 2,084 |

## Counts (for sanity checks)

- `llama-server`: 7,121 functions, 5,158,232 bytes, sha256
  `f741a96bb573b6da6d926fbe0ba6b0ac6d7eb6b0f5bffcfa54b081f79166b93d`
- `libllama.so`: 11,544 functions, 2,336,704 bytes, sha256
  `bc149f112270fd2a50fd6bc2022d4e52206d5340ee2a4817424e80a7dda49e23`
- `libggml*.so`: 698,608 + 766,656 + 55,264 = 1,520,528 bytes combined
- `libmtmd.so`: 830,376 bytes (vision/multimodal support)
- Total deployment size: 5,158,232 + 2,336,704 + 1,520,528 + 830,376 = 9,845,840 bytes
