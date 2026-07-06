#!/usr/bin/env bash
# scripts/import-to-ghidra.sh — import the audited binary into Ghidra
#
# This script runs Ghidra's analyzeHeadless tool against the binary built by
# build.sh. It creates a fresh Ghidra project, imports the binary, runs
# auto-analysis, and (optionally) applies a post-analysis script.
#
# Prerequisites:
#   - Ghidra 11+ installed (the RE_Playground ghidra container ships 12.0.4)
#   - Either run from the ghidra container (`docker compose exec ghidra ...`)
#     or from a host with Ghidra installed at $GHIDRA_HOME.
#
# Usage:
#   ./scripts/import-to-ghidra.sh [--production PRODUCTION_BIN]
#
# Outputs:
#   - Ghidra project at /ghidra-projects/llama-cpp-audit (container path)
#     or $PWD/ghidra-project/llama-cpp-audit (host path)
#   - Headless log at /tmp/ghidra-import.log
#
# The resulting .gpr + .rep files are gitignored (see RE_Playground/.gitignore).
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
TARGET_DIR="$(cd "$HERE/.." && pwd)"
BINARY="$TARGET_DIR/binary/llama-server"
LIBLLAMA="$TARGET_DIR/binary/libllama.so"

GHIDRA_HOME="${GHIDRA_HOME:-/opt/ghidra}"
ANALYZE_HEADLESS="$GHIDRA_HOME/support/analyzeHeadless"
PROJECT_DIR="${GHIDRA_PROJECT_DIR:-$TARGET_DIR/ghidra-project}"
PROJECT_NAME="llama-cpp-audit"
LOG="/tmp/ghidra-import.log"

# ---------------------------------------------------------------------------
# Sanity checks
# ---------------------------------------------------------------------------
if [[ ! -x "$ANALYZE_HEADLESS" ]]; then
    echo "error: analyzeHeadless not found at $ANALYZE_HEADLESS" >&2
    echo "       set GHIDRA_HOME or run from inside the re-ghidra container" >&2
    exit 1
fi

if [[ ! -f "$BINARY" ]]; then
    echo "error: audited binary not found at $BINARY" >&2
    echo "       run scripts/build.sh first" >&2
    exit 1
fi

if [[ ! -f "$LIBLLAMA" ]]; then
    echo "warning: libllama.so not found at $LIBLLAMA" >&2
    echo "         the audit's logits-production target lives in libllama.so" >&2
    echo "         re-run scripts/build.sh to regenerate both binaries" >&2
fi

mkdir -p "$PROJECT_DIR"

# ---------------------------------------------------------------------------
# Import both binaries into the same Ghidra project
# ---------------------------------------------------------------------------
# We use a single project with two programs:
#   /Upstream/llama-server
#   /Upstream/libllama.so
# If --production is passed, we ALSO add a second pair under /Production/.
# The cross-binary diff tools (ghidra-mcp_bulk_fuzzy_match_functions) work
# across programs in the same project.

PRODUCTION_BIN=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --production)
            PRODUCTION_BIN="$2"
            shift 2
            ;;
        *)
            echo "error: unknown argument: $1" >&2
            exit 1
            ;;
    esac
done

log() { printf '[import] %s\n' "$*" >&2; }

log "Ghidra home:   $GHIDRA_HOME"
log "analyzeHeadless: $ANALYZE_HEADLESS"
log "project dir:   $PROJECT_DIR"
log "project name:  $PROJECT_NAME"
log "binary:        $BINARY"
log "libllama.so:   $LIBLLAMA"
log "production:    ${PRODUCTION_BIN:-<none>}"

# Step 1: import llama-server
log "importing llama-server (this takes 5-15 min for auto-analysis)..."
"$ANALYZE_HEADLESS" "$PROJECT_DIR" "$PROJECT_NAME" \
    -import "$BINARY" \
    -analysisProfile "Ghidra:Default" \
    -deleteProject \
    >>"$LOG" 2>&1 || {
        log "first import failed; see $LOG"
        # try again without -deleteProject
        log "retrying without -deleteProject..."
        "$ANALYZE_HEADLESS" "$PROJECT_DIR" "$PROJECT_NAME" \
            -import "$BINARY" \
            -analysisProfile "Ghidra:Default" \
            >>"$LOG" 2>&1
    }

# Step 2: import libllama.so (if present)
if [[ -f "$LIBLLAMA" ]]; then
    log "importing libllama.so..."
    "$ANALYZE_HEADLESS" "$PROJECT_DIR" "$PROJECT_NAME" \
        -import "$LIBLLAMA" \
        >>"$LOG" 2>&1
fi

# Step 3: optionally import the production binary
if [[ -n "$PRODUCTION_BIN" && -f "$PRODUCTION_BIN" ]]; then
    PROD_LIBLLAMA="${PRODUCTION_BIN%/*}/libllama.so"
    log "importing production binary: $PRODUCTION_BIN"
    "$ANALYZE_HEADLESS" "$PROJECT_DIR" "$PROJECT_NAME" \
        -import "$PRODUCTION_BIN" \
        >>"$LOG" 2>&1
    if [[ -f "$PROD_LIBLLAMA" ]]; then
        log "importing production libllama.so: $PROD_LIBLLAMA"
        "$ANALYZE_HEADLESS" "$PROJECT_DIR" "$PROJECT_NAME" \
            -import "$PROD_LIBLLAMA" \
            >>"$LOG" 2>&1
    fi
fi

# Step 4: enumerate programs and print summary
log "done."
log "Ghidra project at: $PROJECT_DIR/$PROJECT_NAME.{gpr,rep}"
log "headless log at:   $LOG"
log ""
log "Next steps:"
log "  1. Open the project in the Ghidra GUI (or via the MCP bridge)."
log "  2. For each audit target in docs/, navigate to the documented address."
log "  3. Apply Hungarian notation to local variables (Edit > Set Variable Type)."
log "  4. Add plate / pre / EOL / post comments per AGENTS.md."
log "  5. Run ghidra-mcp_bulk_fuzzy_match_functions between /Upstream/* and"
log "     /Production/* to populate docs/cross-binary-diff.md."
