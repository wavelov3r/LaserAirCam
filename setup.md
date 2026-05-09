## Hardware Requirements

- **Raspberry Pi Zero 2W** (or higher, if using other printed cases) + at least 8GB SD card
- **Raspberry Pi Camera v1.2 5MPx 75° FOV** (with IR filter, 20cm flat cable recommended)
  *Note: Other cameras may overload the system and require different libraries (e.g., libcamera)*
- **WS2812 Addressable LED Strip** (e.g., 11.5mm wide)
- **2 or 3 lever micro switches** (for buttons)
- **LR784 MOSFET module** (only if you want to add air assist)
- **24V DC air assist pump** (e.g., Lasertree)
- **Tools to cut the engraver top** (grinder, dremel, etc.)
- **3D printer** (or printed parts)
- **Wires, soldering iron, and patience!**

---

## 1. Operating System Setup (DietPi)

1. Download and flash DietPi to the SD card.
2. Before inserting the SD into the Raspberry Pi, configure:
   - `dietpi.txt`
   - `config.txt`
   - `dietpi-wifi.txt`
   to set up WiFi, username, and password.
3. Boot the Raspberry Pi and access it via SSH (e.g., with Putty). First login as root to complete the initial setup.

---

## 2. Raspberry Pi Camera Configuration

### 2.1 Enable the Camera

Edit the configuration file:

```sh
sudo nano /boot/firmware/config.txt
```

Add or update the following lines:

```ini
camera_auto_detect=0
dtoverlay=vc4-fkms-v3d
start_x=1
gpu_mem_1024=128
gpu_mem_512=128
gpu_mem_256=128
gpu_mem=128
disable_camera_led=0
```

Save and exit (`CTRL+X`, `Y`, `Enter`).

### 2.2 Install Video4Linux Utilities

```sh
sudo apt update
sudo apt install v4l-utils -y
sudo modprobe bcm2835-v4l2
```

Reboot the Raspberry Pi.

### 2.3 Check Camera Detection

```sh
sudo ls /dev/video*
sudo v4l2-ctl --list-devices
```
Ensure the camera is detected correctly.

*Note: For other cameras (e.g., HQ, USB), you may need to use `libcamera-vid`.*

---

## 3. Video Streaming with uStreamer

Install uStreamer:

```sh
sudo apt install ustreamer -y
```

Test the stream at:

```
http://RASPI_IP:8080
```

---

## 4. Serial-USB Gateway over WiFi with Ser2Net

### 4.1 Install Ser2Net

```sh
sudo apt install ser2net -y
```

### 4.2 Identify Serial-USB Port

Connect the engraver and check the serial port:

```sh
ls /dev/serial/by-id/
# Example output: usb-1a86_USB_Serial-if00-port0
```

### 4.3 Configure Ser2Net

Remove the existing config file:

```sh
sudo rm /etc/ser2net.yaml
```

Create a new config file:

```sh
sudo nano /etc/ser2net.yaml
```

Configuration (check the serial connector, leave untouched the 2000 port as it is used by the python script, or change its config later):

```yaml
%YAML 1.1
---
# Config ser2net
define: &banner \r\nser2net port \p device \d [\B] (DietPi)\r\n\r\n
connection: &usb0
  accepter: tcp,2000
  enable: on
  options:
    banner: *banner
    kickolduser: true
    telnet-brk-on-sync: true
  connector: serialdev,
    /dev/serial/by-id/usb-1a86_USB_Serial-if00-port0,
    115200n81,local
```

Save and exit.

### 4.4 Connect from Remote PC

Download and install on your PC:
[HW Virtual Serial Port](https://www.hw-group.com/software/hw-vsp3-virtual-serial-port)

Configure the COM port, enter the Raspberry Pi IP and port (default 2000, with Python gateway it will be 4001). You can set it to auto-start in the system tray.

*Note: You do not need virtualHere. The ATOMSTACK USB port is a serial port masked as USB; the serial protocol is simpler and more tolerant over LAN/WiFi.*

---

## 5. Software Dependencies Installation

### 5.1 Python 3 and pip

```sh
sudo apt install python3 python3-pip -y
```

### 5.2 Required Python Modules

Install one at a time to avoid overloading the Raspberry Pi (especially with 4GB SD cards):

```sh
sudo apt install python3-paho-mqtt -y
sudo apt install python3-opencv -y
sudo apt install python3-pil -y
```

### 5.3 Additional Required Python Modules

The following modules are also required for LED and GPIO control:

```sh
sudo apt install python3-rpi.gpio -y
sudo pip3 install rpi_ws281x adafruit-circuitpython-neopixel
```

- `python3-rpi.gpio` provides the RPi.GPIO library for GPIO pin control.
- `rpi_ws281x` and `adafruit-circuitpython-neopixel` are required for WS2812 (NeoPixel) LED control.

If you use a virtual environment, install them with pip inside the venv:

```sh
pip install rpi_ws281x adafruit-circuitpython-neopixel RPi.GPIO
```

---


## 6. LaserAirCam Setup

1. Create a project directory and clone the repository:

```sh
sudo apt install git
mkdir laseraircam && cd laseraircam
git clone https://github.com/wavelov3r/LaserAirCam.git
cd LaserAirCam
```

2. (After installing dependencies) Create and enable a systemd service to run `laseraircam.py` from the current path (check the path and the user):

Create the service file (as root):

```sh
sudo nano /etc/systemd/system/laseraircam.service
```

Paste the following (edit paths and user if needed):

```
[Unit]
Description=LaserAirCam Python Service
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/dietpi/laseraircam
ExecStart=/usr/bin/python3 laseraircam.py
Restart=on-failure
User=dietpi

[Install]
WantedBy=multi-user.target
```

configure the LaserAirCam App:

```sh
sudo nano /home/dietpi/laseraircam/config.py
```
check for errors in the log: 

```sh
sudo python3 /home/dietpi/laseraircam/laseraircam.py
```

if works,
Enable and start the service:

```sh
sudo systemctl daemon-reload
sudo systemctl enable laseraircam.service
sudo systemctl start laseraircam.service
sudo systemctl status laseraircam.service
```

---

You can now connect to http://raspberry_ip for the web interface, to the 4001 port to communicate with the laser, and to http://raspberry_ip/stream, streamhd, or snapshot.


## Final Notes

- For other cameras or hardware configurations, refer to the official Raspberry Pi documentation.
- If you have space or performance issues, consider a larger SD card or a more powerful Raspberry Pi.
- For questions or suggestions, open an issue on GitHub!
