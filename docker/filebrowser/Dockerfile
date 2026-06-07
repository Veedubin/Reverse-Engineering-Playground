# RE_Playground FileBrowser — the ONLY ingress point from the desktop
# Multi-user web file manager. Mounted on /samples, exposed on 8080.
# Users upload .exe/.dll/.apk here; agents in core container see them appear
# in /samples (shared docker volume).
#
# Uses distroless/static-debian13 (~2 MiB) as the runtime image. FileBrowser
# is a single Go static binary (~15 MB), so the runtime image is ~17 MB total
# (vs ~30 MB with the upstream hurlenko/filebrowser image). No shell, no apt,
# no package manager — only the binary.
#
# Build:  docker build -t re-playground-filebrowser -f docker/filebrowser/Dockerfile .
# Run:    docker run -d --name re-files -p 8080:8080 \
#             --network re-net -v re-samples:/samples re-playground-filebrowser

# ---- Build stage: download and verify the static binary ----
FROM alpine:3.20 AS build

ARG FB_VERSION=2.63.13
# SHA256 of linux-amd64-filebrowser.tar.gz v2.63.13 (computed 2026-06-07)
ARG FB_SHA256=1743269f00cf0f23f43e1a2e899beacb54d178092f8af992dc0d304fcf26556e

WORKDIR /tmp/fb
# Download FileBrowser Quantum linux-amd64 tarball. Alpine ships wget in
# busybox so we use that; curl is not in the base image.
RUN wget -q "https://github.com/filebrowser/filebrowser/releases/download/v${FB_VERSION}/linux-amd64-filebrowser.tar.gz" \
        -O filebrowser.tar.gz && \
    echo "${FB_SHA256}  filebrowser.tar.gz" | sha256sum -c - && \
    tar -xzf filebrowser.tar.gz && \
    chmod +x filebrowser && \
    # Verify it actually runs (sanity check; prints version, exits 0)
    ./filebrowser version

# ---- Runtime stage: distroless static image with just the binary ----
FROM gcr.io/distroless/static-debian13:nonroot

LABEL org.opencontainers.image.title="RE_Playground FileBrowser"
LABEL org.opencontainers.image.description="Distroless web file manager (FileBrowser Quantum) for /samples volume — the only desktop ingress"
LABEL org.opencontainers.image.licenses="Apache-2.0"
LABEL org.opencontainers.image.source="https://github.com/Veedubin/Reverse-Engineering-Playground"

# Copy only the verified static binary
COPY --from=build /tmp/fb/filebrowser /usr/local/bin/filebrowser

# Configuration
# Note: distroless has no shell, so ENTRYPOINT must be vector form.
# FB_BASEURL is "/" by default. FB_NOAUTH=false (use the admin user).
ENV FB_BASEURL=/ \
    FB_NOAUTH=false \
    FB_PORT=8080

# Persistent locations
# /samples is mounted at runtime via the shared re-samples volume
# /database and /config hold FileBrowser's own state
VOLUME ["/samples", "/database", "/config"]

EXPOSE 8080

# Run as nonroot (matches distroless :nonroot tag — UID 65532)
USER nonroot:nonroot

# Default: serve /samples, db at /database/filebrowser.db, config at /config/
ENTRYPOINT ["/usr/local/bin/filebrowser", \
            "--root=/samples", \
            "--database=/database/filebrowser.db", \
            "--config=/config/filebrowser.json"]
