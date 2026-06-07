# RE_Playground revula — dedicated MCP server image
# v0.3.0: extracted from re-core so the MCP server has its own cgroup
# boundary and revula's heavy deps (z3, angr, capstone, lief, yara-python)
# don't share RAM with OpenCode.
#
# Pattern: multi-stage build that lands in gcr.io/distroless/python3-debian13:nonroot.
# - Stage 1 (build): python:3.12-slim — has gcc, g++, libfuzzy-dev, headers
#   to compile revula's C extensions. NOT shipped.
# - Stage 2 (runtime): distroless/python3-debian13:nonroot — just Python
#   runtime + ca-certs + nonroot user. No shell, no apt, no package manager.

# ----- Stage 1: build -----
# IMPORTANT: distroless python3-debian13 ships Python 3.13. To avoid
# "ABI mismatch" errors on .so files (e.g. pydantic_core), the build
# stage MUST use the same Python version. See:
# https://github.com/GoogleContainerTools/distroless/blob/main/python3/README.md
# ("when targeting python3-debian13, you should use python:3.13-slim-trixie")
FROM python:3.13-slim-trixie AS build

ARG DEBIAN_FRONTEND=noninteractive

# We need the same compile toolchain that revula's [full] extra requires:
# - gcc/g++/make: build C extensions of ssdeep, python-tlsh, binary2strings
# - libfuzzy-dev: ssdeep C library headers
# - git: clone revula (not on PyPI)
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        build-essential \
        libfuzzy-dev \
        git \
    && rm -rf /var/lib/apt/lists/*

# Install revula from source. revula is not on PyPI; must git clone.
# --ignore-installed: pip on Debian/Ubuntu is marked as "managed" by
# the distro and refuses to overwrite distro packages without it.
RUN git clone --depth 1 https://github.com/president-xd/revula.git /opt/revula && \
    cd /opt/revula && \
    pip install --no-cache-dir --break-system-packages --ignore-installed '.[full]' && \
    python -c "import revula; print('revula installed:', revula.__file__)" && \
    python -m revula.server --help 2>&1 | head -3 || true

# Collect everything we need into a /install prefix that we'll COPY into
# the distroless runtime. We move all installed packages from
# /usr/local/lib/python3.13/site-packages (where `pip install` put them
# above) into /install so the COPY in stage 2 is a single dir.
WORKDIR /install
# Copy the whole site-packages dir produced by the revula install above.
# This is the standard Google "distroless python" pattern: stage
# site-packages, copy it whole into the runtime.
RUN cp -r /usr/local/lib/python3.13/site-packages/. /install/ && \
    cp -r /usr/local/lib/python3.13/dist-packages/. /install/ 2>/dev/null || true && \
    # Verify revula loads from /install
    PYTHONPATH=/install python -c "import revula; print('OK:', revula.__file__)"

# ----- Stage 2: distroless runtime -----
FROM gcr.io/distroless/python3-debian13:nonroot

# OCI labels
LABEL org.opencontainers.image.title="RE_Playground revula"
LABEL org.opencontainers.image.description="revula MCP server (PE/ELF/Mach-O, YARA, Capa, .NET IL, Frida, GDB) on distroless"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.source="https://github.com/Veedubin/Reverse-Engineering-Playground"

# Copy the /install prefix (which is /usr/local/lib/python3.12/site-packages
# contents) into the distroless image. The distroless python3 base adds
# /usr/lib/python3/dist-packages to sys.path automatically.
COPY --from=build /install /usr/lib/python3/dist-packages

# revula is launched as a stdio MCP server by the OpenCode client.
# The MCP server entrypoint is revula.server:main.
# OpenCode opencode.json will configure it as:
#   "revula": {
#     "type": "local",
#     "command": ["python", "-m", "revula.server"],
#     "enabled": true
#   }

# distroless images run as uid 65532 (nonroot) by default.
USER nonroot:nonroot

# Default entrypoint: the revula MCP server. The OpenCode client drives
# the JSON-RPC conversation over stdio.
ENTRYPOINT ["python", "-m", "revula.server"]
