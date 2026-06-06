# Container Deployment — Self-Contained RE_Playground

> Run the entire RE_Playground stack as a set of containers on a single Linux
> host (Docker or Podman). The agents stay inside the container; you only
> touch it from the browser. The desktop shares files in via a dedicated
> filebrowser container, so the agents never have to trust anything from
> your filesystem directly.

---

## Why a multi-container setup?

We deliberately do **not** ship one giant image. Splitting by concern gives you:

| Benefit | How |
|---------|-----|
| **Smaller images** | Core doesn't ship Ghidra's 400 MB JVM; ghidra doesn't ship r2 |
| **Independent scaling** | `docker compose up --scale ghidra=2` if you want two Ghidra instances |
| **Faster rebuilds** | Edit an agent → only `core` rebuilds (~30 s); Ghidra image cached for weeks |
| **Tighter isolation** | The Wine-using r2 container is the only one with `SYS_PTRACE`; if r2 is pwned, Ghidra + core are untouched |
| **Cleaner security posture** | Only `files` has write access to `/samples`; everything else mounts `:ro` |
| **Choice of runtime** | Compose works identically under Docker **and** Podman (rootless) |

---

## Architecture

```
                    Browser
                       │
        ┌──────────────┼───────────────┐
        │              │               │
   :4096 HTTP    :8080 HTTP       :22 SSH (optional)
        │              │               │
   ┌────▼────┐   ┌─────▼─────┐         │
   │  core   │   │   files   │         │
   │ OpenCode│   │FileBrowser│         │
   │ + 7 MCP │   │  :rw      │         │
   │ servers │   └─────┬─────┘         │
   └────┬────┘         │               │
        │              │ writes        │
        │ reads        ▼               │
        │         /samples ◄───────────┘ (desktop uploads here)
        │              │
        │         re-samples  (named volume, shared)
        │
   ┌────┴─────────────┬─────────────────┐
   │                  │                 │
   ▼                  ▼                 ▼
┌──────┐         ┌────────┐         ┌────────┐
│ghidra│         │radare2 │         │ memini │
│ :8089│         │ :9090  │         │ :5432  │
└──────┘         └────────┘         └────────┘
Ghidra SRE        r2 + Wine         PostgreSQL
+ 245 MCP         + r2mcp           + pgvector
(read /samples)   (read /samples)   (memory state)
```

The 5 containers, named volumes, and 1 bridge network are all declared in
`docker-compose.yml` / `podman-compose.yml`.

---

## Quick start (Docker)

```bash
# 1. Clone
git clone https://github.com/Veedubin/Reverse-Engineering-Playground.git
cd Reverse-Engineering-Playground

# 2. Set your secrets (optional but recommended)
export OPENCODE_SERVER_PASSWORD="$(openssl rand -hex 16)"
export OLLAMA_API_KEY="sk-..."

# 3. Build & launch
docker compose up -d --build

# 4. Open the UI
xdg-open http://localhost:4096    # OpenCode web (agent UI)
xdg-open http://localhost:8080    # FileBrowser (sample ingress)

# 5. Check logs if something's wrong
docker compose logs -f core

# 6. Stop (volumes preserved)
docker compose down
```

First build takes ~15 minutes (Ghidra download is the bottleneck). Subsequent
builds are seconds thanks to Docker's layer cache.

## Quick start (Podman, rootless)

```bash
# 1. Install podman + podman-compose
sudo apt install podman python3-pip
pip install --user podman-compose
# On Arch: sudo pacman -S podman podman-compose

# 2. Enable lingering (so containers survive logout)
loginctl enable-linger $USER

# 3. Same as Docker from here
git clone https://github.com/Veedubin/Reverse-Engineering-Playground.git
cd Reverse-Engineering-Playground

export OPENCODE_SERVER_PASSWORD="$(openssl rand -hex 16)"
export OLLAMA_API_KEY="sk-..."

podman-compose up -d --build
# 127.0.0.1:4096 — OpenCode web
# 127.0.0.1:8080 — FileBrowser

podman-compose down
```

The Podman compose file uses `127.0.0.1:` port bindings (not `0.0.0.0:`) for
better rootless safety. To expose to LAN, see "LAN access" below.

---

## File ingress — the security model

This is the bit that needed the most thought. We want:

