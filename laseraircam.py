import os
import json
import http.client
import socket
import struct
import subprocess
import threading
import time
import zlib
from http.server import BaseHTTPRequestHandler
from http.server import ThreadingHTTPServer
from urllib.parse import parse_qs
from urllib.parse import urlparse

import board
import neopixel
import RPi.GPIO as GPIO

from modules.buttons import ButtonRuntimeManager
from modules.leds import LedController
from modules.airassist import AirAssistController
from modules.serial_gateway import LaserMonitorState
from modules.serial_gateway import SerialTrafficProxy

from modules.mqtt import create_homeassistant_bridge
from modules.webui import camera_controls_html
from modules.webui import page_html
from settings import AIR_ASSIST_GPIO_PWM_PIN
from settings import AIR_ASSIST_PWM_FREQ_HZ
from settings import AIR_ASSIST_DEFAULT_SPEED
from settings import LASER_MAXPOWER
from settings import APP_DEFAULTS
from settings import BRIGHTNESS
from settings import CAM_DEVICE
from settings import CAM_MAX_HEIGHT
from settings import CAM_MAX_WIDTH
from settings import CAM_MIN_HEIGHT
from settings import CAM_MIN_WIDTH
from settings import CAM_STEP
from settings import CLICK_WINDOW_S
from settings import DEBOUNCE_S
from settings import DEFAULT_AUTO_EXPOSURE
from settings import DEFAULT_AUTO_EXPOSURE_BIAS
from settings import DEFAULT_BRIGHTNESS
from settings import DEFAULT_COMPRESSION_QUALITY
from settings import DEFAULT_CONTRAST
from settings import DEFAULT_EXPOSURE_DYNAMIC_FRAMERATE
from settings import DEFAULT_EXPOSURE_METERING_MODE
from settings import DEFAULT_EXPOSURE_TIME_ABSOLUTE
from settings import DEFAULT_HORIZONTAL_FLIP
from settings import DEFAULT_ISO_SENSITIVITY
from settings import DEFAULT_ISO_SENSITIVITY_AUTO
from settings import DEFAULT_POWER_LINE_FREQUENCY
from settings import DEFAULT_ROTATE
from settings import DEFAULT_SATURATION
from settings import DEFAULT_SCENE_MODE
from settings import DEFAULT_SCREENSHOT_RESOLUTION
from settings import DEFAULT_SHARPNESS
from settings import DEFAULT_STREAM_FPS
from settings import DEFAULT_STREAMHD_INTERVAL_S
from settings import DEFAULT_STREAM_RESOLUTION
from settings import DEFAULT_VERTICAL_FLIP
from settings import DEFAULT_WHITE_BALANCE_AUTO_PRESET
from settings import FPS_PRESETS
from settings import FRAME_DELAY_S
from settings import GPIO_LED_BUTTON
from settings import GPIO_MODE_BUTTON
from settings import GPIO_POWER_BUTTON
from settings import MQTT_IMAGE_ENABLED
from settings import NUM_PIXELS
from settings import ORDER
from settings import PIXEL_PIN
from settings import POLL_INTERVAL_S
from settings import RESOLUTION_PRESETS
from settings import SERIAL_PROXY_LISTEN_HOST
from settings import SERIAL_PROXY_LISTEN_PORT
from settings import SERIAL_PROXY_TARGET_HOST
from settings import SERIAL_PROXY_TARGET_PORT
from settings import STARTUP_SHUTDOWN_BRIGHTNESS
from settings import STREAMHD_INTERVAL_PRESETS
from settings import SYSTEMD_SERVICE_PATH
from settings import SYSTEM_STATS_CACHE_TTL_S
from settings import USTREAMER_CONNECT_HOST
from settings import USTREAMER_HOST
from settings import USTREAMER_LISTEN_HOST
from settings import USTREAMER_PORT
from settings import V4L2_CTRL_AUTO_EXPOSURE
from settings import V4L2_CTRL_AUTO_EXPOSURE_BIAS
from settings import V4L2_CTRL_BRIGHTNESS
from settings import V4L2_CTRL_COMPRESSION_QUALITY
from settings import V4L2_CTRL_CONTRAST
from settings import V4L2_CTRL_EXPOSURE_DYNAMIC_FRAMERATE
from settings import V4L2_CTRL_EXPOSURE_METERING_MODE
from settings import V4L2_CTRL_EXPOSURE_TIME_ABSOLUTE
from settings import V4L2_CTRL_HORIZONTAL_FLIP
from settings import V4L2_CTRL_ISO_SENSITIVITY
from settings import V4L2_CTRL_ISO_SENSITIVITY_AUTO
from settings import V4L2_CTRL_POWER_LINE_FREQUENCY
from settings import V4L2_CTRL_ROTATE
from settings import V4L2_CTRL_SATURATION
from settings import V4L2_CTRL_SCENE_MODE
from settings import V4L2_CTRL_SHARPNESS
from settings import V4L2_CTRL_VERTICAL_FLIP
from settings import V4L2_CTRL_WHITE_BALANCE_AUTO_PRESET
from settings import WEB_HOST
from settings import WEB_PORT
from settings import SAVED_SETTINGS_PATH
APP_VERSION = "1.2"

_SYSTEM_STATS_LOCK = threading.Lock()
_SYSTEM_STATS_CACHE = {"ts": 0.0, "data": None}
_SETTINGS_CACHE_LOCK = threading.Lock()
_SETTINGS_CACHE = {}


def _default_mqtt_image_enabled():
	value = str(MQTT_IMAGE_ENABLED).strip().lower()
	return 1 if value in ("1", "true", "yes", "on") else 0


def _to_bool(value, default=False):
	if isinstance(value, bool):
		return value
	if isinstance(value, (int, float)):
		return int(value) != 0
	if value is None:
		return bool(default)
	text = str(value).strip().lower()
	if text in ("1", "true", "yes", "on"):
		return True
	if text in ("0", "false", "no", "off"):
		return False
	return bool(default)


def _read_json_file_cached(path):
	try:
		mtime_ns = os.stat(path).st_mtime_ns
	except OSError:
		mtime_ns = None
	with _SETTINGS_CACHE_LOCK:
		cached = _SETTINGS_CACHE.get(path)
		if cached is not None and cached.get("mtime_ns") == mtime_ns:
			return dict(cached.get("data", {}))
	data = {}
	if mtime_ns is not None:
		try:
			with open(path, "r", encoding="utf-8") as f:
				loaded = json.load(f)
				if isinstance(loaded, dict):
					data = loaded
		except Exception:
			data = {}
	with _SETTINGS_CACHE_LOCK:
		_SETTINGS_CACHE[path] = {"mtime_ns": mtime_ns, "data": dict(data)}
	return dict(data)


def _write_json_file_cached(path, payload):
	dir_name = os.path.dirname(path)
	if dir_name and not os.path.exists(dir_name):
		os.makedirs(dir_name, exist_ok=True)
	with open(path, "w", encoding="utf-8") as f:
		json.dump(payload, f)
	try:
		mtime_ns = os.stat(path).st_mtime_ns
	except OSError:
		mtime_ns = None
	with _SETTINGS_CACHE_LOCK:
		_SETTINGS_CACHE[path] = {"mtime_ns": mtime_ns, "data": dict(payload)}


def _load_saved_settings_root():
	if os.path.exists(SAVED_SETTINGS_PATH):
		loaded = _read_json_file_cached(SAVED_SETTINGS_PATH)
		if isinstance(loaded, dict):
			return dict(loaded)
	return {}


def _save_saved_settings_root(root_payload):
	data = dict(root_payload) if isinstance(root_payload, dict) else {}
	_write_json_file_cached(SAVED_SETTINGS_PATH, data)


def load_app_settings():
	root = _load_saved_settings_root()
	data = root.get("app", {}) if isinstance(root.get("app", {}), dict) else {}
	return load_app_settings_from_source(dict(APP_DEFAULTS, **(data if isinstance(data, dict) else {})))


def save_app_settings(settings):
	payload = load_app_settings()
	if isinstance(settings, dict):
		payload.update(settings)
	payload = load_app_settings_dict(payload)
	root = _load_saved_settings_root()
	root["app"] = dict(payload)
	_save_saved_settings_root(root)


def load_app_settings_dict(source):
	base = dict(APP_DEFAULTS)
	if isinstance(source, dict):
		base.update(source)
	return load_app_settings_from_source(base)


