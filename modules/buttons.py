import threading
import time

import RPi.GPIO as GPIO


class ButtonPoller:
	def __init__(self, pin, callback, debounce_s=0.05, poll_interval_s=0.01):
		self.pin = pin
		self.callback = callback
		self.debounce_s = debounce_s
		self.poll_interval_s = poll_interval_s
		self._running = False
		self._thread = None
		self._last_event_ts = 0.0

	def start(self):
		self._running = True
		self._thread = threading.Thread(target=self._run, daemon=True)
		self._thread.start()

	def stop(self):
		self._running = False
		if self._thread is not None:
			self._thread.join(timeout=0.3)

	def _run(self):
		# Pull-up: HIGH = released, LOW = pressed
		prev_state = GPIO.input(self.pin)
		while self._running:
			state = GPIO.input(self.pin)
			if prev_state == GPIO.HIGH and state == GPIO.LOW:
				now = time.monotonic()
				if now - self._last_event_ts >= self.debounce_s:
					self._last_event_ts = now
					self.callback()
			prev_state = state
			time.sleep(self.poll_interval_s)


class ClickDispatcher:
	def __init__(self, click_window_s, actions):
		self.click_window_s = click_window_s
		self.actions = actions
		self._click_count = 0
		self._timer = None
		self._lock = threading.Lock()

	def register_press(self):
		with self._lock:
			self._click_count += 1
			if self._timer is not None:
				self._timer.cancel()
			self._timer = threading.Timer(self.click_window_s, self._dispatch)
			self._timer.daemon = True
			self._timer.start()

	def _dispatch(self):
		with self._lock:
			count = self._click_count
			self._click_count = 0
			self._timer = None

		action = self.actions.get(count)
		if action is not None:
			action()


