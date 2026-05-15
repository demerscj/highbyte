# HighByte IntelligenceHub — Dev Stack

A containerised [HighByte IntelligenceHub](https://highbyte.com) deployment for developing and testing industrial data-product pipelines, with an Ignition SCADA gateway and GitHub-backed configuration management.

## Stack

| Service | UI / API | Notes |
|---------|----------|-------|
| `highbyte-dev` | http://localhost:45245 | Central hub — REST API / MCP on 8885, internal MQTT on 1885 |
| `ignition` | http://localhost:9088 | SCADA gateway (HTTPS 9043) |
| `hivemq` | mqtt://localhost:1883 | Shared MQTT broker |

## GitHub-backed Configuration

`highbyte-dev` loads its project config from this repo's `main` branch on every startup via `HIGHBYTE_DEPLOYMENT_FILE`. The committed deployment file is:

- `intelligencehub-deployment.json` — full project and network config for the hub

Only the `.project` and `.network` sections are applied (controlled by `keyPaths` in `appdata/dev/deployment-settings.json`, which is gitignored).

## Fresh Install (New Site)

### Prerequisites
- Docker Desktop
- Read access to this repository (GitHub PAT)

### 1 — Clone and create the environment file

```bash
git clone https://github.com/demerscj/highbyte.git
cd highbyte

cp .env.example .env
# Edit .env — set IGNITION_ADMIN_PASSWORD to a strong password
```

### 2 — Create appdata/dev/deployment-settings.json

This file is gitignored (contains your GitHub PAT). Create it before first start:

```json
{
  "version": 0,
  "repos": [{
    "type": "git",
    "name": "highbyte-shared",
    "uri": "https://github.com/demerscj/highbyte",
    "author": "HighByte IntelligenceHub",
    "email": "",
    "auth": {
      "type": "pass",
      "username": "<github-username>",
      "password": "<github-pat>"
    }
  }],
  "fragments": [{
    "details": {
      "type": "git",
      "deployFile": "intelligencehub-deployment.json",
      "repoName": "highbyte-shared",
      "ref": "main"
    },
    "keyPaths": [".project", ".network"]
  }]
}
```

### 3 — Start the stack

```bash
docker compose up -d
```

On first start:
- **Ignition** automatically restores from `ignition/gateway.gwbk`
- **HighByte dev** pulls its project config from this repo's `main` branch

### 4 — Encrypt the PAT (optional but recommended)

After the hub has started once (its certificate store is generated on first run):

```bash
docker exec -w /usr/local/highbyte/appData highbyte-dev \
  java -jar /usr/local/highbyte/runtime/intelligencehub-runtime.jar \
  encrypt /usr/local/highbyte/appData/deployment-settings.json
```

> No cert-store copying is needed. `intelligencehub-deployment.json` contains no encrypted values, so a fresh cert store generated on first run is sufficient.

## Repository Layout

```
.
├── intelligencehub-deployment.json   # HighByte project + network config (source of truth)
├── appdata/
│   └── dev/                          # Runtime appData for highbyte-dev (mostly gitignored)
├── hivemq/
│   └── config.xml                    # HiveMQ broker config
├── ignition/
│   ├── gateway.gwbk                  # Validated Ignition gateway backup
│   └── README.md                     # Ignition backup/restore workflow
├── opcua-server/                     # OPC-UA simulation server (reference — not in compose)
├── .env.example                      # Template for required environment variables
├── docker-compose.yml
└── README.md
```

## What Is Gitignored

| Path | Reason |
|------|--------|
| `.env` | Contains real passwords |
| `appdata/**/deployment-settings.json` | GitHub PAT for config sync |
| `appdata/**/intelligencehub-certificatestore.pkcs12` | AES key store |
| `appdata/**/intelligencehub-configuration.json` | Live runtime state |
| `appdata/**/intelligencehub-secrets.json` | Application secrets |
| `appdata/**/intelligencehub-users.json` | User credentials |
| `appdata/**/backups/` | Auto-backup snapshots |
| `appdata/**/*.db` / `*.dat` | Runtime databases |