def load_app_settings_from_source(settings):
	settings = dict(settings)
	settings["led_on_boot"] = 1 if _to_bool(settings.get("led_on_boot", 1), True) else 0
	try:
		default_brightness = float(settings.get("led_default_brightness", BRIGHTNESS))
	except Exception:
		default_brightness = BRIGHTNESS
	settings["led_default_brightness"] = round(max(0.0, min(1.0, default_brightness)), 2)
	try:
		startup_shutdown_brightness = float(settings.get("led_startup_shutdown_brightness", STARTUP_SHUTDOWN_BRIGHTNESS))
	except Exception:
		startup_shutdown_brightness = STARTUP_SHUTDOWN_BRIGHTNESS
	settings["led_startup_shutdown_brightness"] = round(max(0.0, min(1.0, startup_shutdown_brightness)), 2)
	settings["serial_proxy_enabled"] = 1 if _to_bool(settings.get("serial_proxy_enabled", 0), False) else 0
	settings["passthrough_extend_on_realtime"] = 1 if _to_bool(settings.get("passthrough_extend_on_realtime", 0), False) else 0
	settings["laser_led_sync_enabled"] = 1 if _to_bool(settings.get("laser_led_sync_enabled", 1), True) else 0
	settings["laser_led_error_auto_reset_10s"] = 1 if _to_bool(settings.get("laser_led_error_auto_reset_10s", 1), True) else 0
	settings["buttons_reset_mode_opening_door"] = 1 if _to_bool(settings.get("buttons_reset_mode_opening_door", 0), False) else 0
	settings["laser_led_door_light_on_opening"] = 1
	try:
		move_step_mm = float(settings.get("laser_move_step_mm", 20.0))
	except Exception:
		move_step_mm = 20.0
	settings["laser_move_step_mm"] = round(max(0.1, min(100.0, move_step_mm)), 2)
	try:
		move_feed_mm_sec = float(settings.get("laser_move_feed_mm_sec", 10.0))
	except Exception:
		move_feed_mm_sec = 10.0
	settings["laser_move_feed_mm_sec"] = round(max(0.2, min(80.0, move_feed_mm_sec)), 2)
	for key in ("laser_custom_pos_x_mm", "laser_custom_pos_y_mm", "laser_custom_pos_z_mm"):
		try:
			value = float(settings.get(key, 0.0))
		except Exception:
			value = 0.0
		settings[key] = round(max(-1000.0, min(1000.0, value)), 3)
	use_g0_raw = settings.get("laser_custom_pos_use_g0", 1)
	if isinstance(use_g0_raw, str):
		settings["laser_custom_pos_use_g0"] = 1 if use_g0_raw.strip().lower() in ("1", "true", "yes", "on") else 0
	else:
		settings["laser_custom_pos_use_g0"] = 1 if bool(use_g0_raw) else 0
	try:
		settings["serial_proxy_listen_port"] = max(1, min(65535, int(settings.get("serial_proxy_listen_port", SERIAL_PROXY_LISTEN_PORT))))
	except Exception:
		settings["serial_proxy_listen_port"] = SERIAL_PROXY_LISTEN_PORT
	try:
		settings["serial_proxy_target_port"] = max(1, min(65535, int(settings.get("serial_proxy_target_port", SERIAL_PROXY_TARGET_PORT))))
	except Exception:
		settings["serial_proxy_target_port"] = SERIAL_PROXY_TARGET_PORT
	settings["serial_proxy_listen_host"] = str(settings.get("serial_proxy_listen_host", SERIAL_PROXY_LISTEN_HOST) or SERIAL_PROXY_LISTEN_HOST).strip()
	settings["serial_proxy_target_host"] = str(settings.get("serial_proxy_target_host", SERIAL_PROXY_TARGET_HOST) or SERIAL_PROXY_TARGET_HOST).strip()
	try:
		settings["laserbeam_nominal_maxpower"] = max(1, min(20000, int(settings.get("laserbeam_nominal_maxpower", LASER_MAXPOWER))))
	except Exception:
		settings["laserbeam_nominal_maxpower"] = LASER_MAXPOWER
	try:
		settings["airassist_speed"] = max(0, min(100, int(settings.get("airassist_speed", AIR_ASSIST_DEFAULT_SPEED))))
	except Exception:
		settings["airassist_speed"] = AIR_ASSIST_DEFAULT_SPEED
	try:
		airassist_auto_range_min = max(0, min(99, int(settings.get("airassist_auto_range_min", 0))))
	except Exception:
		airassist_auto_range_min = 0
	try:
		airassist_auto_range_max = max(1, min(100, int(settings.get("airassist_auto_range_max", 100))))
	except Exception:
		airassist_auto_range_max = 100
	if airassist_auto_range_min >= airassist_auto_range_max:
		airassist_auto_range_max = min(100, airassist_auto_range_min + 1)
	settings["airassist_auto_range_min"] = airassist_auto_range_min
	settings["airassist_auto_range_max"] = airassist_auto_range_max
	try:
		auto_min_pwm = max(0, min(100, int(settings.get("airassist_auto_min_pwm", 0))))
	except Exception:
		auto_min_pwm = 0
	settings["airassist_auto_min_pwm"] = auto_min_pwm
	settings["airassist_listen_events"] = 1 if _to_bool(settings.get("airassist_listen_events", 0), False) else 0

	valid_effects = set(LedController.EFFECTS) if "LedController" in globals() else {
		"static", "breathe", "pulse", "strobe", "flash", "fire", "disco", "snake", "twinkle",
	}
	valid_color_modes = set(LedController.COLOR_MODES) if "LedController" in globals() else {
		"cool_white", "warm_white", "amber_boost", "sunset_orange", "laser_green", "ruby_red", "ice_cyan", "magenta_pink",
		"blue_intense", "blue_soft", "green_intense", "green_soft", "red_intense", "red_soft",
		"cyan_intense", "cyan_soft", "magenta_intense", "magenta_soft", "amber_intense", "amber_soft",
		"random_solid", "random_per_led", "custom_solid",
	}
	valid_presets = set(LedController.PRESETS) if "LedController" in globals() else {
		"none", "ocean_wave", "red_fire", "green_forest", "sunset_lava", "ice_plasma",
	}
	for key, fallback in (
		("laser_led_idle_effect", "static"),
		("laser_led_running_effect", "pulse"),
		("laser_led_hold_effect", "breathe"),
		("laser_led_door_effect", "strobe"),
		("laser_led_error_effect", "strobe"),
		("laser_led_engrave_complete_effect", "twinkle"),
	):
		value = str(settings.get(key, fallback) or fallback)
		settings[key] = value if value in valid_effects else fallback
	for key, fallback in (
		("laser_led_idle_color_mode", "cool_white"),
		("laser_led_running_color_mode", "laser_green"),
		("laser_led_hold_color_mode", "amber_boost"),
		("laser_led_door_color_mode", "ruby_red"),
		("laser_led_error_color_mode", "ruby_red"),
		("laser_led_engrave_complete_color_mode", "cool_white"),
	):
		value = str(settings.get(key, fallback) or fallback)
		settings[key] = value if value in valid_color_modes else fallback
	for key, fallback in (
		("led_startup_effect", "strobe"),
		("led_shutdown_effect", "strobe"),
	):
		value = str(settings.get(key, fallback) or fallback)
		settings[key] = value if value in valid_effects else fallback
	for key, fallback in (
		("led_startup_color_mode", "laser_green"),
		("led_shutdown_color_mode", "ruby_red"),
	):
		value = str(settings.get(key, fallback) or fallback)
		settings[key] = value if value in valid_color_modes else fallback
	for key in ("led_startup_preset", "led_shutdown_preset"):
		value = str(settings.get(key, "none") or "none")
		settings[key] = value if value in valid_presets else "none"

	valid_entry_modes = {
		"move_x", "move_y", "move_z", "brightness", "change_effect", "select_preset", "change_color",
	}
	valid_single_click_actions = {
		"move_up", "move_down", "move_left", "move_right", "move_forward", "move_backward",
		"next_preset", "previous_preset", "next_effect", "previous_effect", "next_color", "previous_color",
		"brightness_plus", "brightness_minus",
	}
	valid_static_actions = {
		"reboot", "shutdown", "clear_status", "light_toggle", "homing", "custom_position", "none",
	}

	default_mode_profiles = {
		"1": {
			"entry_mode": "move_x",
			"led_effect": "pulse",
			"led_color_mode": "laser_green",
			"led_single_click_action": "next_effect",
			"power_single_click_action": "next_color",
		},
		"2": {
			"entry_mode": "brightness",
			"led_effect": "breathe",
			"led_color_mode": "amber_boost",
			"led_single_click_action": "brightness_plus",
			"power_single_click_action": "brightness_minus",
		},
		"3": {
			"entry_mode": "change_effect",
			"led_effect": "twinkle",
			"led_color_mode": "ice_cyan",
			"led_single_click_action": "next_effect",
			"power_single_click_action": "previous_effect",
		},
		"4": {
			"entry_mode": "select_preset",
			"led_effect": "static",
			"led_color_mode": "cool_white",
			"led_single_click_action": "next_preset",
			"power_single_click_action": "previous_preset",
		},
	}
	mode_profiles = settings.get("mode_button_profiles", {})
	if not isinstance(mode_profiles, dict):
		mode_profiles = {}
	normalized_mode_profiles = {}
	for press_key in ("1", "2", "3", "4"):
		default_profile = dict(default_mode_profiles[press_key])
		raw_profile = mode_profiles.get(press_key, {})
		if not isinstance(raw_profile, dict):
			raw_profile = {}
		entry_mode = str(raw_profile.get("entry_mode", default_profile["entry_mode"]) or default_profile["entry_mode"])
		led_effect = str(raw_profile.get("led_effect", default_profile["led_effect"]) or default_profile["led_effect"])
		led_color_mode = str(raw_profile.get("led_color_mode", default_profile["led_color_mode"]) or default_profile["led_color_mode"])
		led_single_click_action = str(raw_profile.get("led_single_click_action", default_profile["led_single_click_action"]) or default_profile["led_single_click_action"])
		power_single_click_action = str(raw_profile.get("power_single_click_action", default_profile["power_single_click_action"]) or default_profile["power_single_click_action"])
		normalized_mode_profiles[press_key] = {
			"entry_mode": entry_mode if entry_mode in valid_entry_modes else default_profile["entry_mode"],
			"led_effect": led_effect if led_effect in valid_effects else default_profile["led_effect"],
			"led_color_mode": led_color_mode if led_color_mode in valid_color_modes else default_profile["led_color_mode"],
			"led_single_click_action": led_single_click_action if led_single_click_action in valid_single_click_actions else default_profile["led_single_click_action"],
			"power_single_click_action": power_single_click_action if power_single_click_action in valid_single_click_actions else default_profile["power_single_click_action"],
		}
	settings["mode_button_profiles"] = normalized_mode_profiles

	default_static_actions = {
		"led_double_press": "light_toggle",
		"led_triple_press": "clear_status",
		"power_double_press": "reboot",
		"power_triple_press": "shutdown",
	}
	raw_static_actions = settings.get("button_static_actions", {})
	if not isinstance(raw_static_actions, dict):
		raw_static_actions = {}
	normalized_static_actions = {}
	for action_key, fallback_action in default_static_actions.items():
		action_value = str(raw_static_actions.get(action_key, fallback_action) or fallback_action)
		normalized_static_actions[action_key] = action_value if action_value in valid_static_actions else fallback_action
	settings["button_static_actions"] = normalized_static_actions
	return settings

V4L2_MENU_POWER_LINE_FREQUENCY = {
	0: "Disabled",
	1: "50 Hz",
	2: "60 Hz",
	3: "Auto",
}
V4L2_MENU_AUTO_EXPOSURE = {
	0: "Auto Mode",
	1: "Manual Mode",
}
V4L2_MENU_WHITE_BALANCE_AUTO_PRESET = {
	0: "Manual",
	1: "Auto",
	2: "Incandescent",
	3: "Fluorescent",
	4: "Fluorescent H",
	5: "Horizon",
	6: "Daylight",
	7: "Flash",
	8: "Cloudy",
	9: "Shade",
	10: "Greyworld",
}
V4L2_MENU_ISO_SENSITIVITY_AUTO = {
	0: "Manual",
	1: "Auto",
}
V4L2_MENU_EXPOSURE_METERING_MODE = {
	0: "Average",
	1: "Center Weighted",
	2: "Spot",
	3: "Matrix",
}
V4L2_MENU_SCENE_MODE = {
	0: "None",
	8: "Night",
	11: "Sports",
}
V4L2_MENU_AUTO_EXPOSURE_BIAS = {i: str((i - 12) * 333) for i in range(0, 25)}
V4L2_MENU_ISO_SENSITIVITY = {
	0: "0",
	1: "100000",
	2: "200000",
	3: "400000",
	4: "800000",
}
V4L2_MENU_ROTATE = {
	0: "0",
	90: "90",
	180: "180",
	270: "270",
}

V4L2_DEFAULTS = {
	V4L2_CTRL_HORIZONTAL_FLIP: DEFAULT_HORIZONTAL_FLIP,
	V4L2_CTRL_VERTICAL_FLIP: DEFAULT_VERTICAL_FLIP,
	V4L2_CTRL_COMPRESSION_QUALITY: DEFAULT_COMPRESSION_QUALITY,
	V4L2_CTRL_BRIGHTNESS: DEFAULT_BRIGHTNESS,
	V4L2_CTRL_CONTRAST: DEFAULT_CONTRAST,
	V4L2_CTRL_SATURATION: DEFAULT_SATURATION,
	V4L2_CTRL_SHARPNESS: DEFAULT_SHARPNESS,
	V4L2_CTRL_POWER_LINE_FREQUENCY: DEFAULT_POWER_LINE_FREQUENCY,
	V4L2_CTRL_AUTO_EXPOSURE: DEFAULT_AUTO_EXPOSURE,
	V4L2_CTRL_EXPOSURE_TIME_ABSOLUTE: DEFAULT_EXPOSURE_TIME_ABSOLUTE,
	V4L2_CTRL_EXPOSURE_DYNAMIC_FRAMERATE: DEFAULT_EXPOSURE_DYNAMIC_FRAMERATE,
	V4L2_CTRL_ROTATE: DEFAULT_ROTATE,
	V4L2_CTRL_AUTO_EXPOSURE_BIAS: DEFAULT_AUTO_EXPOSURE_BIAS,
	V4L2_CTRL_WHITE_BALANCE_AUTO_PRESET: DEFAULT_WHITE_BALANCE_AUTO_PRESET,
	V4L2_CTRL_ISO_SENSITIVITY_AUTO: DEFAULT_ISO_SENSITIVITY_AUTO,
	V4L2_CTRL_ISO_SENSITIVITY: DEFAULT_ISO_SENSITIVITY,
	V4L2_CTRL_EXPOSURE_METERING_MODE: DEFAULT_EXPOSURE_METERING_MODE,
	V4L2_CTRL_SCENE_MODE: DEFAULT_SCENE_MODE,
}

V4L2_META = {
	V4L2_CTRL_BRIGHTNESS: {"type": "int", "min": 0, "max": 100, "step": 1},
	V4L2_CTRL_CONTRAST: {"type": "int", "min": -100, "max": 100, "step": 1},
	V4L2_CTRL_SATURATION: {"type": "int", "min": -100, "max": 100, "step": 1},
	V4L2_CTRL_SHARPNESS: {"type": "int", "min": -100, "max": 100, "step": 1},
	V4L2_CTRL_COMPRESSION_QUALITY: {"type": "int", "min": 1, "max": 100, "step": 1},
	V4L2_CTRL_HORIZONTAL_FLIP: {"type": "bool"},
	V4L2_CTRL_VERTICAL_FLIP: {"type": "bool"},
	V4L2_CTRL_EXPOSURE_DYNAMIC_FRAMERATE: {"type": "bool"},
	V4L2_CTRL_ROTATE: {"type": "menu", "options": V4L2_MENU_ROTATE},
	V4L2_CTRL_POWER_LINE_FREQUENCY: {"type": "menu", "options": V4L2_MENU_POWER_LINE_FREQUENCY},
	V4L2_CTRL_AUTO_EXPOSURE: {"type": "menu", "options": V4L2_MENU_AUTO_EXPOSURE},
	V4L2_CTRL_EXPOSURE_TIME_ABSOLUTE: {"type": "int", "min": 1, "max": 10000, "step": 1},
	V4L2_CTRL_AUTO_EXPOSURE_BIAS: {"type": "menu", "options": V4L2_MENU_AUTO_EXPOSURE_BIAS},
	V4L2_CTRL_WHITE_BALANCE_AUTO_PRESET: {"type": "menu", "options": V4L2_MENU_WHITE_BALANCE_AUTO_PRESET},
	V4L2_CTRL_ISO_SENSITIVITY_AUTO: {"type": "menu", "options": V4L2_MENU_ISO_SENSITIVITY_AUTO},
	V4L2_CTRL_ISO_SENSITIVITY: {"type": "menu", "options": V4L2_MENU_ISO_SENSITIVITY},
	V4L2_CTRL_EXPOSURE_METERING_MODE: {"type": "menu", "options": V4L2_MENU_EXPOSURE_METERING_MODE},
	V4L2_CTRL_SCENE_MODE: {"type": "menu", "options": V4L2_MENU_SCENE_MODE},
}


