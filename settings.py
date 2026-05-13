#Centralized settings for LaserCam.

import os
import board
import neopixel

# -----------------------------------------------------------------------------
# 1- Settings (device/runtime specific) - Hardcoded
# -----------------------------------------------------------------------------
#LEDS
PIXEL_PIN = board.D18 # The GPIO pin connected to the pixels (18 uses PWM!).
NUM_PIXELS = 24 # Number of LED pixels.
ORDER = neopixel.GRB # The order of the pixel colors - RGB or GRB. Some NeoPixels have red and green reversed!
STARTUP_SHUTDOWN_BRIGHTNESS = 0.90 #animation brightness for startup/shutdown LED sequence
#BUTTONS
GPIO_LED_BUTTON = 17 #physical button 1, connect to GND
GPIO_POWER_BUTTON = 27 #physical button 2, connect to GND
GPIO_MODE_BUTTON = 22 #physical button 3, connect to GND
CLICK_WINDOW_S = 0.65 #time window for counting button clicks (for triggering different actions)
DEBOUNCE_S = 0.05 #debounce time for button presses (for cpu usage)
FRAME_DELAY_S = 0.05 #delay between frames (for cpu usage)
POLL_INTERVAL_S = 0.025 #interval for polling button states (for cpu usage)
#AIR ASSIST
AIR_ASSIST_GPIO_PWM_PIN = 23 #GPIO pin for air-assist PWM (hardware PWM capable: 12, 13, 18, 19)
AIR_ASSIST_PWM_FREQ_HZ = 1000 #PWM frequency in Hz
AIR_ASSIST_DEFAULT_SPEED = 100 #default duty cycle (0-100 %)
LASER_MAXPOWER = 1000 #max S value in GCODE (GRBL $30, default 1000)
#CAMERA MIN/MAXSETTINGS
CAM_MIN_WIDTH = 32
CAM_MIN_HEIGHT = 32
CAM_MAX_WIDTH = 3280
CAM_MAX_HEIGHT = 2464
CAM_STEP = 2

# -----------------------------------------------------------------------------
# (Optional) MQTT/Home Assistant settings (edit these values directly)
# -----------------------------------------------------------------------------
MQTT_ENABLE = False #to be compiled
MQTT_HOST = "192.168.50.2" #to be compiled
MQTT_PORT = 1883 #to be compiled
HA_CAMERA_FPS = 0.5
MQTT_IMAGE_ENABLED = False
MQTT_KEEPALIVE = 30 
MQTT_USERNAME = "MQTTUsername" #to be compiled
MQTT_PASSWORD = "MQTTPassword" #to be compiled
MQTT_CLIENT_ID = ""  # empty = auto-generated
MQTT_BASE_TOPIC = "lasercam"
HA_DISCOVERY_PREFIX = "homeassistant"
DEVICE_NAME = "LaserCam"
DEVICE_ID = ""  # empty = auto-generated from hostname
PUBLIC_HOST = ""  # empty = auto-detect
PUBLIC_BASE_URL = ""  # empty = auto from PUBLIC_HOST + WEB_PORT

# -----------------------------------------------------------------------------
# (VERY Optional) Services and Web settings (edit these values directly)
# -----------------------------------------------------------------------------
#WEB UI
WEB_HOST = "0.0.0.0" #host for the web UI
WEB_PORT = 80 #port for the web UI
#Pi SETTINGS
CAM_DEVICE = "/dev/video0" #video device for the camera (check with v4l2-ctl --list-devices)
SYSTEMD_SERVICE_PATH = "/etc/systemd/system/camerainit.service" #path for the systemd service file (for camera initialization on boot)
SYSTEM_STATS_CACHE_TTL_S = 1.0
#STREAMING SETTINGS
USTREAMER_LISTEN_HOST = "0.0.0.0" #host for ustreamer to listen on
USTREAMER_CONNECT_HOST = "127.0.0.1" #host for ustreamer to connect to (the actual camera stream)
USTREAMER_HOST = "127.0.0.1" #host for clients to connect to for the ustreamer stream (can be different from listen host if behind a reverse proxy)
USTREAMER_PORT = 8080 #port for ustreamer stream

