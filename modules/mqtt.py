import hashlib
import json
import socket
import threading
import time
import urllib.error
import urllib.request

from settings import DEVICE_ID
from settings import DEVICE_NAME
from settings import HA_CAMERA_FPS
from settings import HA_DISCOVERY_PREFIX
from settings import MQTT_BASE_TOPIC
from settings import MQTT_CLIENT_ID
from settings import MQTT_ENABLE
from settings import MQTT_HOST
from settings import MQTT_KEEPALIVE
from settings import MQTT_PASSWORD
from settings import MQTT_PORT
from settings import MQTT_USERNAME
from settings import PUBLIC_BASE_URL
from settings import PUBLIC_HOST
from settings import RESOLUTION_PRESETS as CAMERA_RESOLUTION_PRESETS
from settings import USTREAMER_PORT
APP_VERSION = "1.2"


def create_homeassistant_bridge(web_port=80):
	if not bool(MQTT_ENABLE):
		return None
	try:
		import paho.mqtt.client as mqtt
	except Exception as exc:
		print(f"[mqtt] disabled: paho-mqtt not available ({exc})", flush=True)
		return None
	return HomeAssistantMqttBridge(mqtt_module=mqtt, web_port=web_port)


class HomeAssistantMqttBridge:
	POLL_INTERVAL_S = 2.0
	HTTP_TIMEOUT_S = 12
	HTTP_TIMEOUT_V4L2_SAVE_S = 35
	STREAM_READ_CHUNK = 65536

	LED_EFFECTS = [
		"static",
		"breathe",
		"pulse",
		"strobe",
		"flash",
		"fire",
		"disco",
		"snake",
		"twinkle",
	]
	LED_EFFECT_LABELS = {
		"static": "Static",
		"breathe": "Breathe",
		"pulse": "Pulse",
		"strobe": "Strobe",
		"flash": "Flash",
		"fire": "Fire",
		"disco": "Disco",
		"snake": "Snake",
		"twinkle": "Twinkle",
	}
	LED_COLOR_MODES = [
		"cool_white",
		"warm_white",
		"amber_boost",
		"sunset_orange",
		"laser_green",
		"ruby_red",
		"ice_cyan",
		"magenta_pink",
		"blue_intense",
		"blue_soft",
		"green_intense",
		"green_soft",
		"red_intense",
		"red_soft",
		"cyan_intense",
		"cyan_soft",
		"magenta_intense",
		"magenta_soft",
		"amber_intense",
		"amber_soft",
		"random_solid",
		"random_per_led",
		"custom_solid",
	]
	LED_COLOR_MODE_LABELS = {
		"cool_white": "Cool White",
		"warm_white": "Warm White",
		"amber_boost": "Amber Boost",
		"sunset_orange": "Sunset Orange",
		"laser_green": "Laser Green",
		"ruby_red": "Ruby Red",
		"ice_cyan": "Ice Cyan",
		"magenta_pink": "Magenta Pink",
		"blue_intense": "Blue Intense",
		"blue_soft": "Blue Soft",
		"green_intense": "Green Intense",
		"green_soft": "Green Soft",
		"red_intense": "Red Intense",
		"red_soft": "Red Soft",
		"cyan_intense": "Cyan Intense",
		"cyan_soft": "Cyan Soft",
		"magenta_intense": "Magenta Intense",
		"magenta_soft": "Magenta Soft",
		"amber_intense": "Amber Intense",
		"amber_soft": "Amber Soft",
		"random_solid": "Random Solid",
		"random_per_led": "Random Per LED",
		"custom_solid": "Custom Solid",
	}
	LED_PRESETS = [
		"none",
		"ocean_wave",
		"red_fire",
		"green_forest",
		"sunset_lava",
		"ice_plasma",
	]
	LED_PRESET_LABELS = {
		"none": "Off",
		"ocean_wave": "Ocean Wave",
		"red_fire": "Red Fire",
		"green_forest": "Green Forest",
		"sunset_lava": "Sunset Lava",
		"ice_plasma": "Ice Plasma",
	}
	LIGHT_EFFECT_OPTIONS = [
		"Static",
		"Breathe",
		"Pulse",
		"Strobe",
		"Flash",
		"Fire",
		"Disco",
		"Snake",
		"Twinkle",
		"Off",
		"Ocean Wave",
		"Red Fire",
		"Green Forest",
		"Sunset Lava",
		"Ice Plasma",
	]
	RESOLUTION_PRESETS = list(CAMERA_RESOLUTION_PRESETS)

	V4L2_LABELS = {
		"brightness": "Camera Brightness",
		"contrast": "Camera Contrast",
		"saturation": "Camera Saturation",
		"sharpness": "Camera Sharpness",
		"compression_quality": "JPEG Quality",
		"power_line_frequency": "Power Line Frequency",
		"horizontal_flip": "Horizontal Flip",
		"vertical_flip": "Vertical Flip",
		"rotate": "Rotation",
		"auto_exposure": "Exposure",
		"exposure_time_absolute": "Exposure Time",
		"exposure_dynamic_framerate": "Dynamic FPS",
		"auto_exposure_bias": "Exposure Compensation",
		"white_balance_auto_preset": "White Balance",
		"iso_sensitivity_auto": "ISO Auto",
		"iso_sensitivity": "ISO Manual",
		"exposure_metering_mode": "Exposure Metering",
		"scene_mode": "Scene",
	}

	V4L2_ENTITY_IDS = {
		"brightness": "camera_brightness",
		"contrast": "camera_contrast",
		"saturation": "camera_saturation",
		"sharpness": "camera_sharpness",
		"compression_quality": "jpeg_quality",
		"power_line_frequency": "power_line_filter",
		"horizontal_flip": "horizontal_flip",
		"vertical_flip": "vertical_flip",
		"rotate": "rotation",
		"auto_exposure": "exposure_mode",
		"exposure_time_absolute": "exposure_time",
		"exposure_dynamic_framerate": "dynamic_fps",
		"auto_exposure_bias": "exposure_compensation",
		"white_balance_auto_preset": "white_balance",
		"iso_sensitivity_auto": "auto_iso",
		"iso_sensitivity": "manual_iso",
		"exposure_metering_mode": "exposure_metering",
		"scene_mode": "scene_mode",
	}

	V4L2_ICONS = {
		"brightness": "mdi:brightness-6",
		"contrast": "mdi:contrast-box",
		"saturation": "mdi:palette-outline",
		"sharpness": "mdi:image-filter-center-focus",
		"compression_quality": "mdi:file-image-outline",
		"power_line_frequency": "mdi:sine-wave",
		"horizontal_flip": "mdi:flip-horizontal",
		"vertical_flip": "mdi:flip-vertical",
		"rotate": "mdi:rotate-right",
		"auto_exposure": "mdi:camera-iris",
		"exposure_time_absolute": "mdi:timer-outline",
		"exposure_dynamic_framerate": "mdi:movie-open-cog-outline",
		"auto_exposure_bias": "mdi:tune-variant",
		"white_balance_auto_preset": "mdi:white-balance-auto",
		"iso_sensitivity_auto": "mdi:auto-fix",
		"iso_sensitivity": "mdi:numeric",
		"exposure_metering_mode": "mdi:image-filter-hdr",
		"scene_mode": "mdi:weather-sunset",
	}

	def __init__(self, mqtt_module, web_port):
		self._mqtt = mqtt_module
		self._web_port = int(web_port)
		self._api_base = f"http://127.0.0.1:{self._web_port}"
		self._host = str(PUBLIC_HOST).strip() or self._detect_public_host()
		default_base_url = f"http://{self._host}"
		if self._web_port != 80:
			default_base_url = f"{default_base_url}:{self._web_port}"
		self._public_base_url = (str(PUBLIC_BASE_URL).strip() or default_base_url).rstrip("/")
		self._mqtt_host = str(MQTT_HOST)
		self._mqtt_port = int(MQTT_PORT)
		self._mqtt_keepalive = int(MQTT_KEEPALIVE)
		self._mqtt_username = str(MQTT_USERNAME)
		self._mqtt_password = str(MQTT_PASSWORD)
		self._base_topic = str(MQTT_BASE_TOPIC).strip("/")
		self._discovery_prefix = str(HA_DISCOVERY_PREFIX).strip("/")
		self._device_name = str(DEVICE_NAME)
		device_id_value = str(DEVICE_ID).strip()
		self._device_id = device_id_value or f"lasercam_{socket.gethostname().lower()}"
		self._running = False
		self._connected = False
		self._poll_thread = None
		self._state_cache = {}
		self._lock = threading.Lock()
		self._http_cache = {}
		self._v4l2_options = {}
		self._snapshot_worker_thread = None
		self._snapshot_worker_stop = threading.Event()
		self._camera_snapshot_interval_s = max(0.5, float(HA_CAMERA_FPS) ** -1)
		self._ustreamer_port = int(USTREAMER_PORT)
		self._last_snapshot_digest = ""

		client_id = str(MQTT_CLIENT_ID).strip() or f"{self._device_id}_bridge"
		try:
			self._client = self._mqtt.Client(self._mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)
		except Exception:
			self._client = self._mqtt.Client(client_id=client_id)
		if self._mqtt_username:
			self._client.username_pw_set(self._mqtt_username, self._mqtt_password)
		self._client.will_set(self._availability_topic, payload="offline", qos=1, retain=True)
		self._client.on_connect = self._on_connect
		self._client.on_disconnect = self._on_disconnect
		self._client.on_message = self._on_message

	@property
	def _availability_topic(self):
		return f"{self._base_topic}/availability"

	def _detect_public_host(self):
		host = socket.gethostname().strip()
		if host and "." not in host:
			return f"{host}.local"
		if host:
			return host
		try:
			return socket.gethostbyname(socket.gethostname())
		except Exception:
			return "DEVICE_IP"

	def start(self):
		if self._running:
			return
		self._running = True
		self._client.connect_async(self._mqtt_host, self._mqtt_port, self._mqtt_keepalive)
		self._client.loop_start()
		self._poll_thread = threading.Thread(target=self._poll_loop, daemon=True)
		self._poll_thread.start()
		self._snapshot_worker_stop.clear()
		self._snapshot_worker_thread = threading.Thread(target=self._snapshot_worker_loop, daemon=True)
		self._snapshot_worker_thread.start()
		print(f"[mqtt] bridge enabled broker={self._mqtt_host}:{self._mqtt_port} topic={self._base_topic}", flush=True)

	def stop(self):
		if not self._running:
			return
		self._running = False
		try:
			self._publish(self._availability_topic, "offline", retain=True)
			self._publish(self._topic("state/camera/ha_available"), "offline", retain=True)
		except Exception:
			pass
		self._snapshot_worker_stop.set()
		if self._snapshot_worker_thread is not None:
			self._snapshot_worker_thread.join(timeout=2.0)
			self._snapshot_worker_thread = None
		try:
			self._client.disconnect()
		except Exception:
			pass
		self._client.loop_stop()
		if self._poll_thread is not None:
			self._poll_thread.join(timeout=1.5)

	def _log(self, message):
		print(f"[mqtt] {message}", flush=True)

	def _on_connect(self, client, userdata, flags, reason_code, properties=None):
		self._connected = True
		self._log(f"connected rc={reason_code}")
		self._client.publish(self._availability_topic, payload="online", qos=1, retain=True)
		# Populate _v4l2_options before publishing discovery so menu controls
		# are registered as "select" entities with proper labels.
		self._refresh_v4l2_state()
		self._publish_discovery()
		for topic in self._command_topics():
			self._client.subscribe(topic, qos=1)
		self._publish_full_state(force=True)

	def _on_disconnect(self, client, userdata, disconnect_flags=None, reason_code=None, properties=None):
		self._connected = False
		self._log(f"disconnected rc={reason_code}")

	def _command_topics(self):
		topics = [
			self._topic("cmd/led/power"),
			self._topic("cmd/led/brightness"),
			self._topic("cmd/led/effect"),
			self._topic("cmd/led/color_mode"),
			self._topic("cmd/led/rgb_color"),
			self._topic("cmd/led/preset"),
			self._topic("cmd/led/preset_intensity"),
			self._topic("cmd/camera/stream_resolution"),
			self._topic("cmd/camera/stream_fps"),
			self._topic("cmd/camera/screenshot_resolution"),
			self._topic("cmd/camera/streamhd_interval"),
			self._topic("cmd/camera/mqtt_image"),
			self._topic("cmd/camera/capture"),
			self._topic("cmd/camera/reset_defaults"),
			self._topic("cmd/system/reboot"),
			self._topic("cmd/system/shutdown"),
			self._topic("cmd/laser/led_on_boot"),
			self._topic("cmd/laser/serial_proxy_enabled"),
			self._topic("cmd/laser/led_sync"),
			self._topic("cmd/laser/idle_effect"),
			self._topic("cmd/laser/idle_color_mode"),
			self._topic("cmd/laser/running_effect"),
			self._topic("cmd/laser/running_color_mode"),
			self._topic("cmd/laser/error_effect"),
			self._topic("cmd/laser/error_color_mode"),
			self._topic("cmd/laser/engrave_complete_effect"),
			self._topic("cmd/laser/engrave_complete_color_mode"),
			self._topic("cmd/laser/clear_error"),
			self._topic("cmd/laser/clear_queue"),
			self._topic("cmd/laser/clear_state"),
			self._topic("cmd/laser/gcode"),
			self._topic("cmd/laser/custom_position"),
			self._topic("cmd/laser/custom_pos_x_mm"),
			self._topic("cmd/laser/custom_pos_y_mm"),
			self._topic("cmd/laser/custom_pos_z_mm"),
			self._topic("cmd/laser/custom_pos_use_g0"),
			self._topic("cmd/laser/move_step_mm"),
			self._topic("cmd/laser/move_feed_mm_min"),
			self._topic("cmd/laser/jog/up"),
			self._topic("cmd/laser/jog/down"),
			self._topic("cmd/laser/jog/left"),
			self._topic("cmd/laser/jog/right"),
			self._topic("cmd/laser/jog/home"),
		]
		for key in self.V4L2_LABELS:
			topics.append(self._topic(f"cmd/v4l2/{key}"))
		topics.append(self._topic("cmd/airassist/power"))
		topics.append(self._topic("cmd/airassist/auto"))
		topics.append(self._topic("cmd/airassist/speed"))
		topics.append(self._topic("cmd/airassist/auto_range_min"))
		topics.append(self._topic("cmd/airassist/auto_range_max"))
		return topics

	def _topic(self, suffix):
		return f"{self._base_topic}/{suffix}"

	def _discovery_topic(self, component, object_id):
		return f"{self._discovery_prefix}/{component}/{self._device_id}/{object_id}/config"

	def _device_block(self):
		return {
			"identifiers": [self._device_id],
			"name": self._device_name,
			"manufacturer": "WaveLov3r",
			"model": "Laser AirCam Controller",
			"sw_version": f"{APP_VERSION}",
		}

	def _publish_discovery(self):
		entities = []
		# Remove legacy standalone LED power switch: the light entity already exposes power control.
		self._publish(self._discovery_topic("switch", "led_power"), "", retain=True)
		entities.append((
			"number",
			"led_brightness",
			{
				"name": "LED Brightness",
				"unique_id": f"{self._device_id}_led_brightness",
				"icon": "mdi:brightness-6",
				"command_topic": self._topic("cmd/led/brightness"),
				"state_topic": self._topic("state/led/brightness"),
				"min": 0,
				"max": 100,
				"step": 1,
				"mode": "slider",
				"unit_of_measurement": "%",
			},
		))
		entities.append((
			"select",
			"led_effect",
			{
				"name": "LED Effect",
				"unique_id": f"{self._device_id}_led_effect",
				"icon": "mdi:auto-fix",
				"command_topic": self._topic("cmd/led/effect"),
				"state_topic": self._topic("state/led/effect"),
				"options": self.LIGHT_EFFECT_OPTIONS,
			},
		))
		entities.append((
			"select",
			"led_color_mode",
			{
				"name": "LED Color Mode",
				"unique_id": f"{self._device_id}_led_color_mode",
				"icon": "mdi:palette",
				"command_topic": self._topic("cmd/led/color_mode"),
				"state_topic": self._topic("state/led/color_mode"),
				"options": [self._color_mode_label(mode) for mode in self.LED_COLOR_MODES],
			},
		))
		entities.append((
			"light",
			"led_strip",
			{
				"name": "LED",
				"unique_id": f"{self._device_id}_led_light",
				"icon": "mdi:led-strip-variant",
				"command_topic": self._topic("cmd/led/power"),
				"state_topic": self._topic("state/led/power"),
				"payload_on": "ON",
				"payload_off": "OFF",
				"brightness_command_topic": self._topic("cmd/led/brightness"),
				"brightness_state_topic": self._topic("state/led/brightness"),
				"brightness_scale": 100,
				"effect": True,
				"effect_command_topic": self._topic("cmd/led/effect"),
				"effect_state_topic": self._topic("state/led/effect"),
				"effect_list": self.LIGHT_EFFECT_OPTIONS,
				"rgb_command_topic": self._topic("cmd/led/rgb_color"),
				"rgb_state_topic": self._topic("state/led/rgb_color"),
				"supported_color_modes": ["rgb"],
				"on_command_type": "first",
			},
		))
		entities.append((
			"select",
			"led_preset",
			{
				"name": "LED Preset",
				"unique_id": f"{self._device_id}_led_preset",
				"icon": "mdi:palette-swatch",
				"command_topic": self._topic("cmd/led/preset"),
				"state_topic": self._topic("state/led/preset"),
				"options": [self.LED_PRESET_LABELS.get(preset, preset) for preset in self.LED_PRESETS],
			},
		))
		entities.append((
			"number",
			"led_preset_intensity",
			{
				"name": "LED Preset Intensity",
				"unique_id": f"{self._device_id}_led_preset_intensity",
				"icon": "mdi:triangle-outline",
				"command_topic": self._topic("cmd/led/preset_intensity"),
				"state_topic": self._topic("state/led/preset_intensity"),
				"min": 0,
				"max": 100,
				"step": 1,
				"mode": "slider",
				"unit_of_measurement": "%",
			},
		))

		entities.extend([
			("text", "camera_stream_resolution", {
				"name": "Camera Stream Resolution (PX)",
				"unique_id": f"{self._device_id}_camera_stream_resolution",
				"icon": "mdi:video-box",
				"command_topic": self._topic("cmd/camera/stream_resolution"),
				"state_topic": self._topic("state/camera/stream_resolution"),
				"pattern": "^[0-9]{2,5}x[0-9]{2,5}$",
			}),
			("number", "camera_stream_fps", {
				"name": "Camera Stream FPS",
				"unique_id": f"{self._device_id}_camera_stream_fps",
				"icon": "mdi:video-high-definition",
				"command_topic": self._topic("cmd/camera/stream_fps"),
				"state_topic": self._topic("state/camera/stream_fps"),
				"min": 1,
				"max": 120,
				"step": 1,
				"mode": "box",
				"unit_of_measurement": "fps",
			}),
			("text", "camera_screenshot_resolution", {
				"name": "Camera Snapshot Resolution (PX)",
				"unique_id": f"{self._device_id}_camera_screenshot_resolution",
				"icon": "mdi:camera-image",
				"command_topic": self._topic("cmd/camera/screenshot_resolution"),
				"state_topic": self._topic("state/camera/screenshot_resolution"),
				"pattern": "^[0-9]{2,5}x[0-9]{2,5}$",
			}),
			("number", "camera_streamhd_interval", {
				"name": "Camera StreamHD Interval",
				"unique_id": f"{self._device_id}_camera_streamhd_interval",
				"icon": "mdi:timer-cog-outline",
				"command_topic": self._topic("cmd/camera/streamhd_interval"),
				"state_topic": self._topic("state/camera/streamhd_interval"),
				"min": 1,
				"max": 60,
				"step": 1,
				"mode": "box",
				"unit_of_measurement": "s",
			}),
			("switch", "camera_mqtt_image_feed", {
				"name": "Camera MQTT Image Feed",
				"unique_id": f"{self._device_id}_camera_mqtt_image_feed",
				"icon": "mdi:image-sync",
				"command_topic": self._topic("cmd/camera/mqtt_image"),
				"state_topic": self._topic("state/camera/mqtt_image"),
				"payload_on": "ON",
				"payload_off": "OFF",
				"state_on": "ON",
				"state_off": "OFF",
			}),
			("button", "camera_capture", {
				"name": "Camera Capture Snapshot",
				"unique_id": f"{self._device_id}_camera_capture",
				"icon": "mdi:camera-iris",
				"command_topic": self._topic("cmd/camera/capture"),
				"payload_press": "PRESS",
			}),
			("button", "camera_reset_defaults", {
				"name": "Camera Reset Driver Defaults",
				"unique_id": f"{self._device_id}_camera_reset_defaults",
				"icon": "mdi:camera-retake",
				"command_topic": self._topic("cmd/camera/reset_defaults"),
				"payload_press": "PRESS",
			}),
			("camera", "camera_live_feed", {
				"name": "Camera Live Feed",
				"unique_id": f"{self._device_id}_camera_snapshot",
				"icon": "mdi:cctv",
				"topic": self._topic("state/camera/snapshot_image"),
				"availability_topic": self._topic("state/camera/ha_available"),
				"payload_available": "online",
				"payload_not_available": "offline",
			}),
		])

		entities.extend([
			("button", "system_reboot", {
				"name": "System Reboot",
				"unique_id": f"{self._device_id}_system_reboot",
				"icon": "mdi:restart-alert",
				"command_topic": self._topic("cmd/system/reboot"),
				"payload_press": "PRESS",
			}),
			("button", "system_shutdown", {
				"name": "System Shutdown",
				"unique_id": f"{self._device_id}_system_shutdown",
				"icon": "mdi:power-standby",
				"command_topic": self._topic("cmd/system/shutdown"),
				"payload_press": "PRESS",
			}),
			("sensor", "cpu_usage", {
				"name": "CPU Usage",
				"unique_id": f"{self._device_id}_system_cpu",
				"icon": "mdi:chip",
				"state_topic": self._topic("state/system/cpu_percent"),
				"unit_of_measurement": "%",
				"state_class": "measurement",
			}),
			("sensor", "ram_usage", {
				"name": "RAM Usage",
				"unique_id": f"{self._device_id}_system_ram",
				"icon": "mdi:memory",
				"state_topic": self._topic("state/system/ram_percent"),
				"unit_of_measurement": "%",
				"state_class": "measurement",
			}),
			("sensor", "cpu_temperature", {
				"name": "CPU Temperature",
				"unique_id": f"{self._device_id}_system_temp",
				"icon": "mdi:thermometer",
				"state_topic": self._topic("state/system/cpu_temp"),
				"unit_of_measurement": "°C",
				"device_class": "temperature",
				"state_class": "measurement",
			}),
			("sensor", "camera_owner_mode", {
				"name": "Camera Ownership Mode",
				"unique_id": f"{self._device_id}_camera_owner_mode",
				"icon": "mdi:cctv",
				"state_topic": self._topic("state/camera/owner_mode"),
			}),
			("sensor", "camera_stream_url", {
				"name": "Camera Stream URL",
				"unique_id": f"{self._device_id}_camera_stream_url",
				"icon": "mdi:video-wireless",
				"state_topic": self._topic("state/camera/stream_url"),
			}),
			("sensor", "camera_streamhd_url", {
				"name": "Camera StreamHD URL",
				"unique_id": f"{self._device_id}_camera_streamhd_url",
				"icon": "mdi:video-wireless-outline",
				"state_topic": self._topic("state/camera/streamhd_url"),
			}),
			("sensor", "camera_snapshot_url", {
				"name": "Camera Snapshot URL",
				"unique_id": f"{self._device_id}_camera_snapshot_url",
				"icon": "mdi:image-area",
				"state_topic": self._topic("state/camera/snapshot_url"),
			}),
			("binary_sensor", "camera_ha_feed_active", {
				"name": "Camera Feed Active For Home Assistant",
				"unique_id": f"{self._device_id}_camera_ha_feed_active",
				"icon": "mdi:camera-party-mode",
				"state_topic": self._topic("state/camera/ha_feed_active"),
				"payload_on": "ON",
				"payload_off": "OFF",
			}),
			("binary_sensor", "laser_active", {
				"name": "Laser Active",
				"unique_id": f"{self._device_id}_laser_active",
				"icon": "mdi:laser-pointer",
				"state_topic": self._topic("state/laser/active"),
				"payload_on": "ON",
				"payload_off": "OFF",
			}),
			("binary_sensor", "laser_serial_traffic_active", {
				"name": "Laser Serial Traffic Active",
				"unique_id": f"{self._device_id}_laser_traffic_active",
				"icon": "mdi:lan-connect",
				"state_topic": self._topic("state/laser/traffic_active"),
				"payload_on": "ON",
				"payload_off": "OFF",
			}),
			("sensor", "laser_state", {
				"name": "Laser State",
				"unique_id": f"{self._device_id}_laser_state",
				"icon": "mdi:state-machine",
				"state_topic": self._topic("state/laser/state"),
			}),
			("sensor", "laser_last_error", {
				"name": "Laser Last Error",
				"unique_id": f"{self._device_id}_laser_last_error",
				"icon": "mdi:alert-octagon-outline",
				"state_topic": self._topic("state/laser/last_error"),
			}),
			("sensor", "laser_last_command", {
				"name": "Laser Last Command",
				"unique_id": f"{self._device_id}_laser_last_command",
				"icon": "mdi:code-tags",
				"state_topic": self._topic("state/laser/last_command"),
			}),
			("sensor", "laser_last_tx_command", {
				"name": "Laser Last TX Command",
				"unique_id": f"{self._device_id}_laser_last_tx_command",
				"icon": "mdi:send",
				"state_topic": self._topic("state/laser/last_tx_command"),
			}),
			("sensor", "laser_serial_mode", {
				"name": "Laser Serial Mode",
				"unique_id": f"{self._device_id}_laser_serial_mode",
				"icon": "mdi:lan",
				"state_topic": self._topic("state/laser/serial_mode"),
			}),
			("sensor", "laser_serial_clients", {
				"name": "Laser Serial Clients",
				"unique_id": f"{self._device_id}_laser_serial_clients",
				"icon": "mdi:account-network",
				"state_topic": self._topic("state/laser/serial_clients"),
			}),
			("sensor", "laser_serial_queue_depth", {
				"name": "Laser Serial Queue Depth",
				"unique_id": f"{self._device_id}_laser_serial_queue_depth",
				"icon": "mdi:format-list-bulleted-square",
				"state_topic": self._topic("state/laser/serial_queue_depth"),
			}),
			("switch", "led_on_at_boot", {
				"name": "LED On At Boot",
				"unique_id": f"{self._device_id}_laser_led_on_boot",
				"icon": "mdi:power-plug-outline",
				"command_topic": self._topic("cmd/laser/led_on_boot"),
				"state_topic": self._topic("state/laser/led_on_boot"),
				"payload_on": "ON",
				"payload_off": "OFF",
				"state_on": "ON",
				"state_off": "OFF",
			}),
			("switch", "laser_serial_proxy_enabled", {
				"name": "Laser Serial Proxy Enabled",
				"unique_id": f"{self._device_id}_laser_serial_proxy_enabled",
				"icon": "mdi:swap-horizontal",
				"command_topic": self._topic("cmd/laser/serial_proxy_enabled"),
				"state_topic": self._topic("state/laser/serial_proxy_enabled"),
				"payload_on": "ON",
				"payload_off": "OFF",
				"state_on": "ON",
				"state_off": "OFF",
			}),
			("switch", "laser_led_sync", {
				"name": "Laser LED Sync",
				"unique_id": f"{self._device_id}_laser_led_sync",
				"icon": "mdi:led-strip-variant",
				"command_topic": self._topic("cmd/laser/led_sync"),
				"state_topic": self._topic("state/laser/led_sync"),
				"payload_on": "ON",
				"payload_off": "OFF",
				"state_on": "ON",
				"state_off": "OFF",
			}),
			("select", "laser_idle_effect", {
				"name": "Laser Idle Effect",
				"unique_id": f"{self._device_id}_laser_idle_effect",
				"icon": "mdi:led-strip-variant-off",
				"command_topic": self._topic("cmd/laser/idle_effect"),
				"state_topic": self._topic("state/laser/idle_effect"),
				"options": [self._effect_label(effect) for effect in self.LED_EFFECTS],
			}),
			("select", "laser_idle_color_mode", {
				"name": "Laser Idle Color Mode",
				"unique_id": f"{self._device_id}_laser_idle_color_mode",
				"icon": "mdi:palette",
				"command_topic": self._topic("cmd/laser/idle_color_mode"),
				"state_topic": self._topic("state/laser/idle_color_mode"),
				"options": [self._color_mode_label(mode) for mode in self.LED_COLOR_MODES],
			}),
			("select", "laser_running_effect", {
				"name": "Laser Running Effect",
				"unique_id": f"{self._device_id}_laser_running_effect",
				"icon": "mdi:run-fast",
				"command_topic": self._topic("cmd/laser/running_effect"),
				"state_topic": self._topic("state/laser/running_effect"),
				"options": [self._effect_label(effect) for effect in self.LED_EFFECTS],
			}),
			("select", "laser_running_color_mode", {
				"name": "Laser Running Color Mode",
				"unique_id": f"{self._device_id}_laser_running_color_mode",
				"icon": "mdi:palette",
				"command_topic": self._topic("cmd/laser/running_color_mode"),
				"state_topic": self._topic("state/laser/running_color_mode"),
				"options": [self._color_mode_label(mode) for mode in self.LED_COLOR_MODES],
			}),
			("select", "laser_error_effect", {
				"name": "Laser Error Effect",
				"unique_id": f"{self._device_id}_laser_error_effect",
				"icon": "mdi:alert",
				"command_topic": self._topic("cmd/laser/error_effect"),
				"state_topic": self._topic("state/laser/error_effect"),
				"options": [self._effect_label(effect) for effect in self.LED_EFFECTS],
			}),
			("select", "laser_error_color_mode", {
				"name": "Laser Error Color Mode",
				"unique_id": f"{self._device_id}_laser_error_color_mode",
				"icon": "mdi:palette",
				"command_topic": self._topic("cmd/laser/error_color_mode"),
				"state_topic": self._topic("state/laser/error_color_mode"),
				"options": [self._color_mode_label(mode) for mode in self.LED_COLOR_MODES],
			}),
			("select", "laser_engrave_complete_effect", {
				"name": "Laser Engrave Complete Effect",
				"unique_id": f"{self._device_id}_laser_engrave_complete_effect",
				"icon": "mdi:check-decagram",
				"command_topic": self._topic("cmd/laser/engrave_complete_effect"),
				"state_topic": self._topic("state/laser/engrave_complete_effect"),
				"options": [self._effect_label(effect) for effect in self.LED_EFFECTS],
			}),
			("select", "laser_engrave_complete_color_mode", {
				"name": "Laser Engrave Complete Color Mode",
				"unique_id": f"{self._device_id}_laser_engrave_complete_color_mode",
				"icon": "mdi:palette",
				"command_topic": self._topic("cmd/laser/engrave_complete_color_mode"),
				"state_topic": self._topic("state/laser/engrave_complete_color_mode"),
				"options": [self._color_mode_label(mode) for mode in self.LED_COLOR_MODES],
			}),
			("button", "laser_clear_error", {
				"name": "Laser Clear Error/Completed",
				"unique_id": f"{self._device_id}_laser_clear_error",
				"icon": "mdi:alarm-light-off",
				"command_topic": self._topic("cmd/laser/clear_error"),
				"payload_press": "PRESS",
			}),
			("button", "laser_clear_queue", {
				"name": "Laser Clear Serial Queue",
				"unique_id": f"{self._device_id}_laser_clear_queue",
				"icon": "mdi:playlist-remove",
				"command_topic": self._topic("cmd/laser/clear_queue"),
				"payload_press": "PRESS",
			}),
			("text", "laser_custom_gcode", {
				"name": "Laser Custom G-code",
				"unique_id": f"{self._device_id}_laser_custom_gcode",
				"icon": "mdi:code-braces",
				"command_topic": self._topic("cmd/laser/gcode"),
				"state_topic": self._topic("state/laser/last_tx_command"),
				"max": 180,
				"mode": "text",
			}),
			("button", "laser_custom_position", {
				"name": "Laser Go Custom Position",
				"unique_id": f"{self._device_id}_laser_custom_position",
				"icon": "mdi:crosshairs-gps",
				"command_topic": self._topic("cmd/laser/custom_position"),
				"payload_press": "PRESS",
			}),
			("number", "laser_custom_pos_x_mm", {
				"name": "Laser Custom Position X (mm)",
				"unique_id": f"{self._device_id}_laser_custom_pos_x_mm",
				"icon": "mdi:axis-x-arrow",
				"command_topic": self._topic("cmd/laser/custom_pos_x_mm"),
				"state_topic": self._topic("state/laser/custom_pos_x_mm"),
				"min": -1000,
				"max": 1000,
				"step": 0.1,
				"mode": "box",
				"unit_of_measurement": "mm",
			}),
			("number", "laser_custom_pos_y_mm", {
				"name": "Laser Custom Position Y (mm)",
				"unique_id": f"{self._device_id}_laser_custom_pos_y_mm",
				"icon": "mdi:axis-y-arrow",
				"command_topic": self._topic("cmd/laser/custom_pos_y_mm"),
				"state_topic": self._topic("state/laser/custom_pos_y_mm"),
				"min": -1000,
				"max": 1000,
				"step": 0.1,
				"mode": "box",
				"unit_of_measurement": "mm",
			}),
			("number", "laser_custom_pos_z_mm", {
				"name": "Laser Custom Position Z (mm)",
				"unique_id": f"{self._device_id}_laser_custom_pos_z_mm",
				"icon": "mdi:axis-z-arrow",
				"command_topic": self._topic("cmd/laser/custom_pos_z_mm"),
				"state_topic": self._topic("state/laser/custom_pos_z_mm"),
				"min": -1000,
				"max": 1000,
				"step": 0.1,
				"mode": "box",
				"unit_of_measurement": "mm",
			}),
			("switch", "laser_custom_pos_use_g0", {
				"name": "Laser Custom Position Use G0",
				"unique_id": f"{self._device_id}_laser_custom_pos_use_g0",
				"icon": "mdi:swap-vertical",
				"command_topic": self._topic("cmd/laser/custom_pos_use_g0"),
				"state_topic": self._topic("state/laser/custom_pos_use_g0"),
				"payload_on": "ON",
				"payload_off": "OFF",
				"state_on": "ON",
				"state_off": "OFF",
			}),
			("number", "laser_move_step_mm", {
				"name": "Laser Move Step (mm)",
				"unique_id": f"{self._device_id}_laser_move_step_mm",
				"icon": "mdi:arrow-expand-horizontal",
				"command_topic": self._topic("cmd/laser/move_step_mm"),
				"state_topic": self._topic("state/laser/move_step_mm"),
				"min": 0.1,
				"max": 500,
				"step": 0.1,
				"mode": "box",
				"unit_of_measurement": "mm",
			}),
			("number", "laser_move_feed_mm_min", {
				"name": "Laser Move Speed (mm/min)",
				"unique_id": f"{self._device_id}_laser_move_feed_mm_min",
				"icon": "mdi:speedometer",
				"command_topic": self._topic("cmd/laser/move_feed_mm_min"),
				"state_topic": self._topic("state/laser/move_feed_mm_min"),
				"min": 10,
				"max": 20000,
				"step": 1,
				"mode": "box",
				"unit_of_measurement": "mm/min",
			}),
			("button", "laser_jog_up", {
				"name": "Laser Jog Up",
				"unique_id": f"{self._device_id}_laser_jog_up",
				"icon": "mdi:arrow-up-bold",
				"command_topic": self._topic("cmd/laser/jog/up"),
				"payload_press": "PRESS",
			}),
			("button", "laser_jog_down", {
				"name": "Laser Jog Down",
				"unique_id": f"{self._device_id}_laser_jog_down",
				"icon": "mdi:arrow-down-bold",
				"command_topic": self._topic("cmd/laser/jog/down"),
				"payload_press": "PRESS",
			}),
			("button", "laser_jog_left", {
				"name": "Laser Jog Left",
				"unique_id": f"{self._device_id}_laser_jog_left",
				"icon": "mdi:arrow-left-bold",
				"command_topic": self._topic("cmd/laser/jog/left"),
				"payload_press": "PRESS",
			}),
			("button", "laser_jog_right", {
				"name": "Laser Jog Right",
				"unique_id": f"{self._device_id}_laser_jog_right",
				"icon": "mdi:arrow-right-bold",
				"command_topic": self._topic("cmd/laser/jog/right"),
				"payload_press": "PRESS",
			}),
			("button", "laser_jog_home", {
				"name": "Laser Jog Home",
				"unique_id": f"{self._device_id}_laser_jog_home",
				"icon": "mdi:home-import-outline",
				"command_topic": self._topic("cmd/laser/jog/home"),
				"payload_press": "PRESS",
			}),
		])

		entities.extend([
			("switch", "airassist_on", {
				"name": "Air Assist ON",
				"unique_id": f"{self._device_id}_airassist_on",
				"icon": "mdi:air-purifier",
				"command_topic": self._topic("cmd/airassist/on"),
				"state_topic": self._topic("state/airassist/on"),
				"payload_on": "ON",
				"payload_off": "OFF",
				"state_on": "ON",
				"state_off": "OFF",
			}),
			("switch", "airassist_auto", {
				"name": "Progressive AirAssist",
				"unique_id": f"{self._device_id}_airassist_auto",
				"icon": "mdi:motion-play",
				"command_topic": self._topic("cmd/airassist/auto"),
				"state_topic": self._topic("state/airassist/auto"),
				"payload_on": "ON",
				"payload_off": "OFF",
				"state_on": "ON",
				"state_off": "OFF",
			}),
			("number", "airassist_speed", {
				"name": "Air Assist Fixed Speed",
				"unique_id": f"{self._device_id}_airassist_speed",
				"icon": "mdi:fan",
				"command_topic": self._topic("cmd/airassist/speed"),
				"state_topic": self._topic("state/airassist/speed"),
				"min": 0,
				"max": 100,
				"step": 1,
				"mode": "slider",
				"unit_of_measurement": "%",
			}),
			("number", "airassist_start_at_beam_power", {
				"name": "Progressive AirAssist Start At Beam Power",
				"unique_id": f"{self._device_id}_airassist_start_at_beam_power",
				"icon": "mdi:ray-start-arrow",
				"command_topic": self._topic("cmd/airassist/auto_range_min"),
				"state_topic": self._topic("state/airassist/auto_range_min"),
				"min": 0,
				"max": 99,
				"step": 1,
				"mode": "slider",
				"unit_of_measurement": "%",
			}),
			("number", "airassist_max_flow_at_beam_power", {
				"name": "Progressive AirAssist Max Flow At Beam Power",
				"unique_id": f"{self._device_id}_airassist_max_flow_at_beam_power",
				"icon": "mdi:ray-end-arrow",
				"command_topic": self._topic("cmd/airassist/auto_range_max"),
				"state_topic": self._topic("state/airassist/auto_range_max"),
				"min": 1,
				"max": 100,
				"step": 1,
				"mode": "slider",
				"unit_of_measurement": "%",
			}),
		])

		for key, label in self.V4L2_LABELS.items():
			options = self._v4l2_options.get(key, {})
			entity_object_id = self.V4L2_ENTITY_IDS.get(key, f"v4l2_{key}")
			if options:
				payload = {
					"name": label,
					"unique_id": f"{self._device_id}_v4l2_{key}",
					"icon": self.V4L2_ICONS.get(key, "mdi:tune"),
					"command_topic": self._topic(f"cmd/v4l2/{key}"),
					"state_topic": self._topic(f"state/v4l2/{key}"),
					"options": list(options.values()),
				}
				entities.append(("select", entity_object_id, payload))
			elif key in ("horizontal_flip", "vertical_flip", "exposure_dynamic_framerate"):
				payload = {
					"name": label,
					"unique_id": f"{self._device_id}_v4l2_{key}",
					"icon": self.V4L2_ICONS.get(key, "mdi:tune"),
					"command_topic": self._topic(f"cmd/v4l2/{key}"),
					"state_topic": self._topic(f"state/v4l2/{key}"),
					"payload_on": "ON",
					"payload_off": "OFF",
					"state_on": "ON",
					"state_off": "OFF",
				}
				entities.append(("switch", entity_object_id, payload))
			else:
				limits = self._number_limits_for_v4l2(key)
				payload = {
					"name": label,
					"unique_id": f"{self._device_id}_v4l2_{key}",
					"icon": self.V4L2_ICONS.get(key, "mdi:tune"),
					"command_topic": self._topic(f"cmd/v4l2/{key}"),
					"state_topic": self._topic(f"state/v4l2/{key}"),
					"min": limits[0],
					"max": limits[1],
					"step": limits[2],
					"mode": "slider",
				}
				entities.append(("number", entity_object_id, payload))

		for component, object_id, payload in entities:
			config = dict(payload)
			config["unique_id"] = f"{self._device_id}_{component}_{object_id}"
			config.setdefault("availability_topic", self._availability_topic)
			config["device"] = self._device_block()
			self._publish(
				self._discovery_topic(component, object_id),
				json.dumps(config, ensure_ascii=True),
				retain=True,
			)

	def _number_limits_for_v4l2(self, key):
		mapping = {
			"brightness": (0, 100, 1),
			"contrast": (-100, 100, 1),
			"saturation": (-100, 100, 1),
			"sharpness": (-100, 100, 1),
			"compression_quality": (1, 100, 1),
			"exposure_time_absolute": (1, 10000, 1),
		}
		return mapping.get(key, (0, 100, 1))

	def _poll_loop(self):
		while self._running:
			try:
				self._publish_full_state()
			except Exception as exc:
				self._log(f"poll warning: {exc}")
			time.sleep(self.POLL_INTERVAL_S if self._connected else max(5.0, self.POLL_INTERVAL_S))

	def _refresh_v4l2_state(self):
		"""Fetch V4L2 metadata and publish entity states. Called at startup and after v4l2 commands."""
		try:
			v4l2 = self._http_get_json("/api/camera/v4l2")
			controls = v4l2.get("controls", {})
			meta = v4l2.get("meta", {})
			self._v4l2_options = self._build_v4l2_options(meta)
			for key, value in controls.items():
				options = self._v4l2_options.get(key)
				if options:
					state_value = options.get(str(value), str(value))
				elif key in ("horizontal_flip", "vertical_flip", "exposure_dynamic_framerate"):
					state_value = "ON" if int(value) else "OFF"
				else:
					state_value = str(value)
				self._publish_state(self._topic(f"state/v4l2/{key}"), state_value)
		except Exception as exc:
			self._log(f"v4l2 state refresh warning: {exc}")

	def _publish_full_state(self, force=False):
		led = self._http_get_json_cached("/api/state", ttl_s=1.0, force=force)
		camera = self._http_get_json_cached("/api/camera/settings", ttl_s=6.0, force=force)
		stats = self._http_get_json_cached("/api/system/stats", ttl_s=4.0, force=force)
		try:
			laser = self._http_get_json_cached("/api/laser-monitor", ttl_s=1.0, force=force)
		except Exception:
			laser = {"state": "idle", "laser_active": False, "traffic_active": False, "last_error": "", "config": {}}

		self._publish_state(self._topic("state/led/power"), "ON" if led.get("is_on") else "OFF", force=force)
		brightness_pct = int(round(float(led.get("brightness", 0.0)) * 100.0))
		self._publish_state(self._topic("state/led/brightness"), str(brightness_pct), force=force)
		effect_raw = str(led.get("effect", "static") or "static")
		preset_raw = str(led.get("preset", "none") or "none")
		if preset_raw != "none":
			effect_state = self.LED_PRESET_LABELS.get(preset_raw, preset_raw)
		else:
			effect_state = self._effect_label(effect_raw)
		self._publish_state(
			self._topic("state/led/effect"),
			effect_state,
			force=force,
		)
		self._publish_state(
			self._topic("state/led/color_mode"),
			self._color_mode_label(str(led.get("color_mode", "cool_white"))),
			force=force,
		)
		self._publish_state(self._topic("state/led/preset"), self.LED_PRESET_LABELS.get(preset_raw, preset_raw), force=force)
		self._publish_state(self._topic("state/led/preset_intensity"), str(int(led.get("preset_intensity", 100))), force=force)
		rgb = led.get("custom_color", [255, 255, 255])
		self._publish_state(self._topic("state/led/rgb_color"), ",".join(str(int(v)) for v in list(rgb)[:3]), force=force)

		self._publish_state(self._topic("state/camera/stream_resolution"), str(camera.get("stream_resolution", "")), force=force)
		self._publish_state(self._topic("state/camera/stream_fps"), str(camera.get("stream_fps", "")), force=force)
		self._publish_state(self._topic("state/camera/screenshot_resolution"), str(camera.get("screenshot_resolution", "")), force=force)
		self._publish_state(self._topic("state/camera/streamhd_interval"), str(camera.get("streamhd_interval_s", "")), force=force)
		self._publish_state(
			self._topic("state/camera/mqtt_image"),
			"ON" if int(camera.get("mqtt_image_enabled", 1)) else "OFF",
			force=force,
		)

		self._publish_state(self._topic("state/system/cpu_percent"), self._safe_number(stats.get("cpu_percent")), force=force)
		self._publish_state(self._topic("state/system/ram_percent"), self._safe_number(stats.get("ram_percent")), force=force)
		self._publish_state(self._topic("state/system/cpu_temp"), self._safe_number(stats.get("cpu_temp")), force=force)
		self._publish_state(self._topic("state/camera/owner_mode"), str(stats.get("camera_owner_mode", "idle")), force=force)
		self._publish_state(self._topic("state/camera/stream_url"), f"{self._public_base_url}/stream", force=force)
		self._publish_state(self._topic("state/camera/streamhd_url"), f"{self._public_base_url}/streamhd", force=force)
		self._publish_state(self._topic("state/camera/snapshot_url"), f"{self._public_base_url}/snapshot", force=force)

		laser_cfg = laser.get("config", {}) if isinstance(laser.get("config", {}), dict) else {}
		serial_link = laser.get("serial_link", {}) if isinstance(laser.get("serial_link", {}), dict) else {}
		laser_state_raw = str(laser.get("state", "idle") or "idle")
		laser_active = bool(laser.get("laser_active", False))
		if laser_state_raw == "running":
			laser_state_public = "engraving" if laser_active else "moving"
		else:
			laser_state_public = laser_state_raw
		self._publish_state(self._topic("state/laser/state"), laser_state_public, force=force)
		self._publish_state(self._topic("state/laser/active"), "ON" if laser_active else "OFF", force=force)
		self._publish_state(self._topic("state/laser/traffic_active"), "ON" if bool(laser.get("traffic_active", False)) else "OFF", force=force)
		self._publish_state(self._topic("state/laser/last_error"), str(laser.get("last_error", "") or ""), force=force)
		self._publish_state(self._topic("state/laser/last_command"), str(laser.get("last_command", "") or ""), force=force)
		self._publish_state(self._topic("state/laser/last_tx_command"), str(laser.get("last_tx_command", "") or ""), force=force)
		self._publish_state(self._topic("state/laser/custom_pos_x_mm"), self._safe_number(laser_cfg.get("laser_custom_pos_x_mm", 0.0)), force=force)
		self._publish_state(self._topic("state/laser/custom_pos_y_mm"), self._safe_number(laser_cfg.get("laser_custom_pos_y_mm", 0.0)), force=force)
		self._publish_state(self._topic("state/laser/custom_pos_z_mm"), self._safe_number(laser_cfg.get("laser_custom_pos_z_mm", 0.0)), force=force)
		self._publish_state(self._topic("state/laser/custom_pos_use_g0"), "ON" if int(laser_cfg.get("laser_custom_pos_use_g0", 1)) else "OFF", force=force)
		self._publish_state(self._topic("state/laser/move_step_mm"), self._safe_number(laser_cfg.get("laser_move_step_mm", 20.0)), force=force)
		self._publish_state(self._topic("state/laser/move_feed_mm_min"), self._safe_number(laser_cfg.get("laser_move_feed_mm_min", 300.0)), force=force)
		self._publish_state(self._topic("state/laser/serial_mode"), str(serial_link.get("mode", "disconnected") or "disconnected"), force=force)
		self._publish_state(self._topic("state/laser/serial_clients"), str(int(serial_link.get("active_clients", 0) or 0)), force=force)
		self._publish_state(self._topic("state/laser/serial_queue_depth"), str(int(serial_link.get("queue_depth", 0) or 0)), force=force)
		self._publish_state(self._topic("state/laser/led_on_boot"), "ON" if int(laser_cfg.get("led_on_boot", 1)) else "OFF", force=force)
		self._publish_state(self._topic("state/laser/serial_proxy_enabled"), "ON" if int(laser_cfg.get("serial_proxy_enabled", 0)) else "OFF", force=force)
		self._publish_state(self._topic("state/laser/led_sync"), "ON" if int(laser_cfg.get("laser_led_sync_enabled", 1)) else "OFF", force=force)
		self._publish_state(
			self._topic("state/laser/idle_effect"),
			self._effect_label(str(laser_cfg.get("laser_led_idle_effect", "static"))),
			force=force,
		)
		self._publish_state(
			self._topic("state/laser/idle_color_mode"),
			self._color_mode_label(str(laser_cfg.get("laser_led_idle_color_mode", "cool_white"))),
			force=force,
		)
		self._publish_state(
			self._topic("state/laser/running_effect"),
			self._effect_label(str(laser_cfg.get("laser_led_running_effect", "pulse"))),
			force=force,
		)
		self._publish_state(
			self._topic("state/laser/running_color_mode"),
			self._color_mode_label(str(laser_cfg.get("laser_led_running_color_mode", "laser_green"))),
			force=force,
		)
		self._publish_state(
			self._topic("state/laser/error_effect"),
			self._effect_label(str(laser_cfg.get("laser_led_error_effect", "strobe"))),
			force=force,
		)
		self._publish_state(
			self._topic("state/laser/error_color_mode"),
			self._color_mode_label(str(laser_cfg.get("laser_led_error_color_mode", "ruby_red"))),
			force=force,
		)
		self._publish_state(
			self._topic("state/laser/engrave_complete_effect"),
			self._effect_label(str(laser_cfg.get("laser_led_engrave_complete_effect", "twinkle"))),
			force=force,
		)
		self._publish_state(
			self._topic("state/laser/engrave_complete_color_mode"),
			self._color_mode_label(str(laser_cfg.get("laser_led_engrave_complete_color_mode", "cool_white"))),
			force=force,
		)

		self._update_camera_feed_state(stats)

		try:
			airassist = self._http_get_json_cached("/api/airassist", ttl_s=2.0, force=force)
			self._publish_state(self._topic("state/airassist/power"), "ON" if bool(airassist.get("enabled", False)) else "OFF", force=force)
			self._publish_state(self._topic("state/airassist/auto"), "ON" if bool(airassist.get("auto_mode", False)) else "OFF", force=force)
			self._publish_state(self._topic("state/airassist/speed"), str(int(airassist.get("speed", 100))), force=force)
			self._publish_state(self._topic("state/airassist/auto_range_min"), str(int(airassist.get("auto_range_min", 0))), force=force)
			self._publish_state(self._topic("state/airassist/auto_range_max"), str(int(airassist.get("auto_range_max", 100))), force=force)
		except Exception:
			pass

	def _update_camera_feed_state(self, stats):
		mqtt_image_enabled = str(self._state_cache.get(self._topic("state/camera/mqtt_image"), "ON") or "ON").upper() == "ON"
		availability = str(self._state_cache.get(self._topic("state/camera/ha_available"), "offline") or "offline").lower()
		stream_active = mqtt_image_enabled and availability == "online"
		self._publish_state(self._topic("state/camera/ha_feed_active"), "ON" if stream_active else "OFF")

	def _mqtt_image_feed_enabled(self):
		with self._lock:
			value = self._state_cache.get(self._topic("state/camera/mqtt_image"), "ON")
		return str(value or "ON").upper() == "ON"

	def _snapshot_worker_loop(self):
		"""Reads JPEG frames directly from ustreamer port (bypasses Python proxy / camera ownership).
		Marks the HA camera entity online/offline based on ustreamer availability."""
		snapshot_url = f"http://127.0.0.1:{self._ustreamer_port}/snapshot"
		while self._running and not self._snapshot_worker_stop.is_set():
			mqtt_image_enabled = self._mqtt_image_feed_enabled()
			if not mqtt_image_enabled:
				self._publish_state(self._topic("state/camera/ha_available"), "offline")
				self._publish_state(self._topic("state/camera/ha_feed_active"), "OFF")
				self._snapshot_worker_stop.wait(max(self._camera_snapshot_interval_s, 2.0))
				continue
			try:
				req = urllib.request.Request(snapshot_url)
				with urllib.request.urlopen(req, timeout=3) as resp:
					jpeg = resp.read()
				if jpeg:
					digest = hashlib.blake2s(jpeg, digest_size=16).hexdigest()
					with self._lock:
						publish_frame = digest != self._last_snapshot_digest
						if publish_frame:
							self._last_snapshot_digest = digest
					if publish_frame:
						self._publish(self._topic("state/camera/snapshot_image"), jpeg, retain=True)
					self._publish_state(self._topic("state/camera/ha_available"), "online")
			except Exception:
				self._publish_state(self._topic("state/camera/ha_available"), "offline")
			self._snapshot_worker_stop.wait(self._camera_snapshot_interval_s)

	def _build_v4l2_options(self, meta):
		result = {}
		for key, info in meta.items():
			if info.get("type") != "menu":
				continue
			options = {}
			for raw_key, raw_label in info.get("options", {}).items():
				options[str(raw_key)] = self._normalize_v4l2_option_label(key, raw_label)
			result[key] = options
		return result

	def _normalize_v4l2_option_label(self, key, raw_label):
		label = str(raw_label).strip()
		if not label:
			return "Off"
		lower = label.lower()
		if lower in ("none", "null"):
			if key == "scene_mode":
				return "Disabled"
			return "Off"
		if lower in ("unknown", "unavailable"):
			return "N/A"
		return label

	def _safe_number(self, value):
		if value is None:
			return ""
		if isinstance(value, float):
			return f"{value:.1f}"
		return str(value)

	def _publish_state(self, topic, payload, force=False):
		with self._lock:
			if not force and self._state_cache.get(topic) == payload:
				return
			self._state_cache[topic] = payload
		self._publish(topic, payload, retain=True)

	def _publish(self, topic, payload, retain=False):
		self._client.publish(topic, payload=payload, qos=1, retain=retain)

	def _on_message(self, client, userdata, message):
		topic = message.topic
		payload = message.payload.decode("utf-8", errors="ignore").strip()
		try:
			self._handle_command(topic, payload)
			self._publish_full_state(force=True)
		except Exception as exc:
			self._log(f"command failed topic={topic}: {exc}")

	def _handle_command(self, topic, payload):
		if topic == self._topic("cmd/led/power"):
			self._handle_led_power(payload)
			return
		if topic == self._topic("cmd/led/brightness"):
			value = max(0, min(100, int(float(payload))))
			self._http_post_json("/api/brightness", {"brightness": value / 100.0})
			return
		if topic == self._topic("cmd/led/effect"):
			preset_value = self._parse_led_preset_payload(payload, strict=False)
			if preset_value is not None:
				self._http_post_json("/api/preset", {"preset": preset_value})
				return
			effect_value = self._parse_led_effect_payload(payload)
			self._http_post_json("/api/effect", {"effect": effect_value})
			return
		if topic == self._topic("cmd/led/color_mode"):
			color_mode_value = self._parse_color_mode_payload(payload)
			self._http_post_json("/api/color-mode", {"color_mode": color_mode_value})
			return
		if topic == self._topic("cmd/led/rgb_color"):
			parts = [int(float(x.strip())) for x in payload.split(",")]
			r, g, b = parts[0], parts[1], parts[2]
			self._http_post_json("/api/color", {"r": r, "g": g, "b": b})
			return
		if topic == self._topic("cmd/led/preset"):
			preset_value = self._parse_led_preset_payload(payload)
			self._http_post_json("/api/preset", {"preset": preset_value})
			return
		if topic == self._topic("cmd/led/preset_intensity"):
			self._http_post_json("/api/preset-intensity", {"intensity": int(float(payload))})
			return
		if topic == self._topic("cmd/camera/stream_resolution"):
			self._http_post_json("/api/camera/settings/stream", {"resolution": payload})
			return
		if topic == self._topic("cmd/camera/stream_fps"):
			self._http_post_json("/api/camera/settings/stream", {"fps": int(float(payload))})
			return
		if topic == self._topic("cmd/camera/screenshot_resolution"):
			self._http_post_json("/api/camera/settings/screenshot", {"resolution": payload})
			return
		if topic == self._topic("cmd/camera/streamhd_interval"):
			self._http_post_json("/api/camera/settings/streamhd", {"interval_seconds": int(float(payload))})
			return
		if topic == self._topic("cmd/camera/mqtt_image"):
			enabled = str(payload).strip().upper() == "ON"
			self._http_post_json("/api/camera/settings/mqtt-image", {"enabled": enabled})
			return
		if topic == self._topic("cmd/camera/capture"):
			self._http_post_json("/api/camera/capture", {})
			return
		if topic == self._topic("cmd/camera/reset_defaults"):
			self._http_post_json("/api/camera/v4l2/reset-defaults", {})
			self._refresh_v4l2_state()
			return
		if topic == self._topic("cmd/system/reboot"):
			self._http_post_json("/api/reboot", {})
			return
		if topic == self._topic("cmd/system/shutdown"):
			self._http_post_json("/api/shutdown", {})
			return
		if topic == self._topic("cmd/laser/led_on_boot"):
			self._http_post_json("/api/laser-monitor/config", {"led_on_boot": str(payload).upper() == "ON"})
			return
		if topic == self._topic("cmd/laser/serial_proxy_enabled"):
			self._http_post_json("/api/laser-monitor/config", {"serial_proxy_enabled": str(payload).upper() == "ON"})
			return
		if topic == self._topic("cmd/laser/led_sync"):
			self._http_post_json("/api/laser-monitor/config", {"laser_led_sync_enabled": str(payload).upper() == "ON"})
			return
		if topic == self._topic("cmd/laser/idle_effect"):
			effect_value = self._parse_led_effect_payload(payload)
			self._http_post_json("/api/laser-monitor/config", {"laser_led_idle_effect": effect_value})
			return
		if topic == self._topic("cmd/laser/idle_color_mode"):
			color_mode_value = self._parse_color_mode_payload(payload)
			self._http_post_json("/api/laser-monitor/config", {"laser_led_idle_color_mode": color_mode_value})
			return
		if topic == self._topic("cmd/laser/running_effect"):
			effect_value = self._parse_led_effect_payload(payload)
			self._http_post_json("/api/laser-monitor/config", {"laser_led_running_effect": effect_value})
			return
		if topic == self._topic("cmd/laser/running_color_mode"):
			color_mode_value = self._parse_color_mode_payload(payload)
			self._http_post_json("/api/laser-monitor/config", {"laser_led_running_color_mode": color_mode_value})
			return
		if topic == self._topic("cmd/laser/error_effect"):
			effect_value = self._parse_led_effect_payload(payload)
			self._http_post_json("/api/laser-monitor/config", {"laser_led_error_effect": effect_value})
			return
		if topic == self._topic("cmd/laser/error_color_mode"):
			color_mode_value = self._parse_color_mode_payload(payload)
			self._http_post_json("/api/laser-monitor/config", {"laser_led_error_color_mode": color_mode_value})
			return
		if topic == self._topic("cmd/laser/engrave_complete_effect"):
			effect_value = self._parse_led_effect_payload(payload)
			self._http_post_json("/api/laser-monitor/config", {"laser_led_engrave_complete_effect": effect_value})
			return
		if topic == self._topic("cmd/laser/engrave_complete_color_mode"):
			color_mode_value = self._parse_color_mode_payload(payload)
			self._http_post_json("/api/laser-monitor/config", {"laser_led_engrave_complete_color_mode": color_mode_value})
			return
		if topic == self._topic("cmd/laser/clear_error"):
			self._http_post_json("/api/laser-monitor/clear-error", {})
			return
		if topic == self._topic("cmd/laser/clear_queue"):
			self._http_post_json("/api/laser/queue/clear", {"source": "mqtt"})
			return
		if topic == self._topic("cmd/laser/clear_state"):
			self._http_post_json("/api/laser-monitor/clear-error", {})
			return
		if topic == self._topic("cmd/laser/gcode"):
			if not str(payload or "").strip():
				raise ValueError("empty gcode command")
			self._http_post_json("/api/laser/gcode", {"command": payload, "source": "mqtt"})
			return
		if topic == self._topic("cmd/laser/custom_position"):
			self._http_post_json("/api/laser/custom-position", {"source": "mqtt"})
			return
		if topic == self._topic("cmd/laser/custom_pos_x_mm"):
			x_mm = float(payload)
			self._http_post_json("/api/laser-monitor/config", {"laser_custom_pos_x_mm": x_mm})
			return
		if topic == self._topic("cmd/laser/custom_pos_y_mm"):
			y_mm = float(payload)
			self._http_post_json("/api/laser-monitor/config", {"laser_custom_pos_y_mm": y_mm})
			return
		if topic == self._topic("cmd/laser/custom_pos_z_mm"):
			z_mm = float(payload)
			self._http_post_json("/api/laser-monitor/config", {"laser_custom_pos_z_mm": z_mm})
			return
		if topic == self._topic("cmd/laser/custom_pos_use_g0"):
			self._http_post_json("/api/laser-monitor/config", {"laser_custom_pos_use_g0": str(payload).strip().upper() == "ON"})
			return
		if topic == self._topic("cmd/laser/move_step_mm"):
			step_mm = float(payload)
			self._http_post_json("/api/laser-monitor/config", {"laser_move_step_mm": step_mm})
			return
		if topic == self._topic("cmd/laser/move_feed_mm_min"):
			feed_mm_min = float(payload)
			self._http_post_json("/api/laser-monitor/config", {"laser_move_feed_mm_min": feed_mm_min})
			return
		if topic.startswith(self._topic("cmd/laser/jog/")):
			direction = topic.rsplit("/", 1)[-1]
			self._http_post_json("/api/laser/jog", {"direction": direction, "source": "mqtt"})
			return
		if topic.startswith(self._topic("cmd/v4l2/")):
			key = topic.rsplit("/", 1)[-1]
			self._handle_v4l2_command(key, payload)
			return
		if topic == self._topic("cmd/airassist/power"):
			enabled = str(payload).strip().upper() == "ON"
			self._http_post_json("/api/airassist/power", {"enabled": enabled})
			return
		if topic == self._topic("cmd/airassist/auto"):
			auto_mode = str(payload).strip().upper() == "ON"
			self._http_post_json("/api/airassist/auto", {"auto_mode": auto_mode})
			return
		if topic == self._topic("cmd/airassist/speed"):
			speed = max(0, min(100, int(float(payload))))
			self._http_post_json("/api/airassist/speed", {"speed": speed})
			return
		if topic == self._topic("cmd/airassist/auto_range_min"):
			auto_range_min = max(0, min(99, int(float(payload))))
			current = self._http_get_json("/api/airassist")
			auto_range_max = int(current.get("auto_range_max", 100))
			self._http_post_json("/api/airassist/auto", {"auto_range_min": auto_range_min, "auto_range_max": auto_range_max})
			return
		if topic == self._topic("cmd/airassist/auto_range_max"):
			auto_range_max = max(1, min(100, int(float(payload))))
			current = self._http_get_json("/api/airassist")
			auto_range_min = int(current.get("auto_range_min", 0))
			self._http_post_json("/api/airassist/auto", {"auto_range_min": auto_range_min, "auto_range_max": auto_range_max})
			return
		raise RuntimeError("unsupported command topic")

	def _handle_led_power(self, payload):
		desired_on = str(payload).upper() == "ON"
		state = self._http_get_json("/api/state")
		if bool(state.get("is_on")) != desired_on:
			self._http_post_json("/api/power", {})

	def _parse_led_preset_payload(self, payload, strict=True):
		text = str(payload).strip()
		if not text:
			if strict:
				raise ValueError("invalid empty preset")
			return None
		if text in self.LED_PRESETS:
			return text
		label_to_value = {label: raw for raw, label in self.LED_PRESET_LABELS.items()}
		if text in label_to_value:
			return label_to_value[text]
		lower_to_value = {str(label).lower(): raw for raw, label in self.LED_PRESET_LABELS.items()}
		if text.lower() in lower_to_value:
			return lower_to_value[text.lower()]
		if strict:
			raise ValueError(f"invalid preset {payload!r}")
		return None

	def _effect_label(self, effect_value):
		value = str(effect_value).strip()
		if value in self.LED_EFFECT_LABELS:
			return self.LED_EFFECT_LABELS[value]
		return value.replace("_", " ").title() if value else "Off"

	def _parse_led_effect_payload(self, payload, strict=True):
		text = str(payload).strip()
		if not text:
			if strict:
				raise ValueError("invalid empty effect")
			return None
		if text in self.LED_EFFECTS:
			return text
		label_to_value = {label: raw for raw, label in self.LED_EFFECT_LABELS.items()}
		if text in label_to_value:
			return label_to_value[text]
		lower_to_value = {str(label).lower(): raw for raw, label in self.LED_EFFECT_LABELS.items()}
		if text.lower() in lower_to_value:
			return lower_to_value[text.lower()]
		if strict:
			raise ValueError(f"invalid effect {payload!r}")
		return None

	def _color_mode_label(self, mode_value):
		value = str(mode_value).strip()
		if value in self.LED_COLOR_MODE_LABELS:
			return self.LED_COLOR_MODE_LABELS[value]
		return value.replace("_", " ").title() if value else "N/A"

	def _parse_color_mode_payload(self, payload, strict=True):
		text = str(payload).strip()
		if not text:
			if strict:
				raise ValueError("invalid empty color mode")
			return None
		if text in self.LED_COLOR_MODES:
			return text
		label_to_value = {label: raw for raw, label in self.LED_COLOR_MODE_LABELS.items()}
		if text in label_to_value:
			return label_to_value[text]
		lower_to_value = {str(label).lower(): raw for raw, label in self.LED_COLOR_MODE_LABELS.items()}
		if text.lower() in lower_to_value:
			return lower_to_value[text.lower()]
		if strict:
			raise ValueError(f"invalid color mode {payload!r}")
		return None

	def _handle_v4l2_command(self, key, payload):
		if key in ("horizontal_flip", "vertical_flip", "exposure_dynamic_framerate"):
			value = 1 if str(payload).upper() == "ON" else 0
		elif key in self._v4l2_options:
			label_to_value = {label: raw for raw, label in self._v4l2_options[key].items()}
			if payload not in label_to_value:
				raise ValueError(f"invalid option {payload!r} for {key}")
			value = int(label_to_value[payload])
		else:
			value = int(float(payload))
		self._http_post_json("/api/camera/v4l2/save", {key: value}, timeout=self.HTTP_TIMEOUT_V4L2_SAVE_S)
		self._refresh_v4l2_state()

	def _http_get_json(self, path):
		request = urllib.request.Request(self._api_base + path, headers={"Accept": "application/json"})
		try:
			with urllib.request.urlopen(request, timeout=self.HTTP_TIMEOUT_S) as response:
				return json.loads(response.read().decode("utf-8"))
		except urllib.error.HTTPError as exc:
			raise RuntimeError(f"GET {path} failed: HTTP {exc.code}") from exc

	def _http_get_json_cached(self, path, ttl_s, force=False):
		now = time.monotonic()
		with self._lock:
			cached = self._http_cache.get(path)
			if not force and cached is not None and (now - float(cached.get("ts", 0.0) or 0.0)) < float(ttl_s):
				return dict(cached.get("data", {}))
		data = self._http_get_json(path)
		with self._lock:
			self._http_cache[path] = {"ts": now, "data": dict(data)}
		return dict(data)

	def _http_post_json(self, path, payload, timeout=None):
		data = json.dumps(payload).encode("utf-8")
		request = urllib.request.Request(
			self._api_base + path,
			data=data,
			headers={"Content-Type": "application/json", "Accept": "application/json"},
			method="POST",
		)
		effective_timeout = self.HTTP_TIMEOUT_S if timeout is None else max(1, float(timeout))
		try:
			with urllib.request.urlopen(request, timeout=effective_timeout) as response:
				body = response.read().decode("utf-8")
				return json.loads(body) if body else {}
		except urllib.error.HTTPError as exc:
			detail = exc.read().decode("utf-8", errors="ignore")
			raise RuntimeError(f"POST {path} failed: HTTP {exc.code} {detail}") from exc
		except urllib.error.URLError as exc:
			raise RuntimeError(f"POST {path} failed: {exc}") from exc