def parse_resolution(value):
	text = str(value).strip().lower().replace(" ", "")
	if "x" not in text:
		raise ValueError("resolution must be WIDTHxHEIGHT")
	left, right = text.split("x", 1)
	width = int(left)
	height = int(right)
	if width < CAM_MIN_WIDTH or height < CAM_MIN_HEIGHT:
		raise ValueError("resolution too small")
	if width > CAM_MAX_WIDTH or height > CAM_MAX_HEIGHT:
		raise ValueError("resolution too large")
	if (width % CAM_STEP) != 0 or (height % CAM_STEP) != 0:
		raise ValueError("resolution must follow camera step")
	return width, height, f"{width}x{height}"


def get_system_stats():
	cache_now = time.monotonic()
	with _SYSTEM_STATS_LOCK:
		cached = _SYSTEM_STATS_CACHE.get("data")
		cached_ts = float(_SYSTEM_STATS_CACHE.get("ts", 0.0) or 0.0)
		if cached is not None and (cache_now - cached_ts) < SYSTEM_STATS_CACHE_TTL_S:
			return dict(cached)

	stats = {}
	try:
		with open('/sys/class/thermal/thermal_zone0/temp', 'r') as _f:
			stats['cpu_temp'] = round(int(_f.read().strip()) / 1000.0, 1)
	except Exception:
		stats['cpu_temp'] = None
	try:
		mem = {}
		with open('/proc/meminfo', 'r') as _f:
			for _line in _f:
				_parts = _line.split()
				if _parts[0] in ('MemTotal:', 'MemAvailable:'):
					mem[_parts[0]] = int(_parts[1])
		total = mem.get('MemTotal:', 0)
		avail = mem.get('MemAvailable:', 0)
		if total > 0:
			stats['ram_percent'] = round((total - avail) / total * 100, 1)
			stats['ram_used_mb'] = round((total - avail) / 1024, 1)
			stats['ram_total_mb'] = round(total / 1024, 1)
		else:
			stats['ram_percent'] = None
	except Exception:
		stats['ram_percent'] = None
	try:
		with open('/proc/stat', 'r') as _f:
			_parts = _f.readline().split()
		vals = list(map(int, _parts[1:]))
		idle = vals[3] + (vals[4] if len(vals) > 4 else 0)
		total = sum(vals)
		with _SYSTEM_STATS_LOCK:
			prev_idle = _SYSTEM_STATS_CACHE.get("cpu_idle")
			prev_total = _SYSTEM_STATS_CACHE.get("cpu_total")
			prev_percent = _SYSTEM_STATS_CACHE.get("cpu_percent")
			_SYSTEM_STATS_CACHE["cpu_idle"] = idle
			_SYSTEM_STATS_CACHE["cpu_total"] = total
		if prev_idle is not None and prev_total is not None and total > prev_total:
			stats['cpu_percent'] = round((1 - (idle - prev_idle) / (total - prev_total)) * 100, 1)
		else:
			stats['cpu_percent'] = prev_percent
	except Exception:
		stats['cpu_percent'] = None
	with _SYSTEM_STATS_LOCK:
		_SYSTEM_STATS_CACHE["ts"] = time.monotonic()
		_SYSTEM_STATS_CACHE["cpu_percent"] = stats.get("cpu_percent")
		_SYSTEM_STATS_CACHE["data"] = dict(stats)
	return stats


def load_camera_settings():
	root = _load_saved_settings_root()
	data = root.get("camera", {}) if isinstance(root.get("camera", {}), dict) else {}
	needs_persist = False
	if not data:
		needs_persist = True

	_, _, stream_resolution = parse_resolution(data.get("stream_resolution", DEFAULT_STREAM_RESOLUTION))
	_, _, screenshot_resolution = parse_resolution(data.get("screenshot_resolution", DEFAULT_SCREENSHOT_RESOLUTION))
	try:
		stream_fps = int(data.get("stream_fps", DEFAULT_STREAM_FPS))
	except Exception:
		stream_fps = DEFAULT_STREAM_FPS
	stream_fps = max(1, min(120, stream_fps))
	try:
		streamhd_interval_s = int(data.get("streamhd_interval_s", DEFAULT_STREAMHD_INTERVAL_S))
	except Exception:
		streamhd_interval_s = DEFAULT_STREAMHD_INTERVAL_S
	streamhd_interval_s = max(1, min(60, streamhd_interval_s))
	try:
		mqtt_image_enabled = 1 if int(data.get("mqtt_image_enabled", _default_mqtt_image_enabled())) else 0
	except Exception:
		mqtt_image_enabled = _default_mqtt_image_enabled()
	
	v4l2_controls = normalize_v4l2_settings(data)

	settings = {
		"stream_resolution": stream_resolution,
		"stream_fps": stream_fps,
		"screenshot_resolution": screenshot_resolution,
		"streamhd_interval_s": streamhd_interval_s,
		"mqtt_image_enabled": mqtt_image_enabled,
		**v4l2_controls,
	}
	if needs_persist:
		save_camera_settings(settings)
	return settings


def normalize_v4l2_settings(source):
	normalized = {}
	for key, default_value in V4L2_DEFAULTS.items():
		meta = V4L2_META.get(key, {"type": "int"})
		raw_value = source.get(key, default_value)
		try:
			if meta["type"] == "bool":
				value = 1 if int(raw_value) else 0
			elif meta["type"] == "menu":
				value = int(raw_value)
				if value not in meta.get("options", {}):
					value = default_value
			else:
				value = int(raw_value)
				if "min" in meta:
					value = max(int(meta["min"]), value)
				if "max" in meta:
					value = min(int(meta["max"]), value)
		except Exception:
			value = default_value
		normalized[key] = value
	return normalized


def save_camera_settings(settings):
	_, _, stream_resolution = parse_resolution(settings.get("stream_resolution", DEFAULT_STREAM_RESOLUTION))
	_, _, screenshot_resolution = parse_resolution(settings.get("screenshot_resolution", DEFAULT_SCREENSHOT_RESOLUTION))
	stream_fps = int(settings.get("stream_fps", DEFAULT_STREAM_FPS))
	stream_fps = max(1, min(120, stream_fps))
	streamhd_interval_s = int(settings.get("streamhd_interval_s", DEFAULT_STREAMHD_INTERVAL_S))
	streamhd_interval_s = max(1, min(60, streamhd_interval_s))
	mqtt_image_enabled = 1 if int(settings.get("mqtt_image_enabled", _default_mqtt_image_enabled())) else 0
	v4l2_controls = normalize_v4l2_settings(settings)
	payload = {
		"stream_resolution": stream_resolution,
		"stream_fps": stream_fps,
		"screenshot_resolution": screenshot_resolution,
		"streamhd_interval_s": streamhd_interval_s,
		"mqtt_image_enabled": mqtt_image_enabled,
		**v4l2_controls,
	}
	root = _load_saved_settings_root()
	root["camera"] = dict(payload)
	_save_saved_settings_root(root)


def apply_v4l2_controls(controls):
	"""Apply v4l2-ctl commands to the driver immediately."""
	normalized = normalize_v4l2_settings(controls)
	errors = []
	for ctrl_name, ctrl_value in normalized.items():
		try:
			subprocess.run(
				["sudo", "v4l2-ctl", f"--set-ctrl={ctrl_name}={int(ctrl_value)}"],
				check=True,
				capture_output=True,
				timeout=5,
			)
		except Exception as e:
			errors.append(f"{ctrl_name}: {str(e)}")
	
	if errors:
		raise RuntimeError("Some v4l2 controls failed: " + " | ".join(errors))
	return True


def update_systemd_service(controls):
	"""Update the camerainit.service systemd file with saved v4l2 parameters."""
	normalized = normalize_v4l2_settings(controls)
	exec_lines = "\n".join(
		[f"ExecStart=/usr/bin/v4l2-ctl --set-ctrl={name}={int(value)}" for name, value in normalized.items()]
	)
	service_content = f"""[Unit]
Description=Camera init per LightBurn
After=multi-user.target

[Service]
Type=oneshot
User=root
# Configuration commands executed in sequence
{exec_lines}
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
"""
	try:
		# Create the directory if it does not exist
		service_dir = os.path.dirname(SYSTEMD_SERVICE_PATH)
		if service_dir and not os.path.exists(service_dir):
			os.makedirs(service_dir, exist_ok=True)
		
		# Write the service file
		with open(SYSTEMD_SERVICE_PATH, "w") as f:
			f.write(service_content)
		
		# Reload systemd configuration
		subprocess.run(["sudo", "systemctl", "daemon-reload"], check=True, capture_output=True, timeout=10)
		
		# Enable the service at boot
		subprocess.run(["sudo", "systemctl", "enable", "camerainit.service"], check=True, capture_output=True, timeout=10)
		
		return True
	except Exception as e:
		raise RuntimeError(f"Cannot update systemd service: {str(e)}")


def apply_saved_camera_controls():
	settings = load_camera_settings()
	controls = normalize_v4l2_settings(settings)
	try:
		apply_v4l2_controls(controls)
	except Exception as exc:
		print(f"[camera] startup v4l2 restore failed: {exc}", flush=True)
	try:
		update_systemd_service(controls)
	except Exception as exc:
		print(f"[camera] systemd service refresh failed: {exc}", flush=True)




