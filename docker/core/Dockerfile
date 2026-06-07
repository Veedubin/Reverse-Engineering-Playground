# RE_Playground Core — OpenCode + agents + lightweight MCP servers
# This is the brain: runs opencode web (HTTP browser UI) and serves all agents
# that talk to the other containers over the docker network.
#
# Build:  docker build -t re-playground-core -f docker/core/Dockerfile .
# Run:    docker run -d --name re-core -p 4096:4096 -p 8089:8089 \
#             --network re-net -v re-samples:/samples re-playground-core

FROM ubuntu:24.04

LABEL org.opencontainers.image.title="RE_Playground Core"
LABEL org.opencontainers.image.description="OpenCode + 15 agents + revula/ilspy-mcp/die-mcp"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.source="https://github.com/Veedubin/Reverse-Engineering-Playground"

ENV DEBIAN_FRONTEND=noninteractive
ENV OPENCODE_SERVER_PORT=4096
ENV OPENCODE_SERVER_HOSTNAME=0.0.0.0

# System packages — minimal: just what opencode + python agents need
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates curl git python3 python3-pip python3-venv \
        nodejs npm \
        binutils file xxd upx-ucl \
        yara \
        detect-it-easy \
        mono-runtime mono-utils mono-devel \
        default-jre-headless \
        wine wine64 wine-gecko wine-mono \
        tini \
    && rm -rf /var/lib/apt/lists/*

# Python tooling
RUN pip3 install --no-cache-dir --break-system-packages \
        questionary \
        revula[full] \
        pefile \
        lief \
        yara-python \
        ssdeep tlsh \
        scapy \
        capstone

# .NET SDK 9 (for ilspycmd)
RUN curl -sSL https://dot.net/v1/dotnet-install.sh | bash -s -- --channel 9.0 --install-dir /usr/share/dotnet
ENV DOTNET_ROOT=/usr/share/dotnet
ENV PATH="${PATH}:/usr/share/dotnet:/root/.dotnet/tools"
RUN /usr/share/dotnet/dotnet tool install -g ilspycmd

# Node tooling
RUN npm install -g @anthropic-ai/sdk

# OpenCode
RUN curl -fsSL https://opencode.ai/install | bash
ENV PATH="${PATH}:/root/.opencode/bin"

# Application
WORKDIR /opt/re-playground
COPY . /opt/re-playground

# Make sure agents are readable
RUN chmod -R a+rx /opt/re-playground/.opencode

# Persistent locations
RUN mkdir -p /samples /workspace /memories
ENV RE_SAMPLES_DIR=/samples
ENV RE_WORKSPACE_DIR=/workspace
# Defaults match docker-compose.yml. Override at `docker run` or compose
# with -e MEMINI_DB_URL=... / -e MEMINI_AI_DIR=... to point at a different
# PostgreSQL or a different memini-ai checkout.
ENV MEMINI_AI_DIR=/opt/re-playground/.opencode/memini-ai
ENV MEMINI_DB_URL=postgresql://memini:memini@re-memini:5432/memini
ENV MEMINI_PROJECT_ID=reverse_engineering
ENV OPENCODE_SERVER_PASSWORD=changeme

EXPOSE 4096 8089

# tini for proper signal handling
ENTRYPOINT ["/usr/bin/tini", "--"]

# Default: launch opencode web (browser UI) bound to 0.0.0.0
CMD ["sh", "-c", "opencode web --hostname 0.0.0.0 --port 4096"]
