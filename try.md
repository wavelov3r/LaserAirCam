# 🛰️ LaserAirCam
**Smart Raspberry Pi companion for laser engravers**  
*Wi-Fi Camera • Serial Gateway • AirAssist Control • Visual Feedback*

[![Hardware](https://img.shields.io/badge/Hardware-Raspberry%20Pi-C51A4A?style=flat-square&logo=raspberry-pi)](./setup.md)
[![Integration](https://img.shields.io/badge/Home%20Assistant-Ready-41BDF5?style=flat-square&logo=home-assistant)](./setup.md)
[![Protocol](https://img.shields.io/badge/Protocol-MQTT%20%7C%20GRBL-orange?style=flat-square)](#)

> LaserAirCam makes your laser setup cleaner, safer, and easier to control. It synchronizes camera streaming, Wi-Fi serial communication, and automated hardware control into one reliable node.

---

### 🛠️ Key Features

| 📷 Camera & UI | 🔌 Connectivity | 💨 Hardware & Automation |
| :--- | :--- | :--- |
| **MJPEG Stream:** Live feed via `/stream`. | **Stable Wi-Fi Link:** `ser2net` + Virtual COM. Persistent & transparent TCP link. | **AirAssist:** 24V PWM control. Auto mode (laser-active) or manual override. |
| **StreamHD:** High-res captures every X seconds delivered as MJPEG via `/streamhd`. | **Smart Gateway:** Intercepts GRBL traffic. Queues manual commands if LightBurn is busy. | **RGB Status:** Addressable LEDs with profiles: `idle`, `run`, `pause`, `error`, `door`. |
| **WebUI & API:** Dashboard for laser, LEDs, and system. Fast API for external tools. | **MQTT + HA:** Native discovery. Exposes camera, status, and control entities. | **Physical I/O:** 3 hardware buttons for local control & 3D-printed case for Atomstack A1. |

---

### 🏁 Quick Start
1. Flash your Pi and follow the [**setup.md**](./setup.md) guide.
2. Configure your Virtual COM port and point LightBurn to the device IP.

[**📚 Full Setup Guide**](./setup.md) | [**🐞 Report Issue**](../../issues) | [**💡 Suggest Feature**](../../issues)