1. You can upload `.exe` / `.dll` / `.apk` from your desktop browser
2. The agents can see those files
3. The agents **cannot** reach the rest of your filesystem
4. The browser session is over HTTPS (or at least HTTP Basic Auth on localhost)

The solution is a **one-way file ingress** through FileBrowser:

- `re-files` is the only container with **read-write** access to the named
  volume `re-samples` (mounted at `/samples`)
- `re-core`, `re-ghidra`, `re-radare2` mount the same volume **read-only**
- FileBrowser's web UI (`http://localhost:8080`) is the only way to
  put files into `/samples` — there's no bind mount from your home dir
- FileBrowser's own state (users, DB, config) lives in a **separate**
  named volume (`re-filebrowser-db`, `re-filebrowser-cfg`) so the agent
  containers can't tamper with the auth

When you upload `target.exe` to FileBrowser:
1. FileBrowser writes it to its `/samples` mount
2. The change is reflected in the `re-samples` named volume
3. All other containers see the file appear at their own `/samples` mount
4. You tell the agent: "analyze /samples/target.exe"
5. Agent runs `r2`, `ghidra`, `diec`, `yara`, etc. against the file — **all inside the container network**

To get results back, you can either:
- Read them in the OpenCode web UI (default — agent will show you what it found)
- Or browse to `/samples` in FileBrowser and download the analysis output the agent wrote there

### What you DON'T get

- The agents **cannot** read your home directory
- The agents **cannot** read `/etc/passwd` on your host
- The agents **cannot** reach your SSH keys, browser cookies, or `~/.bash_history`
- Even if a malicious PE exploits a Frida bug and escapes its container, the
  host filesystem is on a different Docker volume entirely

---

## LAN access (share with your team)

By default, only `localhost` can reach the web UIs. To expose to your
LAN, you have three options:

### Option 1: Tailscale (recommended)

Tailscale gives every device a stable `100.x.y.z` IP and WireGuard-encrypted
transport, with zero firewall rules. Ideal for distributed RE teams.

```bash
# On the host running the containers
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up

# Tailscale is a mesh VPN; the other devices install Tailscale and
# authenticate to the same account. They then reach:
#   http://<host-tailscale-ip>:4096   (OpenCode)
#   http://<host-tailscale-ip>:8080   (FileBrowser)
```

### Option 2: nginx reverse proxy with TLS

If you have a domain and want public HTTPS (e.g. for a remote malware-analysis
service), put Caddy or nginx in front of port 4096/8080 and get free Let's
Encrypt certs via DNS-01 challenge.

```nginx
# /etc/nginx/sites-available/re-playground.conf
server {
    listen 443 ssl;
    server_name re.your-domain.com;
    ssl_certificate     /etc/letsencrypt/live/re.your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/re.your-domain.com/privkey.pem;

    # OpenCode web (with HTTP Basic Auth)
    location / {
        proxy_pass         http://127.0.0.1:4096;
        auth_basic         "RE Playground";
        auth_basic_user_file /etc/nginx/.htpasswd;
    }

    # FileBrowser
    location /files/ {
        proxy_pass http://127.0.0.1:8080/;
        auth_basic         "RE Playground Files";
        auth_basic_user_file /etc/nginx/.htpasswd;
    }
}
```

### Option 3: Just bind to 0.0.0.0 (insecure — for trusted LANs only)

Edit `docker-compose.yml` and change `"127.0.0.1:4096:4096"` to
`"4096:4096"`. Now anyone on your LAN who knows the password can reach
OpenCode. **Don't do this on a public network without a reverse proxy.**

---

## Customization

### Add an extra MCP server

Edit `docker/core/Dockerfile` and add the install + `mcpservers` config to
the OpenCode config. Rebuild with `docker compose build core`.

### Pin a Ghidra version

```bash
# in docker/ghidra/Dockerfile, change:
ARG GHIDRA_VERSION=11.3.2
ARG GHIDRA_DATE=20250422
```

The current 11.3.2 is the latest stable as of June 2026. If a new release
ships, update these two lines and `docker compose build ghidra`.

### Persistent samples

The `re-samples` named volume persists across `docker compose down`.
To back it up:

```bash
docker run --rm \
    -v re-samples:/source:ro \
    -v $(pwd)/backup:/dest \
    alpine tar czf /dest/samples-$(date +%Y%m%d).tar.gz -C /source .
```

