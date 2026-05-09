## 1. Operating System Setup (DietPi)

1. Download and flash DietPi to the SD card.
2. Before inserting the SD into the Raspberry Pi, configure:
   - `dietpi.txt`
   - `config.txt`
   - `dietpi-wifi.txt`
   to set up WiFi, username, and password.
3. Boot the Raspberry Pi and access it via SSH (e.g., with Putty). First login as root to complete the initial setup.

---

*Note: If you have low disk space, execute step 5 as first, as it will temporarily occupy about 230 MB*

## 2. Raspberry Pi Camera Configuration

### 2.1 Enable the Camera

Run `sudo dietpi-config`, go to **Display Options**, and enable:

- `8 : RPi Camera` → **[On]**
- `18 : RPi Codecs` → **[On]** *(V4L2 hardware video codecs)*

Then edit the configuration file:

```sh
sudo nano /boot/firmware/config.txt
```

Add or update the following lines:

```ini
#-------RPi camera module-------
camera_auto_detect=0
dtoverlay=vc4-fkms-v3d
start_x=1
gpu_mem_1024=128
gpu_mem_512=128
gpu_mem_256=128
gpu_mem=128
disable_camera_led=0
#----------------------
```

Save and exit (`CTRL+X`, `Y`, `Enter`).

### 2.2 Install Video4Linux Utilities

```sh
sudo apt update
sudo apt install v4l-utils -y
echo "bcm2835-v4l2" | sudo tee /etc/modules-load.d/bcm2835-v4l2.conf
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

Start uStreamer with MJPEG stream:

```sh
sudo ustreamer --device=/dev/video0 --host=0.0.0.0 --port=8080 --format=MJPEG --resolution=1280x960 --desired-fps=20
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

Restart the ser2net service to apply the new configuration:

```sh
sudo systemctl restart ser2net
```

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

The following modules are also required for LED, MQTT, and GPIO control:

```sh
sudo apt install python3-rpi.gpio python3-paho-mqtt -y
```

#### ⚙️ Build dependencies for rpi_ws281x

Unfortunately to install `rpi_ws281x`, you need a C compiler and Python development headers, as this library contains native code that must be compiled on your system. Install them with:

```sh
sudo apt install build-essential python3-dev -y
```

Now you can install the required Python packages:

```sh
pip3 install rpi_ws281x adafruit-circuitpython-neopixel --break-system-packages
```

If you use a virtual environment, install them with pip inside the venv (to avoid --break-system-packages).

**Optional:** After successful installation, you can remove the build tools to save space:

```sh
sudo apt remove --purge build-essential python3-dev -y
sudo apt autoremove --purge -y
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
