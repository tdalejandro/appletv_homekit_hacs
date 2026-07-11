# Apple TV HomeKit Enhanced

Home Assistant helper integration inspired by
[`homebridge-appletv-enhanced`](https://github.com/maxileith/homebridge-appletv-enhanced).

This project extends an Apple TV already configured with Home Assistant's
official Apple TV integration. It reuses the official `media_player` and
`remote` entities instead of creating a second `pyatv` connection.

> [!WARNING]
> Version `0.1.0` is an MVP. Create a backup before installation.

## Architecture

- No duplicated Apple TV pairing or credentials.
- No additional listener, web server, Node.js runtime or Python venv.
- Protocol updates remain managed by Home Assistant Core.
- Removing this helper does not remove the official Apple TV device.

## MVP features

- UI configuration for an official Apple TV `media_player`.
- Sensors for playback, active app and media metadata.
- Binary sensors for playback state and media type.
- Remote command buttons for navigation, playback, skipping and volume.
- English and Spanish configuration translations.

## Requirements

- Home Assistant `2026.7.0` or newer.
- The official
  [Apple TV integration](https://www.home-assistant.io/integrations/apple_tv/)
  configured and working.
- HACS for managed installation, or manual installation under
  `custom_components`.

## Installation with HACS

1. Open HACS and select **Integrations**.
2. Add this repository as a custom repository of type **Integration**.
3. Install **Apple TV HomeKit Enhanced** and restart Home Assistant.
4. Go to **Settings > Devices & services > Add integration**.
5. Select **Apple TV HomeKit Enhanced** and choose the official Apple TV media
   player entity.

## Manual installation

Copy `custom_components/appletv_homekit_hacs` into the Home Assistant
`config/custom_components` directory and restart Home Assistant.

## HomeKit

Expose the official media player and desired enhanced entities through Home
Assistant's
[HomeKit Bridge integration](https://www.home-assistant.io/integrations/homekit/).
The helper does not create a second HomeKit bridge.

## Current limitations

- Power state remains subject to the official integration and tvOS.
- Volume depends on HomePod or HDMI-CEC; IR-only volume is not supported.
- Command sequences, deep-link buttons and close-all-apps are planned.
- Reload the helper after renaming its selected source entity.

## Development checks

```bash
python -m unittest discover -s tests -v
python -m compileall custom_components tests
```

## Security

Only the selected Home Assistant entity ID is stored. The helper does not read
or persist Apple TV credentials and does not make cloud requests.

## Attribution

- Inspiration: [`maxileith/homebridge-appletv-enhanced`](https://github.com/maxileith/homebridge-appletv-enhanced)
- Protocol: [`postlund/pyatv`](https://github.com/postlund/pyatv)
- Integration: [`home-assistant/core`](https://github.com/home-assistant/core/tree/dev/homeassistant/components/apple_tv)

Licensed under the MIT License.
