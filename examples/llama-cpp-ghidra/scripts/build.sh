#!/usr/bin/env bash
# scripts/build.sh — reproducible build of llama-server for the RE audit
#
# Pin to a known-stable llama.cpp commit. Override with LLAMA_CPP_REF=<ref> when
# starting a new audit. The pinned commit becomes the canonical baseline; every
# divergence found in docs/* is measured against THIS exact build.
#
# Usage:
#   LLAMA_CPP_REF=b5788 ./scripts/build.sh        # explicit ref
#   ./scripts/build.sh                             # default = LLAMA_CPP_REF env or b5788
#
# Idempotent: re-running wipes /tmp/llama.cpp-build and rebuilds. The output
# binary is copied to binary/llama-server alongside its sha256.
set -euo pipefail

LLAMA_CPP_REF="${LLAMA_CPP_REF:-b5788}"
TARGET_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BUILD_DIR="${BUILD_DIR:-/tmp/llama.cpp-build}"
JOBS="$(nproc)"

log() { printf '[build] %s\n' "$*" >&2; }

log "pinned commit: ${LLAMA_CPP_REF}"
log "target dir:    ${TARGET_DIR}"
log "build dir:     ${BUILD_DIR}"
log "jobs:          ${JOBS}"

# ---------------------------------------------------------------------------
# Clone (or refresh) the pinned commit
# ---------------------------------------------------------------------------
if [[ -d "${BUILD_DIR}/.git" ]]; then
    log "refreshing existing clone at ${BUILD_DIR}"
    (cd "${BUILD_DIR}" && git fetch --tags --prune origin)
else
    log "cloning llama.cpp -> ${BUILD_DIR}"
    git clone https://github.com/ggerganov/llama.cpp.git "${BUILD_DIR}"
fi

(cd "${BUILD_DIR}" && git checkout "${LLAMA_CPP_REF}")

# Capture the *resolved* full SHA so source-info.json has a 40-char identifier
# even if a short ref like "b5788" is passed.
RESOLVED_SHA="$(cd "${BUILD_DIR}" && git rev-parse HEAD)"
RESOLVED_SHORT="$(cd "${BUILD_DIR}" && git rev-parse --short HEAD)"
RESOLVED_DATE="$(cd "${BUILD_DIR}" && git log -1 --format=%cI)"
log "resolved to:   ${RESOLVED_SHA}  (${RESOLVED_SHORT})  committed ${RESOLVED_DATE}"

# ---------------------------------------------------------------------------
# Configure + build llama-server
# ---------------------------------------------------------------------------
log "configuring (GGML_NATIVE=OFF, Release)"
cmake \
    -S "${BUILD_DIR}" \
    -B "${BUILD_DIR}/build" \
    -DGGML_NATIVE=OFF \
    -DCMAKE_BUILD_TYPE=Release \
    > "${TARGET_DIR}/binary/cmake-configure.log" 2>&1

log "building llama-server (${JOBS} jobs)"
cmake --build "${BUILD_DIR}/build" \
    --config Release \
    --target llama-server \
    -j"${JOBS}" \
    > "${TARGET_DIR}/binary/cmake-build.log" 2>&1

# ---------------------------------------------------------------------------
# Promote the binary into the audit tree + record provenance
# ---------------------------------------------------------------------------
cp "${BUILD_DIR}/build/bin/llama-server" "${TARGET_DIR}/binary/llama-server"
chmod +x "${TARGET_DIR}/binary/llama-server"

sha256sum "${TARGET_DIR}/binary/llama-server" \
    | tee "${TARGET_DIR}/binary/llama-server.sha256"

# File size for the docs
BIN_PATH="${TARGET_DIR}/binary/llama-server"
BIN_SIZE="$(stat -c%s "${BIN_PATH}")"
log "binary size:   ${BIN_SIZE} bytes"

BIN_SHA="$(sha256sum "${BIN_PATH}" | awk '{print $1}')"
cat > "${TARGET_DIR}/binary/source-info.json" <<EOF
{
  "binary": "llama-server",
  "source_repo": "https://github.com/ggerganov/llama.cpp",
  "ref_requested": "${LLAMA_CPP_REF}",
  "sha256_short": "${RESOLVED_SHORT}",
  "sha256_full": "${RESOLVED_SHA}",
  "commit_date": "${RESOLVED_DATE}",
  "build_flags": ["-DGGML_NATIVE=OFF", "-DCMAKE_BUILD_TYPE=Release"],
  "build_host": "$(uname -a)",
  "build_date": "$(date -Iseconds)",
  "build_jobs": ${JOBS},
  "binary_size_bytes": ${BIN_SIZE},
  "binary_sha256": "${BIN_SHA}"
}
EOF

log "wrote ${TARGET_DIR}/binary/source-info.json"
log "done."
