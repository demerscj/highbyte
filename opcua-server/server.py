import asyncio
import json
import os
from datetime import UTC, datetime

from asyncua import Server, ua
from asyncua.ua import VariantType


def _load_config() -> dict:
    config_path = os.environ.get("CONFIG_PATH", "/config/config.json")
    config = {}
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as handle:
            config = json.load(handle)

    return {
        "server_name": os.environ.get("OPCUA_SERVER_NAME", config.get("server_name", "opcua-test-server")),
        "host": os.environ.get("OPCUA_HOST", config.get("host", "0.0.0.0")),
        "port": int(os.environ.get("OPCUA_PORT", config.get("port", 4840))),
        "namespace": os.environ.get("OPCUA_NAMESPACE", config.get("namespace", "urn:highbyte:opcua:test")),
        "status": os.environ.get("OPCUA_STATUS", config.get("status", "READY")),
        "counter_start": int(os.environ.get("OPCUA_COUNTER_START", config.get("counter_start", 0))),
        "temperature_start": float(os.environ.get("OPCUA_TEMP_START", config.get("temperature_start", 20.0))),
    }


async def main() -> None:
    cfg = _load_config()

    server = Server()
    await server.init()
    endpoint = f"opc.tcp://{cfg['host']}:{cfg['port']}/"
    server.set_endpoint(endpoint)
    server.set_server_name(cfg["server_name"])
    server.set_security_policy([ua.SecurityPolicyType.NoSecurity])

    idx = await server.register_namespace(cfg["namespace"])

    objects = server.nodes.objects
    device = await objects.add_object(idx, "SimDevice")

    status_var = await device.add_variable(idx, "Status", cfg["status"])
    vessel_temp_var = await device.add_variable(idx, "VesselTemperature", cfg["temperature_start"])
    jacket_temp_var = await device.add_variable(idx, "JacketTemperature", cfg["temperature_start"] - 1.0)
    ph_var = await device.add_variable(idx, "pH", 7.0)
    do_var = await device.add_variable(idx, "DO", 60.0)
    agitation_speed_var = await device.add_variable(idx, "AgitationSpeed", 250.0)
    air_flow_rate_var = await device.add_variable(idx, "AirFlowRate", 1.2)
    co2_flow_rate_var = await device.add_variable(idx, "CO2FlowRate", 0.15)
    o2_flow_rate_var = await device.add_variable(idx, "O2FlowRate", 0.2)
    timestamp_var = await device.add_variable(idx, "Timestamp", datetime.now(UTC).isoformat())

    await status_var.set_writable()
    await vessel_temp_var.set_writable()
    await jacket_temp_var.set_writable()
    await ph_var.set_writable()
    await do_var.set_writable()
    await agitation_speed_var.set_writable()
    await air_flow_rate_var.set_writable()
    await co2_flow_rate_var.set_writable()
    await o2_flow_rate_var.set_writable()

    async with server:
        vessel_temperature = cfg["temperature_start"]
        jacket_temperature = cfg["temperature_start"] - 1.0
        ph = 7.0
        dissolved_oxygen = 60.0
        agitation_speed = 250.0
        air_flow_rate = 1.2
        co2_flow_rate = 0.15
        o2_flow_rate = 0.2

        print(f"[{cfg['server_name']}] listening at {endpoint}")
        print(f"[{cfg['server_name']}] namespace: {cfg['namespace']}")

        while True:
            vessel_temperature += 0.03
            jacket_temperature += 0.02
            ph += 0.001
            dissolved_oxygen += 0.05
            agitation_speed += 0.4
            air_flow_rate += 0.002
            co2_flow_rate += 0.001
            o2_flow_rate += 0.0015

            await vessel_temp_var.write_value(round(vessel_temperature, 3), VariantType.Double)
            await jacket_temp_var.write_value(round(jacket_temperature, 3), VariantType.Double)
            await ph_var.write_value(round(ph, 3), VariantType.Double)
            await do_var.write_value(round(dissolved_oxygen, 3), VariantType.Double)
            await agitation_speed_var.write_value(round(agitation_speed, 3), VariantType.Double)
            await air_flow_rate_var.write_value(round(air_flow_rate, 4), VariantType.Double)
            await co2_flow_rate_var.write_value(round(co2_flow_rate, 4), VariantType.Double)
            await o2_flow_rate_var.write_value(round(o2_flow_rate, 4), VariantType.Double)
            await timestamp_var.write_value(datetime.now(UTC).isoformat(), VariantType.String)
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
