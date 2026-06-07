# RE_Playground radare2 — r2 + rizin + r2mcp + Wine for Win32 debugging
# Isolated because r2 + r2mcp + Wine are the only tools that need privileged
# ptrace. Runs the r2mcp HTTP server on port 9090.
#
# Build:  docker build -t re-playground-radare2 -f docker/radare2/Dockerfile .
# Run:    docker run -d --name re-radare2 -p 9090:9090 \
#             --network re-net --cap-add=SYS_PTRACE -v re-samples:/samples re-playground-radare2

FROM ubuntu:24.04

LABEL org.opencontainers.image.title="RE_Playground radare2"
LABEL org.opencontainers.image.description="radare2 + rizin + r2mcp + Wine for Win32 PE debugging"
LABEL org.opencontainers.image.licenses="LGPL-3.0"

ENV DEBIAN_FRONTEND=noninteractive
ENV R2MCP_PORT=9090

# System packages. NB: `wine-gecko` and `wine-mono` are NOT in Ubuntu 24.04
# (noble) — they were removed in jammy. Wine now ships without them; the
# Mono runtime is provided by the `mono-runtime` package we install in core.
# `rizin` is also not in noble (only in Ubuntu 24.10+ and as snap); we get
# rizin functionality from r2 itself plus `pip install rizin` if needed.
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates curl git python3 python3-pip \
        radare2 \
        binutils file xxd \
        wine wine64 \
        build-essential pkg-config \
        tini \
    && rm -rf /var/lib/apt/lists/*

# Install r2mcp via r2pm (radare2's package manager)
RUN r2pm -U && \
    r2pm -ci r2mcp || echo "r2mcp install via r2pm failed, falling back to pip" && \
    (pip3 install --no-cache-dir --break-system-packages r2mcp 2>/dev/null || true)

# Python helpers
RUN pip3 install --no-cache-dir --break-system-packages r2pipe

# Persistent locations
RUN mkdir -p /samples /workspace
ENV RE_SAMPLES_DIR=/samples
ENV RE_WORKSPACE_DIR=/workspace

EXPOSE 9090

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -fs http://localhost:${R2MCP_PORT}/health || exit 1

ENTRYPOINT ["/usr/bin/tini", "--"]

# r2mcp runs as stdio by default; we wrap it with a small Python shim that
# also serves the HTTP health endpoint. See docker/radare2/entrypoint.sh.
COPY docker/radare2/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
CMD ["/entrypoint.sh"]
