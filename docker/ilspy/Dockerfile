# RE_Playground ilspy — dedicated .NET decompiler MCP server
# v0.3.0: extracted from re-core. Provides ilspycmd as a stdio MCP server
# so .NET decompilation has its own cgroup boundary.
#
# Pattern: multi-stage build. Google's gcr.io/distroless catalog does
# NOT include a dotnet variant as of 2026-06, so we use Microsoft's
# "runtime-deps" base image which is the closest distroless equivalent
# (no SDK, no .NET runtime, just the system shared libraries needed
# for a self-contained .NET app to run).
# See: https://learn.microsoft.com/en-us/dotnet/core/docker/build-container
#
# - Stage 1 (build): mcr.microsoft.com/dotnet/sdk:9.0 — installs the
#   ilspycmd tool with its full .NET runtime. NOT shipped.
# - Stage 2 (runtime): mcr.microsoft.com/dotnet/runtime-deps:9.0-bookworm-slim —
#   ~80 MB, just glibc + ca-certs + the libgssapi/icu libs that
#   .NET apps dynamically link to. No SDK, no package manager.

# ----- Stage 1: build -----
FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build

ENV DEBIAN_FRONTEND=noninteractive

# Install ilspycmd. Pin 8.2.0.7535 because 10.x NuGet is broken on .NET 9
# SDK (missing DotnetToolSettings.xml). See docker/core/Dockerfile for
# the same fix.
RUN dotnet tool install -g ilspycmd --version 8.2.0.7535 && \
    ls -la /root/.dotnet/tools/ && \
    /root/.dotnet/tools/ilspycmd --version 2>&1 | head -3

# ----- Stage 2: distroless-like runtime -----
FROM mcr.microsoft.com/dotnet/runtime-deps:9.0-bookworm-slim

# OCI labels
LABEL org.opencontainers.image.title="RE_Playground ilspy"
LABEL org.opencontainers.image.description="ilspycmd .NET decompiler MCP server (PE/IL decompilation) on distroless .NET 9"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.source="https://github.com/Veedubin/Reverse-Engineering-Playground"

# Copy the ilspycmd binary AND its .store/ directory (the actual DLL lives
# in /root/.dotnet/tools/.store/ilspycmd/<version>/...). Without the
# store, the launcher can't find the assembly.
# Copy to /opt/ilspy (not /root/.dotnet/tools) so nonroot user can read it.
COPY --from=build --chown=app:app /root/.dotnet/tools /opt/ilspy/tools
COPY --from=build /usr/share/dotnet /usr/share/dotnet

# Set up the .NET runtime environment
ENV DOTNET_ROOT=/usr/share/dotnet
ENV PATH="${PATH}:/usr/share/dotnet:/opt/ilspy/tools"
ENV DOTNET_RUNNING_IN_CONTAINER=true
# ilspycmd 8.2.0.7535 was built for net6.0; the runtime image only ships
# .NET 9. Allow major-version roll-forward.
ENV DOTNET_ROLL_FORWARD=Major

# Persistent locations
VOLUME ["/samples", "/workspace"]
ENV RE_SAMPLES_DIR=/samples
ENV RE_WORKSPACE_DIR=/workspace

# ilspycmd runs as a stdio MCP server invoked by the OpenCode client.
# The MCP server for ilspy is "ilspy-mcp" which wraps ilspycmd — the
# client is in /opt/ilspy-mcp/ilspy_mcp/server.py in the re-playground
# source tree.
# OpenCode opencode.json will configure it as:
#   "ilspy-mcp": {
#     "type": "local",
#     "command": ["python", "-m", "ilspy_mcp.server"],
#     "enabled": true
#   }
# (ilspy-mcp itself is a Python MCP server that calls ilspycmd under
# the hood; both can be in this image if we add Python — for v0.3.0 we
# keep it pure-dotnet and let the Python wrapper live in re-core's
# python interpreter.)

# mcr.microsoft.com/dotnet/runtime-deps runs as nonroot user 65532 by
# default.
USER app

# Default entrypoint: ilspycmd. The OpenCode client or the ilspy-mcp
# Python wrapper drives the CLI.
ENTRYPOINT ["/opt/ilspy/tools/ilspycmd"]
CMD ["--help"]