### Mount a real directory as /samples

If you'd rather have the host filesystem be the source of truth (e.g. you
have a big malware corpus on a NAS):

```yaml
# docker-compose.yml
services:
  files:
    volumes:
      - /mnt/nas/malware-corpus:/samples:rw   # <-- replaces the named volume
```

This breaks the security model slightly (the agents can now read whatever
the host user can read in that directory). Make sure it's a directory
dedicated to RE samples.

---

## GPU / model acceleration

If your host has an NVIDIA GPU and you want fast local embeddings for
memini-ai, install the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)
then add to the `core` and `memini` services in `docker-compose.yml`:

```yaml
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

For the `memini` service (PostgreSQL + pgvector), no GPU is needed —
embeddings are computed by the `core` container, not the database.

---

## Persistent services with systemd

To make the stack auto-start on boot (and survive reboots), create
`/etc/systemd/system/re-playground.service`:

```ini
[Unit]
Description=RE_Playground
After=docker.service network-online.target
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/Reverse-Engineering-Playground
ExecStart=/usr/bin/docker compose up -d --build
ExecStop=/usr/bin/docker compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now re-playground
```

For Podman, use a [quadlet](https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html)
or `podman-compose systemd` plugin instead.

---

## Troubleshooting

### `bind: address already in use` on port 4096 or 8080

Something else on the host is using that port. Find it:

```bash
sudo lsof -i :4096
sudo lsof -i :8080
```

Either stop the conflicting service or change the port mapping in
`docker-compose.yml` (e.g. `"127.0.0.1:5090:4096"` maps host 5090 → container 4096).

### Ghidra container OOMKilled

Ghidra's JVM is hungry. The compose file already sets `mem_limit: 4g`.
If you have less RAM, drop it to `2g` and accept slower analysis.
If you have more, bump to `8g` for faster decompilation.

### `permission denied` on the Wine container

The r2 container needs `SYS_PTRACE` for debug. Under Docker this works
out of the box. Under rootless Podman, you need `userns_mode: keep-id`
(already in the podman compose) **and** your kernel must support
`/proc/sys/kernel/yama/ptrace_scope=0` or similar. Check
`cat /proc/sys/kernel/yama/ptrace_scope` — if it's `1` or higher, you
can't ptrace processes you don't own, which is the whole point.

### `opencode web` exits immediately

Check `docker compose logs core` for the actual error. Common causes:
- `OPENCODE_SERVER_PASSWORD` env var not set (then it starts on
  127.0.0.1 only — fine, but you may have set the wrong password)
- A required env var like `MEMINI_DB_URL` is wrong (e.g. pointing at
  `re-memini` but the container is named `re_playground_memini_1` —
  pin the name in `container_name:` which we already do)

### Build fails: `Could not resolve github.com`

Corporate proxy? Configure Docker's buildkit:

```json
// ~/.docker/config.json
{
  "proxies": {
    "default": {
      "httpProxy": "http://proxy.corp:8080",
      "httpsProxy": "http://proxy.corp:8080",
      "noProxy": "localhost,127.0.0.1"
    }
  }
}
```

### I'm not seeing my uploaded file in /samples

The named volume is mounted in 5 places. FileBrowser writes
async — give it a second, then refresh. If it still doesn't appear:

```bash
docker exec -it re-core ls -la /samples
# if empty, the upload didn't actually land
docker exec -it re-files ls -la /samples
# should show your file
```

If `re-files` shows the file but `re-core` doesn't, the named volume
got remounted weirdly. Restart everything:

```bash
docker compose down
docker volume ls | grep re-samples
docker volume inspect re-samples
docker compose up -d
```

---

## See also

- [learn-more.md](learn-more.md) — curated reading list for every tool
- [windows-re/tools-and-mcp-servers.md](windows-re/tools-and-mcp-servers.md)
  — Windows-specific tool research
- [OpenCode web docs](https://opencode.ai/docs/web/) — upstream reference
- [OpenCode server docs](https://opencode.ai/docs/server/) — for the
  programmatic OpenAPI alternative
- [Docker compose spec](https://docs.docker.com/compose/compose-file/)
- [Podman compose spec](https://github.com/containers/podman-compose)
