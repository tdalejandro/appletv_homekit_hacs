"""Config flow for Apple TV HomeKit Enhanced."""

from typing import Any, override

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.selector import (
    BooleanSelector,
    EntitySelector,
    EntitySelectorConfig,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
)

from .const import (
    APPLE_TV_DOMAIN,
    CONF_CLOSE_APPS_COUNT,
    CONF_ENABLE_HOMEKIT_QR,
    CONF_MEDIA_PLAYER_ENTITY_ID,
    DOMAIN,
)
from .helpers import (
    DEFAULT_CLOSE_APPS_COUNT,
    MAX_CLOSE_APPS_COUNT,
    MIN_CLOSE_APPS_COUNT,
    clamp_close_apps_count,
)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_MEDIA_PLAYER_ENTITY_ID): EntitySelector(
            EntitySelectorConfig(domain="media_player")
        ),
        vol.Optional(CONF_ENABLE_HOMEKIT_QR, default=True): BooleanSelector(),
        vol.Optional(
            CONF_CLOSE_APPS_COUNT, default=DEFAULT_CLOSE_APPS_COUNT
        ): NumberSelector(
            NumberSelectorConfig(
                min=MIN_CLOSE_APPS_COUNT,
                max=MAX_CLOSE_APPS_COUNT,
                mode=NumberSelectorMode.BOX,
            )
        ),
    }
)


class AppleTVHomeKitConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle configuration for Apple TV HomeKit Enhanced."""

    VERSION = 1

    @override
    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Validate and store an official Apple TV media player."""
        errors: dict[str, str] = {}

        if user_input is not None:
            entity_id = user_input[CONF_MEDIA_PLAYER_ENTITY_ID]
            registry_entry = er.async_get(self.hass).async_get(entity_id)

            if registry_entry is None:
                errors["base"] = "entity_not_found"
            elif (
                registry_entry.domain != "media_player"
                or registry_entry.platform != APPLE_TV_DOMAIN
            ):
                errors["base"] = "not_apple_tv"
            else:
                await self.async_set_unique_id(registry_entry.unique_id or entity_id)
                self._abort_if_unique_id_configured()
                state = self.hass.states.get(entity_id)
                title = (
                    state.name
                    if state
                    else registry_entry.original_name or entity_id
                )
                data = {
                    **user_input,
                    CONF_CLOSE_APPS_COUNT: clamp_close_apps_count(
                        user_input.get(CONF_CLOSE_APPS_COUNT)
                    ),
                }
                return self.async_create_entry(title=title, data=data)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    @staticmethod
    @callback
    @override
    def async_get_options_flow(config_entry):
        """Create the options flow."""
        return AppleTVHomeKitOptionsFlow()


class AppleTVHomeKitOptionsFlow(OptionsFlow):
    """Handle Apple TV HomeKit Enhanced options."""

    @override
    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage QR and launcher sequence options."""
        if user_input is not None:
            options = {
                **user_input,
                CONF_CLOSE_APPS_COUNT: clamp_close_apps_count(
                    user_input.get(CONF_CLOSE_APPS_COUNT)
                ),
            }
            return self.async_create_entry(title="", data=options)

        data = self.config_entry.data
        options = self.config_entry.options
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_ENABLE_HOMEKIT_QR,
                        default=options.get(
                            CONF_ENABLE_HOMEKIT_QR,
                            data.get(CONF_ENABLE_HOMEKIT_QR, False),
                        ),
                    ): BooleanSelector(),
                    vol.Optional(
                        CONF_CLOSE_APPS_COUNT,
                        default=clamp_close_apps_count(
                            options.get(
                                CONF_CLOSE_APPS_COUNT,
                                data.get(
                                    CONF_CLOSE_APPS_COUNT, DEFAULT_CLOSE_APPS_COUNT
                                ),
                            )
                        ),
                    ): NumberSelector(
                        NumberSelectorConfig(
                            min=MIN_CLOSE_APPS_COUNT,
                            max=MAX_CLOSE_APPS_COUNT,
                            mode=NumberSelectorMode.BOX,
                        )
                    ),
                }
            ),
        )
