# Ignition Gateway Configuration

## Version-Controlled Config: Gateway Backup (`.gwbk`)

Ignition's validated deployment artifact is a **gateway backup file** (`.gwbk`).
This directory holds that backup once it has been created and validated.

---

## First-Time Setup

On a fresh launch the container auto-commissions from environment variables
defined in `docker-compose.yml` (no `.gwbk` needed):

```
ACCEPT_IGNITION_EULA=Y
GATEWAY_ADMIN_USERNAME / GATEWAY_ADMIN_PASSWORD
IGNITION_EDITION=standard
```

1. `docker compose up -d ignition`
2. Open http://localhost:9088 and complete any first-run prompts.
3. Configure the gateway (tags, connections, projects, etc.).
4. Validate everything works as expected.

---

## Exporting the Validated Backup

Once the gateway is in the desired validated state:

1. In the Ignition Gateway web interface go to
   **Config → System → Backup/Restore**.
2. Click **Download Backup** — save the file as `gateway.gwbk`.
3. Place it in this directory:
   ```
   ignition/gateway.gwbk
   ```
4. Git commit and push:
   ```bash
   git add ignition/gateway.gwbk
   git commit -m "feat: add validated Ignition gateway backup"
   git push
   ```

---

## Restoring from the Validated Backup

Uncomment the restore command in `docker-compose.yml`:

```yaml
  ignition:
    ...
    volumes:
      - ./appdata/ignition:/usr/local/bin/ignition/data
      - ./ignition:/restore:ro          # mount this dir read-only
    command: >
      -n ignition
      -a localhost
      -h 9088
      -s 9043
      -r /restore/gateway.gwbk         # restore on first fresh launch
```

The `-r` flag only takes effect when the gateway data directory is empty
(i.e., a fresh container). Existing data is never overwritten.

---

## Promotion Pattern

```
dev  →  validate  →  commit gateway.gwbk  →  test  →  approve  →  site-b  →  ...
```

The same `gateway.gwbk` is used across all environments; site-specific
differences (tag providers, DB connections, etc.) should be parameterised
using Ignition's built-in **Gateway Network** or environment-variable–driven
scripting rather than baked into the backup.
