import os
import time
from homeassistant_api import Client

URL = "http://192.168.1.6/api/"
TOKEN = "<LONG LIVED ACCESS TOKEN>"


def handle_command(command: str, domain: str, friendly_name: str, temperature: int = 0):
    # Mapping friendly names to entity IDs
    name_to_entity_id = {
        "thermostat": "climate.nest_thermostat",
        "bedroom curtains": "cover.bedroom_curtains",
        "living room curtains": "cover.livingroom_curtains",
        "bedroom lights": "light.bedroom_lights_helper_group",
        "bathroom lights": "light.bathroom",
        "kitchen lights": "light.kitchen_lights_helper_group",
        "living room lights": "light.living_room",
        "bedroom tv": "media_player.bedroom_tv",
        "living room tv": "media_player.living_room_tv",
        "vacuum": "vacuum.kaamwaali",
        "mop": "vacuum.poochewaali",
        "Main PC": "switch.main_pc_power",
        "Computer": "switch.main_pc_power",
        "sim rig": "switch.sim_rig_pc_power",
        "Cloud PC": "switch.cloud_pc_power",
    }

    # Convert the friendly name to an entity ID
    entity_id = name_to_entity_id.get(friendly_name)
    # Mapping of commands to their respective functions
    command_actions = {
        "turn_on": lambda: turn_on(entity_id=entity_id, domain=domain),
        "start": lambda: turn_on(entity_id=entity_id, domain=domain),
        "open": lambda: turn_on(entity_id=entity_id, domain=domain),
        "turn_off": lambda: turn_off(entity_id=entity_id, domain=domain),
        "stop": lambda: turn_off(entity_id=entity_id, domain=domain),
        "close": lambda: turn_off(entity_id=entity_id, domain=domain),
        "restart": lambda: restart_device(entity_id=entity_id, domain=domain),
        "set_temperature": lambda: set_temperature(
            entity_id=entity_id, domain=domain, temperature=temperature
        ),
    }

    # Execute the corresponding function
    action = command_actions.get(command)
    if action:
        action()
    else:
        return "Unknown command"


def set_temperature(entity_id, domain, temperature):
    client = Client(URL, TOKEN)
    with client:
        service = client.get_domain(domain)
        if service is None:
            return "Unknown service"
        service.set_temperature(entity_id=entity_id, temperature=temperature)  # type: ignore


def restart_device(entity_id, domain):
    client = Client(URL, TOKEN)
    with client:
        service = client.get_domain(domain)
        if service is None:
            return "Unknown service"
        service.restart(entity_id=entity_id)  # type: ignore


def turn_on(entity_id, domain):
    client = Client(URL, TOKEN)
    with client:
        service = client.get_domain(domain)
        if service is None:
            return "Unknown service"
        service.turn_on(entity_id=entity_id)  # type: ignore


def turn_off(entity_id, domain):
    client = Client(URL, TOKEN)
    with client:
        service = client.get_domain(domain)
        if service is None:
            return "Unknown service"
        service.turn_off(entity_id=entity_id)  # type: ignore
