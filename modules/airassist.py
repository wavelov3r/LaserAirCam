import threading
import time

import RPi.GPIO as GPIO


class AirAssistController:
	"""Controls the air-assist pump/fan via software PWM on a single GPIO pin.

	Supports manual mode (fixed speed) and auto mode where the duty cycle is
	computed proportionally from the live laser S-value received via serial.

	Auto-mode mapping:
	  - laser_pct < auto_range_min  → duty 0 (off)
	  - auto_range_min <= laser_pct <= auto_range_max → duty linearly 0-100 %
	  - laser_pct > auto_range_max  → duty 100 %

	Where laser_pct = (current_S / laser_max_power) * 100.
	"""

	def __init__(self, pin, freq_hz=1000, default_speed=100, laser_max_power=1000):
		self._pin = int(pin)
		self._freq_hz = max(1, int(freq_hz))
		self._default_speed = max(0, min(100, int(default_speed)))
		self._lock = threading.Lock()
		self._pwm = None
		self._enabled = False
		self._speed = self._default_speed
		self._started = False
		self._listen_events = False

		# Auto mode
		self._laser_max_power = max(1, int(laser_max_power))
		self._auto_mode = False
		self._auto_range_min = 0    # laser % at which air assist starts
		self._auto_range_max = 100  # laser % at which air assist hits 100 % PWM
		self._auto_min_pwm = 0      # PWM % applied exactly at auto_range_min
		self._get_laser_power_fn = None   # callable() → int S value
		self._auto_thread = None
		self._auto_stop = threading.Event()

	# ------------------------------------------------------------------
	# Lifecycle
	# ------------------------------------------------------------------

	def start(self):
		with self._lock:
			if self._started:
				return
			GPIO.setup(self._pin, GPIO.OUT)
			self._pwm = GPIO.PWM(self._pin, self._freq_hz)
			self._pwm.start(0)
			self._started = True
			if self._enabled:
				self._pwm.ChangeDutyCycle(self._speed)
		if self._get_laser_power_fn is not None:
			self._auto_stop.clear()
			self._auto_thread = threading.Thread(target=self._auto_loop, daemon=True)
			self._auto_thread.start()

	def stop(self):
		self._auto_stop.set()
		with self._lock:
			if not self._started:
				return
			try:
				self._pwm.stop()
			except Exception:
				pass
			self._pwm = None
			self._started = False
		if self._auto_thread is not None:
			self._auto_thread.join(timeout=1.0)
			self._auto_thread = None

	# ------------------------------------------------------------------
	# Configuration
	# ------------------------------------------------------------------

	def set_laser_source(self, get_fn):
		"""Provide a callable that returns the current laser S value (int)."""
		with self._lock:
			self._get_laser_power_fn = get_fn

	def set_auto_mode(self, enabled: bool):
		with self._lock:
			self._auto_mode = bool(enabled)
			if self._started and self._pwm is not None and not self._auto_mode and not self._enabled:
				self._pwm.ChangeDutyCycle(0)

	def set_auto_range(self, range_min, range_max):
		mn = max(0, min(99, int(round(float(range_min)))))
		mx = max(1, min(100, int(round(float(range_max)))))
		if mn >= mx:
			mx = min(100, mn + 1)
		with self._lock:
			self._auto_range_min = mn
			self._auto_range_max = mx

	def set_auto_min_pwm(self, min_pwm):
		value = max(0, min(100, int(round(float(min_pwm)))))
		with self._lock:
			self._auto_min_pwm = value

	def set_laser_max_power(self, val):
		with self._lock:
			self._laser_max_power = max(1, int(round(float(val))))

	def set_listen_events(self, enabled: bool):
		with self._lock:
			self._listen_events = bool(enabled)

	# ------------------------------------------------------------------
	# Manual control
	# ------------------------------------------------------------------

	def set_enabled(self, enabled: bool):
		with self._lock:
			self._enabled = bool(enabled)
			if self._started and self._pwm is not None:
				if not self._enabled:
					# Global gate: OFF always forces PWM off, even if auto mode is active.
					self._pwm.ChangeDutyCycle(0)
				elif not self._auto_mode:
					self._pwm.ChangeDutyCycle(self._speed)

	def set_speed(self, speed):
		value = max(0, min(100, int(round(float(speed)))))
		with self._lock:
			self._speed = value
			if self._started and self._pwm is not None and self._enabled and not self._auto_mode:
				self._pwm.ChangeDutyCycle(self._speed)

	# ------------------------------------------------------------------
	# Auto loop
	# ------------------------------------------------------------------

	def _compute_auto_duty(self, s_value):
		"""Map a raw S value to a duty cycle 0-100, using the range settings."""
		with self._lock:
			laser_pct = min(100.0, (s_value / self._laser_max_power) * 100.0)
			rmin = self._auto_range_min
			rmax = self._auto_range_max
			min_pwm = self._auto_min_pwm
		if laser_pct < rmin:
			return 0
		if laser_pct >= rmax:
			return 100
		span = rmax - rmin
		if span <= 0:
			return 100
		ratio = max(0.0, min(1.0, (laser_pct - rmin) / span))
		target = min_pwm + (100.0 - min_pwm) * ratio
		return int(round(max(min_pwm, min(100.0, target))))

	def _auto_loop(self):
		while not self._auto_stop.is_set():
			with self._lock:
				auto_on = self._auto_mode
				enabled = self._enabled
				started = self._started
				pwm = self._pwm
				get_fn = self._get_laser_power_fn
			if auto_on and enabled and started and pwm is not None and get_fn is not None:
				try:
					s_val = int(get_fn())
					duty = self._compute_auto_duty(s_val)
					with self._lock:
						if self._started and self._pwm is not None and self._auto_mode and self._enabled:
							self._pwm.ChangeDutyCycle(duty)
				except Exception:
					pass
			elif started and pwm is not None:
				try:
					with self._lock:
						if self._started and self._pwm is not None and not self._enabled:
							self._pwm.ChangeDutyCycle(0)
				except Exception:
					pass
			self._auto_stop.wait(timeout=0.25)

	# ------------------------------------------------------------------
	# State
	# ------------------------------------------------------------------

	def get_state(self) -> dict:
		with self._lock:
			return {
				"enabled": self._enabled,
				"speed": self._speed,
				"auto_mode": self._auto_mode,
				"auto_range_min": self._auto_range_min,
				"auto_range_max": self._auto_range_max,
				"auto_min_pwm": self._auto_min_pwm,
				"laser_max_power": self._laser_max_power,
				"listen_events": self._listen_events,
			}