# -----------------------------------------------------------------------------
# Settings below are mostly defaults that can be overridden by the UI or Home Assistant or environment variables. Edit with caution.
# -----------------------------------------------------------------------------


BRIGHTNESS = 0.60
DEFAULT_STREAM_RESOLUTION = "1280x960"
DEFAULT_SCREENSHOT_RESOLUTION = "3280x2464"
DEFAULT_STREAM_FPS = 20 #ustreamer 
DEFAULT_STREAMHD_INTERVAL_S = 4 #streamed hires images
FPS_PRESETS = [5, 10, 15, 20, 24, 25, 30]
STREAMHD_INTERVAL_PRESETS = [1, 2, 3, 4, 5, 8, 10]
RESOLUTION_PRESETS = [
    "640x480",
    "800x600",
    "1024x768",
    "1280x720",
    "1280x960",
    "1600x1200",
    "1920x1080",
    "1920x1440",
    "2592x1944",
    "3280x2464",
]

# Camera control keys
V4L2_CTRL_HORIZONTAL_FLIP = "horizontal_flip"
V4L2_CTRL_VERTICAL_FLIP = "vertical_flip"
V4L2_CTRL_COMPRESSION_QUALITY = "compression_quality"
V4L2_CTRL_BRIGHTNESS = "brightness"
V4L2_CTRL_CONTRAST = "contrast"
V4L2_CTRL_SATURATION = "saturation"
V4L2_CTRL_SHARPNESS = "sharpness"
V4L2_CTRL_POWER_LINE_FREQUENCY = "power_line_frequency"
V4L2_CTRL_AUTO_EXPOSURE = "auto_exposure"
V4L2_CTRL_EXPOSURE_TIME_ABSOLUTE = "exposure_time_absolute"
V4L2_CTRL_EXPOSURE_DYNAMIC_FRAMERATE = "exposure_dynamic_framerate"
V4L2_CTRL_ROTATE = "rotate"
V4L2_CTRL_AUTO_EXPOSURE_BIAS = "auto_exposure_bias"
V4L2_CTRL_WHITE_BALANCE_AUTO_PRESET = "white_balance_auto_preset"
V4L2_CTRL_ISO_SENSITIVITY_AUTO = "iso_sensitivity_auto"
V4L2_CTRL_ISO_SENSITIVITY = "iso_sensitivity"
V4L2_CTRL_EXPOSURE_METERING_MODE = "exposure_metering_mode"
V4L2_CTRL_SCENE_MODE = "scene_mode"

# Camera control defaults
DEFAULT_HORIZONTAL_FLIP = 1
DEFAULT_VERTICAL_FLIP = 1
DEFAULT_COMPRESSION_QUALITY = 90
DEFAULT_BRIGHTNESS = 50
DEFAULT_CONTRAST = 0
DEFAULT_SATURATION = 0
DEFAULT_SHARPNESS = 0
DEFAULT_POWER_LINE_FREQUENCY = 1
DEFAULT_AUTO_EXPOSURE = 0
DEFAULT_EXPOSURE_TIME_ABSOLUTE = 1000
DEFAULT_EXPOSURE_DYNAMIC_FRAMERATE = 0
DEFAULT_ROTATE = 0
DEFAULT_AUTO_EXPOSURE_BIAS = 12
DEFAULT_WHITE_BALANCE_AUTO_PRESET = 1
DEFAULT_ISO_SENSITIVITY_AUTO = 1
DEFAULT_ISO_SENSITIVITY = 0
DEFAULT_EXPOSURE_METERING_MODE = 0
DEFAULT_SCENE_MODE = 0