class LaserAutomationManager:
	def __init__(self, controller):
		self._controller = controller
		_laser_logger = lambda m: print(f"[laser] {m}", flush=True)
		self._logger = _laser_logger
		self._monitor = LaserMonitorState(logger=_laser_logger)
		self._proxy = SerialTrafficProxy(self._monitor, _laser_logger)
		self._lock = threading.Lock()
		self._settings = load_app_settings()
		self._running = False
		self._thread = None
		self._last_led_profile = ""
		self._door_state_active = False
		self._door_prev_led_on = None
		self._door_forced_led_on = False
		self._error_state_since = None
		self._buttons_manager = None
		self._air_assist = None
		self._airassist_event_manual_forced = False
		self._airassist_event_latched_enabled = None
		self._sync_power_cycle_led_feedback_config()

	def _sync_power_cycle_led_feedback_config(self):
		controller = self._controller
		if controller is None or not hasattr(controller, "configure_power_cycle_feedback"):
			return
		settings = self.get_settings()
		try:
			controller.configure_power_cycle_feedback(
				startup_effect=str(settings.get("led_startup_effect", "strobe")),
				startup_color_mode=str(settings.get("led_startup_color_mode", "laser_green")),
				startup_preset=str(settings.get("led_startup_preset", "none")),
				shutdown_effect=str(settings.get("led_shutdown_effect", "strobe")),
				shutdown_color_mode=str(settings.get("led_shutdown_color_mode", "ruby_red")),
				shutdown_preset=str(settings.get("led_shutdown_preset", "none")),
				brightness=float(settings.get("led_startup_shutdown_brightness", STARTUP_SHUTDOWN_BRIGHTNESS)),
			)
		except Exception as exc:
			self._log(f"startup/shutdown LED config sync failed: {exc}")

	def _log(self, message):
		self._logger(message)

	def laser_power_s(self):
		"""Return the current laser S value parsed from upstream GCODE."""
		return self._monitor.get_laser_power_s()

	def start(self):
		with self._lock:
			if self._running:
				return
			self._running = True
		self._proxy.apply_config(self._settings)
		self._thread = threading.Thread(target=self._loop, daemon=True)
		self._thread.start()

	def stop(self):
		with self._lock:
			self._running = False
		thread = self._thread
		self._thread = None
		if thread is not None:
			thread.join(timeout=1.0)
		self._proxy.stop()

	def bind_buttons_manager(self, buttons_manager):
		with self._lock:
			self._buttons_manager = buttons_manager

	def bind_air_assist(self, air_assist):
		with self._lock:
			self._air_assist = air_assist

	def set_airassist_power(self, enabled, source="manual"):
		air_assist = None
		with self._lock:
			air_assist = self._air_assist
		if air_assist is None:
			raise RuntimeError("air_assist_unavailable")
		air_assist.set_enabled(enabled)
		try:
			state = air_assist.get_state()
		except Exception:
			state = {"enabled": bool(enabled), "auto_mode": False, "listen_events": False}
		if bool(state.get("listen_events", False)) and not bool(state.get("auto_mode", False)):
			self._airassist_event_latched_enabled = bool(enabled)
			self._airassist_event_manual_forced = bool(enabled)
			self._log(f"airassist manual override: {'ON' if enabled else 'OFF'} (source={source})")
		return state

	def set_airassist_auto_mode(self, enabled, source="manual"):
		air_assist = None
		with self._lock:
			air_assist = self._air_assist
		if air_assist is None:
			raise RuntimeError("air_assist_unavailable")
		air_assist.set_auto_mode(enabled)
		try:
			state = air_assist.get_state()
		except Exception:
			state = {"enabled": False, "auto_mode": bool(enabled), "listen_events": False}
		listen_events = bool(state.get("listen_events", False))
		current_enabled = bool(state.get("enabled", False))
		if bool(enabled):
			self._airassist_event_latched_enabled = None
			self._airassist_event_manual_forced = False
		else:
			if listen_events:
				self._airassist_event_latched_enabled = current_enabled
				self._airassist_event_manual_forced = current_enabled
			else:
				self._airassist_event_latched_enabled = None
				self._airassist_event_manual_forced = False
		self._log(f"airassist auto_mode set to {bool(enabled)} (source={source})")
		return state

	def _loop(self):
		while True:
			with self._lock:
				if not self._running:
					break
			status = self._monitor.snapshot()
			self._apply_airassist_event_policy(status)
			self._apply_bridge_commands()
			self._apply_led_profile(status)
			state = str(status.get("state", "idle") or "idle")
			if state in ("running", "door", "hold", "error"):
				sleep_s = 0.25
			elif bool(status.get("traffic_active")):
				sleep_s = 0.50
			else:
				sleep_s = 1.0
			time.sleep(sleep_s)

	def _apply_airassist_event_policy(self, laser_status):
		air_assist = None
		with self._lock:
			air_assist = self._air_assist
		if air_assist is None:
			return
		try:
			state = air_assist.get_state()
		except Exception:
			return

		listen_events = bool(state.get("listen_events", False))
		auto_mode = bool(state.get("auto_mode", False))
		enabled = bool(state.get("enabled", False))
		laser_active = bool(laser_status.get("laser_active", False))
		s_value = int(laser_status.get("laser_power_s", 0) or 0)
		airassist_event = str(self._monitor.pop_airassist_event() or "")
		if airassist_event:
			self._log(f"airassist serial event: {airassist_event.upper()} (auto_mode={auto_mode}, listen_events={listen_events}, S={s_value})")

		if not listen_events:
			if self._airassist_event_manual_forced and enabled and not auto_mode:
				air_assist.set_enabled(False)
			self._airassist_event_manual_forced = False
			self._airassist_event_latched_enabled = None
			return

		if auto_mode:
			if airassist_event == "on":
				if not enabled:
					air_assist.set_enabled(True)
				self._log("airassist progressive gate: ON via serial event M7/M8")
			elif airassist_event == "off":
				if enabled:
					air_assist.set_enabled(False)
				self._log("airassist progressive gate: OFF via serial event M9")
			self._airassist_event_manual_forced = False
			self._airassist_event_latched_enabled = None
			return

		if airassist_event == "on":
			self._airassist_event_latched_enabled = True
		elif airassist_event == "off":
			self._airassist_event_latched_enabled = False

		if self._airassist_event_latched_enabled is None:
			# In manual listen_events mode, keep current state until explicit M7/M8/M9.
			self._airassist_event_manual_forced = bool(enabled)
			return

		desired_enabled = bool(self._airassist_event_latched_enabled)
		if desired_enabled != enabled:
			air_assist.set_enabled(desired_enabled)
		self._airassist_event_manual_forced = desired_enabled
		if airassist_event:
			self._log(f"airassist listen_events: manual mode {'ON' if desired_enabled else 'OFF'} (reason=serial_event, laser_active={laser_active})")

	def _apply_bridge_commands(self):
		"""Process (BRIDGE:key=value) gcode commands from LightBurn."""
		air_assist = None
		with self._lock:
			air_assist = self._air_assist
		
		bridge_cmds = self._monitor.pop_bridge_commands()
		if not bridge_cmds:
			return
		
		for cmd in bridge_cmds:
			key = str(cmd.get('key', '')).lower()
			val = str(cmd.get('value', '')).strip()
			try:
				if key == 'aa_speed':
					speed = int(float(val))
					if air_assist is not None:
						air_assist.set_speed(speed)
						self._log(f"BRIDGE: aa_speed set to {speed}%")
				
				elif key == 'aa_progressive':
					enabled = val.lower() in ('on', 'true', '1', 'yes')
					if air_assist is not None:
						self.set_airassist_auto_mode(enabled, source="bridge")
						self._log(f"BRIDGE: aa_progressive set to {enabled}")
				
				elif key == 'aa_tune':
					parts = val.split(',')
					if len(parts) >= 2:
						range_min = int(float(parts[0].strip()))
						range_max = int(float(parts[1].strip()))
						min_pwm = None
						if len(parts) >= 3:
							min_pwm = int(float(parts[2].strip()))
						if air_assist is not None:
							air_assist.set_auto_range(range_min, range_max)
							if min_pwm is not None:
								air_assist.set_auto_min_pwm(min_pwm)
								self._log(f"BRIDGE: aa_tune set to {range_min}%-{range_max}%, min_pwm={min_pwm}%")
							else:
								self._log(f"BRIDGE: aa_tune set to {range_min}%-{range_max}%")

				elif key == 'aa_min_pwm':
					min_pwm = int(float(val))
					if air_assist is not None:
						air_assist.set_auto_min_pwm(min_pwm)
						self._log(f"BRIDGE: aa_min_pwm set to {min_pwm}%")
				
				elif key == 'light':
					enabled = val.lower() in ('on', 'true', '1', 'yes')
					controller = None
					with self._lock:
						controller = self._controller
					if controller is not None:
						controller.is_on = enabled
						self._log(f"BRIDGE: light set to {enabled}")
				
				elif key == 'light_brightness':
					brightness = float(val)
					if brightness > 1.0:
						brightness = brightness / 100.0
					controller = None
					with self._lock:
						controller = self._controller
					if controller is not None:
						controller.set_brightness(brightness)
						self._log(f"BRIDGE: light_brightness set to {brightness:.2f}")
				
				elif key == 'light_color':
					color_name = val.lower()
					controller = None
					with self._lock:
						controller = self._controller
					if controller is not None:
						try:
							color_map = {
								'red': (255, 0, 0),
								'green': (0, 255, 0),
								'blue': (0, 0, 255),
								'white': (255, 255, 255),
								'yellow': (255, 255, 0),
								'cyan': (0, 255, 255),
								'magenta': (255, 0, 255),
								'orange': (255, 165, 0),
								'purple': (128, 0, 128),
							}
							if color_name in color_map:
								r, g, b = color_map[color_name]
								controller.set_custom_color(r, g, b)
								self._log(f"BRIDGE: light_color set to {color_name}")
							else:
								self._log(f"BRIDGE: light_color '{color_name}' not recognized")
						except Exception as e:
							self._log(f"BRIDGE: light_color error: {e}")
				
				elif key == 'light_effect':
					effect_name = val.lower()
					controller = None
					with self._lock:
						controller = self._controller
					if controller is not None:
						if effect_name in controller.EFFECTS:
							controller.set_effect(effect_name)
							self._log(f"BRIDGE: light_effect set to {effect_name}")
						else:
							self._log(f"BRIDGE: light_effect '{effect_name}' not recognized")
				
				else:
					self._log(f"BRIDGE: unknown command '{key}={val}'")
			
			except Exception as e:
				self._log(f"BRIDGE: error processing '{key}={val}': {e}")

	def _apply_led_profile(self, status):
		settings = self.get_settings()
		if int(settings.get("laser_led_sync_enabled", 1)) != 1:
			self._door_state_active = False
			self._door_prev_led_on = None
			self._door_forced_led_on = False
			self._error_state_since = None
			self._last_led_profile = ""
			return
		state = str(status.get("state", "idle") or "idle")
		if state not in ("idle", "running", "hold", "door", "error", "engrave_complete"):
			state = "idle"

		is_on = bool(self._controller.get_state().get("is_on"))
		if state == "door":
			if not self._door_state_active:
				self._door_state_active = True
				self._door_prev_led_on = is_on
				self._door_forced_led_on = False
				if int(settings.get("buttons_reset_mode_opening_door", 0)) == 1 and self._buttons_manager is not None:
					try:
						self._buttons_manager.reset_to_mode_one()
					except Exception as exc:
						print(f"[buttons] mode reset on door opening failed: {exc}", flush=True)
			if not is_on:
				self._controller.toggle_power(with_fade=False)
				self._door_forced_led_on = True
				is_on = True
		elif self._door_state_active:
			if self._door_forced_led_on and self._door_prev_led_on is False and is_on:
				self._controller.toggle_power(with_fade=False)
				is_on = False
			self._door_state_active = False
			self._door_prev_led_on = None
			self._door_forced_led_on = False

		if state == "error" and not is_on:
			self._controller.toggle_power(with_fade=False)
			is_on = bool(self._controller.get_state().get("is_on"))

		state_for_led = state
		if state == "error":
			now = time.monotonic()
			if self._error_state_since is None:
				self._error_state_since = now
			if int(settings.get("laser_led_error_auto_reset_10s", 1)) == 1 and (now - self._error_state_since) >= 10.0:
				# Keep UI/status consistent with LED auto-reset behavior.
				# When auto-reset is enabled, clear sticky monitor error too so
				# the dashboard does not remain in ERROR until manual clear.
				self._monitor.clear_error()
				self._error_state_since = None
				state_for_led = "idle"
		else:
			self._error_state_since = None
		
		profile = f"{state_for_led}:{settings.get(f'laser_led_{state_for_led}_effect')}:{settings.get(f'laser_led_{state_for_led}_color_mode')}"
		if profile == self._last_led_profile:
			return
		if is_on:
			self._controller.set_preset("none")
			self._controller.set_color_mode(str(settings.get(f"laser_led_{state_for_led}_color_mode", "cool_white")))
			self._controller.set_effect(str(settings.get(f"laser_led_{state_for_led}_effect", "static")))
		self._last_led_profile = profile

	def get_settings(self):
		with self._lock:
			return dict(self._settings)

	def get_payload(self):
		payload = self._monitor.snapshot()
		payload["config"] = self.get_settings()
		payload["serial_link"] = self._proxy.get_link_state()
		return payload

	def send_gcode_command(self, command, source="api"):
		return self._proxy.enqueue_command(command, source=source)

	def clear_command_queue(self, source="api"):
		return self._proxy.clear_command_queue(source=source)

	def send_jog_command(self, direction, step_mm=None, feed_mm_sec=None, source="api"):
		dir_value = str(direction or "").strip().lower()
		if dir_value not in ("up", "down", "left", "right", "home"):
			raise ValueError("invalid jog direction")

		settings = self.get_settings()
		if dir_value == "home":
			result = self.send_gcode_command("$H", source=f"{source}:jog_home")
			result["jog"] = {"direction": "home", "step_mm": 0.0}
			return result

		try:
			step = float(step_mm if step_mm is not None else settings.get("laser_move_step_mm", 20.0))
		except Exception:
			step = 20.0
		step = round(max(0.1, min(100.0, step)), 2)
		try:
			if feed_mm_sec is not None:
				feed_sec = float(feed_mm_sec)
			else:
				feed_sec = float(settings.get("laser_move_feed_mm_sec", 10.0))
		except Exception:
			feed_sec = 10.0
		feed_sec = round(max(0.2, min(80.0, feed_sec)), 2)
		feed = round(feed_sec * 60.0, 1)

		delta_x = 0.0
		delta_y = 0.0
		if dir_value == "up":
			delta_y = step
		elif dir_value == "down":
			delta_y = -step
		elif dir_value == "right":
			delta_x = step
		elif dir_value == "left":
			delta_x = -step

		commands = ["G91"]
		if abs(delta_x) > 0.0:
			commands.append(f"G1 X{delta_x:.3f} F{feed:.1f}")
		if abs(delta_y) > 0.0:
			commands.append(f"G1 Y{delta_y:.3f} F{feed:.1f}")
		commands.append("G90")

		results = []
		for cmd in commands:
			results.append(self.send_gcode_command(cmd, source=f"{source}:jog_{dir_value}"))

		final = dict(results[-1])
		final["queued_commands"] = commands
		final["jog"] = {"direction": dir_value, "step_mm": step, "feed_mm_sec": feed_sec}
		return final

	def execute_custom_position(self, source="api"):
		settings = self.get_settings()
		try:
			x_mm = float(settings.get("laser_custom_pos_x_mm", 0.0))
		except Exception:
			x_mm = 0.0
		try:
			y_mm = float(settings.get("laser_custom_pos_y_mm", 0.0))
		except Exception:
			y_mm = 0.0
		try:
			z_mm = float(settings.get("laser_custom_pos_z_mm", 0.0))
		except Exception:
			z_mm = 0.0
		try:
			feed_mm_sec = float(settings.get("laser_move_feed_mm_sec", 10.0))
		except Exception:
			feed_mm_sec = 10.0
		use_g0 = bool(int(settings.get("laser_custom_pos_use_g0", 1) or 0))
		feed_mm_sec = max(0.2, min(80.0, feed_mm_sec))
		feed_mm_min = feed_mm_sec * 60.0
		motion_cmd = "G0" if use_g0 else "G1"

		commands = [
			"G90",
			(f"{motion_cmd} X{x_mm:.3f} Y{y_mm:.3f} Z{z_mm:.3f}" if use_g0 else f"{motion_cmd} X{x_mm:.3f} Y{y_mm:.3f} Z{z_mm:.3f} F{feed_mm_min:.1f}"),
		]
		results = []
		for cmd in commands:
			results.append(self.send_gcode_command(cmd, source=f"{source}:custom_position"))
		final = dict(results[-1])
		final["queued_commands"] = commands
		final["custom_position"] = {
			"x_mm": x_mm,
			"y_mm": y_mm,
			"z_mm": z_mm,
			"use_g0": use_g0,
			"motion_cmd": motion_cmd,
			"feed_mm_sec": feed_mm_sec,
		}
		return final

	def serial_link_state(self):
		return self._proxy.get_link_state()

	def update_settings(self, patch):
		if not isinstance(patch, dict):
			raise ValueError("payload must be object")
		with self._lock:
			merged = dict(self._settings)
			for key, value in patch.items():
				if key in APP_DEFAULTS:
					merged[key] = value
			self._settings = load_app_settings_from_source(merged)
			save_app_settings(self._settings)
		self._sync_power_cycle_led_feedback_config()
		self._proxy.apply_config(self._settings)
		return self.get_payload()

	def clear_error(self):
		self._monitor.clear_error()
		with self._lock:
			merged = dict(self._settings)
			merged["laser_led_idle_effect"] = APP_DEFAULTS.get("laser_led_idle_effect", "static")
			self._settings = load_app_settings_from_source(merged)
			save_app_settings(self._settings)
			# Force re-application at next loop tick with updated idle effect.
			self._last_led_profile = ""
		self._proxy.apply_config(self._settings)


