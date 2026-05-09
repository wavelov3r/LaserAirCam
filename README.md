# 🛰️ LaserAirCam
**Smart Raspberry Pi companion for laser engravers**  
*Wi-Fi Camera • Serial Gateway • AirAssist Control • Visual Status Feedback*

[![Hardware](https://img.shields.io/badge/Hardware-Raspberry%20Pi-C51A4A?style=flat-square&logo=raspberry-pi)](./docs/setup.md)
[![Integration](https://img.shields.io/badge/Home%20Assistant-Ready-41BDF5?style=flat-square&logo=home-assistant)](./docs/setup.md)
[![Protocol](https://img.shields.io/badge/Protocol-MQTT%20%7C%20GRBL-orange?style=flat-square)](#)

> LaserAirCam is an all-in-one control node designed to make your laser setup cleaner, safer, and synchronized. It combines HD streaming, robust wireless serial, and automated hardware feedback.

---

### 🛠️ Key Features

| 📷 Vision & UI | 🔌 Connectivity & Control | 💨 Automation & Body |
| :--- | :--- | :--- |
| 🖼️ **Smart Stream:** Live MJPEG (`/stream`), snapshots (`/snapshot`), and **StreamHD** (`/streamhd`) for timed high-res captures. | 📶 **Stable Wi-Fi Link:** Transparent serial via `ser2net` & Virtual COM. Monitors GRBL traffic end-to-end for total stability. | 🌬️ **AirAssist:** 24V PWM control. Automatic mode (laser-power based) with manual override via UI or Home Assistant. |
| 💻 **WebUI & API:** Full browser dashboard for laser status, LEDs, and system. Fast API endpoints for custom automation. | 🔁 **Serial Gateway:** Intercepts traffic; if LightBurn is active, manual commands are safely queued and sent when possible. | 🌈 **RGB Status:** Addressable LED profiles: `idle`, `running`, `engraving`, `hold/pause`, `error`, and `door` alerts. |
| 🏠 **MQTT + HA:** Native bridge with auto-discovery. Exposes camera, status, and control entities for smart workflows. | 📡 **Remote Ready:** Designed for reliable long-range control, eliminating unstable and messy USB cable runs. | 📦 **Hardware:** 3x physical buttons for local interaction + custom 3D-printed case for Atomstack A1 & similar. |

---

### 🏁 Quick Start
1. Flash your Raspberry Pi and follow the detailed guide in [**setup.md**](./docs/setup.md).
2. Configure your Virtual COM port on PC and point LightBurn to the device IP.
3. Enjoy a wireless, automated, and visually interactive laser engraving experience.

**🖥️ Hardware Requirements:** [See Hardware requirements](./docs/hwreq.md)

[**📚 Full Setup Guide**](./docs/setup.md) | [**🐞 Report Issue**](../../issues) | [**💡 Suggest Feature**](../../discussions)



---


## 🖼️ Preview


<table>
	<tr>
		<td align="center">
			<img src="images/capture.png" width="150" alt="Capture Preview"><br>
			<b>Capture</b><br>
			Camera capture snapshot and StreamHD.
		</td>
		<td align="center">
			<img src="images/customgcode.png" width="150" alt="Custom GCode Preview"><br>
			<b>Custom GCode</b><br>
			Send custom GCode commands or manual moves.
		</td>
		<td align="center">
			<img src="images/v4l2camera.png" width="150" alt="V4L2 Camera Preview"><br>
			<b>V4L2 Camera</b><br>
			Camera device and V4L2 controls settings.
		</td>
	</tr>
	<tr>
		<td align="center">
			<img src="images/lasermonitor.png" width="150" alt="Laser Monitor Preview"><br>
			<b>Laser Monitor</b><br>
			Laser parameters and LED notifications.
		</td>
		<td align="center">
			<img src="images/ledmgmnt.png" width="150" alt="LED Management Preview"><br>
			<b>LED Management</b><br>
			LED color and effect controls.
		</td>
		<td align="center">
			<img src="images/main.png" width="150" alt="Main Dashboard Preview"><br>
			<b>Main Dashboard</b><br>
			Main control and status overview.
		</td>
	</tr>
	<tr>
		<td align="center">
			<img src="images/stream.png" width="150" alt="Stream Preview"><br>
			<b>Stream</b><br>
			Stream settings and live video.
		</td>
		<td align="center">
			<img src="images/fullsizescreen.png" width="150" alt="Full Size Screen Preview"><br>
			<b>Full Size Screen</b><br>
			Full UI.
		</td>
		<td></td>
	</tr>
</table>


