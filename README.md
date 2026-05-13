# HighByte IntelligenceHub — Dev / Test / Prod Stack

A containerised three-tier [HighByte IntelligenceHub](https://highbyte.com) deployment used for developing and testing industrial data-product pipelines, with simulated OPC-UA device data and GitHub-backed configuration management.

## Architecture

```
dev  (central hub — config source of truth)
 └── test  (remote of dev | also a central hub)
       └── prod  (remote of test)
```

Each hub runs in its own Docker container. `dev` and `test` pull their project configuration from this GitHub repo on startup.

## Services

| Service | REST API / UI | MQTT broker | Data / MCP |
|---------|--------------|-------------|------------|
| `highbyte-dev` | http://localhost:45245 | 1885 | 8885 |
| `highbyte-test` | http://localhost:45246 | 1886 | 8886 |
| `highbyte-prod` | http://localhost:45247 | 1887 | 8887 |
| `opcua-dev` | opc.tcp://localhost:4840 | — | — |
| `opcua-test` | opc.tcp://localhost:4841 | — | — |

## Simulated OPC-UA Device

Two containerised OPC-UA servers (`opcua-dev`, `opcua-test`) expose a `SimDevice` object with bioreactor-style variables:

`Status` · `VesselTemperature` · `JacketTemperature` · `pH` · `DO` · `AgitationSpeed` · `AirFlowRate` · `CO2FlowRate` · `O2FlowRate` · `Timestamp`

See [OPCUA_TEST_SERVERS.md](OPCUA_TEST_SERVERS.md) for connection URIs and config options.

## GitHub-backed Configuration

`dev` and `test` hubs load their project configuration from this repo on startup via the `HIGHBYTE_DEPLOYMENT_FILE` environment variable. The deployment files are:

- `dev/intelligencehub-deployment.json` — project config for the dev hub
- `test/intelligencehub-deployment.json` — project config for the test hub

Only the `.project` and `.network` sections are imported (controlled by `keyPaths` in each hub's `appdata/*/deployment-settings.json`).

> **Important:** The `github_datamodels` connection in the deployment files uses a Bearer Token PAT that is **not** committed. After cloning, enter your GitHub PAT in the dev UI under Settings → Connections → `github_datamodels`.

## Quick Start

### Prerequisites
- Docker Desktop
- Access to this repository

### First run

```bash
git clone https://github.com/demerscj/highbyte.git
cd highbyte
docker compose up -d
```

Open the dev UI at http://localhost:45245 and log in with the default credentials.

### Central-config wiring (one-time)

The hub network requires tokens to be wired up after first start:

1. Open **dev UI** → Network → Hubs → Create Network Group → copy the **TOKEN**
2. Paste the token into `appdata/test/intelligencehub-remoteconfig.json` (`"token"` field)
3. Open **test UI** → Network → Hubs → Create Network Group → copy the **TOKEN**
4. Paste the token into `appdata/prod/intelligencehub-remoteconfig.json` (`"token"` field)
5. `docker compose restart test prod`

### Deployment credential setup (one-time)

The `deployment-settings.json` files hold the GitHub credentials used for startup config sync. These are gitignored. After cloning, populate `appdata/dev/deployment-settings.json` and `appdata/test/deployment-settings.json` with your repo URI and PAT, then encrypt them:

```bash
docker compose exec dev java -jar /usr/local/highbyte/runtime/intelligencehub-runtime.jar \
  encrypt /usr/local/highbyte/appData/deployment-settings.json
```

## Repository Layout

```
.
├── dev/                        # HighByte deployment config — dev hub
├── test/                       # HighByte deployment config — test hub
├── appdata/
│   ├── dev/                    # Runtime appData for dev (mostly gitignored)
│   ├── test/                   # Runtime appData for test (mostly gitignored)
│   ├── prod/                   # Runtime appData for prod (mostly gitignored)
│   └── opcua/{dev,test}/       # OPC-UA server config per environment
├── opcua-server/               # Python OPC-UA simulation server (asyncua)
├── docker-compose.yml
└── README.md
```

## What Is Gitignored

The following are never committed to keep credentials and live state out of the repo:

- `appdata/**/intelligencehub-configuration.json` — live runtime config (contains connection tokens)
- `appdata/**/intelligencehub-remoteconfig.json` — network hub tokens
- `appdata/**/deployment-settings.json` — GitHub PAT for config sync
- `appdata/**/intelligencehub-certificatestore.pkcs12` — TLS key store
- `appdata/**/intelligencehub-secrets.json` / `intelligencehub-users.json` — credentials
- `appdata/**/backups/` — auto-backup copies
- `appdata/**/*.db` / `*.dat` — runtime databases