SERIAL_PROXY_LISTEN_HOST = "0.0.0.0"
SERIAL_PROXY_LISTEN_PORT = 4001
SERIAL_PROXY_TARGET_HOST = "127.0.0.1"
SERIAL_PROXY_TARGET_PORT = 2000

APP_DEFAULTS = {
    "laserbeam_nominal_maxpower": 1000,
    "airassist_speed": AIR_ASSIST_DEFAULT_SPEED,
    "airassist_auto_range_min": 0,
    "airassist_auto_range_max": 100,
    "airassist_auto_min_pwm": 0,
    "airassist_listen_events": 0,
    "laser_led_error_auto_reset_10s": 1,
    "buttons_reset_mode_opening_door": 0,
    "led_on_boot": 1,
    "led_default_brightness": BRIGHTNESS,
    "led_startup_shutdown_brightness": STARTUP_SHUTDOWN_BRIGHTNESS,
    "led_startup_effect": "strobe",
    "led_startup_color_mode": "laser_green",
    "led_startup_preset": "none",
    "led_shutdown_effect": "strobe",
    "led_shutdown_color_mode": "ruby_red",
    "led_shutdown_preset": "none",
    "serial_proxy_enabled": 1,
    "passthrough_extend_on_realtime": 0,
    "laser_move_step_mm": 20.0,
    "laser_move_feed_mm_sec": 10.0,
    "laser_custom_pos_x_mm": 0.0,
    "laser_custom_pos_y_mm": 110.0,
    "laser_custom_pos_z_mm": 0.0,
    "laser_custom_pos_use_g0": 0,
    "serial_proxy_listen_host": SERIAL_PROXY_LISTEN_HOST,
    "serial_proxy_listen_port": SERIAL_PROXY_LISTEN_PORT,
    "serial_proxy_target_host": SERIAL_PROXY_TARGET_HOST,
    "serial_proxy_target_port": SERIAL_PROXY_TARGET_PORT,
    "laser_led_sync_enabled": 1,
    "laser_led_idle_effect": "static",
    "laser_led_idle_color_mode": "cool_white",
    "laser_led_running_effect": "pulse",
    "laser_led_running_color_mode": "laser_green",
    "laser_led_hold_effect": "breathe",
    "laser_led_hold_color_mode": "amber_boost",
    "laser_led_door_effect": "strobe",
    "laser_led_door_color_mode": "ruby_red",
    "laser_led_door_light_on_opening": 1,
    "laser_led_error_effect": "strobe",
    "laser_led_error_color_mode": "ruby_red",
    "laser_led_engrave_complete_effect": "twinkle",
    "laser_led_engrave_complete_color_mode": "cool_white",
    "mode_button_profiles": {
        "1": {
            "entry_mode": "brightness",
            "led_effect": "static",
            "led_color_mode": "cool_white",
            "led_single_click_action": "brightness_plus",
            "power_single_click_action": "brightness_minus",
        },
        "2": {
            "entry_mode": "move_x",
            "led_effect": "breathe",
            "led_color_mode": "warm_white",
            "led_single_click_action": "move_left",
            "power_single_click_action": "move_right",
        },
        "3": {
            "entry_mode": "move_y",
            "led_effect": "breathe",
            "led_color_mode": "laser_green",
            "led_single_click_action": "move_left",
            "power_single_click_action": "move_right",
        },
        "4": {
            "entry_mode": "select_preset",
            "led_effect": "strobe",
            "led_color_mode": "laser_green",
            "led_single_click_action": "previous_preset",
            "power_single_click_action": "next_preset",
        },
    },
    "button_static_actions": {
        "led_double_press": "light_toggle",
        "led_triple_press": "clear_status",
        "power_double_press": "reboot",
        "power_triple_press": "shutdown",
    },
}


# -----------------------------------------------------------------------------
# Paths
# -----------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVED_SETTINGS_PATH = os.path.join(BASE_DIR, "saved_settings.json")


