# Apple TV HomeKit Enhanced

Home Assistant helper integration inspired by
[`homebridge-appletv-enhanced`](https://github.com/maxileith/homebridge-appletv-enhanced).

This project extends an Apple TV already configured with Home Assistant's
official Apple TV integration. It reuses the official `media_player` and
`remote` entities instead of creating a second `pyatv` connection.

> [!WARNING]
> Version `0.2.0` is still early. Create a backup before installation.

## Architecture

- No duplicated Apple TV pairing or credentials.
- No additional listener, web server, Node.js runtime or Python venv.
- Protocol updates remain managed by Home Assistant Core.
- Dedicated HomeKit QR codes are created through Home Assistant's official
  HomeKit integration.
- Removing this helper does not remove the official Apple TV device.

## Features

- UI configuration for an official Apple TV `media_player`.
- Dedicated HomeKit Television accessory per Apple TV, with its own QR code.
- Apple TV apps are exposed as HomeKit TV inputs when the official integration
  provides them in `source_list`.
- HomeKit inputs include `Inicio` and `Cerrar Apps`.
- `Cerrar Apps` runs the same blind launcher sweep used by
  `homebridge-appletv-enhanced`: Home, Home, Left, then Up/Up per configured
  app slot, then Home.
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

For new entries, the helper creates one official Home Assistant HomeKit
accessory entry for the generated `HomeKit TV` media player. Home Assistant
shows the QR/pairing notification and stores the pairing data.

Existing `0.1.0` entries keep QR creation disabled until enabled in the
integration options. Disabling QR creation later does not delete an existing
HomeKit accessory, so pairing is preserved.

## Current limitations

- Power state remains subject to the official integration and tvOS.
- Volume depends on HomePod or HDMI-CEC; IR-only volume is not supported.
- `Cerrar Apps` is intentionally blind because tvOS does not expose a reliable
  app switcher state through Home Assistant.
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
