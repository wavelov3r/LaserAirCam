# 🛠️ Setup Guide: LaserAirCam

Follow these steps to transform your Raspberry Pi into a professional laser control node.

---

### 📦 Hardware Requirements

| Component | Specification / Notes |
| :--- | :--- |
| **🧠 Compute** | **Raspberry Pi Zero 2W** (or higher) + 8GB+ SD Card. |
| **📷 Camera** | **RPi Camera v1.2 5MPx 75° FOV** (IR filter, 20cm cable). *Note: libcamera required for other models.* |
| **🌈 Feedback** | **WS2812 Addressable LED Strip** (approx. 11.5mm wide). |
| **💨 AirAssist** | **24V Pump** (e.g. Lasertree) + **LR784 MOSFET** module. |
| **🔘 Controls** | **2-3 Lever Micro Switches** + Wires & Soldering iron. |
| **🏗️ Body** | **3D Printer** for the enclosure + Dremel/Grinder to cut engraver top. |

---

### 1️⃣ OS & Camera Setup (DietPi)

1. **Flash DietPi:** Configure `dietpi.txt`, `config.txt`, and `dietpi-wifi.txt` before booting.
2. **First Boot:** SSH via root. Run `sudo apt update`.
3. **Enable Camera:** `sudo nano /boot/firmware/config.txt` and ensure these lines exist:
   ```ini
   camera_auto_detect=1
   dtoverlay=vc4-kms-v3d
   start_x=1
   gpu_mem_1024=128 | gpu_mem_512=128 | gpu_mem_256=128 | gpu_mem=128
   disable_camera_led=0