class ButtonRuntimeManager:
	"""Runtime executor for LED/POWER/MODE physical buttons using app settings profiles."""

	DEFAULT_MODE_PROFILES = {
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

	DEFAULT_STATIC_ACTIONS = {
		"led_double_press": "light_toggle",
		"led_triple_press": "clear_status",
		"power_double_press": "reboot",
		"power_triple_press": "shutdown",
	}

	def __init__(
		self,
		controller,
		laser_manager,
		led_pin,
		power_pin,
		mode_pin,
		click_window_s=0.65,
		debounce_s=0.05,
		poll_interval_s=0.025,
		reboot_callback=None,
		shutdown_callback=None,
		logger=None,
	):
		self._controller = controller
		self._laser_manager = laser_manager
		self._led_pin = int(led_pin)
		self._power_pin = int(power_pin)
		self._mode_pin = int(mode_pin)
		self._click_window_s = float(click_window_s)
		self._debounce_s = float(debounce_s)
		self._poll_interval_s = float(poll_interval_s)
		self._reboot_callback = reboot_callback
		self._shutdown_callback = shutdown_callback
		self._logger = logger or (lambda _msg: None)
		self._active_mode_key = "1"

		self._led_clicks = ClickDispatcher(
			self._click_window_s,
			actions={
				1: self._on_led_single_click,
				2: lambda: self._on_static_press("led_double_press"),
				3: lambda: self._on_static_press("led_triple_press"),
			},
		)
		self._power_clicks = ClickDispatcher(
			self._click_window_s,
			actions={
				1: self._on_power_single_click,
				2: lambda: self._on_static_press("power_double_press"),
				3: lambda: self._on_static_press("power_triple_press"),
			},
		)
		self._mode_clicks = ClickDispatcher(
			self._click_window_s,
			actions={
				1: lambda: self._activate_mode("1"),
				2: lambda: self._activate_mode("2"),
				3: lambda: self._activate_mode("3"),
				4: lambda: self._activate_mode("4"),
			},
		)

		self._led_button = ButtonPoller(
			self._led_pin,
			self._led_clicks.register_press,
			debounce_s=self._debounce_s,
			poll_interval_s=self._poll_interval_s,
		)
		self._power_button = ButtonPoller(
			self._power_pin,
			self._power_clicks.register_press,
			debounce_s=self._debounce_s,
			poll_interval_s=self._poll_interval_s,
		)
		self._mode_button = ButtonPoller(
			self._mode_pin,
			self._mode_clicks.register_press,
			debounce_s=self._debounce_s,
			poll_interval_s=self._poll_interval_s,
		)

	def start(self):
		self._led_button.start()
		self._power_button.start()
		self._mode_button.start()
		# Activate default profile at startup so single clicks are immediately meaningful.
		self._activate_mode(self._active_mode_key)

	def stop(self):
		self._led_button.stop()
		self._power_button.stop()
		self._mode_button.stop()

	def _settings(self):
		try:
			settings = self._laser_manager.get_settings()
			return settings if isinstance(settings, dict) else {}
		except Exception:
			return {}

	def _mode_profiles(self):
		settings = self._settings()
		raw = settings.get("mode_button_profiles", {})
		if not isinstance(raw, dict):
			raw = {}
		profiles = {}
		for key in ("1", "2", "3", "4"):
			fallback = dict(self.DEFAULT_MODE_PROFILES[key])
			value = raw.get(key, {})
			if not isinstance(value, dict):
				value = {}
			merged = dict(fallback)
			merged.update(value)
			profiles[key] = merged
		return profiles

	def _static_actions(self):
		settings = self._settings()
		raw = settings.get("button_static_actions", {})
		if not isinstance(raw, dict):
			raw = {}
		merged = dict(self.DEFAULT_STATIC_ACTIONS)
		merged.update(raw)
		return merged

	def _active_profile(self):
		profiles = self._mode_profiles()
		return profiles.get(self._active_mode_key, profiles.get("1", dict(self.DEFAULT_MODE_PROFILES["1"])))

	def reset_to_mode_one(self):
		self._activate_mode("1")

	def _activate_mode(self, mode_key):
		key = str(mode_key or "1")
		if key not in ("1", "2", "3", "4"):
			key = "1"
		self._active_mode_key = key
		profile = self._active_profile()
		try:
			self._controller.set_preset("none")
		except Exception:
			pass
		try:
			self._controller.set_color_mode(str(profile.get("led_color_mode", "cool_white")))
		except Exception:
			pass
		try:
			self._controller.set_effect(str(profile.get("led_effect", "static")))
		except Exception:
			pass
		self._logger(f"mode activated: {key} ({profile.get('entry_mode', 'n/a')})")

	def _on_led_single_click(self):
		profile = self._active_profile()
		action = str(profile.get("led_single_click_action", "next_effect") or "next_effect")
		self._execute_mode_action(action)

	def _on_power_single_click(self):
		profile = self._active_profile()
		action = str(profile.get("power_single_click_action", "next_color") or "next_color")
		self._execute_mode_action(action)

	def _on_static_press(self, static_key):
		actions = self._static_actions()
		action = str(actions.get(static_key, "none") or "none")
		self._execute_static_action(action)

	def _execute_mode_action(self, action):
		action_name = str(action or "").strip().lower()
		if not action_name:
			return
		try:
			if action_name == "move_up":
				self._laser_manager.send_jog_command("up", source="button:ledpower")
				return
			if action_name == "move_down":
				self._laser_manager.send_jog_command("down", source="button:ledpower")
				return
			if action_name == "move_left":
				self._laser_manager.send_jog_command("left", source="button:ledpower")
				return
			if action_name == "move_right":
				self._laser_manager.send_jog_command("right", source="button:ledpower")
				return
			if action_name == "move_forward":
				self._send_z_jog(+1.0)
				return
			if action_name == "move_backward":
				self._send_z_jog(-1.0)
				return
			if action_name == "next_effect":
				self._cycle_effect(+1)
				return
			if action_name == "previous_effect":
				self._cycle_effect(-1)
				return
			if action_name == "next_color":
				self._cycle_color(+1)
				return
			if action_name == "previous_color":
				self._cycle_color(-1)
				return
			if action_name == "next_preset":
				self._cycle_preset(+1)
				return
			if action_name == "previous_preset":
				self._cycle_preset(-1)
				return
			if action_name == "brightness_plus":
				self._step_brightness(+0.05)
				return
			if action_name == "brightness_minus":
				self._step_brightness(-0.05)
				return
		except Exception as exc:
			self._logger(f"mode action failed ({action_name}): {exc}")

	def _execute_static_action(self, action):
		action_name = str(action or "none").strip().lower()
		try:
			if action_name == "none":
				return
			if action_name == "light_toggle":
				self._controller.toggle_power(with_fade=True)
				return
			if action_name == "clear_status":
				self._laser_manager.clear_error()
				return
			if action_name == "homing":
				self._laser_manager.send_jog_command("home", source="button:static")
				return
			if action_name == "custom_position":
				self._laser_manager.execute_custom_position(source="button:custom_position")
				return
			if action_name == "reboot":
				if callable(self._reboot_callback):
					self._reboot_callback()
				return
			if action_name == "shutdown":
				if callable(self._shutdown_callback):
					self._shutdown_callback()
				return
		except Exception as exc:
			self._logger(f"static action failed ({action_name}): {exc}")

	def _cycle_effect(self, delta):
		state = self._controller.get_state()
		current = str(state.get("effect", "static") or "static")
		values = list(getattr(self._controller, "EFFECTS", ("static",)))
		if not values:
			return
		try:
			index = values.index(current)
		except ValueError:
			index = 0
		next_index = (index + int(delta)) % len(values)
		self._controller.set_effect(values[next_index])

	def _cycle_color(self, delta):
		state = self._controller.get_state()
		current = str(state.get("color_mode", "cool_white") or "cool_white")
		values = list(getattr(self._controller, "BUTTON_COLOR_MODES", getattr(self._controller, "COLOR_MODES", ("cool_white",))))
		if not values:
			return
		try:
			index = values.index(current)
		except ValueError:
			index = 0
		next_index = (index + int(delta)) % len(values)
		self._controller.set_color_mode(values[next_index])

	def _cycle_preset(self, delta):
		state = self._controller.get_state()
		current = str(state.get("preset", "none") or "none")
		values = list(getattr(self._controller, "PRESETS", ("none",)))
		if not values:
			return
		try:
			index = values.index(current)
		except ValueError:
			index = 0
		next_index = (index + int(delta)) % len(values)
		self._controller.set_preset(values[next_index])

	def _step_brightness(self, step):
		state = self._controller.get_state()
		current = float(state.get("brightness", 0.6) or 0.6)
		next_value = max(0.0, min(1.0, current + float(step)))
		self._controller.set_brightness(next_value)

	def _send_z_jog(self, sign):
		settings = self._settings()
		try:
			step_mm = float(settings.get("laser_move_step_mm", 20.0))
		except Exception:
			step_mm = 20.0
		try:
			feed_mm_sec = float(settings.get("laser_move_feed_mm_sec", 10.0))
		except Exception:
			feed_mm_sec = 10.0
		step_mm = max(0.1, min(100.0, step_mm))
		feed_mm_sec = max(0.2, min(80.0, feed_mm_sec))
		delta_z = step_mm * (1.0 if sign >= 0 else -1.0)
		feed_mm_min = feed_mm_sec * 60.0
		self._laser_manager.send_gcode_command("G91", source="button:z_jog")
		self._laser_manager.send_gcode_command(f"G1 Z{delta_z:.3f} F{feed_mm_min:.1f}", source="button:z_jog")
		self._laser_manager.send_gcode_command("G90", source="button:z_jog")
