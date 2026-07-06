# Output Filtering Audit — `llama-server` (AttackLM, pinned commit `79b33b231`)

## Purpose

This document audits the **post-sampling output pipeline** in the `llama-server`
binary (and its dynamically-linked `libllama.so`) for any non-upstream
**content filtering**, **string matching**, **token replacement**, or
**policy enforcement** code that would modify the model's raw output before it
is returned to the HTTP client.

This is the highest-priority finding target of the inversion-audit: a custom
fork might add a "safety filter" or "response sanitizer" that replaces
specific tokens or rewrites whole substrings. If any such filter is present in
the audited build, it is a **finding** — the production binary is no longer
a clean derivative of upstream llama.cpp.

## Method

1. **String-table search** for filter-related keywords (`filter`, `censor`,
   `block`, `deny`, `policy`, `harmful`, `content`, `refuse`, `sanitize`,
   `blacklist`).
2. **String-table search** for the call patterns of the standard C string-match
   family (`strncmp`, `memmem`, `strstr`, `strcasestr`).
3. **Function-level xref traversal** of the post-sampling path:
   `common_sampler_sample` (returns a single token) →
   `common_sampler_accept` →
   `completion_token_output` (in `server_task.h` / `server-context.cpp`) →
   `server_context::process_token` →
   `server_context::send_final_response`.
4. **Cross-check** against the upstream string catalogue from the
   [`llama.cpp` `common/sampling.cpp` reference](https://github.com/ggerganov/llama.cpp/blob/master/common/sampling.cpp)
   at the pinned commit.

## Findings

### Finding 0F-1: NO output filter present in the audited build

- **String-table search** for `filter|censor|block|deny|policy|harmful|content|refuse|sanitize|blacklist`
  on the `llama-server` binary returns **zero matches** in any non-mangled
  C++ symbol.
- **String-table search** for the standard C string-match family
  (`strncmp|memmem|strstr|strcasestr`) returns **zero matches** in the
  `.rodata` of `llama-server` and **zero matches** in the `.rodata` of the
  linked `libllama.so` (only the standard `strcmp` from libc is imported).
- **Post-sampling call graph** in `server_context::process_token`
  (`0x000c0080`, 3452 bytes) and `server_context::send_final_response`
  (`0x000c28e0`, 3824 bytes) shows the predicted token is:
  1. Detokenized via `llama_token_to_str` (`llama_vocab_get_text`) into a UTF-8
     `std::string`.
  2. Appended to the per-slot generated-text buffer.
  3. Streamed to the HTTP response in `send_final_response` (SSE chunk for
     `/v1/chat/completions`, JSON object for `/completion`).
- **No intervening function** between (1) and (3) performs a string match
  against any embedded policy table.

### Finding 0F-2: The standard logit-level **bias** sampler is present, not a filter

The string `--logit-bias` and the symbol `imp.llama_sampler_init_logit_bias`
(`0x0001e460`) confirm that the upstream **logit-bias sampler** is present
(see `docs/sampling.md`). This is **not a post-sampling filter** — it adjusts
*logits* before sampling, which is the standard mechanism the upstream exposes
for users to bias the model. It is invoked at request time, not at response
time, and its contents come from the API request JSON, not from the binary.

### Finding 0F-3: The standard **grammar** sampler is present, not a filter

`imp.llama_sampler_init_grammar` and `imp.llama_sampler_init_grammar_lazy_patterns`
are present (see `docs/sampling.md`). This is the upstream **GBNF grammar**
sampler. Like the logit-bias sampler, it is invoked before sampling
(constraining the *output distribution*), not after. It is also user-supplied
per request.

## Function addresses (Hungarian notation applied to local variables)

| Address | Symbol | Size | Role |
|---|---|---:|---|
| `0x00210980` | `common_sampler_sample` | 2747 B | Returns single sampled token ID; **end of sampling, no filter here** |
| `0x00210870` | `common_sampler_accept` | 153 B | Updates sampler state for the next round |
| `0x000c0080` | `server_context::process_token` | 3452 B | Per-token post-processing in the server loop |
| `0x000c28e0` | `server_context::send_final_response` | 3824 B | Sends token to HTTP client; **no filter here either** |
| `0x00211440` | `common_sampler_sample_and_accept_n` (5-arg) | 824 B | Multi-token speculative sampling helper |
| `0x00211780` | `common_sampler_sample_and_accept_n` (3-arg) | 532 B | Single-token batch helper |

### Pseudocode (Hungarian notation) for the end of `common_sampler_sample`

```c
// PLATE
//  common_sampler_sample — the final decision point for one token.
//  This is the LAST function upstream llama.cpp invokes before the
//  predicted token ID is returned to the caller (server_context in
//  this build). Any output filter MUST live in the caller's frame
//  between the return value of this function and the network write.
//
//  PRE: arg1 = psampler   (non-NULL, owns the sampler chain)
//       arg2 = pctx       (non-NULL, llama_context*)
//
//  POST: returns the chosen llama_token in eax.
//        No I/O. No string operations. The returned token ID is
//        the raw model output.
// EOL
int32_t dwPickedTokenId = common_sampler_sample(
    common_sampler *psampler,
    llama_context   *pctx,
    int32_t          iTokenIdx,
    bool             bIsReSample);

//  Hungarian key:
//    dwPickedTokenId   uint32  — chosen token ID
//    psampler          ptr     — sampler state
//    pctx              ptr     — llama context
//    iTokenIdx         int32   — which position to sample
//    bIsReSample       bool    — true if we're re-sampling
//                                (e.g. grammar retry)
//
//  The pdc decompiler produces fragmentary output for this function
//  (it's 2747 bytes, contains the full candidate-pool heap dance).
//  The behaviour to audit is: no string ops, no I/O, no policy table
//  lookup. Confirmed by xref walk from this function's return value
//  through process_token -> send_final_response — see METHODOLOGY.md.
return dwPickedTokenId;
```

## Conclusion

The audited build (`llama-server` pinned to llama.cpp `79b33b231`, sha256
`f741a96bb573b6da6d926fbe0ba6b0ac6d7eb6b0f5bffcfa54b081f79166b93d`) is **a
clean derivative of upstream llama.cpp with respect to output filtering**. No
post-sampling content filter, no string-replacement guard, no policy
blacklist was found.

If a production binary claims to be a derivative of this commit and **does**
ship a filter, the cross-binary diff (see `cross-binary-diff.md`) will show
the filter functions as **Custom additions in production** — that is the
specific finding pattern to look for.
