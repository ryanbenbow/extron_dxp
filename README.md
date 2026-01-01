# extron_dxp
Extron DXP 168 HD (non plus) Matrix Control for Home Assistant

# Extron DXP Matrix Integration for Home Assistant

A custom integration to control Extron DXP Matrix Switchers via Ethernet (Telnet).

## Features
- **Config Flow:** Setup via the Home Assistant UI (Settings > Devices > Add Integration).
- **Authentication:** Supports Password-protected Extron devices.
- **Select Entities:** Automatically creates `select` entities for each Output (1-8).
- **Live Status:** Polls the device status every 30 seconds to keep Home Assistant in sync.

## Installation via HACS
1. Go to **HACS** > **Integrations**.
2. Click the 3 dots (top right) > **Custom Repositories**.
3. Add `https://github.com/ryanbenbow/extron_dxp` as an **Integration**.
4. Click **Download**.
5. Restart Home Assistant.

## Configuration
1. Go to **Settings** > **Devices & Services**.
2. Click **Add Integration** and search for **Extron**.
3. Enter your Matrix IP Address, Port (default 23), and Password.
