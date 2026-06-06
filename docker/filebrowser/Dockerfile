# RE_Playground FileBrowser — the ONLY ingress point from the desktop
# Multi-user web file manager. Mounted on /samples, exposed on 8080.
# Users upload .exe/.dll/.apk here; agents in core container see them appear
# in /samples (shared docker volume).
#
# Build:  docker build -t re-playground-filebrowser -f docker/filebrowser/Dockerfile .
# Run:    docker run -d --name re-files -p 8080:8080 \
#             --network re-net -v re-samples:/samples re-playground-filebrowser

FROM hurlenko/filebrowser:latest

LABEL org.opencontainers.image.title="RE_Playground FileBrowser"
LABEL org.opencontainers.image.description="Web UI for /samples volume — the only desktop ingress"
LABEL org.opencontainers.image.licenses="Apache-2.0"

# FileBrowser Quantum image already has the right defaults; we just need
# to point it at /samples and create an admin user via env vars on first run.
# Note: the upstream image auto-generates a random password on first boot
# and writes it to the container logs. We override with predictable env vars.

ENV FB_BASEURL=/
ENV FB_NOAUTH=false

# Persistent locations
# /samples is mounted at runtime via the shared re-samples volume
# /db and /config hold FileBrowser's own state (separate volume recommended)
VOLUME ["/samples", "/database", "/config"]

EXPOSE 8080

# Default cmd is fine; the upstream image handles first-boot setup