def poweroff_now():
	subprocess.Popen(["sudo", "shutdown", "-h", "now"])


def poweroff_with_feedback(controller):
	controller.run_poweroff_feedback()
	poweroff_now()


def reboot_with_feedback(controller):
	controller.run_poweroff_feedback()
	subprocess.Popen(["sudo", "reboot"])


class UstreamerManager:
	def __init__(self, logger, listen_host=USTREAMER_HOST, connect_host="127.0.0.1", port=USTREAMER_PORT):
		self._logger = logger
		self._listen_host = listen_host
		self._connect_host = connect_host
		self._port = int(port)
		self._lock = threading.Lock()
		self._proc = None
		self._config = None

	def _log(self, message):
		self._logger(message)

	def ensure_running(self, width, height, fps):
		config = (int(width), int(height), max(1, int(fps)))
		old_proc = None
		old_config = None
		with self._lock:
			if self._proc is not None and self._proc.poll() is not None:
				self._proc = None
				self._config = None
			if self._proc is not None and self._config == config:
				return
			old_proc = self._proc
			old_config = self._config
			self._proc = None
			self._config = None
		if old_proc is not None:
			self._terminate_proc(old_proc, f"ustreamer reconfigure {old_config} -> {config}")
		proc = subprocess.Popen(
			[
				"ustreamer",
				f"--device={CAM_DEVICE}",
				f"--host={self._listen_host}",
				f"--port={self._port}",
				"--format=MJPEG",
				f"--resolution={config[0]}x{config[1]}",
				f"--desired-fps={config[2]}",
				"--workers=1",
			],
			stdout=subprocess.DEVNULL,
			stderr=subprocess.DEVNULL,
		)
		self._wait_until_ready(proc, config)
		with self._lock:
			self._proc = proc
			self._config = config
		self._log(
			f"ustreamer ready width={config[0]} height={config[1]} fps={config[2]} listen={self._listen_host}:{self._port} connect={self._connect_host}:{self._port}",
		)

	def stop(self, reason=""):
		with self._lock:
			proc = self._proc
			self._proc = None
			self._config = None
		if proc is not None:
			self._terminate_proc(proc, reason or "ustreamer stop")

	def open_stream_response(self):
		conn = http.client.HTTPConnection(self._connect_host, self._port, timeout=15)
		conn.putrequest("GET", "/stream", skip_host=False, skip_accept_encoding=True)
		conn.putheader("Connection", "close")
		conn.endheaders()
		response = conn.getresponse()
		return conn, response

	def _wait_until_ready(self, proc, config):
		deadline = time.monotonic() + 6.0
		last_error = "ustreamer did not open port"
		while time.monotonic() < deadline:
			if proc.poll() is not None:
				raise RuntimeError(f"ustreamer exited early for {config}")
			try:
				with socket.create_connection((self._connect_host, self._port), timeout=0.25):
					return
			except OSError as exc:
				last_error = str(exc)
				time.sleep(0.15)
		self._terminate_proc(proc, "ustreamer startup timeout")
		raise RuntimeError(f"ustreamer startup timeout: {last_error}")

	def _terminate_proc(self, proc, reason):
		try:
			proc.terminate()
		except Exception:
			pass
		try:
			proc.wait(timeout=2.0)
		except Exception:
			try:
				proc.kill()
			except Exception:
				pass
		self._log(reason)


