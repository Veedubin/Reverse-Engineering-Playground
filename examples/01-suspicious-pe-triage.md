# Example 01 — Triage a suspicious Windows PE

> **Audience**: a first-time user who just installed RE_Playground and wants
> to see what an actual session looks like end-to-end.
>
> **What you'll learn**: how to drop a binary into `/samples`, ask the
> orchestrator to triage it, and read the per-tool outputs it produces.
>
> **Time to complete**: ~5 minutes of reading, ~15 minutes of agent time
> for the actual analysis.

## The scenario

A friend forwards you `zadig-2.8.exe` from
[https://zadig.akeo.ie/](https://zadig.akeo.ie/). The publisher says it's a
"USB driver installer". Your spidey-sense is tingling because:

- The binary arrived as an unsolicited attachment
- The publisher's site is fine, but you want to verify the binary actually
  does what the site says
- The file is 4.7 MB — a USB driver installer doesn't need to be that big

You'll use RE_Playground to answer three questions:

1. **What is this file, structurally?** (PE headers, sections, entropy)
2. **What does it import from the OS?** (which Windows APIs it calls tells
   you what *kind* of program it is)
3. **Does it contain anything weird?** (high-entropy regions = packed or
   encrypted payloads; unsigned binaries are a smell)

## Setup

### Bare metal (Linux/macOS host)

```bash
# 1. Start the OpenCode web UI on localhost:4096
opencode web --hostname 0.0.0.0 --port 4096

# 2. Open http://localhost:4096 in your browser
# 3. Open a new session
```

### Multi-container (recommended for hostile binaries)

```bash
# 1. Start the stack
docker compose up -d

# 2. Drop the binary in via FileBrowser
xdg-open http://localhost:8080          # or just visit it
#    default creds: admin / admin   (CHANGE THESE — see docs/container.md)
#    navigate to /samples, click "Upload", pick zadig-2.8.exe

# 3. Open the OpenCode UI
xdg-open http://localhost:4096
```

> **Security note**: FileBrowser is the *only* way to drop files into the
> agent's world. The agent's containers mount `/samples` as `:ro`. Even if
> a malware sample escapes the `re-radare2` container, it cannot reach
> your home directory or browser cookies.

## The session

### Step 1 — Drop the file

Upload `zadig-2.8.exe` to `/samples` via FileBrowser (containerized) or
just `cp` it to `./samples/` (bare metal).

### Step 2 — The opening prompt

In the OpenCode chat box, paste:

```
Please triage /samples/zadig-2.8.exe. I want to know:
  1. Is this a real PE file? (use diec + pefile)
  2. What sections does it have, and what's the entropy of each?
     (use radare2 — `iS` for sections, `iE` for entropy)
  3. List its imports — what Windows APIs does it call?
     (use radare2 — `ii`)
  4. Does it have any high-entropy regions that might be packed payloads?
     (use radare2 + YARA)
  5. Is it signed? If so, by whom?

Please use the boomerang orchestrator to delegate the static analysis parts
to re-architect (binary analysis) and keep this conversation readable by
summarizing each tool's output.
```

### What happens behind the scenes

1. **The orchestrator** (`boomerang`, Kimi K2.6) reads your prompt and
   decides it has 5 distinct sub-tasks. It builds a dependency graph:
   ```
   file-type-id ─┐
                 ├─► entropy + imports (can run in parallel)
   section-list ─┘
                 └─► signature-check (independent, can run in parallel)
                       └─► final synthesis
   ```
2. **First wave (parallel)**:
   - `re-architect` (DeepSeek V4 Pro) loads the binary in Ghidra via the
     245-tool `ghidra-mcp` bridge and runs the PE header analysis
   - `re-architect` (different instance) opens the binary in radare2 via
     `radare2-mcp`, runs `iS`, `iE`, `ii`
   - `re-architect` (third instance) runs `pefile` + `YARA` + `osslsigncode`
3. **Synthesis** — the orchestrator collects all outputs, calls
   `memini-ai-dev_add_memory` to remember "zadig-2.8.exe structure" for
   future cross-binary matching, and writes a final report.

### What the report looks like

A typical triage report from this prompt:

```markdown
# Triage Report: /samples/zadig-2.8.exe

## 1. File identity
- **Format**: PE32+ executable (GUI) x86-64, for MS Windows
- **Packer**: None detected (UPX strings absent, entropy 5.8/8.0 average)
- **Compiler**: Microsoft Visual C++ 2019 v16.10 (based on .rdata strings)
- **File size**: 4,927,488 bytes (4.7 MB)
- **SHA-256**: 7b9f...e4a2  (full hash in notes)

## 2. Sections (radare2 `iS`)
| Name   | Virtual Size | Raw Size | Entropy |
|--------|--------------|----------|---------|
| .text  |   892,416    | 892,416  |   6.21  |
| .rdata | 1,048,576    | 1,048,576|   5.43  |
| .data  |   524,288    | 524,288  |   4.87  |
| .pdata |    65,536    |  65,536  |   5.91  |
| .rsrc  | 2,359,296    | 2,359,296|   7.12  |   <-- HIGH

The .rsrc section is suspiciously high-entropy for a resource section.
This is consistent with bundled icons/bitmaps, but worth a closer look
in step 4.

## 3. Imports (top 15 by name)
- `KERNEL32.dll`: CreateFileW, WriteFile, ReadFile, LoadLibraryW,
                  GetProcAddress, ExitProcess, VirtualAlloc, VirtualProtect
- `SETUPAPI.dll`: SetupDiGetClassDevsW, SetupDiEnumDeviceInfo,
                  SetupDiGetDeviceRegistryPropertyW   <-- USB device enumeration
- `WINUSB.dll`: WinUsb_Initialize, WinUsb_QueryInterface,
                WinUsb_WritePipe, WinUsb_ReadPipe  <-- direct USB comms
- `ADVAPI32.dll`: RegOpenKeyExW, RegSetValueExW, RegCloseKey
- `CRYPT32.dll`: CertOpenStore, CertVerifyCertificateChainPolicy

## 4. High-entropy regions
No packed payloads detected. The .rsrc entropy of 7.12 is normal for
embedded PNG icons (verified: strings `IHDR`, `IDAT`, `IEND` present).

YARA scan against a default ruleset: **0 hits** for known malware families.
PE-sieve equivalent analysis: no overlapping section headers, no
suspicious TLS callbacks.

## 5. Authenticode signature
**Not signed.** Raw Authenticode timestamp is missing. Publisher field
empty. This is a smell but not proof of malice — the legitimate zadig
distribution at zadig.akeo.ie also ships an unsigned build (the signed
build is distributed via a separate `.msi`).

## Conclusion
The binary matches the published behavior of Zadig 2.8: a USB driver
installer that uses libwdi to enumerate devices and install WinUSB
drivers. The lack of an Authenticode signature is consistent with the
upstream release artifacts. **No malicious indicators found.**

Trust score: 0.78 (high) — recommend proceeding with the install on a
test VM, NOT a production workstation.
```

The trust score (0.78) is fed back into `memini-ai` so the next time
you see a similar binary, the agent starts with a "this is probably
benign" prior instead of cold-starting.

### Step 3 — Drill in (optional)

If anything in the report looks off, ask follow-ups:

```
re-architect — please decompile the function that calls WinUsb_Initialize
and show me the C code. I want to verify it's just looking up a device
by VID/PID, not enumerating all USB devices.
```

The orchestrator will route that to `re-architect` with the
`ghidra-mcp` tools loaded, which uses `ghidra_decompile_function` on
the address identified by cross-referencing the `WINUSB.dll` import.

## What you should take away

- **RE_Playground is a coordinator, not a magic oracle.** The agent
  delegates to specialist tools (Ghidra, radare2, YARA, pefile) — the
  same tools you'd use manually — and synthesizes the results.
- **Multi-step analysis is the default, not a power-user feature.**
  The 5-line prompt you typed produced 5 parallel sub-tasks.
- **The report is human-readable by design.** You don't need to read
  800 lines of `iE` output to answer "is this malware?".
- **Memory persists across sessions.** The next time you analyze a
  binary from the same publisher, the agent will compare against the
  prior `zadig-2.8.exe` structure stored in `memini-ai`.
