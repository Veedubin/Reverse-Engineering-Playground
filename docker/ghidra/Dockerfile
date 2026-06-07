# RE_Playground Ghidra — NSA SRE framework + ghidra-mcp server
# Isolated because Ghidra is 400+ MB of JVM + 245 MCP tools and benefits from
# a dedicated JVM heap. Talks to core over the docker network on port 8089.
#
# Build:  docker build -t re-playground-ghidra -f docker/ghidra/Dockerfile .
# Run:    docker run -d --name re-ghidra -p 8089:8089 \
#             --network re-net -v re-samples:/samples re-playground-ghidra

FROM ubuntu:24.04

LABEL org.opencontainers.image.title="RE_Playground Ghidra"
LABEL org.opencontainers.image.description="Ghidra 11+ SRE framework + 245-tool MCP server"
LABEL org.opencontainers.image.licenses="Apache-2.0"

ENV DEBIAN_FRONTEND=noninteractive
ENV GHIDRA_INSTALL_DIR=/opt/ghidra
ENV GHIDRA_HOME=/opt/ghidra
ENV GHIDRA_MCP_PORT=8089
ENV GHIDRA_MCP_BRIDGE=/opt/ghidra-mcp/bridge_mcp_ghidra.py

# JDK 21 (Ghidra 11+ requires JDK 21)
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates curl wget unzip git python3 python3-pip \
        openjdk-21-jdk-headless \
        tini \
    && rm -rf /var/lib/apt/lists/*

# Download Ghidra (the URL is the official NSA release; pin a version for reproducibility)
ARG GHIDRA_VERSION=11.3.2
ARG GHIDRA_DATE=20250422
RUN mkdir -p /opt && \
    cd /tmp && \
    curl -fsSL "https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_${GHIDRA_VERSION}_build/${GHIDRA_DATE}_ghidra_${GHIDRA_VERSION}_PUBLIC.zip" \
        -o ghidra.zip && \
    unzip -q ghidra.zip -d /opt && \
    rm ghidra.zip && \
    ls /opt | grep -i ghidra | xargs -I{} mv /opt/{} /opt/ghidra && \
    chmod +x /opt/ghidra/ghidraRun /opt/ghidra/support/analyzeHeadless

# Ghidra MCP bridge (https://github.com/bethington/ghidra-mcp or whatever fork)
RUN mkdir -p /opt/ghidra-mcp && \
    cd /opt/ghidra-mcp && \
    curl -fsSL https://github.com/bethington/ghidra-mcp/archive/refs/heads/main.tar.gz | tar xz --strip-components=1 && \
    pip3 install --no-cache-dir --break-system-packages -r requirements.txt 2>/dev/null || true

# Persistent locations
RUN mkdir -p /samples /workspace /ghidra-projects
ENV RE_SAMPLES_DIR=/samples
ENV RE_WORKSPACE_DIR=/workspace
ENV GHIDRA_PROJECTS=/ghidra-projects

EXPOSE 8089

# Healthcheck — confirm Ghidra JVM started
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -fs http://localhost:${GHIDRA_MCP_PORT}/health || exit 1

ENTRYPOINT ["/usr/bin/tini", "--"]

# Launch the ghidra-mcp bridge; it auto-spawns analyzeHeadless
CMD ["python3", "/opt/ghidra-mcp/bridge_mcp_ghidra.py", "--host", "0.0.0.0", "--port", "8089"]