class LedWebServer:
	def __init__(self, controller, host=WEB_HOST, port=WEB_PORT):
		self.controller = controller
		self.laser_manager = LaserAutomationManager(controller)
		app_settings = self.laser_manager.get_settings()
		laser_max_power = int(app_settings.get("laserbeam_nominal_maxpower", LASER_MAXPOWER) or LASER_MAXPOWER)
		self.air_assist = AirAssistController(
			pin=AIR_ASSIST_GPIO_PWM_PIN,
			freq_hz=AIR_ASSIST_PWM_FREQ_HZ,
			default_speed=int(app_settings.get("airassist_speed", AIR_ASSIST_DEFAULT_SPEED) or AIR_ASSIST_DEFAULT_SPEED),
			laser_max_power=laser_max_power,
		)
		self.air_assist.set_speed(app_settings.get("airassist_speed", AIR_ASSIST_DEFAULT_SPEED))
		self.air_assist.set_auto_range(
			app_settings.get("airassist_auto_range_min", 0),
			app_settings.get("airassist_auto_range_max", 100),
		)
		self.air_assist.set_auto_min_pwm(app_settings.get("airassist_auto_min_pwm", 0))
		self.air_assist.set_listen_events(app_settings.get("airassist_listen_events", 0))
		self.air_assist.set_laser_source(self.laser_manager.laser_power_s)
		self.laser_manager.bind_air_assist(self.air_assist)
		self.host = host
		self.port = port
		self._httpd = None
		self._thread = None
		self._capture_lock = threading.Lock()
		ustreamer_listen_host = USTREAMER_LISTEN_HOST
		ustreamer_connect_host = USTREAMER_CONNECT_HOST
		ustreamer_port = int(USTREAMER_PORT)
		self._ustreamer = UstreamerManager(
			lambda message: print(f"[camera] {message}", flush=True),
			listen_host=ustreamer_listen_host,
			connect_host=ustreamer_connect_host,
			port=ustreamer_port,
		)
		self._handler_cls = None
		self._watchdog_thread = None
		self._watchdog_stop = threading.Event()
		self._watchdog_last_error = ""

	def start(self):
		handler_cls = self._build_handler(self.controller)
		handler_cls.bind_capture_lock(self._capture_lock)
		handler_cls.bind_ustreamer(self._ustreamer)
		handler_cls.bind_laser_manager(self.laser_manager)
		handler_cls.bind_air_assist(self.air_assist)
		self._handler_cls = handler_cls
		self._httpd = ThreadingHTTPServer((self.host, self.port), handler_cls)
		self._thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)
		self._thread.start()
		self._watchdog_stop.clear()
		self._watchdog_thread = threading.Thread(target=self._ustreamer_watchdog_loop, daemon=True)
		self._watchdog_thread.start()
		self.laser_manager.start()
		self.air_assist.start()

	def stop(self):
		self._watchdog_stop.set()
		self.laser_manager.stop()
		self.air_assist.stop()
		if self._watchdog_thread is not None:
			self._watchdog_thread.join(timeout=2.0)
			self._watchdog_thread = None
		self._ustreamer.stop("server shutdown")
		if self._httpd is not None:
			self._httpd.shutdown()
			self._httpd.server_close()
		if self._thread is not None:
			self._thread.join(timeout=1.0)

	def _ustreamer_watchdog_loop(self):
		"""Mantiene ustreamer disponibile per Home Assistant anche senza client /stream attivi.
		Quando la camera e' occupata da stream esclusivi (snapshot/streamhd), evita restart concorrenti."""
		while not self._watchdog_stop.is_set():
			try:
				owner_mode = "idle"
				if self._handler_cls is not None:
					status = self._handler_cls._camera_status_payload()
					owner_mode = str(status.get("camera_owner_mode", "idle") or "idle")
				if owner_mode not in ("snapshot", "streamhd"):
					settings = load_camera_settings()
					width, height, _ = parse_resolution(settings.get("stream_resolution", DEFAULT_STREAM_RESOLUTION))
					fps = max(1, int(settings.get("stream_fps", DEFAULT_STREAM_FPS)))
					self._ustreamer.ensure_running(width, height, fps)
				self._watchdog_last_error = ""
			except Exception as exc:
				msg = str(exc)
				if msg != self._watchdog_last_error:
					print(f"[camera] ustreamer watchdog warning: {msg}", flush=True)
					self._watchdog_last_error = msg
			self._watchdog_stop.wait(5.0)

	@staticmethod
	def _build_handler(controller):
		class Handler(BaseHTTPRequestHandler):
			_capture_lock = None
			_ustreamer = None
			_laser_manager = None
			_air_assist = None
			_pwa_icon_cache = {}
			_camera_owner_lock = threading.Lock()
			_camera_owner = None          # used by snapshot / streamhd (exclusive)
			_stream_client_count = 0      # concurrent /stream proxy connections
			_camera_notice = None

			@classmethod
			def bind_capture_lock(cls, lock_obj):
				cls._capture_lock = lock_obj

			@classmethod
			def bind_ustreamer(cls, ustreamer):
				cls._ustreamer = ustreamer

			@classmethod
			def bind_laser_manager(cls, laser_manager):
				cls._laser_manager = laser_manager

			@classmethod
			def bind_air_assist(cls, air_assist):
				cls._air_assist = air_assist

			@classmethod
			def _stop_active_stream(cls, reason):
				if cls._ustreamer is not None:
					cls._ustreamer.stop(reason)

			@classmethod
			def _set_camera_notice(cls, message, level="info", ttl_s=10.0):
				with cls._camera_owner_lock:
					cls._camera_notice = {
						"message": str(message),
						"level": str(level),
						"until": time.monotonic() + max(1.0, float(ttl_s)),
					}

			@classmethod
			def _claim_camera_owner(cls, mode, client_hint):
				"""Exclusive ownership for snapshot / streamhd. Stops any active stream."""
				token = f"{mode}:{time.monotonic_ns()}"
				with cls._camera_owner_lock:
					cls._camera_notice = {
						"message": f"Camera priority: {str(mode).upper()} (external request)",
						"level": "info",
						"until": time.monotonic() + 12.0,
					}
					cls._camera_owner = {
						"token": token,
						"mode": str(mode),
						"client": str(client_hint),
						"since": time.time(),
					}
				return token

			@classmethod
			def _enter_stream_client(cls, client_hint):
				"""Register a new concurrent /stream proxy client."""
				with cls._camera_owner_lock:
					cls._stream_client_count += 1
					if cls._camera_owner is None or cls._camera_owner.get("mode") == "stream":
						cls._camera_owner = {
							"token": "stream",
							"mode": "stream",
							"client": str(client_hint),
							"since": time.time(),
						}

			@classmethod
			def _exit_stream_client(cls):
				"""Unregister a /stream proxy client; release ownership when last one disconnects."""
				with cls._camera_owner_lock:
					cls._stream_client_count = max(0, cls._stream_client_count - 1)
					if cls._stream_client_count == 0 and cls._camera_owner is not None and cls._camera_owner.get("mode") == "stream":
						cls._camera_owner = None

			@classmethod
			def _is_camera_owner(cls, token):
				with cls._camera_owner_lock:
					return cls._camera_owner is not None and cls._camera_owner.get("token") == token

			@classmethod
			def _camera_owner_mode(cls):
				with cls._camera_owner_lock:
					if cls._camera_owner is None:
						return "idle"
					return str(cls._camera_owner.get("mode") or "idle")

			@classmethod
			def _release_camera_owner(cls, token):
				with cls._camera_owner_lock:
					if cls._camera_owner is not None and cls._camera_owner.get("token") == token:
						cls._camera_owner = None

			@classmethod
			def _camera_status_payload(cls):
				now = time.monotonic()
				with cls._camera_owner_lock:
					owner = cls._camera_owner
					notice = cls._camera_notice
					payload = {}
					owner_mode = ""
					if owner is not None:
						owner_mode = str(owner.get("mode") or "")
						payload["camera_owner_mode"] = owner_mode
					if notice is not None and notice.get("until", 0) > now:
						payload["camera_notice"] = notice.get("message")
						payload["camera_notice_level"] = notice.get("level", "info")
					elif notice is not None:
						cls._camera_notice = None
					if "camera_notice" not in payload and owner_mode in ("snapshot", "streamhd"):
						payload["camera_notice"] = f"Camera priority: {owner_mode.upper()}"
						payload["camera_notice_level"] = "info"
					return payload

			@staticmethod
			def _get_param(params, key, default=""):
				values = params.get(key)
				if not values:
					return default
				return values[0]

			@staticmethod
			def _log(message):
				print(f"[camera] {message}", flush=True)

			def _capture_camera_jpeg_bytes(self, width, height, timeout=25):
				if self._capture_lock is None:
					raise RuntimeError("capture lock is not configured")

				if not self._capture_lock.acquire(timeout=4.0):
					raise RuntimeError("camera busy: stream already using device")
				try:
					last_error = None
					for attempt in range(3):
						try:
							result = subprocess.run(
								[
									"v4l2-ctl",
									"-d",
									CAM_DEVICE,
									f"--set-fmt-video=width={width},height={height},pixelformat=JPEG",
									"--stream-mmap=4",
									"--stream-count=1",
									"--stream-to=-",
								],
								check=True,
								capture_output=True,
								timeout=timeout,
							)
							frame = result.stdout
							if not frame:
								raise RuntimeError("empty frame from camera")
							return frame
						except subprocess.CalledProcessError as exc:
							stderr_text = (exc.stderr or b"").decode("utf-8", errors="ignore").lower()
							last_error = exc
							busy_like = (exc.returncode == 255) or ("resource busy" in stderr_text) or ("device or resource busy" in stderr_text)
							if attempt < 2 and busy_like:
								time.sleep(0.25)
								continue
							raise
					if last_error is not None:
						raise last_error
					raise RuntimeError("capture failed")
				finally:
					self._capture_lock.release()

			def _stream_mjpeg_interval_capture(self, settings, interval_s):
				boundary = "frame"
				interval_value = max(0.2, float(interval_s))
				frame_timeout = max(8.0, interval_value + 5.0)
				resolution = settings["screenshot_resolution"]
				width, height, _ = parse_resolution(resolution)
				token = self._claim_camera_owner("streamhd", self.client_address[0])
				self._set_camera_notice("Camera priority: STREAMHD", level="info", ttl_s=max(10.0, interval_value + 4.0))
				self._stop_active_stream("streamhd interval capture")
				self._log(
					f"streamhd request exact={resolution} interval_s={interval_value}",
				)
				self.send_response(200)
				self.send_header("Content-Type", f"multipart/x-mixed-replace; boundary={boundary}")
				self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
				self.send_header("Pragma", "no-cache")
				self.end_headers()

				try:
					while True:
						if not self._is_camera_owner(token):
							self._set_camera_notice("StreamHD stopped: another stream took priority", level="info", ttl_s=10.0)
							return
						self._set_camera_notice("Camera priority: STREAMHD", level="info", ttl_s=max(10.0, interval_value + 4.0))
						started = time.monotonic()
						frame = self._capture_camera_jpeg_bytes(width, height, timeout=frame_timeout)
						self.wfile.write(("--" + boundary + "\r\n").encode("ascii"))
						self.wfile.write(b"Content-Type: image/jpeg\r\n")
						self.wfile.write(("Content-Length: " + str(len(frame)) + "\r\n\r\n").encode("ascii"))
						self.wfile.write(frame)
						self.wfile.write(b"\r\n")
						self.wfile.flush()
						remaining = interval_value - (time.monotonic() - started)
						if remaining > 0:
							time.sleep(remaining)
				except (BrokenPipeError, ConnectionResetError):
					return
				except Exception as exc:
					self._set_camera_notice(f"StreamHD failed on {resolution}: {exc}", level="warn", ttl_s=12.0)
					self._log(f"streamhd failed: {exc}")
				finally:
					self._release_camera_owner(token)

			def _proxy_ustreamer_stream(self, width, height, fps):
				if self._ustreamer is None:
					self._write_json({"error": "ustreamer_missing"}, status=500)
					return
				owner_mode = self._camera_owner_mode()
				if owner_mode in ("snapshot", "streamhd"):
					self._set_camera_notice(
						f"Stream waiting: camera is busy with {owner_mode.upper()}",
						level="info",
						ttl_s=20.0,
					)
					self._write_json({"error": "camera_busy", "owner_mode": owner_mode}, status=409)
					return
				self._log(f"stream request width={width} height={height} fps={fps} via=ustreamer")
				try:
					self._ustreamer.ensure_running(width, height, fps)
					conn, upstream = self._ustreamer.open_stream_response()
				except Exception as exc:
					self._set_camera_notice(f"Stream failed: {exc}", level="warn", ttl_s=10.0)
					self._write_json({"error": "stream_start_failed", "detail": str(exc)}, status=500)
					return
				self._enter_stream_client(self.client_address[0])
				try:
					self.send_response(upstream.status)
					for key, value in upstream.getheaders():
						header = key.lower()
						if header in ("connection", "transfer-encoding", "server", "date"):
							continue
						self.send_header(key, value)
					self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
					self.send_header("Pragma", "no-cache")
					self.end_headers()
					while True:
						chunk = upstream.read(65536)
						if not chunk:
							break
						self.wfile.write(chunk)
						self.wfile.flush()
				except (BrokenPipeError, ConnectionResetError):
					pass
				except Exception as exc:
					self._set_camera_notice(f"Stream proxy failed: {exc}", level="warn", ttl_s=10.0)
					self._log(f"stream proxy failed: {exc}")
				finally:
					try:
						upstream.close()
					except Exception:
						pass
					try:
						conn.close()
					except Exception:
						pass
					self._exit_stream_client()

			def _camera_settings_payload(self):
				settings = load_camera_settings()
				app_settings = load_app_settings()
				return {
					"stream_resolution": settings["stream_resolution"],
					"stream_fps": settings["stream_fps"],
					"screenshot_resolution": settings["screenshot_resolution"],
					"streamhd_interval_s": settings["streamhd_interval_s"],
					"mqtt_image_enabled": settings["mqtt_image_enabled"],
					"horizontal_flip": settings["horizontal_flip"],
					"vertical_flip": settings["vertical_flip"],
					"compression_quality": settings["compression_quality"],
					"resolution_presets": RESOLUTION_PRESETS,
					"fps_presets": FPS_PRESETS,
					"streamhd_interval_presets": STREAMHD_INTERVAL_PRESETS,
					"led_on_boot": int(app_settings.get("led_on_boot", 1)),
				}

			def _camera_v4l2_payload(self):
				settings = load_camera_settings()
				controls = normalize_v4l2_settings(settings)
				return {
					"controls": controls,
					"meta": V4L2_META,
				}

			def _apply_webhook_params(self, params):
				errors = []

				power = self._get_param(params, "power", "").lower()
				if power:
					if power in ("toggle", "switch"):
						controller.toggle_power()
					elif power in ("on", "1", "true"):
						if not controller.get_state()["is_on"]:
							controller.toggle_power()
					elif power in ("off", "0", "false"):
						if controller.get_state()["is_on"]:
							controller.toggle_power()
					else:
						errors.append("invalid_power")

				effect = self._get_param(params, "effect", "")
				if effect and not controller.set_effect(effect):
					errors.append("invalid_effect")

				color_mode = self._get_param(params, "color_mode", "") or self._get_param(params, "mode", "")
				if color_mode and not controller.set_color_mode(color_mode):
					errors.append("invalid_color_mode")

				preset = self._get_param(params, "preset", "")
				if preset and not controller.set_preset(preset):
					errors.append("invalid_preset")

				preset_intensity_raw = self._get_param(params, "preset_intensity", "")
				if preset_intensity_raw:
					if not controller.set_preset_intensity(preset_intensity_raw):
						errors.append("invalid_preset_intensity")

				brightness_raw = self._get_param(params, "brightness", "")
				if brightness_raw:
					try:
						brightness = float(brightness_raw)
						if brightness > 1.0:
							brightness = brightness / 100.0
						controller.set_brightness(brightness)
					except Exception:
						errors.append("invalid_brightness")

				color_hex = self._get_param(params, "color", "") or self._get_param(params, "hex", "")
				if color_hex:
					try:
						hex_value = color_hex.strip().lstrip("#")
						if len(hex_value) != 6:
							raise ValueError("invalid hex length")
						r = int(hex_value[0:2], 16)
						g = int(hex_value[2:4], 16)
						b = int(hex_value[4:6], 16)
						controller.set_custom_color(r, g, b)
					except Exception:
						errors.append("invalid_color")
				else:
					r_raw = self._get_param(params, "r", "")
					g_raw = self._get_param(params, "g", "")
					b_raw = self._get_param(params, "b", "")
					if r_raw or g_raw or b_raw:
						try:
							controller.set_custom_color(int(r_raw), int(g_raw), int(b_raw))
						except Exception:
							errors.append("invalid_rgb")

				action = self._get_param(params, "action", "").lower()
				if action == "shutdown":
					threading.Thread(target=poweroff_with_feedback, args=(controller,), daemon=True).start()
				elif action == "reboot":
					threading.Thread(target=reboot_with_feedback, args=(controller,), daemon=True).start()
				elif action:
					errors.append("invalid_action")

				state = controller.get_state()
				return {
					"ok": len(errors) == 0,
					"errors": errors,
					"state": state,
				}

			def _write_json(self, payload, status=200):
				body = json.dumps(payload).encode("utf-8")
				self.send_response(status)
				self.send_header("Content-Type", "application/json; charset=utf-8")
				self.send_header("Content-Length", str(len(body)))
				self.end_headers()
				try:
					self.wfile.write(body)
				except (BrokenPipeError, ConnectionResetError):
					self._log("json response aborted by client")

			def _write_jpeg(self, jpeg_bytes):
				try:
					self.send_response(200)
					self.send_header("Content-Type", "image/jpeg")
					self.send_header("Content-Length", str(len(jpeg_bytes)))
					self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
					self.send_header("Pragma", "no-cache")
					self.end_headers()
					self.wfile.write(jpeg_bytes)
				except (BrokenPipeError, ConnectionResetError):
					self._log("jpeg response aborted by client")

			def _read_json(self):
				length = int(self.headers.get("Content-Length", "0"))
				if length <= 0:
					return {}
				raw = self.rfile.read(length)
				if not raw:
					return {}
				return json.loads(raw.decode("utf-8"))

			def _write_html(self, html):
				body = html.encode("utf-8")
				self.send_response(200)
				self.send_header("Content-Type", "text/html; charset=utf-8")
				self.send_header("Content-Length", str(len(body)))
				self.end_headers()
				self.wfile.write(body)

			def _write_bytes(self, content_type, payload_bytes, cache_control=None):
				self.send_response(200)
				self.send_header("Content-Type", str(content_type))
				self.send_header("Content-Length", str(len(payload_bytes)))
				if cache_control:
					self.send_header("Cache-Control", str(cache_control))
				self.end_headers()
				try:
					self.wfile.write(payload_bytes)
				except (BrokenPipeError, ConnectionResetError):
					self._log("binary response aborted by client")

			@classmethod
			def _pwa_manifest_payload(cls):
				return {
					"id": "/",
					"name": "Laser AirCam",
					"short_name": "Laser AirCam",
					"description": "Laser AirCam control dashboard",
					"start_url": "/",
					"scope": "/",
					"display": "standalone",
					"background_color": "#041a2f",
					"theme_color": "#0c3a66",
								"version": str(APP_VERSION),
					"icons": [
						{"src": "/pwa-icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable"},
						{"src": "/pwa-icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"},
					],
				}

			@staticmethod
			def _png_chunk(tag, data):
				return (
					struct.pack("!I", len(data))
					+ tag
					+ data
					+ struct.pack("!I", zlib.crc32(tag + data) & 0xFFFFFFFF)
				)

			@classmethod
			def _build_pwa_icon_png(cls, size):
				size = int(size)
				if size in cls._pwa_icon_cache:
					return cls._pwa_icon_cache[size]

				# Lightweight icon renderer to avoid CPU spikes on low-power devices
				# when browsers request 512x512 during PWA install.
				cx = int(size * 0.36)
				cy = int(size * 0.5)
				radius = max(6, int(size * 0.18))
				ring = max(2, int(size * 0.05))
				cross = max(2, int(size * 0.03))
				beam_h = max(2, int(size * 0.06))
				beam_x0 = int(size * 0.50)
				beam_x1 = int(size * 0.88)
				beam_y0 = cy - beam_h // 2
				beam_y1 = cy + beam_h // 2
				r2 = radius * radius
				inner2 = max(0, (radius - ring) * (radius - ring))
				bar_h = int(radius * 0.72)

				rows = bytearray()
				max_index = max(1, size - 1)
				beam_span = max(1, beam_x1 - beam_x0)
				for y in range(size):
					rows.append(0)
					# Vertical base gradient with subtle top highlight.
					y_ratio = y / max_index
					base_r = int(6 + 24 * y_ratio)
					base_g = int(28 + 78 * y_ratio)
					base_b = int(54 + 115 * y_ratio)
					if y < int(size * 0.24):
						base_r = min(255, base_r + 8)
						base_g = min(255, base_g + 10)
						base_b = min(255, base_b + 12)

					for x in range(size):
						r = min(255, base_r + int(10 * (x / max_index)))
						g = min(255, base_g + int(7 * (x / max_index)))
						b = min(255, base_b + int(5 * (x / max_index)))

						dx = x - cx
						dy = y - cy
						d2 = dx * dx + dy * dy

						# Laser glyph ring + cross.
						if inner2 <= d2 <= r2 or (abs(dx) <= cross and abs(dy) <= bar_h) or (abs(dy) <= cross and abs(dx) <= bar_h):
							r, g, b = 255, 168, 168

						# Beam to the right with a warm gradient.
						if beam_x0 <= x <= beam_x1 and beam_y0 <= y <= beam_y1:
							t = (x - beam_x0) / beam_span
							r = 255
							g = int(198 - 112 * t)
							b = int(190 - 112 * t)

						rows.extend((r, g, b, 255))

				compressed = zlib.compress(bytes(rows), level=1)
				ihdr = struct.pack("!IIBBBBB", size, size, 8, 6, 0, 0, 0)
				png = (
					b"\x89PNG\r\n\x1a\n"
					+ cls._png_chunk(b"IHDR", ihdr)
					+ cls._png_chunk(b"IDAT", compressed)
					+ cls._png_chunk(b"IEND", b"")
				)
				cls._pwa_icon_cache[size] = png
				return png

			def log_message(self, format_str, *args):
				return

			def _laser_monitor_payload(self):
				if self._laser_manager is None:
					return {"state": "unavailable", "laser_active": False, "traffic_active": False, "config": {}}
				try:
					# Return the full payload expected by the dashboard (state + config).
					return self._laser_manager.get_payload()
				except Exception:
					return {"state": "unavailable", "laser_active": False, "traffic_active": False, "config": {}}

			def do_GET(self):
				parsed = urlparse(self.path)
				path = parsed.path
				params = parse_qs(parsed.query)

				if path == "/manifest.webmanifest":
					manifest = json.dumps(self._pwa_manifest_payload(), ensure_ascii=True).encode("utf-8")
					self._write_bytes("application/manifest+json; charset=utf-8", manifest, cache_control="no-store")
					return

				if path in ("/pwa-icon-192.png", "/icon-192.png"):
					icon = self._build_pwa_icon_png(192)
					self._write_bytes("image/png", icon, cache_control="public, max-age=604800")
					return

				if path in ("/pwa-icon-512.png", "/icon-512.png"):
					icon = self._build_pwa_icon_png(512)
					self._write_bytes("image/png", icon, cache_control="public, max-age=604800")
					return

				if path in ("/favicon.png", "/favicon.ico"):
					icon = self._build_pwa_icon_png(192)
					self._write_bytes("image/png", icon, cache_control="public, max-age=604800")
					return

				if path == "/api/state":
					state = controller.get_state()
					if self._air_assist is not None:
						try:
							aa = self._air_assist.get_state()
							state["airassist"] = {
								"enabled": bool(aa.get("enabled", False)),
								"auto_mode": bool(aa.get("auto_mode", False)),
								"speed": int(aa.get("speed", 0)),
							}
						except Exception:
							pass
					self._write_json(state)
					return

				if path == "/api/camera/settings":
					self._write_json(self._camera_settings_payload())
					return

				if path == "/api/camera/v4l2":
					self._write_json(self._camera_v4l2_payload())
					return

				if path in ("/camera-controls", "/camera-v4l2", "/v4l2"):
					self._log(f"GET {path}")
					self._write_html(self._camera_controls_html())
					return

				if path in ("/hook", "/api/webhook", "/api/set"):
					result = self._apply_webhook_params(params)
					self._write_json(result, status=200 if result["ok"] else 400)
					return

				if path == "/stream":
					try:
						settings = load_camera_settings()
						width, height, _ = parse_resolution(settings["stream_resolution"])
						fps = settings["stream_fps"]
					except Exception as exc:
						self._write_json({"error": "stream_config_failed", "detail": str(exc)}, status=500)
						return
					self._proxy_ustreamer_stream(width, height, fps)
					return

				if path == "/streamhd":
					try:
						settings = load_camera_settings()
						interval_s = settings["streamhd_interval_s"]
					except Exception as exc:
						self._write_json({"error": "streamhd_config_failed", "detail": str(exc)}, status=500)
						return
					self._stream_mjpeg_interval_capture(settings, float(interval_s))
					return

				if path in ("/snapshot", "/snap.jpg", "/photo.jpg", "/snap", "/foto"):
					try:
						settings = load_camera_settings()
						width, height, _ = parse_resolution(settings["screenshot_resolution"])
						token = self._claim_camera_owner("snapshot", self.client_address[0])
						self._stop_active_stream("snapshot")
						try:
							jpeg = self._capture_camera_jpeg_bytes(width, height)
						finally:
							self._release_camera_owner(token)
					except Exception as exc:
						self._set_camera_notice(f"Snapshot failed: {exc}", level="warn", ttl_s=12.0)
						self._write_json({"error": "capture_failed", "detail": str(exc)}, status=500)
						return
					self._write_jpeg(jpeg)
					return

				if path == "/api/system/stats":
					stats = get_system_stats()
					stats.update(self._camera_status_payload())
					laser = self._laser_monitor_payload()
					stats["laser_state"] = laser.get("state", "idle")
					stats["laser_active"] = bool(laser.get("laser_active", False))
					stats["laser_traffic_active"] = bool(laser.get("traffic_active", False))
					stats["laser_last_error"] = str(laser.get("last_error", "") or "")
					self._write_json(stats)
					return

				if path == "/api/laser-monitor":
					self._write_json(self._laser_monitor_payload())
					return

				if path == "/api/airassist":
					if self._air_assist is None:
						self._write_json({"error": "air_assist_unavailable"}, status=500)
						return
					self._write_json(self._air_assist.get_state())
					return

				if path == "/api/app/settings":
					if self._laser_manager is None:
						self._write_json({"error": "laser_manager unavailable"}, status=500)
						return
					payload = self._laser_manager.get_payload()
					self._write_json(payload.get("config", {}))
					return

				if path == "/api/laser/state":
					if self._laser_manager is None:
						self._write_json({"error": "laser_manager unavailable"}, status=500)
						return
					payload = self._laser_manager.get_payload()
					self._write_json(payload)
					return

				if path == "/api/laser/serial-link":
					if self._laser_manager is None:
						self._write_json({"error": "laser_manager unavailable"}, status=500)
						return
					self._write_json(self._laser_manager.serial_link_state())
					return

				if path == "/":
					self._write_html(self._page_html())
					return
				

			def do_POST(self):
				try:
					payload = self._read_json()
				except Exception:
					self._write_json({"error": "invalid_json"}, status=400)
					return

				if self.path == "/api/effect":
					effect = payload.get("effect", "")
					if not controller.set_effect(effect):
						self._write_json({"error": "invalid_effect"}, status=400)
						return
					self._write_json(controller.get_state())
					return

				if self.path == "/api/color-mode":
					color_mode = payload.get("color_mode", "")
					if not controller.set_color_mode(color_mode):
						self._write_json({"error": "invalid_color_mode"}, status=400)
						return
					self._write_json(controller.get_state())
					return

				if self.path == "/api/preset":
					preset_name = payload.get("preset", "")
					if not controller.set_preset(preset_name):
						self._write_json({"error": "invalid_preset"}, status=400)
						return
					self._write_json(controller.get_state())
					return

				if self.path == "/api/preset-intensity":
					if not controller.set_preset_intensity(payload.get("intensity", 100)):
						self._write_json({"error": "invalid_preset_intensity"}, status=400)
						return
					self._write_json(controller.get_state())
					return

				if self.path == "/api/color":
					try:
						controller.set_custom_color(payload.get("r", 0), payload.get("g", 0), payload.get("b", 0))
					except Exception:
						self._write_json({"error": "invalid_color"}, status=400)
						return
					self._write_json(controller.get_state())
					return

				if self.path == "/api/brightness":
					try:
						controller.set_brightness(payload.get("brightness", 0.3))
					except Exception:
						self._write_json({"error": "invalid_brightness"}, status=400)
						return
					self._write_json(controller.get_state())
					return

				if self.path == "/api/power":
					controller.toggle_power()
					self._write_json(controller.get_state())
					return

				if self.path == "/api/shutdown":
					threading.Thread(target=poweroff_with_feedback, args=(controller,), daemon=True).start()
					self._write_json({"ok": True})
					return

				if self.path == "/api/reboot":
					threading.Thread(target=reboot_with_feedback, args=(controller,), daemon=True).start()
					self._write_json({"ok": True})
					return

				if self.path == "/api/camera/capture":
					try:
						settings = load_camera_settings()
						width, height, _ = parse_resolution(settings["screenshot_resolution"])
						token = self._claim_camera_owner("snapshot", self.client_address[0])
						self._stop_active_stream("snapshot")
						try:
							jpeg = self._capture_camera_jpeg_bytes(width, height)
						finally:
							self._release_camera_owner(token)
					except Exception as exc:
						self._set_camera_notice(f"Snapshot failed: {exc}", level="warn", ttl_s=12.0)
						self._write_json({"ok": False, "error": "capture_failed", "detail": str(exc)}, status=500)
						return
					self._write_jpeg(jpeg)
					return

				if self.path == "/api/camera/settings/screenshot":
					try:
						_, _, normalized = parse_resolution(payload.get("resolution", ""))
						settings = load_camera_settings()
						settings["screenshot_resolution"] = normalized
						save_camera_settings(settings)
					except Exception as exc:
						self._write_json({"ok": False, "error": "invalid_resolution", "detail": str(exc)}, status=400)
						return
					self._write_json({"ok": True, **self._camera_settings_payload()})
					return

				if self.path == "/api/camera/settings/stream":
					try:
						resolution_raw = payload.get("resolution", "")
						fps_raw = payload.get("fps", None)
						settings = load_camera_settings()
						if resolution_raw:
							_, _, settings["stream_resolution"] = parse_resolution(resolution_raw)
						if fps_raw is not None:
							new_fps = int(fps_raw)
							if new_fps < 1 or new_fps > 120:
								raise ValueError("fps out of range (1-120)")
							settings["stream_fps"] = new_fps
						if not resolution_raw and fps_raw is None:
							raise ValueError("resolution or fps required")
						save_camera_settings(settings)
						if self._ustreamer is not None:
							self._ustreamer.stop("ustreamer stream settings updated")
					except Exception as exc:
						self._write_json({"ok": False, "error": "update_stream_failed", "detail": str(exc)}, status=500)
						return
					self._write_json({"ok": True, **self._camera_settings_payload()})
					return

				if self.path == "/api/camera/settings/streamhd":
					try:
						interval_raw = payload.get("interval_seconds", None)
						if interval_raw is None:
							raise ValueError("interval_seconds required")
						interval_value = int(interval_raw)
						if interval_value < 1 or interval_value > 60:
							raise ValueError("interval_seconds out of range (1-60)")
						settings = load_camera_settings()
						settings["streamhd_interval_s"] = interval_value
						save_camera_settings(settings)
					except Exception as exc:
						self._write_json({"ok": False, "error": "update_streamhd_failed", "detail": str(exc)}, status=500)
						return
					self._write_json({"ok": True, **self._camera_settings_payload()})
					return

				if self.path == "/api/camera/settings/mqtt-image":
					try:
						enabled_raw = payload.get("enabled", None)
						if enabled_raw is None:
							raise ValueError("enabled required")
						if isinstance(enabled_raw, bool):
							enabled = 1 if enabled_raw else 0
						elif isinstance(enabled_raw, (int, float)):
							enabled = 1 if int(enabled_raw) else 0
						else:
							text = str(enabled_raw).strip().lower()
							if text in ("1", "true", "yes", "on"):
								enabled = 1
							elif text in ("0", "false", "no", "off"):
								enabled = 0
							else:
								raise ValueError("enabled must be boolean")
						settings = load_camera_settings()
						settings["mqtt_image_enabled"] = enabled
						save_camera_settings(settings)
						self._log(f"mqtt image feed set to {enabled}")
					except Exception as exc:
						self._write_json({"ok": False, "error": "update_mqtt_image_failed", "detail": str(exc)}, status=400)
						return
					self._write_json({"ok": True, **self._camera_settings_payload()})
					return

				if self.path == "/api/laser-monitor/config":
					try:
						if self._laser_manager is None:
							raise RuntimeError("laser monitor unavailable")
						self._log(f"laser monitor config patch: {payload}")
						updated = self._laser_manager.update_settings(payload)
					except Exception as exc:
						self._write_json({"ok": False, "error": "laser_config_failed", "detail": str(exc)}, status=400)
						return
					self._write_json({"ok": True, **updated})
					return

				if self.path == "/api/laser-monitor/clear-error":
					if self._laser_manager is None:
						self._write_json({"ok": False, "error": "laser_monitor_unavailable"}, status=500)
						return
					self._laser_manager.clear_error()
					self._write_json({"ok": True, **self._laser_manager.get_payload()})
					return

				if self.path == "/api/laser/gcode":
					try:
						if self._laser_manager is None:
							raise RuntimeError("laser manager unavailable")
						command = str(payload.get("command", "") or "").strip()
						if not command:
							raise ValueError("command is required")
						source = str(payload.get("source", "api") or "api")
						result = self._laser_manager.send_gcode_command(command, source=source)
					except Exception as exc:
						self._write_json({"ok": False, "error": "laser_gcode_failed", "detail": str(exc)}, status=400)
						return
					self._write_json({"ok": True, **result, "serial_link": self._laser_manager.serial_link_state()})
					return

				if self.path == "/api/laser/queue/clear":
					try:
						if self._laser_manager is None:
							raise RuntimeError("laser manager unavailable")
						source = str(payload.get("source", "api") or "api")
						result = self._laser_manager.clear_command_queue(source=source)
					except Exception as exc:
						self._write_json({"ok": False, "error": "laser_clear_queue_failed", "detail": str(exc)}, status=400)
						return
					self._write_json({"ok": True, **result, "serial_link": self._laser_manager.serial_link_state()})
					return

				if self.path == "/api/laser/jog":
					try:
						if self._laser_manager is None:
							raise RuntimeError("laser manager unavailable")
						direction = str(payload.get("direction", "") or "").strip().lower()
						if not direction:
							raise ValueError("direction is required")
						step_raw = payload.get("step_mm", None)
						feed_sec_raw = payload.get("feed_mm_sec", None)
						source = str(payload.get("source", "api") or "api")
						result = self._laser_manager.send_jog_command(direction=direction, step_mm=step_raw, feed_mm_sec=feed_sec_raw, source=source)
					except Exception as exc:
						self._write_json({"ok": False, "error": "laser_jog_failed", "detail": str(exc)}, status=400)
						return
					self._write_json({"ok": True, **result, "serial_link": self._laser_manager.serial_link_state()})
					return

				if self.path == "/api/laser/custom-position":
					try:
						if self._laser_manager is None:
							raise RuntimeError("laser manager unavailable")
						source = str(payload.get("source", "api") or "api")
						result = self._laser_manager.execute_custom_position(source=source)
					except Exception as exc:
						self._write_json({"ok": False, "error": "laser_custom_position_failed", "detail": str(exc)}, status=400)
						return
					self._write_json({"ok": True, **result, "serial_link": self._laser_manager.serial_link_state()})
					return

				if self.path == "/api/camera/settings/v4l2":
					try:
						if not payload:
							raise ValueError("at least one v4l2 parameter required")
						settings = load_camera_settings()
						for key, value in payload.items():
							if key in V4L2_DEFAULTS:
								settings[key] = value
						controls = normalize_v4l2_settings(settings)
						save_camera_settings(settings)
						if self._ustreamer is not None:
							self._ustreamer.stop("ustreamer v4l2 settings updated")
						apply_v4l2_controls(controls)
						update_systemd_service(controls)
						self._log("v4l2 settings updated")
					except Exception as exc:
						self._write_json({"ok": False, "error": "v4l2_update_failed", "detail": str(exc)}, status=500)
						return
					self._write_json({"ok": True, **self._camera_settings_payload()})
					return

				if self.path == "/api/camera/v4l2/preview":
					try:
						self._log("POST /api/camera/v4l2/preview")
						if not payload:
							raise ValueError("payload required")
						settings = load_camera_settings()
						for key, value in payload.items():
							if key in V4L2_DEFAULTS:
								settings[key] = value
						controls = normalize_v4l2_settings(settings)
						apply_v4l2_controls(controls)
					except Exception as exc:
						self._write_json({"ok": False, "error": "v4l2_preview_failed", "detail": str(exc)}, status=500)
						return
					self._write_json({"ok": True, "controls": controls})
					return

				if self.path == "/api/camera/v4l2/save":
					try:
						self._log("POST /api/camera/v4l2/save")
						if not payload:
							raise ValueError("payload required")
						settings = load_camera_settings()
						for key, value in payload.items():
							if key in V4L2_DEFAULTS:
								settings[key] = value
						controls = normalize_v4l2_settings(settings)
						save_camera_settings(settings)
						if self._ustreamer is not None:
							self._ustreamer.stop("ustreamer v4l2 profile saved")
						apply_v4l2_controls(controls)
						update_systemd_service(controls)
					except Exception as exc:
						self._write_json({"ok": False, "error": "v4l2_save_failed", "detail": str(exc)}, status=500)
						return
					self._write_json({"ok": True, "controls": controls})
					return

				if self.path == "/api/camera/v4l2/reset-defaults":
					try:
						self._log("POST /api/camera/v4l2/reset-defaults")
						settings = load_camera_settings()
						for key, value in V4L2_DEFAULTS.items():
							settings[key] = value
						controls = normalize_v4l2_settings(settings)
						save_camera_settings(settings)
						if self._ustreamer is not None:
							self._ustreamer.stop("ustreamer v4l2 reset defaults")
						apply_v4l2_controls(controls)
						update_systemd_service(controls)
					except Exception as exc:
						self._write_json({"ok": False, "error": "v4l2_reset_defaults_failed", "detail": str(exc)}, status=500)
						return
					self._write_json({"ok": True, "controls": controls})
					return

				if self.path == "/api/airassist/power":
					if self._air_assist is None:
						self._write_json({"ok": False, "error": "air_assist_unavailable"}, status=500)
						return
					enabled_raw = payload.get("enabled")
					if enabled_raw is None:
						self._write_json({"ok": False, "error": "enabled_required"}, status=400)
						return
					if isinstance(enabled_raw, str):
						enabled = enabled_raw.strip().lower() in ("1", "true", "yes", "on")
					else:
						enabled = bool(enabled_raw)
					if self._laser_manager is not None:
						state = self._laser_manager.set_airassist_power(enabled, source="api")
					else:
						self._air_assist.set_enabled(enabled)
						state = self._air_assist.get_state()
					self._write_json({"ok": True, **state})
					return

				if self.path == "/api/airassist/speed":
					if self._air_assist is None:
						self._write_json({"ok": False, "error": "air_assist_unavailable"}, status=500)
						return
					speed_raw = payload.get("speed")
					if speed_raw is None:
						self._write_json({"ok": False, "error": "speed_required"}, status=400)
						return
					try:
						self._air_assist.set_speed(speed_raw)
						persisted = load_app_settings()
						persisted["airassist_speed"] = self._air_assist.get_state().get("speed", AIR_ASSIST_DEFAULT_SPEED)
						save_app_settings(persisted)
					except Exception as exc:
						self._write_json({"ok": False, "error": "invalid_speed", "detail": str(exc)}, status=400)
						return
					self._write_json({"ok": True, **self._air_assist.get_state()})
					return

				if self.path == "/api/airassist/auto":
					if self._air_assist is None:
						self._write_json({"ok": False, "error": "air_assist_unavailable"}, status=500)
						return
					auto_mode = payload.get("auto_mode")
					range_min = payload.get("auto_range_min")
					range_max = payload.get("auto_range_max")
					auto_min_pwm = payload.get("auto_min_pwm")
					laser_max = payload.get("laser_max_power")
					if auto_mode is not None:
						if isinstance(auto_mode, str):
							auto_mode = auto_mode.strip().lower() in ("1", "true", "yes", "on")
						if self._laser_manager is not None:
							self._laser_manager.set_airassist_auto_mode(bool(auto_mode), source="api")
						else:
							self._air_assist.set_auto_mode(bool(auto_mode))
					if range_min is not None or range_max is not None or auto_min_pwm is not None:
						try:
							state_before = self._air_assist.get_state()
							effective_min = state_before.get("auto_range_min", 0) if range_min is None else range_min
							effective_max = state_before.get("auto_range_max", 100) if range_max is None else range_max
							self._air_assist.set_auto_range(effective_min, effective_max)
							if auto_min_pwm is not None:
								self._air_assist.set_auto_min_pwm(auto_min_pwm)
							persisted = load_app_settings()
							state = self._air_assist.get_state()
							persisted["airassist_auto_range_min"] = state.get("auto_range_min", 0)
							persisted["airassist_auto_range_max"] = state.get("auto_range_max", 100)
							persisted["airassist_auto_min_pwm"] = state.get("auto_min_pwm", 0)
							save_app_settings(persisted)
						except Exception as exc:
							self._write_json({"ok": False, "error": "invalid_range", "detail": str(exc)}, status=400)
							return
					if laser_max is not None:
						try:
							if self._laser_manager is not None:
								updated_payload = self._laser_manager.update_settings({"laserbeam_nominal_maxpower": int(round(float(laser_max)))})
								persisted_max = int(updated_payload.get("config", {}).get("laserbeam_nominal_maxpower", laser_max))
							else:
								persisted_max = int(round(float(laser_max)))
							self._air_assist.set_laser_max_power(persisted_max)
						except Exception as exc:
							self._write_json({"ok": False, "error": "invalid_laser_max_power", "detail": str(exc)}, status=400)
							return
					self._write_json({"ok": True, **self._air_assist.get_state()})
					return

				if self.path == "/api/airassist/listen_events":
					if self._air_assist is None:
						self._write_json({"ok": False, "error": "air_assist_unavailable"}, status=500)
						return
					listen_raw = payload.get("listen_events")
					if listen_raw is None:
						self._write_json({"ok": False, "error": "listen_events_required"}, status=400)
						return
					if isinstance(listen_raw, str):
						listen = listen_raw.strip().lower() in ("1", "true", "yes", "on")
					else:
						listen = bool(listen_raw)
					self._air_assist.set_listen_events(listen)
					persisted = load_app_settings()
					persisted["airassist_listen_events"] = 1 if listen else 0
					save_app_settings(persisted)
					self._write_json({"ok": True, **self._air_assist.get_state()})
					return

				self._write_json({"error": "not_found"}, status=404)
				return

			@staticmethod
			def _camera_controls_html():
				return camera_controls_html()
			@staticmethod
			def _page_html():
				return page_html(APP_VERSION)

		return Handler


