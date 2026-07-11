"""Remote command buttons for Apple TV HomeKit Enhanced."""

from dataclasses import dataclass
from typing import override

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.const import ATTR_ENTITY_ID, STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .entity import AppleTVEnhancedEntity
from .runtime import AppleTVEnhancedConfigEntry, AppleTVEnhancedRuntimeData


@dataclass(frozen=True, kw_only=True)
class AppleTVEnhancedButtonDescription(ButtonEntityDescription):
    """Describe an Apple TV remote command button."""

    command: str


BUTTON_DESCRIPTIONS = (
    AppleTVEnhancedButtonDescription(
        key="wakeup", name="Wake", icon="mdi:power", command="wakeup"
    ),
    AppleTVEnhancedButtonDescription(
        key="suspend", name="Suspend", icon="mdi:power-sleep", command="suspend"
    ),
    AppleTVEnhancedButtonDescription(
        key="home", name="Home", icon="mdi:home", command="home"
    ),
    AppleTVEnhancedButtonDescription(
        key="menu", name="Menu", icon="mdi:menu", command="menu"
    ),
    AppleTVEnhancedButtonDescription(
        key="select",
        name="Select",
        icon="mdi:checkbox-blank-circle",
        command="select",
    ),
    AppleTVEnhancedButtonDescription(
        key="up", name="Up", icon="mdi:chevron-up", command="up"
    ),
    AppleTVEnhancedButtonDescription(
        key="down", name="Down", icon="mdi:chevron-down", command="down"
    ),
    AppleTVEnhancedButtonDescription(
        key="left", name="Left", icon="mdi:chevron-left", command="left"
    ),
    AppleTVEnhancedButtonDescription(
        key="right", name="Right", icon="mdi:chevron-right", command="right"
    ),
    AppleTVEnhancedButtonDescription(
        key="play", name="Play", icon="mdi:play", command="play"
    ),
    AppleTVEnhancedButtonDescription(
        key="pause", name="Pause", icon="mdi:pause", command="pause"
    ),
    AppleTVEnhancedButtonDescription(
        key="previous",
        name="Previous",
        icon="mdi:skip-previous",
        command="previous",
    ),
    AppleTVEnhancedButtonDescription(
        key="next", name="Next", icon="mdi:skip-next", command="next"
    ),
    AppleTVEnhancedButtonDescription(
        key="skip_backward",
        name="Skip backward",
        icon="mdi:rewind-10",
        command="skip_backward",
    ),
    AppleTVEnhancedButtonDescription(
        key="skip_forward",
        name="Skip forward",
        icon="mdi:fast-forward-10",
        command="skip_forward",
    ),
    AppleTVEnhancedButtonDescription(
        key="volume_down",
        name="Volume down",
        icon="mdi:volume-minus",
        command="volume_down",
    ),
    AppleTVEnhancedButtonDescription(
        key="volume_up",
        name="Volume up",
        icon="mdi:volume-plus",
        command="volume_up",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AppleTVEnhancedConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Apple TV remote command buttons."""
    if entry.runtime_data.remote_entity_id is None:
        return

    async_add_entities(
        AppleTVEnhancedButton(entry, entry.runtime_data, description)
        for description in BUTTON_DESCRIPTIONS
    )


class AppleTVEnhancedButton(AppleTVEnhancedEntity, ButtonEntity):
    """Button that delegates a command to the official remote entity."""

    entity_description: AppleTVEnhancedButtonDescription

    def __init__(
        self,
        entry: AppleTVEnhancedConfigEntry,
        runtime_data: AppleTVEnhancedRuntimeData,
        description: AppleTVEnhancedButtonDescription,
    ) -> None:
        """Initialize an Apple TV command button."""
        super().__init__(entry, runtime_data, description.key)
        self.entity_description = description

    @property
    def available(self) -> bool:
        """Return whether the official remote entity is available."""
        remote_entity_id = self.runtime_data.remote_entity_id
        if remote_entity_id is None:
            return False
        state = self.hass.states.get(remote_entity_id)
        return state is not None and state.state not in {
            STATE_UNAVAILABLE,
            STATE_UNKNOWN,
        }

    @override
    async def async_press(self) -> None:
        """Send the configured command through the official remote service."""
        remote_entity_id = self.runtime_data.remote_entity_id
        if remote_entity_id is None:
            return

        await self.hass.services.async_call(
            "remote",
            "send_command",
            {
                ATTR_ENTITY_ID: remote_entity_id,
                "command": self.entity_description.command,
            },
            blocking=True,
        )

