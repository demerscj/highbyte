# OPC UA Test Servers (Dev + Test)

This workspace includes two minimal OPC UA servers for connectivity testing.

## Endpoints

Use these URIs when connecting from your Mac host (for example UaExpert running locally):

- Dev: opc.tcp://localhost:4840/
- Test: opc.tcp://localhost:4841/

Use these URIs when connecting from another Docker container on `highbyte-net` (for example `highbyte-dev`):

- Dev: opc.tcp://opcua-dev:4840/
- Test: opc.tcp://opcua-test:4840/

Important: `localhost` inside a container refers to that same container, not the OPC UA server containers.

Both endpoints expose a `SimDevice` object with these variables:

- `Status` (string)
- `VesselTemperature` (double)
- `JacketTemperature` (double)
- `pH` (double)
- `DO` (double)
- `AgitationSpeed` (double)
- `AirFlowRate` (double)
- `CO2FlowRate` (double)
- `O2FlowRate` (double)
- `Timestamp` (ISO-8601 UTC string)

## Start only OPC UA servers

```bash
docker compose up -d --build opcua-dev opcua-test
```

## View logs

```bash
docker compose logs -f opcua-dev opcua-test
```

## Stop servers

```bash
docker compose stop opcua-dev opcua-test
```

## Environment-specific config

- Dev config: `appdata/opcua/dev/config.json`
- Test config: `appdata/opcua/test/config.json`

Adjust `status`, `counter_start`, and `temperature_start` to make each endpoint easily distinguishable to clients.