def main():
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(GPIO_LED_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(GPIO_POWER_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(GPIO_MODE_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)

	pixels = neopixel.NeoPixel(
		PIXEL_PIN,
		NUM_PIXELS,
		brightness=BRIGHTNESS,
		auto_write=False,
		pixel_order=ORDER,
	)

	controller = LedController(pixels)
	app_settings = load_app_settings()
	controller.set_brightness(app_settings.get("led_default_brightness", BRIGHTNESS))
	if int(app_settings.get("led_on_boot", 1)) != 1 and controller.get_state().get("is_on"):
		controller.toggle_power()
	web = LedWebServer(controller, host=WEB_HOST, port=WEB_PORT)
	apply_saved_camera_controls()

	button_manager = ButtonRuntimeManager(
		controller=controller,
		laser_manager=web.laser_manager,
		led_pin=GPIO_LED_BUTTON,
		power_pin=GPIO_POWER_BUTTON,
		mode_pin=GPIO_MODE_BUTTON,
		click_window_s=CLICK_WINDOW_S,
		debounce_s=DEBOUNCE_S,
		poll_interval_s=POLL_INTERVAL_S,
		reboot_callback=lambda: threading.Thread(target=reboot_with_feedback, args=(controller,), daemon=True).start(),
		shutdown_callback=lambda: threading.Thread(target=poweroff_with_feedback, args=(controller,), daemon=True).start(),
		logger=lambda m: print(f"[buttons] {m}", flush=True),
	)
	web.laser_manager.bind_buttons_manager(button_manager)

	web.start()
	button_manager.start()

	mqtt_bridge = create_homeassistant_bridge(web_port=WEB_PORT)
	if mqtt_bridge is not None:
		mqtt_bridge.start()

	controller.play_startup_effect()

	try:
		controller.run()
	except KeyboardInterrupt:
		pass
	finally:
		if mqtt_bridge is not None:
			mqtt_bridge.stop()
		web.stop()
		button_manager.stop()
		controller.stop()
		pixels.fill((0, 0, 0))
		pixels.show()
		GPIO.cleanup()


if __name__ == "__main__":
	main()

