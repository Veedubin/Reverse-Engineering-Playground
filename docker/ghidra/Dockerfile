# RE_Playground Ghidra — NSA SRE framework + 256-tool MCP server
# Multi-stage build: (1) build the GhidraMCP Java plugin with Maven,
# (2) runtime image with Ghidra headless MCP server on port 8089.
#
# Architecture (single-process, no Python bridge):
#   MCP clients ──streamable-http──► Java GhidraMCP headless server (port 8089)
#
# The 245 MCP tools are served by the Java plugin itself (com.xebyte.headless.
# GhidraMCPHeadlessServer). There is no separate Python bridge — the upstream
# bethington/ghidra-mcp v5.14.2 project uses a single Java process.
#
# Build:  podman-compose -f docker-compose.yml build ghidra
# Run:    podman-compose -f docker-compose.yml up -d ghidra

# =============================================================================
# Stage 1: Builder — download Ghidra, build GhidraMCP plugin with Maven
# =============================================================================
FROM docker.io/library/eclipse-temurin:21-jdk AS builder

ARG GHIDRA_VERSION=12.1.2
ARG GHIDRA_DATE=20260605

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        wget unzip maven git \
    && rm -rf /var/lib/apt/lists/*

# Download Ghidra
WORKDIR /opt
RUN wget -q --no-check-certificate \
    "https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_${GHIDRA_VERSION}_build/ghidra_${GHIDRA_VERSION}_PUBLIC_${GHIDRA_DATE}.zip" \
    -O ghidra.zip || \
    wget -q --no-check-certificate \
    "https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_${GHIDRA_VERSION}_build/ghidra_${GHIDRA_VERSION}_PUBLIC.zip" \
    -O ghidra.zip

RUN unzip -q ghidra.zip && rm ghidra.zip && mv ghidra_* ghidra

ENV GHIDRA_HOME=/opt/ghidra

# Install Ghidra JARs to Maven local repository (required for plugin build)
RUN mvn -q install:install-file -Dfile=/opt/ghidra/Ghidra/Framework/Generic/lib/Generic.jar \
        -DgroupId=ghidra -DartifactId=Generic -Dversion=${GHIDRA_VERSION} -Dpackaging=jar && \
    mvn -q install:install-file -Dfile=/opt/ghidra/Ghidra/Framework/SoftwareModeling/lib/SoftwareModeling.jar \
        -DgroupId=ghidra -DartifactId=SoftwareModeling -Dversion=${GHIDRA_VERSION} -Dpackaging=jar && \
    mvn -q install:install-file -Dfile=/opt/ghidra/Ghidra/Framework/Project/lib/Project.jar \
        -DgroupId=ghidra -DartifactId=Project -Dversion=${GHIDRA_VERSION} -Dpackaging=jar && \
    mvn -q install:install-file -Dfile=/opt/ghidra/Ghidra/Framework/Docking/lib/Docking.jar \
        -DgroupId=ghidra -DartifactId=Docking -Dversion=${GHIDRA_VERSION} -Dpackaging=jar && \
    mvn -q install:install-file -Dfile=/opt/ghidra/Ghidra/Framework/Utility/lib/Utility.jar \
        -DgroupId=ghidra -DartifactId=Utility -Dversion=${GHIDRA_VERSION} -Dpackaging=jar && \
    mvn -q install:install-file -Dfile=/opt/ghidra/Ghidra/Framework/Gui/lib/Gui.jar \
        -DgroupId=ghidra -DartifactId=Gui -Dversion=${GHIDRA_VERSION} -Dpackaging=jar && \
    mvn -q install:install-file -Dfile=/opt/ghidra/Ghidra/Framework/FileSystem/lib/FileSystem.jar \
        -DgroupId=ghidra -DartifactId=FileSystem -Dversion=${GHIDRA_VERSION} -Dpackaging=jar && \
    mvn -q install:install-file -Dfile=/opt/ghidra/Ghidra/Framework/Help/lib/Help.jar \
        -DgroupId=ghidra -DartifactId=Help -Dversion=${GHIDRA_VERSION} -Dpackaging=jar && \
    mvn -q install:install-file -Dfile=/opt/ghidra/Ghidra/Features/Base/lib/Base.jar \
        -DgroupId=ghidra -DartifactId=Base -Dversion=${GHIDRA_VERSION} -Dpackaging=jar && \
    mvn -q install:install-file -Dfile=/opt/ghidra/Ghidra/Features/Decompiler/lib/Decompiler.jar \
        -DgroupId=ghidra -DartifactId=Decompiler -Dversion=${GHIDRA_VERSION} -Dpackaging=jar && \
    mvn -q install:install-file -Dfile=/opt/ghidra/Ghidra/Framework/DB/lib/DB.jar \
        -DgroupId=ghidra -DartifactId=DB -Dversion=${GHIDRA_VERSION} -Dpackaging=jar && \
    mvn -q install:install-file -Dfile=/opt/ghidra/Ghidra/Framework/Emulation/lib/Emulation.jar \
        -DgroupId=ghidra -DartifactId=Emulation -Dversion=${GHIDRA_VERSION} -Dpackaging=jar && \
    mvn -q install:install-file -Dfile=/opt/ghidra/Ghidra/Debug/Debugger-api/lib/Debugger-api.jar \
        -DgroupId=ghidra -DartifactId=Debugger-api -Dversion=${GHIDRA_VERSION} -Dpackaging=jar && \
    mvn -q install:install-file -Dfile=/opt/ghidra/Ghidra/Debug/Framework-TraceModeling/lib/Framework-TraceModeling.jar \
        -DgroupId=ghidra -DartifactId=Framework-TraceModeling -Dversion=${GHIDRA_VERSION} -Dpackaging=jar && \
    mvn -q install:install-file -Dfile=/opt/ghidra/Ghidra/Debug/Debugger-rmi-trace/lib/Debugger-rmi-trace.jar \
        -DgroupId=ghidra -DartifactId=Debugger-rmi-trace -Dversion=${GHIDRA_VERSION} -Dpackaging=jar

# Clone and build GhidraMCP plugin
ARG GHIDRA_MCP_VERSION=5.14.2
WORKDIR /build
RUN git clone --depth 1 --branch v${GHIDRA_MCP_VERSION} \
    https://github.com/bethington/ghidra-mcp.git /build/ghidra-mcp && \
    cd /build/ghidra-mcp && \
    mvn clean package -P headless -DskipTests -q

# =============================================================================
# Stage 2: Runtime — Ghidra + GhidraMCP headless server + Python MCP bridge
# =============================================================================
# NOTE: must be a JDK (not JRE) — Ghidra's OSGi loader uses
# javax.tools.ToolProvider.getSystemJavaCompiler() which returns null on JRE.
FROM docker.io/library/eclipse-temurin:21-jdk

LABEL org.opencontainers.image.title="RE_Playground Ghidra"
LABEL org.opencontainers.image.description="Ghidra SRE + 256-tool MCP bridge (headless server + streamable-http)"
LABEL org.opencontainers.image.licenses="Apache-2.0"

ENV DEBIAN_FRONTEND=noninteractive
ENV GHIDRA_HOME=/opt/ghidra
ENV GHIDRA_MCP_PORT=8089
ENV GHIDRA_MCP_BIND_ADDRESS=0.0.0.0
ENV JAVA_OPTS="-Xmx4g -XX:+UseG1GC"

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates curl unzip python3 python3-pip tini \
    && rm -rf /var/lib/apt/lists/*

# Copy Ghidra from builder
COPY --from=builder /opt/ghidra /opt/ghidra

# Install the Jython extension (required by Ghidra 12.1.2+)
RUN set -eux; \
    EXT_DIR="/opt/ghidra/Extensions/Ghidra"; \
    JYTHON_ZIP="$(ls "$EXT_DIR"/*_Jython.zip 2>/dev/null | head -n1)"; \
    if [ -n "$JYTHON_ZIP" ]; then \
        mkdir -p /opt/ghidra/Ghidra/Extensions && \
        unzip -q "$JYTHON_ZIP" -d /opt/ghidra/Ghidra/Extensions/ && \
        echo "Installed Jython extension: $(basename "$JYTHON_ZIP")"; \
    fi

# Copy the built headless JAR
COPY --from=builder /build/ghidra-mcp/target/GhidraMCP-*.jar /app/GhidraMCP.jar

# NOTE: There is no `ghidra-mcp-bridge` PyPI package. The 245 MCP tools are
# served by the GhidraMCP Java plugin itself when run headless on port 8089.
# The bethington/ghidra-mcp repo's `bridge_mcp_ghidra.py` is a separate
# optional Python script, not a PyPI package. If you need HTTP transport,
# run the upstream entrypoint.sh from the ghidra-mcp repo directly.

# Persistent locations
RUN mkdir -p /samples /workspace /ghidra-projects /data /projects
ENV RE_SAMPLES_DIR=/samples
ENV RE_WORKSPACE_DIR=/workspace
ENV GHIDRA_PROJECTS=/ghidra-projects

EXPOSE 8089

# Health check — confirm the GhidraMCP headless server is serving
HEALTHCHECK --interval=30s --timeout=10s --start-period=90s --retries=3 \
    CMD curl -fs http://localhost:${GHIDRA_MCP_PORT}/check_connection || exit 1

# Copy the entrypoint script
COPY docker/ghidra/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Single-process: the Java GhidraMCP headless server is the foreground process.
# tini handles PID-1 signal forwarding.
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/app/entrypoint.sh"]