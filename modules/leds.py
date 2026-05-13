import math
import random
import threading
import time

from settings import FRAME_DELAY_S
from settings import NUM_PIXELS
from settings import STARTUP_SHUTDOWN_BRIGHTNESS


class LedController:
	EFFECTS = (
		"static",
		"breathe",
		"pulse",
		"strobe",
		"flash",
		"fire",
		"disco",
		"snake",
		"twinkle",
	)
	COLOR_MODES = (
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
	)
	BUTTON_COLOR_MODES = (
		"cool_white",
		"warm_white",
		"amber_boost",
		"sunset_orange",
		"laser_green",
		"ruby_red",
		"ice_cyan",
		"magenta_pink",
		"blue_intense",
		"green_intense",
		"red_intense",
		"cyan_intense",
		"magenta_intense",
		"amber_intense",
		"random_solid",
	)
	PRESETS = (
		"none",
		"ocean_wave",
		"red_fire",
		"green_forest",
		"sunset_lava",
		"ice_plasma",
	)

	def __init__(self, pixels):
		self.pixels = pixels
		self.is_on = True
		self.effect_index = 0
		self.color_mode_index = 0  # Start in cool white
		self.preset_index = 0
		self._preset_intensity = 100

		self._lock = threading.Lock()
		self._running = True
		self._freeze_output = False
		self._phase = 0.0
		self._snake_pos = 0
		self._random_solid_color = self._new_random_color()
		self._random_palette = [self._new_random_color() for _ in range(NUM_PIXELS)]
		self._custom_color = (210, 235, 255)
		self._preset_phase = 0.0
		self._ocean_cycle = 0.0
		self._fire_heat = [0.0 for _ in range(NUM_PIXELS)]
		self._dirty = True  # When True, force pixels.show() even in static mode
		self._startup_shutdown_brightness = float(STARTUP_SHUTDOWN_BRIGHTNESS)
		self._startup_effect = "strobe"
		self._startup_color_mode = "laser_green"
		self._startup_preset = "none"
		self._shutdown_effect = "strobe"
		self._shutdown_color_mode = "ruby_red"
		self._shutdown_preset = "none"

	@staticmethod
	def _new_random_color():
		return (
			random.randint(25, 255),
			random.randint(25, 255),
			random.randint(25, 255),
		)

	@staticmethod
	def _scale(color, factor):
		return tuple(max(0, min(255, int(c * factor))) for c in color)

	@staticmethod
	def _blend(color_a, color_b, t):
		t = max(0.0, min(1.0, float(t)))
		return (
			int(color_a[0] + (color_b[0] - color_a[0]) * t),
			int(color_a[1] + (color_b[1] - color_a[1]) * t),
			int(color_a[2] + (color_b[2] - color_a[2]) * t),
		)

	def _palette_for_preset(self):
		preset = self.PRESETS[self.preset_index]
		if preset == "ocean_wave":
			return [(0, 110, 255), (0, 200, 255), (0, 255, 235), (0, 150, 255)]
		if preset == "red_fire":
			return [(255, 30, 0), (255, 95, 0), (255, 185, 20), (190, 0, 0)]
		if preset == "green_forest":
			return [(0, 105, 20), (0, 170, 45), (35, 230, 80), (0, 130, 34)]
		if preset == "sunset_lava":
			return [(255, 55, 0), (255, 125, 0), (255, 35, 105), (235, 0, 35)]
		if preset == "ice_plasma":
			return [(0, 230, 255), (0, 125, 255), (145, 45, 255), (40, 255, 255)]
		return None

	def _preset_color_for_pixel(self, idx):
		preset = self.PRESETS[self.preset_index]
		p = max(0.0, min(1.0, self._preset_intensity / 100.0))
		if preset == "ocean_wave":
			# Wave behavior: fast brightness crash followed by slower pullback.
			self._ocean_cycle = (self._ocean_cycle + 0.018) % 1.0
			if self._ocean_cycle < 0.16:
				energy = min(1.0, self._ocean_cycle / 0.16)
			else:
				energy = max(0.0, ((1.0 - self._ocean_cycle) / 0.84) ** 1.85)
			self._preset_phase += 0.08 + (0.12 * p)
			wave = (math.sin(self._preset_phase + idx * 0.55) + 1.0) / 2.0
			foam = (math.sin(self._preset_phase * 1.9 - idx * 0.23) + 1.0) / 2.0
			base = self._blend((0, 115, 255), (0, 255, 245), 0.22 + 0.78 * foam)
			intensity = (0.14 + 0.86 * p) * (0.22 + 0.78 * energy * (0.50 + 0.50 * wave))
			return self._scale(base, intensity)

		if preset == "red_fire":
			# Dynamic flame: turbulence, hotspots, and red/orange/yellow shifts.
			self._preset_phase += 0.06 + (0.10 * p)
			i = idx
			left = self._fire_heat[(i - 1) % NUM_PIXELS]
			right = self._fire_heat[(i + 1) % NUM_PIXELS]
			center = self._fire_heat[i]
			noise = random.uniform(-0.08 * p, 0.18 * p)
			next_heat = (center * 0.78) + ((left + right) * 0.11) + noise
			if random.random() < (0.02 + 0.08 * p):
				next_heat += random.uniform(0.18 * p, 0.55 * p)
			next_heat = max(0.0, min(1.0, next_heat))
			self._fire_heat[i] = next_heat
			if next_heat < 0.35:
				base = self._blend((115, 8, 0), (230, 30, 0), next_heat / 0.35)
			elif next_heat < 0.72:
				base = self._blend((230, 30, 0), (255, 120, 0), (next_heat - 0.35) / 0.37)
			else:
				base = self._blend((255, 120, 0), (255, 230, 120), (next_heat - 0.72) / 0.28)
			flicker = (0.48 + 0.52 * p) * (0.72 + 0.28 * ((math.sin(self._preset_phase + i * 0.71) + 1.0) / 2.0))
			return self._scale(base, flicker)

		if preset == "green_forest":
			# Forest: slow wind motion with gentle green breathing highlights.
			self._preset_phase += 0.03 + (0.06 * p)
			w = (math.sin(self._preset_phase + idx * 0.42) + 1.0) / 2.0
			m = (math.sin(self._preset_phase * 0.53 - idx * 0.21) + 1.0) / 2.0
			base = self._blend((0, 98, 22), (10, 220, 72), w)
			high = self._blend(base, (80, 255, 125), m * 0.36)
			return self._scale(high, (0.28 + 0.72 * p) * (0.52 + 0.48 * w))

		if preset == "sunset_lava":
			# Lava: slow incandescent waves with pulsing peaks.
			self._preset_phase += 0.04 + (0.09 * p)
			a = (math.sin(self._preset_phase + idx * 0.33) + 1.0) / 2.0
			b = (math.sin(self._preset_phase * 1.7 - idx * 0.19) + 1.0) / 2.0
			base = self._blend((215, 0, 18), (255, 105, 0), a)
			core = self._blend(base, (255, 165, 40), b * 0.32)
			return self._scale(core, (0.24 + 0.76 * p) * (0.46 + 0.54 * a))

		if preset == "ice_plasma":
			# Cold plasma: electric shimmer with cyan/blue/magenta shifts.
			self._preset_phase += 0.06 + (0.13 * p)
			a = (math.sin(self._preset_phase + idx * 0.57) + 1.0) / 2.0
			b = (math.sin(self._preset_phase * 2.2 + idx * 0.28) + 1.0) / 2.0
			base = self._blend((0, 210, 255), (0, 85, 255), a)
			arc = self._blend(base, (170, 45, 255), b * 0.62)
			flash = (0.36 + 0.64 * p) * (0.70 + 0.30 * (1.0 if random.random() < (0.01 + 0.04 * p) else b))
			return self._scale(arc, flash)

		palette = self._palette_for_preset()
		if not palette:
			return self._base_color()
		position = ((idx / max(1, NUM_PIXELS - 1)) + self._preset_phase) % 1.0
		scaled = position * len(palette)
		left = int(scaled) % len(palette)
		right = (left + 1) % len(palette)
		mix = scaled - int(scaled)
		return self._blend(palette[left], palette[right], mix)

	def _base_color(self):
		mode = self.COLOR_MODES[self.color_mode_index]
		if mode == "cool_white":
			return (210, 235, 255)
		if mode == "warm_white":
			return (255, 180, 120)
		if mode == "amber_boost":
			return (255, 140, 35)
		if mode == "sunset_orange":
			return (255, 110, 20)
		if mode == "laser_green":
			return (50, 255, 80)
		if mode == "ruby_red":
			return (220, 20, 60)
		if mode == "ice_cyan":
			return (95, 235, 255)
		if mode == "magenta_pink":
			return (255, 70, 190)
		if mode == "blue_intense":
			return (15, 60, 255)
		if mode == "blue_soft":
			return (140, 170, 255)
		if mode == "green_intense":
			return (25, 255, 90)
		if mode == "green_soft":
			return (140, 255, 178)
		if mode == "red_intense":
			return (255, 24, 48)
		if mode == "red_soft":
			return (255, 128, 146)
		if mode == "cyan_intense":
			return (0, 240, 255)
		if mode == "cyan_soft":
			return (150, 245, 255)
		if mode == "magenta_intense":
			return (255, 30, 210)
		if mode == "magenta_soft":
			return (255, 150, 230)
		if mode == "amber_intense":
			return (255, 150, 0)
		if mode == "amber_soft":
			return (255, 200, 130)
		if mode == "random_solid":
			return self._random_solid_color
		if mode == "custom_solid":
			return self._custom_color
		return (255, 255, 255)

	def _color_for_pixel(self, idx):
		if self.PRESETS[self.preset_index] != "none":
			return self._preset_color_for_pixel(idx)
		mode = self.COLOR_MODES[self.color_mode_index]
		if mode == "random_per_led":
			return self._random_palette[idx]
		return self._base_color()

	def _apply_off(self):
		self.pixels.fill((0, 0, 0))
		self.pixels.show()

	def _blink_fill(self, color, duration_s=2.0, on_s=0.08, off_s=0.07, intensity=1.0):
		blink_color = self._scale(color, intensity)
		end_ts = time.monotonic() + duration_s
		while time.monotonic() < end_ts:
			self.pixels.fill(blink_color)
			self.pixels.show()
			time.sleep(on_s)
			self.pixels.fill((0, 0, 0))
			self.pixels.show()
			time.sleep(off_s)

	def _fade_fill(self, color, duration_s=1.0, fade_in=True):
		steps = max(1, int(duration_s / FRAME_DELAY_S))
		for step in range(steps + 1):
			pct = step / steps
			if not fade_in:
				pct = 1.0 - pct
			self.pixels.fill(self._scale(color, pct))
			self.pixels.show()
			time.sleep(FRAME_DELAY_S)

	def _blink_fill_at_brightness(self, color, brightness, duration_s=2.0, on_s=0.08, off_s=0.07):
		previous_brightness = float(self.pixels.brightness)
		self.pixels.brightness = max(0.0, min(1.0, float(brightness)))
		try:
			self._blink_fill(color, duration_s=duration_s, on_s=on_s, off_s=off_s, intensity=1.0)
		finally:
			self.pixels.brightness = previous_brightness

	def configure_power_cycle_feedback(self, startup_effect=None, startup_color_mode=None, startup_preset=None, shutdown_effect=None, shutdown_color_mode=None, shutdown_preset=None, brightness=None):
		with self._lock:
			if startup_effect in self.EFFECTS:
				self._startup_effect = startup_effect
			if startup_color_mode in self.COLOR_MODES:
				self._startup_color_mode = startup_color_mode
			if startup_preset in self.PRESETS:
				self._startup_preset = startup_preset
			if shutdown_effect in self.EFFECTS:
				self._shutdown_effect = shutdown_effect
			if shutdown_color_mode in self.COLOR_MODES:
				self._shutdown_color_mode = shutdown_color_mode
			if shutdown_preset in self.PRESETS:
				self._shutdown_preset = shutdown_preset
			if brightness is not None:
				self._startup_shutdown_brightness = max(0.0, min(1.0, float(brightness)))

	def _render_effect_once(self, effect):
		if effect == "static":
			self._render_static()
		elif effect == "breathe":
			self._render_breathe()
		elif effect == "pulse":
			self._render_pulse()
		elif effect == "strobe":
			self._render_strobe()
		elif effect == "flash":
			self._render_flash()
		elif effect == "fire":
			self._render_fire()
		elif effect == "disco":
			self._render_disco()
		elif effect == "snake":
			self._render_snake()
		elif effect == "twinkle":
			self._render_twinkle()
		else:
			self._render_static()

	def _play_power_cycle_profile(self, effect_name, color_mode, preset_name, brightness, duration_s=2.0):
		with self._lock:
			prev_state = {
				"is_on": self.is_on,
				"freeze": self._freeze_output,
				"effect_idx": self.effect_index,
				"color_idx": self.color_mode_index,
				"preset_idx": self.preset_index,
				"phase": self._phase,
				"preset_phase": self._preset_phase,
				"ocean_cycle": self._ocean_cycle,
				"snake_pos": self._snake_pos,
				"brightness": float(self.pixels.brightness),
			}
			self._freeze_output = True
			self.is_on = True
			self.effect_index = self.EFFECTS.index(effect_name) if effect_name in self.EFFECTS else self.EFFECTS.index("strobe")
			self.color_mode_index = self.COLOR_MODES.index(color_mode) if color_mode in self.COLOR_MODES else self.COLOR_MODES.index("cool_white")
			self.preset_index = self.PRESETS.index(preset_name) if preset_name in self.PRESETS else self.PRESETS.index("none")
			self._phase = 0.0
			self._preset_phase = 0.0
			self._ocean_cycle = 0.0
			self._snake_pos = 0
			self.pixels.brightness = max(0.0, min(1.0, float(brightness)))

		try:
			end_ts = time.monotonic() + max(0.2, float(duration_s))
			while time.monotonic() < end_ts:
				with self._lock:
					effect = self.EFFECTS[self.effect_index]
				self._render_effect_once(effect)
				self.pixels.show()
				time.sleep(FRAME_DELAY_S)
			self._apply_off()
		finally:
			with self._lock:
				self.is_on = prev_state["is_on"]
				self._freeze_output = prev_state["freeze"]
				self.effect_index = prev_state["effect_idx"]
				self.color_mode_index = prev_state["color_idx"]
				self.preset_index = prev_state["preset_idx"]
				self._phase = prev_state["phase"]
				self._preset_phase = prev_state["preset_phase"]
				self._ocean_cycle = prev_state["ocean_cycle"]
				self._snake_pos = prev_state["snake_pos"]
				self.pixels.brightness = prev_state["brightness"]
				self._dirty = True

	def play_startup_effect(self):
		with self._lock:
			effect = str(self._startup_effect)
			color_mode = str(self._startup_color_mode)
			preset = str(self._startup_preset)
			brightness = float(self._startup_shutdown_brightness)
		self._play_power_cycle_profile(effect, color_mode, preset, brightness, duration_s=2.0)

	def play_shutdown_effect(self):
		with self._lock:
			effect = str(self._shutdown_effect)
			color_mode = str(self._shutdown_color_mode)
			preset = str(self._shutdown_preset)
			brightness = float(self._startup_shutdown_brightness)
		self._play_power_cycle_profile(effect, color_mode, preset, brightness, duration_s=2.0)

	def toggle_power(self, with_fade=False):
		with self._lock:
			self.is_on = not self.is_on
			is_on = self.is_on
			if is_on:
				self.color_mode_index = 0  # Always reset to cool white on power-on.
				self.effect_index = 0      # Always reset to static on power-on.
				self._freeze_output = with_fade
			else:
				self._freeze_output = with_fade

		if not is_on:
			if with_fade:
				cool = (210, 235, 255)
				self._fade_fill(cool, duration_s=0.8, fade_in=False)
				self._apply_off()
			else:
				self._apply_off()
		else:
			with self._lock:
				self._dirty = True
			if with_fade:
				cool = (210, 235, 255)
				with self._lock:
					self._freeze_output = True
				self._fade_fill(cool, duration_s=0.8, fade_in=True)
				with self._lock:
					self._freeze_output = False

	def next_effect(self):
		with self._lock:
			self.effect_index = (self.effect_index + 1) % len(self.EFFECTS)
			self._phase = 0.0
			self._dirty = True

	def next_color_mode(self):
		with self._lock:
			current_mode = self.COLOR_MODES[self.color_mode_index]
			try:
				idx = self.BUTTON_COLOR_MODES.index(current_mode)
			except ValueError:
				idx = 0

			next_idx = (idx + 1) % len(self.BUTTON_COLOR_MODES)
			next_mode = self.BUTTON_COLOR_MODES[next_idx]
			self.color_mode_index = self.COLOR_MODES.index(next_mode)
			mode = next_mode
			if mode == "random_solid":
				self._random_solid_color = self._new_random_color()
			elif mode == "random_per_led":
				self._random_palette = [self._new_random_color() for _ in range(NUM_PIXELS)]
			self._dirty = True
			do_blink = (mode == "cool_white")

		if do_blink:
			self._blink_fill((210, 235, 255), duration_s=2.0, on_s=0.15, off_s=0.18, intensity=0.9)

	def set_effect(self, effect_name):
		if effect_name not in self.EFFECTS:
			return False
		with self._lock:
			self.effect_index = self.EFFECTS.index(effect_name)
			self._phase = 0.0
			self._dirty = True
		return True

	def set_color_mode(self, color_mode):
		if color_mode not in self.COLOR_MODES:
			return False
		with self._lock:
			self.color_mode_index = self.COLOR_MODES.index(color_mode)
			self.preset_index = self.PRESETS.index("none")
			if color_mode == "random_solid":
				self._random_solid_color = self._new_random_color()
			elif color_mode == "random_per_led":
				self._random_palette = [self._new_random_color() for _ in range(NUM_PIXELS)]
			self._dirty = True
		return True

	def set_custom_color(self, r, g, b):
		with self._lock:
			self._custom_color = (
				max(0, min(255, int(r))),
				max(0, min(255, int(g))),
				max(0, min(255, int(b))),
			)
			self.color_mode_index = self.COLOR_MODES.index("custom_solid")
			self.preset_index = self.PRESETS.index("none")
			self._dirty = True

	def set_preset(self, preset_name):
		if preset_name not in self.PRESETS:
			return False
		with self._lock:
			self.preset_index = self.PRESETS.index(preset_name)
			self._preset_phase = 0.0
			self._ocean_cycle = 0.0
			if preset_name != "red_fire":
				self._fire_heat = [0.0 for _ in range(NUM_PIXELS)]
			self._dirty = True
		return True

	def set_preset_intensity(self, value):
		try:
			ivalue = int(value)
		except Exception:
			return False
		ivalue = max(0, min(100, ivalue))
		with self._lock:
			self._preset_intensity = ivalue
			self._dirty = True
		return True

	def set_brightness(self, brightness):
		value = max(0.0, min(1.0, float(brightness)))
		with self._lock:
			self.pixels.brightness = value
			self._dirty = True

	def get_state(self):
		with self._lock:
			return {
				"is_on": self.is_on,
				"effect": self.EFFECTS[self.effect_index],
				"color_mode": self.COLOR_MODES[self.color_mode_index],
				"preset": self.PRESETS[self.preset_index],
				"preset_intensity": int(self._preset_intensity),
				"brightness": round(float(self.pixels.brightness), 3),
				"custom_color": list(self._custom_color),
			}

	def run_poweroff_feedback(self):
		with self._lock:
			self.is_on = False
			self._freeze_output = True
		self.play_shutdown_effect()

	def stop(self):
		with self._lock:
			self._running = False

	def run(self):
		while True:
			sleep_s = FRAME_DELAY_S
			with self._lock:
				if not self._running:
					break
				is_on = self.is_on
				freeze_output = self._freeze_output
				effect = self.EFFECTS[self.effect_index]
				preset_name = self.PRESETS[self.preset_index]
				if preset_name != "none":
					self._preset_phase = (self._preset_phase + 0.012) % 1.0

			if freeze_output:
				sleep_s = max(FRAME_DELAY_S, 0.12)
				time.sleep(sleep_s)
				continue

			if not is_on:
				sleep_s = max(FRAME_DELAY_S, 0.20)
				time.sleep(sleep_s)
				continue

			if effect == "static":
				with self._lock:
					dirty = self._dirty or (preset_name != "none")
					self._dirty = False
				if dirty:
					self._render_static()
					self.pixels.show()
				sleep_s = FRAME_DELAY_S if preset_name != "none" else (FRAME_DELAY_S if dirty else 0.12)
			else:
				if effect == "breathe":
					self._render_breathe()
				elif effect == "pulse":
					self._render_pulse()
				elif effect == "strobe":
					self._render_strobe()
				elif effect == "flash":
					self._render_flash()
				elif effect == "fire":
					self._render_fire()
				elif effect == "disco":
					self._render_disco()
				elif effect == "snake":
					self._render_snake()
				elif effect == "twinkle":
					self._render_twinkle()
				self.pixels.show()

			time.sleep(sleep_s)

		self._apply_off()

	def _render_static(self):
		if self.PRESETS[self.preset_index] != "none":
			for i in range(NUM_PIXELS):
				self.pixels[i] = self._preset_color_for_pixel(i)
			return
		mode = self.COLOR_MODES[self.color_mode_index]
		if mode == "random_per_led":
			for i in range(NUM_PIXELS):
				self.pixels[i] = self._random_palette[i]
		else:
			self.pixels.fill(self._base_color())

	def _render_breathe(self):
		self._phase += 0.08
		factor = 0.15 + 0.85 * ((math.sin(self._phase) + 1.0) / 2.0)
		for i in range(NUM_PIXELS):
			self.pixels[i] = self._scale(self._color_for_pixel(i), factor)

	def _render_pulse(self):
		self._phase += 0.24
		factor = 0.08 + 0.92 * ((math.sin(self._phase) + 1.0) / 2.0)
		for i in range(NUM_PIXELS):
			self.pixels[i] = self._scale(self._color_for_pixel(i), factor)

	def _render_strobe(self):
		self._phase = (self._phase + 1.0) % 1000.0
		on = (int(self._phase) % 2) == 0
		if on:
			for i in range(NUM_PIXELS):
				self.pixels[i] = self._color_for_pixel(i)
		else:
			self.pixels.fill((0, 0, 0))

	def _render_flash(self):
		self._phase = (self._phase + 1.0) % 40.0
		step = int(self._phase)
		if step in (0, 1, 4, 5):
			factor = 1.0
		elif step in (2, 3, 6, 7):
			factor = 0.35
		else:
			factor = 0.0
		self.pixels.fill(self._scale(self._base_color(), factor))

	def _render_fire(self):
		base = self._base_color()
		for i in range(NUM_PIXELS):
			flicker = random.uniform(0.35, 1.0)
			r = max(0, min(255, int(base[0] * flicker + random.randint(0, 20))))
			g = max(0, min(255, int(base[1] * random.uniform(0.4, 0.95))))
			b = max(0, min(120, int(base[2] * random.uniform(0.0, 0.25))))
			self.pixels[i] = (r, g, b)

	def _render_disco(self):
		self._phase += 0.4
		if int(self._phase) % 3 == 0:
			self._random_solid_color = self._new_random_color()
		factor = 0.45 + 0.55 * ((math.sin(self._phase) + 1.0) / 2.0)
		self.pixels.fill(self._scale(self._random_solid_color, factor))

	def _render_snake(self):
		self.pixels.fill((0, 0, 0))
		length = max(3, NUM_PIXELS // 6)

		for i in range(length):
			idx = (self._snake_pos - i) % NUM_PIXELS
			fade = 1.0 - (i / length)
			color = self._color_for_pixel(idx)
			self.pixels[idx] = self._scale(color, fade)

		self._snake_pos = (self._snake_pos + 1) % NUM_PIXELS
		self._phase += 0.05

	def _render_twinkle(self):
		for i in range(NUM_PIXELS):
			self.pixels[i] = self._scale(self.pixels[i], 0.75)

		burst = max(1, NUM_PIXELS // 8)
		for _ in range(burst):
			idx = random.randint(0, NUM_PIXELS - 1)
			self.pixels[idx] = self._color_for_pixel(idx)
