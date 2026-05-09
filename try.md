# 🛰️ LaserAirCam
**The ultimate Raspberry Pi companion for laser engravers.** *Wi-Fi Camera • Serial Gateway • AirAssist Control • RGB Status Feedback*

[![Hardware](https://img.shields.io/badge/Hardware-Raspberry%20Pi-C51A4A?style=flat-square&logo=raspberry-pi)](./setup.md)
[![Integration](https://img.shields.io/badge/Home%20Assistant-Ready-41BDF5?style=flat-square&logo=home-assistant)](./setup.md)
[![Protocol](https://img.shields.io/badge/Protocol-MQTT%20%7C%20GRBL-orange?style=flat-square)](#)

LaserAirCam centralizza lo streaming video HD, il ponte seriale Wi-Fi e l'automazione dell'AirAssist in un unico dispositivo compatto, rendendo il tuo setup laser più pulito, sicuro e smart.

---

### 🛠️ Key Features

| 📷 Vision & UI | 🔌 Connectivity & Control |
| :--- | :--- |
| **Smart Streaming:** MJPEG standard, snapshots HD e modalità **StreamHD** (high-res a intervalli). | **Wi-Fi Serial Bridge:** Link stabile via `ser2net`. Gestione intelligente delle code comandi durante il lavoro. |
| **Web Dashboard:** Controllo totale da browser per camera, LED, stato laser e configurazioni API. | **AirAssist Pro:** Controllo PWM 24V automatico (basato sulla potenza laser) o manuale via UI/HA. |
| **RGB Feedback:** Stato laser visivo (`idle`, `running`, `error`) tramite LED indirizzabili. | **Home Assistant:** Integrazione MQTT nativa con auto-discovery di sensori e controlli. |

### 📦 Hardware & Design
* 🔘 **Physical Buttons:** 3 tasti hardware per comandi rapidi a bordo macchina.
* 🧩 **3D Case:** Enclosure dedicata per Atomstack A1 e simili, con cablaggio integrato.

---

### 🚀 Quick Start
1. Prepara la tua Raspberry Pi con l'immagine suggerita.
2. Segui i passaggi dettagliati in [**setup.md**](./setup.md).
3. Connetti LightBurn tramite l'IP della camera e la porta seriale virtuale.

[**📚 Manuale Installazione**](./setup.md) | [**🐞 Segnala Bug**](../../issues) | [**💡 Proponi Feature**](../../issues)
