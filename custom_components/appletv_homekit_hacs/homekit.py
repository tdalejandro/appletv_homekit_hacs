"""HomeKit accessory bridge helpers."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.homekit.const import (
    CONF_FILTER,
    CONF_HOMEKIT_MODE,
    DEFAULT_CONFIG_FLOW_PORT,
    DOMAIN as HOMEKIT_DOMAIN,
    HOMEKIT_MODE_ACCESSORY,
)
from homeassistant.components.homekit.util import async_find_next_available_port
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ENTITY_ID, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from .const import CONF_HOMEKIT_ENTRY_ID
from .runtime import AppleTVEnhancedConfigEntry

CONF_INCLUDE_ENTITIES = "include_entities"

_LOGGER = logging.getLogger(__name__)


async def async_ensure_homekit_accessory(
    hass: HomeAssistant,
    entry: AppleTVEnhancedConfigEntry,
    entity_id: str,
) -> None:
    """Create or link one official HomeKit accessory entry for a proxy entity."""
    async with entry.runtime_data.homekit_lock:
        homekit_entry = _find_homekit_accessory_entry(hass, entity_id)
        if homekit_entry is None:
            port = async_find_next_available_port(hass, DEFAULT_CONFIG_FLOW_PORT)
            result = await hass.config_entries.flow.async_init(
                HOMEKIT_DOMAIN,
                context={"source": HOMEKIT_MODE_ACCESSORY},
                data={CONF_ENTITY_ID: entity_id, CONF_PORT: port},
            )
            if result["type"] != FlowResultType.CREATE_ENTRY:
                _LOGGER.warning(
                    "Could not create HomeKit accessory for %s: %s",
                    entity_id,
                    result["type"],
                )
                return
            homekit_entry = result.get("result")
            if not isinstance(homekit_entry, ConfigEntry):
                _LOGGER.warning(
                    "HomeKit accessory flow for %s did not return a config entry",
                    entity_id,
                )
                return

        entry.runtime_data.homekit_entry_id = homekit_entry.entry_id
        if entry.data.get(CONF_HOMEKIT_ENTRY_ID) != homekit_entry.entry_id:
            hass.config_entries.async_update_entry(
                entry,
                data={**entry.data, CONF_HOMEKIT_ENTRY_ID: homekit_entry.entry_id},
            )


def _find_homekit_accessory_entry(
    hass: HomeAssistant, entity_id: str
) -> ConfigEntry | None:
    """Find an existing official HomeKit accessory entry for an entity."""
    for entry in hass.config_entries.async_entries(HOMEKIT_DOMAIN):
        target = entry.options if CONF_HOMEKIT_MODE in entry.options else entry.data
        if target.get(CONF_HOMEKIT_MODE) != HOMEKIT_MODE_ACCESSORY:
            continue
        filter_data: dict[str, Any] = target.get(CONF_FILTER, {})
        if entity_id in filter_data.get(CONF_INCLUDE_ENTITIES, []):
            return entry
    return None
