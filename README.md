# LaserAirCam

Smart Raspberry Pi companion for laser engravers: Wi-Fi camera, serial gateway, AirAssist control, and visual status feedback in one compact system.

## Why LaserAirCam

LaserAirCam is built to make your laser setup cleaner, safer, and easier to control remotely.
It combines camera streaming for LightBurn, robust Wi-Fi serial communication, Home Assistant integration, automated AirAssist, and RGB status lighting into a single device.

## Key Features

- 📷 **Camera for LightBurn over Wi-Fi**
	- Live MJPEG stream (`/stream`)
	- **StreamHD** mode (`/streamhd`): high-resolution captures every X seconds, delivered as MJPEG
	- High-resolution screenshot endpoint for framing and checks (`/snapshot`)

- 🌐 **Built-in WebUI**
	- Full browser dashboard for camera, laser status, LEDs, and system controls
	- Fast API endpoints for automation and external tools

- 🏠 **MQTT + Home Assistant Ready**
	- Native MQTT bridge with Home Assistant discovery
	- Exposes camera, status, and control entities for automation workflows

- 🔌 **Stable Wi-Fi Laser Control (ser2net + Virtual COM Port)**
	- Works with `ser2net` and a virtual serial port on the PC (freeware tools)
	- Designed for stability because the TCP serial link is persistent, transparent, and GRBL traffic is monitored end-to-end

- 🔁 **Serial Gateway with Smart Command Handling**
	- Intercepts and forwards serial traffic to/from the laser
	- If LightBurn is actively connected, manual commands are queued and sent safely when possible

- 💨 **AirAssist 24V PWM Control**
	- Automatic mode based on laser power/activity
	- Manual override mode from UI/automation

- 🌈 **Addressable RGB LED Status System**
	- Decorative and functional lighting effects
	- Laser-state aware profiles: `idle`, `running`, `engraving`, `hold/pause`, `error`, `door`

- 🧩 **3D-Printed Enclosure**
	- Dedicated case design for Atomstack A1 (and similar machines)
	- Integrates electronics, wiring, airflow, and controls in a clean layout

- 🔘 **3 Hardware Buttons**
	- Physical controls for quick local interaction even without opening the WebUI

LaserAirCam is intended for makers who want a reliable all-in-one control node around their laser: camera, transport, automation, and feedback, all synchronized.

## Setup

Follow the installation and configuration steps in [setup.md](./setup.md).
