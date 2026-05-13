def camera_controls_html():
	html = """<!doctype html>
			<html lang=\"en\">
<head>
	<meta charset=\"utf-8\">
	<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
	<title>Camera v4l2 Controls</title>
	<link rel=\"manifest\" href=\"/manifest.webmanifest\">
	<meta name=\"theme-color\" content=\"#0c3a66\">
	<meta name=\"apple-mobile-web-app-capable\" content=\"yes\">
	<meta name=\"apple-mobile-web-app-status-bar-style\" content=\"black-translucent\">
	<meta name=\"msapplication-TileColor\" content=\"#0c3a66\">
	<link rel=\"icon\" type=\"image/png\" sizes=\"192x192\" href=\"/pwa-icon-192.png\">
	<link rel=\"icon\" type=\"image/png\" sizes=\"512x512\" href=\"/pwa-icon-512.png\">
	<link rel=\"apple-touch-icon\" href=\"/pwa-icon-192.png\">
	<style>
		:root {
			--bg1: #041a2f;
			--bg2: #0c3a66;
			--bg3: #16558b;
			--card: rgba(7, 26, 45, 0.82);
			--text: #eaf4ff;
			--muted: #b7d3ef;
			--accent: #74c2ff;
			--accent2: #2f8ee5;
			--line: rgba(140, 199, 255, 0.33);
		}
		* { box-sizing: border-box; }
		body {
			margin: 0;
			min-height: 100vh;
			font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
			color: var(--text);
			background: radial-gradient(circle at 10% 10%, rgba(116, 194, 255, 0.22), transparent 36%), radial-gradient(circle at 92% 16%, rgba(47, 142, 229, 0.22), transparent 34%), linear-gradient(130deg, #7b7b7b, var(--bg2) 52%, #6e706e);
			padding: 12px;
		}
		.layout {
			display: grid;
			grid-template-columns: 1fr 1fr;
			gap: 12px;
			max-width: 1800px;
			margin: 12px;
		}
		.card {
			background: var(--card);
			border: 1px solid var(--line);
			border-radius: 16px;
			padding: 14px;
			backdrop-filter: blur(9px);
			box-shadow: 0 14px 34px rgba(0, 20, 43, 0.42);
		}
		h1 { margin: 0 0 6px; font-size: 1.2rem; }
		.lead { margin: 0 0 12px; color: var(--muted); font-size: 0.9rem; }
		.toolbar {
			display: grid;
			grid-template-columns: 1fr 1fr;
			gap: 8px;
			margin-bottom: 12px;
		}
		button {
			width: 100%;
			border-radius: 10px;
			border: 1px solid rgba(179, 222, 255, 0.78);
			padding: 8px 10px;
			font-size: 0.88rem;
			font-weight: 700;
			cursor: pointer;
			background: linear-gradient(120deg, var(--accent2), var(--accent));
			color: #042641;
		}
		button.secondary {
			background: linear-gradient(120deg, #184f81, #2d77b8);
			color: #dff0ff;
			border-color: rgba(140, 199, 255, 0.48);
		}
		button:disabled { opacity: 0.7; cursor: wait; }
		#controls {
			display: grid;
			gap: 9px;
			max-height: calc(100vh - 190px);
			overflow: auto;
			padding-right: 4px;
		}
		.ctrl {
			padding: 10px;
			border-radius: 10px;
			background: rgba(116, 194, 255, 0.08);
			border: 1px solid rgba(116, 194, 255, 0.24);
		}
		.ctrl-head {
			display: flex;
			align-items: center;
			justify-content: space-between;
			gap: 8px;
			margin-bottom: 7px;
			font-size: 0.86rem;
		}
		.ctrl-val { font-weight: 700; color: #e8f4ff; }
		input[type=\"range\"], select {
			width: 100%;
			border-radius: 8px;
			border: 1px solid rgba(140, 199, 255, 0.33);
			background: rgba(6, 31, 56, 0.78);
			color: var(--text);
			padding: 7px 9px;
			font-size: 0.88rem;
		}
		.ctrl select {
			width: 84%;
			min-width: 210px;
			max-width: 360px;
		}
		select option { background: #0a2a4a; color: #eaf4ff; }
		.ctrl-check {
			display: flex;
			align-items: center;
			gap: 8px;
			color: var(--muted);
			font-size: 0.86rem;
		}
		.status { margin-top: 10px; color: var(--muted); font-size: 0.86rem; min-height: 1.1rem; }
		#controls {
			scrollbar-width: thin;
			scrollbar-color: rgba(116, 194, 255, 0.8) rgba(8, 33, 61, 0.55);
		}
		#controls::-webkit-scrollbar {
			width: 10px;
		}
		#controls::-webkit-scrollbar-track {
			background: linear-gradient(180deg, rgba(6, 25, 45, 0.75), rgba(10, 36, 62, 0.75));
			border-radius: 999px;
			border: 1px solid rgba(116, 194, 255, 0.2);
		}
		#controls::-webkit-scrollbar-thumb {
			background: linear-gradient(180deg, #82cbff, #4f9fe5);
			border-radius: 999px;
			border: 2px solid rgba(5, 24, 43, 0.85);
		}
		#controls::-webkit-scrollbar-thumb:hover {
			background: linear-gradient(180deg, #9dd9ff, #64b1f2);
		}
		.preview-wrap {
			height: 100%;
			display: grid;
			gap: 10px;
			grid-template-rows: auto 1fr;
		}
		.preview-sticky {
			position: sticky;
			top: 12px;
			align-self: start;
			max-height: calc(100vh - 24px);
		}
		.preview-box {
			position: relative;
			background: rgba(116, 194, 255, 0.08);
			border: 1px solid rgba(116, 194, 255, 0.24);
			border-radius: 12px;
			padding: 10px;
			height: min(74vh, calc(100vh - 150px));
			min-height: 240px;
		}
		.fullscreen-btn {
			position: absolute;
			top: 14px;
			right: 14px;
			z-index: 20;
			width: auto;
			padding: 4px 8px;
			border-radius: 8px;
			font-size: 0.78rem;
			font-weight: 700;
			letter-spacing: 0.03em;
			background: rgba(5, 26, 47, 0.6);
			color: #dff2ff;
			border: 1px solid rgba(140, 199, 255, 0.45);
			backdrop-filter: blur(4px);
			opacity: 0.8;
		}
		.fullscreen-btn:hover {
			opacity: 1;
			background: rgba(8, 36, 64, 0.85);
		}
		.preview-box img {
			width: 100%;
			height: 100%;
			object-fit: contain;
			background: #000;
			border-radius: 10px;
			border: 1px solid rgba(140, 199, 255, 0.45);
		}
		.preview-note { color: var(--muted); font-size: 0.84rem; }
		@media (max-width: 980px) {
			.layout { grid-template-columns: 1fr; }
			#controls { max-height: none; }
			.preview-sticky {
				position: static;
				top: auto;
				max-height: none;
			}
			.preview-box {
				height: auto;
				min-height: 220px;
			}
			.preview-box img {
				height: auto;
				aspect-ratio: 4 / 3;
			}
		}
	</style>
</head>
<body>
	<main class=\"layout\">
		<section class=\"card\">
			<h1>V4L2 Camera Parameters</h1>
			<p class=\"lead\">Adjust quality and auto controls in real time, then save the profile to restore it at startup.</p>
			<div class=\"toolbar\">
				<button id=\"goBack\" class=\"secondary\">Back to Dashboard</button>
				<button id=\"reloadBtn\" class=\"secondary\">Reload</button>
				<button id=\"resetDefaultsBtn\" class=\"secondary\">Reset Default Driver</button>
				<button id=\"saveBtn\">Save Profile</button>
			</div>
			<div id=\"controls\"></div>
			<div class=\"status\" id=\"status\">Loading parameters...<br>AirAssist: <span id=\"airAssistStatusText\">--</span></div>
		</section>
		<section class=\"card preview-wrap preview-sticky\">
			<div>
				<h1>Preview Live</h1>
				<p class=\"preview-note\">Preview stream</p>
			</div>
			<div class=\"preview-box\">
				<button id=\"previewFullscreenBtn\" class=\"fullscreen-btn\" type=\"button\" title=\"Fullscreen\">fullscreen</button>
				<img id=\"preview\" src=\"\" alt=\"Preview camera\">
			</div>
		</section>
	</main>

	<script>
		const statusEl = document.getElementById('status');
		const controlsEl = document.getElementById('controls');
		const previewEl = document.getElementById('preview');
		const previewFullscreenBtn = document.getElementById('previewFullscreenBtn');
		const saveBtn = document.getElementById('saveBtn');
		const reloadBtn = document.getElementById('reloadBtn');
		const resetDefaultsBtn = document.getElementById('resetDefaultsBtn');
		const order = [
			'brightness',
			'contrast',
			'saturation',
			'sharpness',
			'compression_quality',
			'power_line_frequency',
			'rotate',
			'horizontal_flip',
			'vertical_flip',
			'auto_exposure',
			'exposure_time_absolute',
			'exposure_dynamic_framerate',
			'auto_exposure_bias',
			'white_balance_auto_preset',
			'iso_sensitivity_auto',
			'iso_sensitivity',
			'exposure_metering_mode',
			'scene_mode'
		];
		const labels = {
			brightness: 'Brightness',
			contrast: 'Contrast',
			saturation: 'Saturation',
			sharpness: 'Sharpness',
			compression_quality: 'JPEG Quality',
			power_line_frequency: 'Power Line Filter',
			rotate: 'Rotate',
			horizontal_flip: 'Horizontal Flip',
			vertical_flip: 'Vertical Flip',
			auto_exposure: 'Exposure',
			exposure_time_absolute: 'Exposure Time',
			exposure_dynamic_framerate: 'Dynamic FPS',
			auto_exposure_bias: 'Exposure Compensation',
			white_balance_auto_preset: 'White Balance',
			iso_sensitivity_auto: 'ISO Auto',
			iso_sensitivity: 'ISO Manual',
			exposure_metering_mode: 'Exposure Metering',
			scene_mode: 'Scene'
		};
		let meta = {};
		let current = {};
		let previewTimer = null;
		let streamFallbackUsed = false;

		function setStatus(msg) { statusEl.textContent = msg; }

		function streamStart() {
			const mode = streamFallbackUsed ? '/streamhd' : '/stream';
			previewEl.src = mode + '?t=' + Date.now();
		}

		previewEl.addEventListener('error', () => {
			if (!streamFallbackUsed) {
				streamFallbackUsed = true;
				setStatus('Primary stream unavailable, trying StreamHD...');
			}
			setTimeout(streamStart, 1200);
		});

		previewEl.addEventListener('load', () => {
			if (streamFallbackUsed) {
				setStatus('Preview running on StreamHD (fallback).');
			}
		});

		async function togglePreviewFullscreen() {
			if (!document.fullscreenElement) {
				try {
					await previewEl.requestFullscreen();
				} catch (err) {
					setStatus('Fullscreen is not available in this browser.');
				}
				return;
			}
			await document.exitFullscreen();
		}

		previewFullscreenBtn.addEventListener('click', togglePreviewFullscreen);
		previewEl.addEventListener('dblclick', togglePreviewFullscreen);
		document.addEventListener('fullscreenchange', () => {
			previewFullscreenBtn.textContent = document.fullscreenElement ? 'exit' : 'fullscreen';
		});

		function renderControl(name) {
			const info = meta[name];
			if (!info) return null;
			const wrap = document.createElement('div');
			wrap.className = 'ctrl';
			const head = document.createElement('div');
			head.className = 'ctrl-head';
			const title = document.createElement('span');
			title.textContent = labels[name] || name;
			const valueLabel = document.createElement('span');
			valueLabel.className = 'ctrl-val';
			head.appendChild(title);
			head.appendChild(valueLabel);
			wrap.appendChild(head);

			let input = null;
			if (info.type === 'bool') {
				const line = document.createElement('label');
				line.className = 'ctrl-check';
				input = document.createElement('input');
				input.type = 'checkbox';
				input.checked = Number(current[name] || 0) === 1;
				valueLabel.textContent = input.checked ? 'ON' : 'OFF';
				line.appendChild(input);
				line.appendChild(document.createTextNode(input.checked ? 'Enabled' : 'Disabled'));
				wrap.appendChild(line);
				input.addEventListener('change', () => {
					current[name] = input.checked ? 1 : 0;
					valueLabel.textContent = input.checked ? 'ON' : 'OFF';
					line.lastChild.textContent = input.checked ? 'Enabled' : 'Disabled';
					schedulePreview();
					toggleDependencies();
				});
			} else if (info.type === 'menu') {
				input = document.createElement('select');
				const options = info.options || {};
				Object.keys(options)
					.sort((a, b) => Number(a) - Number(b))
					.forEach((key) => {
						const opt = document.createElement('option');
						opt.value = key;
						opt.textContent = options[key];
						input.appendChild(opt);
					});
				input.value = String(current[name]);
				valueLabel.textContent = options[String(current[name])] || options[current[name]] || current[name];
				input.addEventListener('change', () => {
					current[name] = parseInt(input.value, 10);
					valueLabel.textContent = options[input.value] || input.value;
					schedulePreview();
					toggleDependencies();
				});
				wrap.appendChild(input);
			} else {
				input = document.createElement('input');
				input.type = 'range';
				input.min = info.min;
				input.max = info.max;
				input.step = info.step || 1;
				input.value = current[name];
				valueLabel.textContent = input.value;
				input.addEventListener('input', () => {
					current[name] = parseInt(input.value, 10);
					valueLabel.textContent = input.value;
					schedulePreview();
					toggleDependencies();
				});
				wrap.appendChild(input);
			}

			wrap.dataset.ctrl = name;
			wrap.dataset.inputType = info.type;
			return wrap;
		}

		function toggleDependencies() {
			const autoExposure = Number(current.auto_exposure || 0);
			const isoAuto = Number((current.iso_sensitivity_auto ?? 1));
			const expoWrap = controlsEl.querySelector('[data-ctrl="exposure_time_absolute"]');
			const isoWrap = controlsEl.querySelector('[data-ctrl="iso_sensitivity"]');
			if (expoWrap) {
				const input = expoWrap.querySelector('input,select');
				if (input) input.disabled = autoExposure !== 1;
				expoWrap.style.opacity = autoExposure === 1 ? '1' : '0.55';
			}
			if (isoWrap) {
				const input = isoWrap.querySelector('input,select');
				if (input) input.disabled = isoAuto !== 0;
				isoWrap.style.opacity = isoAuto === 0 ? '1' : '0.55';
			}
		}

		async function loadV4L2() {
			setStatus('Loading parameters...');
			const res = await fetch('/api/camera/v4l2');
			if (!res.ok) {
				let detail = 'load failed';
				try {
					const body = await res.json();
					detail = body.detail || body.error || detail;
				} catch (err) {}
				throw new Error(detail + ' (HTTP ' + res.status + ')');
			}
			const data = await res.json();
			meta = data.meta || {};
			current = data.controls || {};
			controlsEl.innerHTML = '';
			order.forEach((name) => {
				const node = renderControl(name);
				if (node) controlsEl.appendChild(node);
			});
			toggleDependencies();
			setStatus('Realtime preview active. Press Save Profile to persist values.');
		}

		async function previewApply() {
			await fetch('/api/camera/v4l2/preview', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(current),
			});
		}

		function schedulePreview() {
			if (previewTimer) clearTimeout(previewTimer);
			previewTimer = setTimeout(async () => {
				try {
					await previewApply();
					setStatus('Realtime preview updated.');
				} catch (err) {
					setStatus('Realtime apply failed.');
				}
			}, 180);
		}

		saveBtn.addEventListener('click', async () => {
			saveBtn.disabled = true;
			setStatus('Saving profile...');
			try {
				const res = await fetch('/api/camera/v4l2/save', {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify(current),
				});
				if (!res.ok) throw new Error('save failed');
				setStatus("Profile saved. Values will be restored at script startup.");
			} catch (err) {
				setStatus('Profile save failed.');
			} finally {
				saveBtn.disabled = false;
			}
		});

		reloadBtn.addEventListener('click', async () => {
			try {
				await loadV4L2();
			} catch (err) {
				setStatus('Parameter reload failed.');
			}
		});

		resetDefaultsBtn.addEventListener('click', async () => {
			resetDefaultsBtn.disabled = true;
			setStatus('Reset ai default driver in corso...');
			try {
				const res = await fetch('/api/camera/v4l2/reset-defaults', {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({}),
				});
				if (!res.ok) throw new Error('reset failed');
				await loadV4L2();
				setStatus('Driver defaults restored and saved.');
			} catch (err) {
				setStatus('Driver default reset failed.');
			} finally {
				resetDefaultsBtn.disabled = false;
			}
		});

		document.getElementById('goBack').addEventListener('click', () => {
			window.location.href = '/';
		});

		streamStart();
		loadV4L2().catch((err) => setStatus('Initial load failed: ' + err.message));
	</script>
</body>
</html>
"""
	return html


def page_html(app_version):
	html = """<!doctype html>
<html lang=\"it\">
<head>
	<meta charset=\"utf-8\">
	<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
	<title>Laser AirCam</title>
	<link rel=\"manifest\" href=\"/manifest.webmanifest\">
	<meta name=\"theme-color\" content=\"#0c3a66\">
	<meta name=\"apple-mobile-web-app-capable\" content=\"yes\">
	<meta name=\"apple-mobile-web-app-status-bar-style\" content=\"black-translucent\">
	<meta name=\"msapplication-TileColor\" content=\"#0c3a66\">
	<link rel=\"icon\" type=\"image/png\" sizes=\"192x192\" href=\"/pwa-icon-192.png\">
	<link rel=\"icon\" type=\"image/png\" sizes=\"512x512\" href=\"/pwa-icon-512.png\">
	<link rel=\"apple-touch-icon\" href=\"/pwa-icon-192.png\">
	<style>
			:root {
			--bg1: #041a2f;
			--bg2: #0c3a66;
			--bg3: #16558b;
			--card: rgba(7, 26, 45, 0.82);
			--glass: rgba(133, 197, 255, 0.12);
			--text: #eaf4ff;
			--muted: #b7d3ef;
			--accent: #74c2ff;
			--accent2: #2f8ee5;
			}
			body {
			margin: 0;
			min-height: 100vh;
			font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
			color: var(--text);
			background:
				radial-gradient(circle at 10% 10%, rgba(116, 194, 255, 0.22), transparent 36%),
				radial-gradient(circle at 92% 16%, rgba(47, 142, 229, 0.22), transparent 34%),
				linear-gradient(130deg, var(--bg1), var(--bg2) 52%, var(--bg3));
			}
			.layout {
			margin: 0 auto;
			display: grid;
			gap: 12px;
			grid-template-columns: 1fr 2fr;
			}
			.card {
			background: var(--card);
			border: 1px solid rgba(140, 199, 255, 0.33);
			border-radius: 18px;
			backdrop-filter: blur(9px);
			padding: 16px;
			box-shadow: 0 14px 34px rgba(0, 20, 43, 0.42);
			}
			h1 { margin: 0 0 6px; font-size: 1.45rem; letter-spacing: 0.3px; }
			.app-icon {
			position: relative;
			display: inline-flex;
			align-items: center;
			justify-content: center;
			width: 1.05em;
			height: 1.05em;
			margin-right: 14px;
			color: #ff9d9d;
			text-shadow: 0 0 6px rgba(255, 122, 122, 0.52);
			filter: drop-shadow(0 2px 5px rgba(116, 194, 255, 0.32));
			}
			.app-icon::after {
			content: '';
			position: absolute;
			left: 82%;
			top: 50%;
			width: 0.92em;
			height: 2px;
			transform: translateY(-50%);
			border-radius: 999px;
			background: linear-gradient(90deg, rgba(255, 149, 149, 0.2), rgba(255, 108, 108, 0.95));
			box-shadow: 0 0 9px rgba(255, 98, 98, 0.62);
			}
			.lead { margin: 0 0 14px; color: var(--muted); font-size: 0.95rem; }
			.grid { display: grid; gap: 12px; }
			label { color: var(--muted); font-size: 0.95rem; display: block; margin-bottom: 6px; }
			.ico {
			display: inline-block;
			width: 1.05em;
			text-align: center;
			margin-right: 7px;
			opacity: 0.9;
			font-weight: 700;
			}
			.preset-icon {
			font-family: 'Segoe UI Symbol', 'Noto Sans Symbols 2', 'Segoe UI', sans-serif;
			}
			label .ico,
			.sysstat-label .ico {
			color: rgba(210, 231, 250, 0.95);
			}
			button .ico {
			color: inherit;
			opacity: 0.86;
			}
			select, input[type=\"range\"], input[type=\"color\"] {
			width: 100%;
			border-radius: 8px;
			border: 1px solid rgba(140, 199, 255, 0.33);
			color: var(--text);
			padding: 7px 9px;
			font-size: 0.88rem;
			box-sizing: border-box;
			}
			select {
			appearance: none;
			padding: 9px 34px 9px 11px;
			border-radius: 11px;
			border: 1px solid rgba(170, 219, 255, 0.48);
			background:
				linear-gradient(180deg, rgba(8, 33, 61, 0.96), rgba(4, 26, 47, 0.96)),
				url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='14' height='9' viewBox='0 0 14 9'%3E%3Cpath d='M1 1l6 6 6-6' fill='none' stroke='%23e6f4ff' stroke-width='2' stroke-linecap='round'/%3E%3C/svg%3E") no-repeat right 10px center;
			box-shadow:
				inset 0 1px 0 rgba(255, 255, 255, 0.12),
				inset 0 -10px 18px rgba(2, 15, 28, 0.45),
				0 6px 14px rgba(1, 15, 31, 0.35);
			transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.18s ease;
			}
			select:hover {
			transform: translateY(-1px);
			border-color: rgba(184, 227, 255, 0.72);
			box-shadow:
				inset 0 1px 0 rgba(255, 255, 255, 0.28),
				inset 0 -8px 14px rgba(7, 39, 72, 0.34),
				0 10px 20px rgba(1, 15, 31, 0.38);
			}
			select:focus {
			outline: none;
			border-color: rgba(195, 233, 255, 0.9);
			box-shadow:
				inset 0 1px 0 rgba(255, 255, 255, 0.32),
				inset 0 -8px 14px rgba(7, 39, 72, 0.36),
				0 0 0 2px rgba(116, 194, 255, 0.3),
				0 12px 24px rgba(1, 15, 31, 0.42);
			}
			select option {
			background: #0a2a4a;
			color: #eaf4ff;
			}
			input[type=\"color\"] {
			height: 54px;
			padding: 4px;
			cursor: pointer;
			}
			input[type=\"color\"]::-webkit-color-swatch-wrapper { padding: 0; }
			input[type=\"color\"]::-webkit-color-swatch { border: none; border-radius: 8px; }
			@media (max-width: 640px) {
				input[type=\"color\"] {
					-webkit-appearance: auto;
					appearance: auto;
					height: 44px;
					padding: 0;
					border: none;
					background: transparent;
				}
				input[type=\"color\"]::-webkit-color-swatch {
					border-radius: 6px;
				}
			}
			button {
			width: 100%;
			border-radius: 9px;
			border: 1px solid rgba(172, 208, 241, 0.38);
			padding: 7px 10px;
			font-size: 0.84rem;
			box-sizing: border-box;
			background: rgba(10, 40, 68, 0.72);
			color: #dceeff;
			font-weight: 600;
			letter-spacing: 0.01em;
			cursor: pointer;
			box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05);
			transition: border-color 0.15s ease, background 0.15s ease, color 0.15s ease, transform 0.12s ease;
			}
			button:hover {
			transform: translateY(-1px);
			border-color: rgba(198, 228, 255, 0.58);
			background: rgba(14, 49, 81, 0.84);
			}
			button:active {
			transform: translateY(0);
			background: rgba(8, 33, 58, 0.9);
			}
			button:disabled {
			opacity: 0.62;
			cursor: wait;
			transform: none;
			background: rgba(10, 31, 51, 0.75);
			border-color: rgba(150, 183, 214, 0.24);
			}
			button.warn {
			background: rgba(19, 64, 104, 0.85);
			border-color: rgba(117, 177, 230, 0.5);
			}
			button.danger {
			background: rgba(72, 48, 48, 0.82);
			border-color: rgba(208, 149, 149, 0.5);
			}
			button .ico {
			color: #dceeff;
			opacity: 0.92;
			}
			#laserClearErrorBtn,
			#openSettingsMenu,
			#openButtonsSettings,
			#openAirAssist,
			#rebootPi,
			#shutdownPi {
			background: rgba(10, 40, 68, 0.72);
			border-color: rgba(172, 208, 241, 0.38);
			}
			#laserClearErrorBtn .ico,
			#shutdownPi .ico {
			color: #ff6b6b;
			opacity: 1;
			}
			#rebootPi .ico {
			color: #ffd257;
			opacity: 1;
			}
			.row { display: grid; gap: 10px; grid-template-columns: 1fr 1fr; }
			.actions-block { gap: 0; }
			.actions-block .row { gap: 6px; }
			.actions-block .row + .row { margin-top: 4px !important; }
			.actions-block button {
				padding: 4px 6px;
				font-size: 0.74rem;
				border-radius: 7px;
				min-height: 30px;
			}
			.actions-block .brightness-compact {
				display: grid;
				grid-template-columns: 16px minmax(0, 1fr) auto;
				align-items: center;
				gap: 6px;
				margin-top: 4px;
			}
			.actions-block .compact-actions {
				margin-top: 6px;
			}
			.actions-block .airassist-compact {
				display: grid;
				grid-template-columns: 16px minmax(0, 1fr) auto;
				align-items: center;
				gap: 6px;
				margin-top: 4px;
			}
			.actions-block .airassist-compact .aa-mini-val,
			.actions-block .brightness-compact .aa-mini-val {
				font-size: 0.72rem;
				color: var(--muted);
				min-width: 36px;
				text-align: right;
			}
			.actions-block .airassist-toggle-row {
				margin-top: 4px;
			}
			.actions-block .quick-toggle-line {
				display: grid;
				grid-template-columns: minmax(0, 1fr) auto;
				align-items: center;
				gap: 8px;
				margin-top: 4px;
			}
			.actions-block .quick-toggle-line.inline {
				display: inline-grid;
				width: auto;
				margin-right: 12px;
			}
			.actions-block .airassist-toggle-row .quick-toggle-line-row {
				display: grid;
				grid-template-columns: 1fr 1fr;
				gap: 8px;
				margin-top: 4px;
			}
			.actions-block .airassist-toggle-row .quick-toggle-line-row .quick-toggle-line {
				margin-top: 0;
			}
			.actions-block .quick-toggle-label {
				display: inline-flex;
				align-items: center;
				gap: 5px;
				font-size: 0.74rem;
				font-weight: 700;
				color: #dceeff;
				opacity: 0.96;
			}
			.actions-block .quick-toggle-label .ico {
				font-size: 0.78rem;
				opacity: 0.95;
			}
			.actions-block .aa-switch-btn {
				position: relative;
				min-height: 34px;
				height: 34px;
				border-radius: 999px;
				padding: 0 16px;
				display: inline-flex;
				align-items: center;
				justify-content: center;
				font-size: 0.74rem;
				font-weight: 800;
				letter-spacing: 0.03em;
				text-transform: uppercase;
				color: #f2fff6;
				background: linear-gradient(120deg, #c23030, #a01c1c);
				border-color: rgba(232, 115, 115, 0.6);
				box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08);
			}
			.actions-block .aa-switch-btn::after {
				content: '';
				position: absolute;
				top: 50%;
				left: 3px;
				width: 26px;
				height: 26px;
				border-radius: 50%;
				background: #ffffff;
				border: 1px solid rgba(98, 134, 107, 0.65);
				box-shadow: 0 2px 5px rgba(0, 0, 0, 0.24);
				transform: translateY(-50%);
				transition: left 0.18s ease, background 0.18s ease, transform 0.18s ease;
			}
			.actions-block .aa-switch-btn.on {
				background: linear-gradient(120deg, #1d8c41, #35cf6d);
				border-color: rgba(129, 225, 157, 0.72);
				color: #fff;
			}
			.actions-block .aa-switch-btn.on::after {
				left: calc(100% - 29px);
			}
			.actions-block .aa-switch-btn.aa-switch-btn-tiny {
				width: 52px;
				min-width: 52px;
				height: 18px;
				min-height: 18px;
				padding: 0;
				font-size: 0;
				line-height: 0;
				background: linear-gradient(120deg, #c23030, #a01c1c);
				border-color: rgba(232, 115, 115, 0.6);
			}
			.actions-block .aa-switch-btn.aa-switch-btn-tiny::after {
				top: 50%;
				left: 3px;
				width: 12px;
				height: 12px;
				box-shadow: 0 1px 3px rgba(0, 0, 0, 0.24);
				transform: translateY(-50%);
			}
			.actions-block .aa-switch-btn.aa-switch-btn-tiny.on {
				background: linear-gradient(120deg, #1d8c41, #35cf6d);
				border-color: rgba(129, 225, 157, 0.72);
			}
			.actions-block .aa-switch-btn.aa-switch-btn-tiny.on::after {
				left: 37px;
			}
			.actions-block .aa-switch-btn.aa-switch-btn-tiny.light-off {
				background: linear-gradient(120deg, #505050, #3a3a3a);
				border-color: rgba(128, 128, 128, 0.6);
			}
			.actions-block .aa-switch-btn.aa-switch-btn-tiny.light-on {
				background: linear-gradient(120deg, #ffb81c, #ffa500);
				border-color: rgba(255, 200, 100, 0.7);
			}
			.actions-block .aa-switch-btn.aa-switch-btn-tiny.light-off::after {
				left: 3px;
			}
			.actions-block .aa-switch-btn.aa-switch-btn-tiny.light-on::after {
				left: 37px;
			}
			.actions-block .brightness-compact .ico {
				font-size: 0.88rem;
				opacity: 0.92;
			}
			.actions-block #brightness {
				margin: 0;
				height: 16px;
			}
			.actions-block input[type="range"] {
				-webkit-appearance: none;
				appearance: none;
				height: 16px;
				padding: 0;
				border: none;
				background: transparent;
				box-shadow: none;
			}
			.actions-block input[type="range"]::-webkit-slider-runnable-track {
				height: 4px;
				border-radius: 999px;
				background: rgba(140, 199, 255, 0.45);
			}
			.actions-block input[type="range"]::-moz-range-track {
				height: 4px;
				border-radius: 999px;
				background: rgba(140, 199, 255, 0.45);
			}
			.actions-block input[type="range"]::-webkit-slider-thumb {
				-webkit-appearance: none;
				appearance: none;
				width: 12px;
				height: 12px;
				border-radius: 50%;
				background: #dceeff;
				border: 1px solid rgba(42, 92, 132, 0.9);
				box-shadow: 0 0 0 1px rgba(140, 199, 255, 0.28);
				margin-top: -4px;
				cursor: pointer;
			}
			.actions-block input[type="range"]::-moz-range-thumb {
				width: 12px;
				height: 12px;
				border-radius: 50%;
				background: #dceeff;
				border: 1px solid rgba(42, 92, 132, 0.9);
				box-shadow: 0 0 0 1px rgba(140, 199, 255, 0.28);
				cursor: pointer;
			}
			.collapsible-block > summary {
				display: flex;
				align-items: center;
				justify-content: space-between;
				gap: 8px;
				margin-bottom: 8px;
				font-weight: 700;
				cursor: pointer;
				color: #dceeff;
				user-select: none;
				list-style: none;
			}
			.collapsible-block > summary::-webkit-details-marker { display: none; }
			.collapsible-block > summary::after {
				content: '\\25BE';
				color: var(--muted);
				font-size: 0.8rem;
				transition: transform 0.2s ease;
			}
			.collapsible-block:not([open]) > summary::after { transform: rotate(-90deg); }
			.summary-title {
				display: inline-flex;
				align-items: center;
				gap: 8px;
			}
			.monitor-glyph {
				width: 14px;
				height: 14px;
				display: inline-flex;
				margin-right: 7px;
				color: #dceeff;
				opacity: 0.92;
			}
			.monitor-glyph svg {
				width: 100%;
				height: 100%;
				display: block;
				fill: none;
				stroke: currentColor;
				stroke-width: 1.8;
				stroke-linecap: round;
				stroke-linejoin: round;
			}
			.row.single-center {
			grid-template-columns: 1fr;
			justify-items: center;
			}
			.row.single-center button {
			max-width: 280px;
			}
			.settings-menu-grid {
				display: grid;
				grid-template-columns: 1fr 1fr;
				gap: 8px;
			}
			.settings-menu-grid button {
				width: 100%;
			}
			.settings-menu-grid .settings-menu-title {
				grid-column: 1 / -1;
				background: rgba(13, 51, 84, 0.78);
				border-color: rgba(172, 208, 241, 0.3);
				color: #dff0ff;
				cursor: default;
			}
			.buttons-settings-grid {
			display: grid;
			grid-template-columns: 1fr;
			gap: 10px;
			}
			.buttons-settings-section {
			margin-top: 10px;
			padding: 10px 12px;
			border-radius: 10px;
			background: rgba(116, 194, 255, 0.08);
			border: 1px solid rgba(140, 199, 255, 0.24);
			}
			.buttons-settings-row {
			display: grid;
			grid-template-columns: 1fr 1fr;
			gap: 10px;
			margin-top: 8px;
			}
			.buttons-settings-field {
			display: grid;
			gap: 4px;
			}
			.buttons-settings-field label {
			margin: 0;
			font-size: 0.82rem;
			}
			.buttons-settings-title {
			font-size: 0.86rem;
			font-weight: 700;
			color: #dff1ff;
			margin-bottom: 6px;
			}
			.buttons-settings-hint {
			color: var(--muted);
			font-size: 0.82rem;
			line-height: 1.3;
			}
			.buttons-settings-status {
			margin-top: 8px;
			font-size: 0.82rem;
			color: var(--muted);
			min-height: 1.1rem;
			}
			#buttonsSettingsModal {
			background: transparent;
			align-items: flex-start;
			justify-content: flex-start;
			}
			#buttonsSettingsModal .modal-card {
			position: absolute;
			margin: 0;
			width: min(980px, calc(100vw - 24px));
			max-height: calc(100vh - 24px);
			overflow: auto;
			touch-action: none;
			}
			@media (max-width: 980px) {
				.buttons-settings-section {
					padding: 9px;
				}
				.buttons-settings-row {
					grid-template-columns: 1fr;
				}
			}
			.slider-label-row {
			display: flex;
			align-items: center;
			justify-content: space-between;
			}
			.slider-label-row label { margin-bottom: 0; }
			.brightness-val {
			font-size: 0.84rem;
			font-weight: 700;
			color: #d9ecff;
			min-width: 40px;
			text-align: right;
			}
			.led-state {
			font-weight: 800;
			letter-spacing: 0.02em;
			color: inherit;
			}
			.bulb-icon {
			display: inline-flex;
			align-items: center;
			justify-content: center;
			min-width: 1.1rem;
			transition: color 0.18s ease, text-shadow 0.18s ease;
			color: inherit;
			}
			.bulb-icon svg {
			width: 1.05rem;
			height: 1.05rem;
			display: block;
			fill: currentColor;
			}
			.bulb-icon.on {
			color: #ffbd4a;
			filter: drop-shadow(0 0 6px rgba(255, 189, 74, 0.75)) drop-shadow(0 0 14px rgba(255, 162, 59, 0.48));
			}
			.bulb-icon.off {
			color: inherit;
			filter: none;
			}
			.status { font-size: 0.9rem; color: var(--muted); }
			.quick-links {
			margin-top: 10px;
			padding: 5px;
			border-radius: 10px;
			background: rgba(116, 194, 255, 0.08);
			border: 1px solid rgba(116, 194, 255, 0.24);
			}
			.quick-links.in-camera {
			margin-top: 10px;
			}
			.quick-links-title {
			font-size: 0.8rem;
			font-weight: 700;
			letter-spacing: 0.04em;
			text-transform: uppercase;
			color: var(--accent);
			margin-bottom: 7px;
			}
			.quick-links-row {
			display: flex;
			align-items: center;
			gap: 20px;
			flex-wrap: nowrap;
		    justify-content: center;
			}
			.quick-link-item {
			display: inline-flex;
			align-items: center;
			gap: 6px;
			font-size: 0.83rem;
			line-height: 1.45;
			color: #d9ecff;
			text-decoration: none;
			padding: 2px 0;
			}
			.quick-link-prefix {
			display: inline-flex;
			align-items: center;
			gap: 4px;
			color: var(--muted);
			font-weight: 700;
			white-space: nowrap;
			}
			.quick-link-icon {
			display: inline-block;
			font-size: 0.8rem;
			color: #b7c9dc;
			line-height: 1;
			}
			.quick-link-url {
			color: #d9ecff;
			word-break: break-all;
			}
			.quick-link-item:hover {
			color: #ffffff;
			text-decoration: underline;
			}
			.settings-block {
			padding: 10px;
			border-radius: 12px;
			background: rgba(90, 170, 238, 0.12);
			border: 1px solid rgba(140, 199, 255, 0.33);
			}
			.actions-block {
			display: grid;
			gap: 8px;
			}
			.app-version {
			display: inline-block;
			margin-left: 8px;
			font-size: 0.74rem;
			font-weight: 700;
			padding: 2px 7px;
			border-radius: 999px;
			background: rgba(116, 194, 255, 0.18);
			border: 1px solid rgba(116, 194, 255, 0.45);
			color: #d8edff;
			vertical-align: middle;
			}
			.media {
			background: var(--glass);
			border: 1px solid rgba(140, 199, 255, 0.33);
			border-radius: 14px;
			padding: 12px;
			}
			.media h2 { margin: 0 0 10px; font-size: 1rem; color: #d8ebff; }
			.video, .photo {
			width: 100%;
			height: auto;
			display: block;
			background: #000;
			border-radius: 12px;
			object-fit: contain;
			border: 1px solid rgba(140, 199, 255, 0.45);
			}
			.photo { aspect-ratio: auto; }
						.photo-placeholder {
						display: flex;
						align-items: center;
						justify-content: center;
						color: rgba(140, 199, 255, 0.55);
						font-size: 1rem;
						letter-spacing: 0.04em;
						background: #0a0f1a;
						}
			.snapshot-wrap {
			position: relative;
			display: block;
			min-height: 260px;
			}
			.snapshot-wrap .photo,
			.snapshot-wrap .photo-placeholder {
			width: 100%;
			height: 100%;
			}
			.serial-msg-wrap {
			display: block;
			width: 100%;
			margin-top: 4px;
			padding: 7px 9px;
			border-radius: 8px;
			background: linear-gradient(180deg, rgba(6, 18, 28, 0.92), rgba(3, 12, 20, 0.92));
			border: 1px solid rgba(116, 194, 255, 0.28);
			box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05);
			font-family: Consolas, "SFMono-Regular", Menlo, Monaco, "Liberation Mono", monospace;
			}
			/* Match the visual inset of .settings-block siblings in the top grid. */
			.grid > #laserSerialMessagesHint.serial-msg-wrap {
			width: calc(100% - 20px);
			justify-self: center;
			}
			.serial-link-head {
			display: block;
			font-size: 0.74rem;
			line-height: 1.2;
			color: #8fcfff;
			border-bottom: 1px solid rgba(116, 194, 255, 0.22);
			padding-bottom: 4px;
			margin-bottom: 2px;
			white-space: normal;
			overflow-wrap: anywhere;
			word-break: break-word;
			}
			.serial-msg-line {
			display: -webkit-box;
			width: 100%;
			max-width: 100%;
			min-width: 0;
			overflow: hidden;
			text-overflow: ellipsis;
			white-space: normal;
			overflow-wrap: anywhere;
			word-break: break-word;
			-webkit-box-orient: vertical;
			-webkit-line-clamp: 2;
			line-clamp: 2;
			font-size: 0.76rem;
			line-height: 1.25;
			letter-spacing: 0;
			}
			#laserSerialTxHint { color: #9ed7ff; }
			#laserSerialRxHint { color: #b6f3be; }
			#laserSerialRxHint {
			min-height: 2.5em;
			}
			.laser-monitor-checks {
			display: grid;
			gap: 6px;
			margin-top: 4px;
			}
			.laser-monitor-checks label {
			display: flex;
			align-items: center;
			gap: 10px;
			margin: 0;
			}
			.laser-monitor-checks span {
			color: var(--muted);
			font-size: 0.86rem;
			}
			.laser-jog-wrap {
			display: grid;
			gap: 8px;
			margin-top: 6px;
			}
			.laser-jog-main {
			display: grid;
			grid-template-columns: minmax(0, 1fr) auto;
			gap: 12px;
			align-items: center;
			}
			.laser-jog-controls {
			display: grid;
			gap: 6px;
			align-content: start;
			}
			.laser-jog-step-row {
			display: grid;
			grid-template-columns: 86px minmax(88px, 96px);
			gap: 8px;
			align-items: center;
			font-size: 0.82rem;
			color: var(--muted);
			}
			.laser-jog-label {
			display: grid;
			gap: 1px;
			line-height: 1.1;
			}
			.laser-jog-label .unit {
			font-size: 0.68rem;
			opacity: 0.82;
			letter-spacing: 0.01em;
			}
			.laser-jog-step-row.feed {
			margin-top: -2px;
			}
			.laser-jog-step-row input {
			height: 36px;
			padding: 6px 8px;
			width: 60%;
			}
			.laser-jog-pad {
			display: grid;
			grid-template-columns: repeat(3, minmax(50px, 64px));
			grid-template-rows: repeat(3, minmax(42px, 48px));
			gap: 6px;
			justify-content: center;
			}
			@media (max-width: 640px) {
				.laser-jog-main {
					grid-template-columns: 1fr;
				}
				.laser-jog-pad {
					justify-content: start;
				}
			}
			.laser-jog-pad button {
			padding: 0;
			min-height: 42px;
			font-size: 1rem;
			line-height: 1;
			}
			.laser-jog-pad .home {
			font-size: 0.82rem;
			}
			.laser-jog-status {
			text-align: right;
			font-size: 0.78rem;
			color: var(--muted);
			min-height: 1.15em;
			}
			.pill {
			display: inline-block;
			padding: 5px 10px;
			border-radius: 99px;
			font-size: 0.8rem;
			background: rgba(116, 194, 255, 0.18);
			color: #d8edff;
			border: 1px solid rgba(116, 194, 255, 0.52);
			margin-bottom: 10px;
			}
			.menu-tab {
			display: block;
			text-align: center;
			text-decoration: none;
			cursor: pointer;
			margin: 0;
			padding: 8px 10px;
			font-size: 0.83rem;
			font-weight: 700;
			background: linear-gradient(120deg, #e7f5ff, #d7ebff);
			color: #295174;
			border: 1px solid rgba(194, 225, 255, 0.95);
			border-radius: 8px;
			transition: transform 0.15s ease, filter 0.15s ease, background 0.15s ease, border-color 0.15s ease;
			}
			.menu-tab:hover { transform: translateY(-1px); filter: saturate(1.06); }
			.menu-tab.active {
			background: linear-gradient(120deg, #4b97ea, #7dbdff);
			border-color: #a9d3ff;
			color: #041b32;
			box-shadow: 0 0 0 2px rgba(123, 184, 247, 0.28), 0 6px 16px rgba(41, 104, 172, 0.35);
			}
			.menu-tab-main { display: block; line-height: 1.05; }
			.menu-tab-sub { display: block; margin-top: 3px; font-size: 0.68rem; font-weight: 600; opacity: 0.9; }
			.stream-wrap { position: relative; display: block; }
			.camera-column {
				position: sticky;
				top: 8px;
				align-self: start;
			}
			@media (min-width: 981px) {
				.camera-column .stream-wrap {
					height: min(72vh, calc(100vh - 240px));
					min-height: 260px;
				}
				.camera-column .video {
					height: 100%;
				}
				.camera-column .snapshot-wrap .photo,
				.camera-column .snapshot-wrap .photo-placeholder {
					height: 100%;
				}
			}
			.fullscreen-btn {
				position: absolute;
				top: 10px;
				right: 10px;
				z-index: 18;
				width: auto;
				padding: 4px 8px;
				border-radius: 8px;
				font-size: 0.76rem;
				line-height: 1.1;
				font-weight: 700;
				letter-spacing: 0.03em;
				background: rgba(5, 26, 47, 0.58);
				color: #dff2ff;
				border: 1px solid rgba(140, 199, 255, 0.45);
				backdrop-filter: blur(4px);
				opacity: 0.78;
				box-shadow: none;
				text-shadow: none;
				transform: none;
			}
			.fullscreen-btn::before {
				display: none;
			}
			.fullscreen-btn:hover {
				opacity: 1;
				transform: none;
				filter: none;
				box-shadow: none;
				background: rgba(8, 36, 64, 0.86);
			}
			.fullscreen-btn:active {
				transform: none;
				box-shadow: none;
			}
			.fs-zoom-hud {
			position: fixed;
			left: 50%;
			bottom: 16px;
			transform: translateX(-50%);
			display: none;
			align-items: center;
			gap: 8px;
			padding: 8px 10px;
			z-index: 1300;
			border-radius: 999px;
			background: rgba(4, 24, 43, 0.82);
			border: 1px solid rgba(140, 199, 255, 0.46);
			backdrop-filter: blur(5px);
			}
			.fs-zoom-hud.active { display: flex; }
			.fs-zoom-btn {
			width: 34px;
			height: 34px;
			padding: 0;
			border-radius: 999px;
			font-size: 1.05rem;
			font-weight: 700;
			line-height: 1;
			}
			.fs-zoom-indicator {
			min-width: 78px;
			text-align: center;
			font-size: 0.82rem;
			font-weight: 700;
			color: #e7f4ff;
			}
			.zoom-target {
			transform-origin: center center;
			transition: transform 0.12s ease;
			}
			.stream-loading {
			display: none;
			position: absolute;
			inset: 0;
			align-items: center;
			justify-content: center;
			background: rgba(4, 27, 50, 0.72);
			border-radius: 12px;
			z-index: 10;
			font-size: 1rem;
			font-weight: 700;
			letter-spacing: 0.12em;
			color: #74c2ff;
			gap: 10px;
			}
			.stream-loading.active { display: flex; }
			.stream-busy {
			display: none;
			position: absolute;
			inset: 0;
			align-items: center;
			justify-content: center;
			text-align: center;
			padding: 12px;
			background: rgba(2, 14, 28, 0.86);
			border-radius: 12px;
			z-index: 11;
			font-size: 0.9rem;
			line-height: 1.4;
			font-weight: 700;
			color: #ffe3b5;
			letter-spacing: 0.01em;
			}
			.stream-busy.active { display: flex; }
			.stream-loading::before {
			content: '';
			width: 20px;
			height: 20px;
			border: 3px solid rgba(116, 194, 255, 0.25);
			border-top-color: #74c2ff;
			border-radius: 50%;
			animation: spin 0.8s linear infinite;
			}
			@keyframes spin { to { transform: rotate(360deg); } }
			.sysstat-block {
			padding: 10px 12px;
			border-radius: 10px;
			background: rgba(116, 194, 255, 0.07);
			font-size: 0.82rem;
			color: var(--muted);
		    margin-bottom: 15px;
			}
			.sysstat-block h4 {
			font-size: 0.75rem;
			font-weight: 700;
			letter-spacing: 0.08em;
			text-transform: uppercase;
			color: var(--accent);
			margin-bottom: 8px;
			opacity: 0.85;
			}
			.cpu-mini-chart {
			display: block;
			width: 100%;
			height: 136px;
			margin: 0 0 10px;
			border-radius: 9px;
			background: linear-gradient(180deg, rgba(116, 194, 255, 0.12), rgba(13, 50, 84, 0.12));
			border: none;
			}
			.sysstat-row {
			display: flex;
			align-items: center;
			justify-content: space-between;
			margin-bottom: 6px;
			gap: 8px;
			}
			.sysstat-row:last-child { margin-bottom: 0; }
			.sysstat-label { opacity: 0.75; flex-shrink: 0; }
			.sysstat-bar-wrap {
			flex: 1;
			height: 5px;
			background: rgba(255,255,255,0.1);
			border-radius: 99px;
			overflow: hidden;
			}
			.sysstat-bar {
			height: 100%;
			border-radius: 99px;
			transition: width 0.6s ease;
			}
			.sysstat-bar.cpu { background: linear-gradient(90deg, #4b97ea, #74c2ff); }
			.sysstat-bar.ram { background: linear-gradient(90deg, #a07aff, #c9b0ff); }
			.sysstat-bar.temp { background: linear-gradient(90deg, #ff9d3d, #ffb570); }
			.sysstat-val { font-weight: 700; color: var(--text); min-width: 38px; text-align: right; flex-shrink: 0; }
			.camera-notice {
			display: none;
			margin-top: 8px;
			padding: 7px 8px;
			border-radius: 8px;
			font-size: 0.78rem;
			line-height: 1.35;
			border: 1px solid rgba(116, 194, 255, 0.22);
			background: rgba(116, 194, 255, 0.08);
			color: #d9ebff;
			}
			.camera-notice::before {
			content: '';
			display: none;
			}
			.camera-notice.warn {
			border-color: rgba(255, 183, 111, 0.35);
			background: rgba(255, 183, 111, 0.1);
			color: #ffe9c9;
			}
			.camera-notice.warn::before { content: ''; display: none; }
			.tabs-row {
			display: grid;
			grid-template-columns: 1fr 1fr 1fr;
			gap: 8px;
			margin-bottom: 10px;
			padding: 7px;
			border-radius: 12px;
			background: rgba(227, 242, 255, 0.12);
			border: 1px solid rgba(176, 212, 248, 0.35);
			}
			.laser-mini-status {
			display: flex;
			align-items: center;
			justify-content: center;
			gap: 10px;
			margin-bottom: 8px;
			padding: 7px 9px;
			border-radius: 10px;
			background: rgba(116, 194, 255, 0.08);
			border: 1px solid rgba(140, 199, 255, 0.26);
			font-size: 0.78rem;
			line-height: 1.2;
			color: #d8ebff;
			}
			.laser-mini-status .dot {
			width: 8px;
			height: 8px;
			border-radius: 999px;
			background: #c7d9ea;
			box-shadow: 0 0 0 2px rgba(199, 217, 234, 0.2);
			flex: 0 0 auto;
			}
			.laser-mini-status .label {
			display: flex;
			align-items: center;
			justify-content: center;
			gap: 7px;
			font-weight: 700;
			letter-spacing: 0.01em;
			width: 100%;
			}
			.laser-mini-status .meta {
			opacity: 0.9;
			font-size: 0.74rem;
			white-space: nowrap;
			}
			.laser-mini-status.error-code-visible {
			justify-content: center;
			}
			.laser-mini-status.error-code-visible .dot {
			display: none;
			}
			.laser-mini-status.error-code-visible .label {
			width: 100%;
			justify-content: center;
			}
			.laser-mini-status.error-code-visible #laserMiniStatusText {
			color: #ff9aa2;
			font-weight: 800;
			text-align: center;
			}
			.laser-mini-status.error {
			background: rgba(186, 37, 49, 0.34);
			border-color: rgba(255, 117, 126, 0.58);
			color: #ffe3e7;
			}
			.laser-mini-status.door {
			background: rgba(208, 141, 42, 0.3);
			border-color: rgba(255, 204, 120, 0.58);
			color: #ffebc8;
			}
			.laser-mini-status.idle {
			justify-content: center;
			}
			.laser-mini-status.idle .dot {
			display: none;
			}
			.laser-mini-status.running .dot { background: #ff5f5f; box-shadow: 0 0 0 2px rgba(255, 95, 95, 0.24); }
			.laser-mini-status.moving .dot { background: #74c2ff; box-shadow: 0 0 0 2px rgba(116, 194, 255, 0.24); }
			.laser-mini-status.engraving { background: rgba(220, 50, 50, 0.18); border-color: rgba(255, 80, 80, 0.5); color: #ffd5d5; }
			.laser-mini-status.engraving .dot { background: #ff3333; box-shadow: 0 0 0 2px rgba(255, 51, 51, 0.32); }
			.laser-mini-status.hold .dot { background: #ffb45b; box-shadow: 0 0 0 2px rgba(255, 180, 91, 0.24); }
			.laser-mini-status.door .dot { background: #ffbf5c; box-shadow: 0 0 0 2px rgba(255, 191, 92, 0.3); }
			.laser-mini-status.error .dot { background: #ff3f54; box-shadow: 0 0 0 2px rgba(255, 63, 84, 0.25); }
			.laser-mini-status.engrave_complete {
			background: rgba(79, 151, 104, 0.26);
			border-color: rgba(127, 201, 152, 0.44);
			color: #d9f0e0;
			}
			.laser-mini-status.engrave_complete .dot { background: #6ab584; box-shadow: 0 0 0 2px rgba(106, 181, 132, 0.26); }
			.media-panel { display: none; }
			.media-panel.active { display: block; }
			.modal {
			position: fixed;
			inset: 0;
			display: none;
			align-items: center;
			justify-content: center;
			overflow-y: auto;
			padding: 12px;
			background: rgba(0, 0, 0, 0.55);
			z-index: 1200;
			}
			.modal.open { display: flex; }
			.modal-card {
			width: min(420px, 92vw);
			background: #0a2642;
			border: 1px solid rgba(140, 199, 255, 0.33);
			border-radius: 14px;
			padding: 14px;
			max-height: calc(100dvh - 24px);
			overflow: auto;
			box-shadow: 0 20px 60px rgba(0,0,0,0.45);
			}
			.modal-card h3 { margin: 0 0 8px; }
			.modal-card p { margin: 0 0 10px; color: var(--muted); font-size: 0.9rem; }
			.modal-card .row button {
				justify-self: center;
			}
			.modal-card .row > button:only-child {
				grid-column: 1 / -1;
				justify-self: center;
			}
			#settingsMenuModal,
			#videoSettingsModal,
			#screenshotSettingsModal,
			#ledPreviewModal {
			background: transparent;
			align-items: flex-start;
			justify-content: flex-start;
			}
			#settingsMenuModal .modal-card,
			#videoSettingsModal .modal-card,
			#screenshotSettingsModal .modal-card,
			#ledPreviewModal .modal-card {
			position: absolute;
			margin: 0;
			max-width: calc(100vw - 24px);
			touch-action: none;
			}
			#settingsMenuModal .modal-card {
			width: min(980px, 96vw);
			}
			#videoSettingsModal .modal-card,
			#screenshotSettingsModal .modal-card {
			width: min(900px, 96vw);
			}
			#ledPreviewModal .modal-card {
			width: min(790px, 94vw);
			}
			.led-mgmt-stack {
			display: grid;
			gap: 8px;
			}
			.led-mgmt-section {
			border: 1px solid var(--border);
			border-radius: 10px;
			padding: 8px;
			background: rgba(9, 32, 56, 0.24);
			display: grid;
			gap: 2px;
			}
			.led-mgmt-section.live-section {
			background: linear-gradient(180deg, rgba(18, 47, 74, 0.28), rgba(9, 32, 56, 0.20));
			box-shadow: inset 0 1px 0 rgba(186, 224, 255, 0.22), inset 0 -10px 22px rgba(92, 158, 214, 0.08);
			}
			.led-mgmt-section.powercycle-section {
			background: linear-gradient(180deg, rgba(26, 56, 84, 0.28), rgba(12, 35, 58, 0.20));
			box-shadow: inset 0 1px 0 rgba(194, 229, 255, 0.20), inset 0 -10px 22px rgba(101, 170, 230, 0.08);
			}
			.led-mgmt-section-title {
			color: var(--muted);
			font-size: 0.84rem;
			font-weight: 700;
			margin-bottom: 2px;
			}
			.led-mgmt-3col {
			display: grid;
			grid-template-columns: repeat(3, minmax(0, 1fr));
			gap: 8px;
			align-items: end;
			}
			.led-mgmt-field {
			display: grid;
			gap: 2px;
			}
			.led-mgmt-field label {
			margin-bottom: 1px;
			}
			.led-mgmt-section select {
			width: min(230px, 100%);
			justify-self: start;
			}
			.led-mgmt-section .slider-label-row {
			margin-top: -14px !important;
			margin-bottom: 0;
			}
			.led-mgmt-section input[type="range"] {
			margin-top: -10px;
			}
			.led-mgmt-toggle-row {
			display: grid;
			grid-template-columns: 1fr 1fr;
			gap: 8px;
			align-items: center;
			}
			.led-custom-inline {
			display: flex;
			align-items: center;
			gap: 8px;
			margin-top: 2px;
			}
			.led-custom-inline label {
			margin: 0;
			}
			.led-custom-inline .color-picker-row {
			display: inline-flex;
			grid-template-columns: none;
			align-items: center;
			gap: 8px;
			}
			.led-custom-inline #customColor {
			width: 34px;
			height: 34px;
			min-width: 34px;
			padding: 0;
			border-radius: 8px;
			cursor: pointer;
			}
			.led-custom-inline .color-preview {
			min-height: 34px;
			padding: 0 8px;
			font-size: 0.76rem;
			min-width: 98px;
			}
			#grblCommandsModal .modal-card {
			width: min(1480px, 98vw);
			}
			.grbl-layout {
			max-height: calc(100dvh - 180px);
			overflow-y: auto;
			padding-right: 8px;
			font-size: 0.9rem;
			line-height: 1.6;
			}
			.grbl-grid {
			display: grid;
			grid-template-columns: repeat(3, minmax(0, 1fr));
			gap: 14px;
			align-items: start;
			}
			.grbl-panel {
			border: 1px solid var(--border);
			border-radius: 10px;
			padding: 10px;
			background: rgba(9, 32, 56, 0.24);
			}
			.grbl-howto-grid {
			display: grid;
			grid-template-columns: repeat(3, minmax(0, 1fr));
			gap: 10px;
			align-items: start;
			}
			.grbl-howto-item {
			background: rgba(6, 20, 34, 0.42);
			border: 1px solid rgba(140, 199, 255, 0.20);
			border-radius: 8px;
			padding: 8px;
			}
			.grbl-span-all {
			grid-column: 1 / -1;
			}
			@media (max-width: 980px) {
				.modal {
					align-items: flex-start;
					justify-content: center;
					padding: 10px;
				}
				#settingsMenuModal,
				#videoSettingsModal,
				#screenshotSettingsModal,
				#ledPreviewModal,
				#buttonsSettingsModal {
					background: rgba(0, 0, 0, 0.55);
					align-items: flex-start;
					justify-content: center;
				}
				#settingsMenuModal .modal-card,
				#videoSettingsModal .modal-card,
				#screenshotSettingsModal .modal-card,
				#ledPreviewModal .modal-card,
				#buttonsSettingsModal .modal-card {
					position: relative !important;
					left: auto !important;
					top: auto !important;
					margin: 0 auto;
					width: min(680px, calc(100vw - 20px));
					max-width: calc(100vw - 20px);
					max-height: calc(100dvh - 20px);
					overflow: auto;
					touch-action: auto;
				}
				.modal-card .row {
					grid-template-columns: 1fr;
				}
				.led-mgmt-3col {
					grid-template-columns: 1fr;
				}
				.led-mgmt-toggle-row {
					grid-template-columns: 1fr;
				}
				.grbl-grid {
					grid-template-columns: 1fr;
				}
				.grbl-howto-grid {
					grid-template-columns: 1fr;
				}
				.grbl-span-all {
					grid-column: auto;
				}
				.modal-card .row button {
					width: min(300px, 100%);
				}
			}
			.modal-drag-handle {
			display: flex;
			align-items: center;
			justify-content: space-between;
			gap: 10px;
			cursor: move;
			user-select: none;
			-webkit-user-select: none;
			touch-action: none;
			padding-bottom: 2px;
			}
			.modal-drag-handle::after {
			content: '\\2630';
			font-size: 0.9rem;
			letter-spacing: 0.08em;
			color: rgba(210, 231, 250, 0.7);
			}
			.input-line {
			width: 100%;
			border-radius: 10px;
			border: 1px solid rgba(140, 199, 255, 0.33);
			background: rgba(6, 31, 56, 0.72);
			color: var(--text);
			padding: 10px;
			box-sizing: border-box;
			}
			.color-picker-row {
			display: grid;
			grid-template-columns: 64px 1fr;
			gap: 10px;
			align-items: stretch;
			}
			.color-preview {
			display: flex;
			align-items: center;
			justify-content: center;
			border-radius: 10px;
			border: 1px solid rgba(140, 199, 255, 0.33);
			min-height: 44px;
			font-weight: 700;
			letter-spacing: 0.06em;
			font-size: 0.85rem;
			text-transform: uppercase;
			box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.06);
			}
			@keyframes slideIn {
			from { opacity: 0; transform: translateY(16px); }
			to { opacity: 1; transform: translateY(0); }
			}
			.card, .media { animation: slideIn 420ms ease both; }
			@media (max-width: 980px) {
				.layout { grid-template-columns: 1fr; }
				.camera-column {
					position: static;
					top: auto;
				}
				.camera-column .stream-wrap {
					height: auto;
					min-height: 220px;
				}
				.camera-column .video {
					height: auto;
				}
			}
			@media (max-width: 640px) { .row { grid-template-columns: 1fr 1fr; } }
			/* --- AirAssist dual-range slider --- */
			.aa-drs-wrap { position: relative; height: 30px; margin: 4px 0; }
			.aa-drs-track-bg { position: absolute; z-index: 1; height: 6px; left: 2px; right: 18px; top: 12px; background: linear-gradient(to right, rgba(255,255,255,0.85) 0%, #e53935 50%, #7b1fa2 100%); border-radius: 3px; }
			.aa-drs-fill { position: absolute; z-index: 2; height: 6px; top: 12px; border-radius: 3px; pointer-events: none; box-sizing: border-box; }
			.aa-drs-input { position: absolute; z-index: 3; width: calc(100% + 17px); left: -8px; top: 3px; height: 24px; margin: 0; padding: 0; background: transparent; appearance: none; -webkit-appearance: none; pointer-events: none; }
			.aa-drs-input::-webkit-slider-runnable-track { background: transparent; height: 6px; }
			.aa-drs-input::-webkit-slider-thumb { appearance: none; -webkit-appearance: none; pointer-events: all; width: 17px; height: 17px; border-radius: 50%; background: #fff; cursor: pointer; border: 2px solid #888; box-shadow: 0 1px 5px rgba(0,0,0,0.6); margin-top: -6px; }
			.aa-drs-input::-moz-range-track { background: transparent; border: none; height: 6px; }
			.aa-drs-input::-moz-range-progress { background: transparent; }
			.aa-drs-input::-moz-range-thumb { pointer-events: all; width: 17px; height: 17px; border-radius: 50%; background: #fff; cursor: pointer; border: 2px solid #888; box-shadow: 0 1px 5px rgba(0,0,0,0.6); }
			#aaRangeMin { background: transparent !important; }
			#aaRangeMin::-webkit-slider-runnable-track { background: transparent !important; }
			#aaRangeMin::-moz-range-track { background: transparent !important; }
			#aaRangeMin::-moz-range-progress { background: transparent !important; }
			.aa-drs-ticks { display: flex; justify-content: space-between; color: var(--muted); font-size: 0.75rem; margin-top: 3px; padding: 0 1px; }
	</style>
</head>
<body>
	<main class=\"layout\">
			<section class=\"card\">
			<h1><span class=\"app-icon\" aria-hidden=\"true\">&#9678;</span>Laser AirCam<span class=\"app-version\">v{APP_VERSION}</span></h1>
			<div class=\"grid\">
				<div id=\"laserSerialMessagesHint\" class=\"serial-msg-wrap\">
					<div id=\"laserSerialLinkHint\" class=\"serial-link-head\">Serial link: --</div>
					<span id=\"laserSerialTxHint\" class=\"serial-msg-line\">TX: --</span>
					<span id=\"laserSerialRxHint\" class=\"serial-msg-line\">RX: --</span>
				</div>
				<div class=\"settings-block actions-block\" style=\"margin-bottom: 10px;\">
				<div class=\"brightness-compact\">
						<span class=\"ico\" aria-hidden=\"true\">&#9728;</span>
						<input id=\"brightness\" type=\"range\" min=\"0\" max=\"1\" step=\"0.01\">
						<span id=\"brightnessVal\" class=\"aa-mini-val\">--%</span>
					</div>
					<div class="quick-toggle-line" style="margin-top: -3px;">
						<span class="quick-toggle-label"><span class="ico" aria-hidden="true">&#9728;</span>Light:</span>
						<button id="togglePower" type="button" class="aa-switch-btn aa-switch-btn-tiny light-off" aria-label="Light quick switch" aria-pressed="false">OFF</button>
					</div>
					<div class="airassist-compact">
						<span class="ico" aria-hidden="true">&#128168;</span>
						<input id="quickAirAssistSpeed" type="range" min="0" max="100" step="1">
						<span id="quickAirAssistSpeedVal" class="aa-mini-val">--%</span>
					</div>
					<div class="airassist-toggle-row" style="margin-top: -10px;">
						<div class="quick-toggle-line-row">
							<div class="quick-toggle-line">
								<span class="quick-toggle-label"><span class="ico" aria-hidden="true">&#128168;</span>Airassist ON:</span>
								<button id="quickAirAssistToggle" type="button" class="aa-switch-btn aa-switch-btn-tiny" aria-label="AirAssist quick switch">OFF</button>
							</div>
							<div class="quick-toggle-line">
								<span class="quick-toggle-label"><span class="ico" aria-hidden="true">&#9881;</span>Progressive Airassist</span>
								<button id="quickAirAssistAutoToggle" type="button" class="aa-switch-btn aa-switch-btn-tiny" aria-label="AirAssist auto quick switch">OFF</button>
							</div>
						</div>
					</div>
					<div class="row compact-actions">
						<button id="laserClearErrorBtn" class="warn"><span class="ico">&#9888;</span>Clear status</button>
						<button id="openSettingsMenu"><span class="ico">&#9881;</span>SETTINGS</button>
					</div>
				</div>
				<div class=\"status\" id=\"status\" style=\"display:none;\">Connecting...</div>
				<div class=\"settings-block\">
					<details class=\"collapsible-block\">
						<summary>
							<span class=\"summary-title\"><span class=\"monitor-glyph\" aria-hidden=\"true\"><svg viewBox=\"0 0 24 24\" focusable=\"false\"><rect x=\"3\" y=\"4\" width=\"18\" height=\"12\" rx=\"2\"></rect><path d=\"M9 20h6\"></path><path d=\"M12 16v4\"></path></svg></span>Hardware Monitor</span>
						</summary>
						<div class=\"sysstat-block\" id=\"sysstatBlock\">
						<canvas class=\"cpu-mini-chart\" id=\"cpuSparkline\"></canvas>
						<div class=\"sysstat-row\">
							<span class=\"sysstat-label\"><span class=\"ico\">&#9881;</span>CPU</span>
							<div class=\"sysstat-bar-wrap\"><div class=\"sysstat-bar cpu\" id=\"cpuBar\" style=\"width:0%\"></div></div>
							<span class=\"sysstat-val\" id=\"cpuVal\">--</span>
						</div>
						<div class=\"sysstat-row\">
							<span class=\"sysstat-label\"><span class=\"ico\">&#9776;</span>RAM</span>
							<div class=\"sysstat-bar-wrap\"><div class=\"sysstat-bar ram\" id=\"ramBar\" style=\"width:0%\"></div></div>
							<span class=\"sysstat-val\" id=\"ramVal\">--</span>
						</div>
						<div class=\"sysstat-row\">
							<span class=\"sysstat-label\"><span class=\"ico\">&#8451;</span>Temp</span>
							<div class=\"sysstat-bar-wrap\"><div class=\"sysstat-bar temp\" id=\"tempBar\" style=\"width:0%\"></div></div>
							<span class=\"sysstat-val\" id=\"tempVal\">--</span>
						</div>
						<div id=\"laserStatusHint\" style=\"color:var(--muted); text-align:center;font-size:0.84rem; margin-top:6px; white-space:pre-line;\">Laser: --</div>
						<div class=\"camera-notice\" id=\"cameraNotice\"></div>
						<div class=\"row\" style=\"margin-top: 8px;\">
							<button class=\"warn\" id=\"rebootPi\"><span class=\"ico\">&#8635;</span>Reboot</button>
							<button class=\"danger\" id=\"shutdownPi\"><span class=\"ico\">&#10006;</span>Shutdown</button>
						</div>
						</div>
					</details>
				</div>
				<div class=\"settings-block\" style=\"margin-top:10px;\">
					<details class=\"collapsible-block\">
						<summary><span class=\"summary-title\"><span class=\"ico\">&#9881;</span>Laser Monitor / Serial Proxy</span></summary>
						<div style=\"display:grid; gap:8px; margin-top: 18px;\">
						<div style=\"display:grid; grid-template-columns:auto 1fr 1fr; gap:6px; align-items:center;\">
							<div style=\"color:var(--muted); font-size:0.85rem;\">Running</div>
							<select id=\"laserRunningEffect\"></select>
							<select id=\"laserRunningColor\"></select>
							<div style=\"color:var(--muted); font-size:0.85rem;\">Idle</div>
							<select id=\"laserIdleEffect\"></select>
							<select id=\"laserIdleColor\"></select>
							<div style=\"color:var(--muted); font-size:0.85rem;\">Hold/Pause</div>
							<select id=\"laserHoldEffect\"></select>
							<select id=\"laserHoldColor\"></select>
							<div style=\"color:var(--muted); font-size:0.85rem;\">Door Open</div>
							<select id=\"laserDoorEffect\"></select>
							<select id=\"laserDoorColor\"></select>
							<div style=\"color:var(--muted); font-size:0.85rem;\">Error</div>
							<select id=\"laserErrorEffect\"></select>
							<select id=\"laserErrorColor\"></select>
							<div style="color:var(--muted); font-size:0.85rem;">Engrave Complete</div>
							<select id="laserCompleteEffect"></select>
							<select id="laserCompleteColor"></select>
						</div>
						<div class=\"laser-monitor-checks\">
							<label><input type=\"checkbox\" id=\"mqttImageEnabled\" style=\"width:20px;height:20px;cursor:pointer\"><span id=\"mqttImageHint\">MQTT Images (needs CPU)</span></label>
							<label><input type=\"checkbox\" id=\"serialProxyEnabled\" style=\"width:20px;height:20px;cursor:pointer\"><span>TCP serial proxy enabled</span></label>
							<label><input type=\"checkbox\" id=\"passthroughExtendOnRealtime\" style=\"width:20px;height:20px;cursor:pointer\"><span>Keep passthrough locked on status poll <code>?</code> (hybrid OFF)</span></label>
							<label><input type=\"checkbox\" id=\"laserLedSyncEnabled\" style=\"width:20px;height:20px;cursor:pointer\"><span>LED synced to laser state</span></label>
						</div>
						<div id="serialProxyPortsHint" style="color:var(--muted); font-size:0.82rem; margin-top:4px;">Serial monitor port target --; listen on port --</div>

												</div>
					</details>
				</div>
				<div class=\"settings-block\" style=\"margin-top:10px;\">
					<details class=\"collapsible-block\">
						<summary><span class=\"summary-title\"><span class=\"ico\">&#9881;</span>Custom G-code / Manual Move</span></summary>
						<div style="display:grid; gap:8px;">
							<div style="display:grid; gap:6px; margin-top:4px;">
								<div style="color:var(--muted); font-size:0.85rem;">Send Custom G-code</div>
									<div style="display:grid; grid-template-columns:1fr auto auto; gap:6px; align-items:center;">
									<input id="laserCustomGcode" class="input-line" type="text" placeholder="es. ?  or  M8  or  G0 X0 Y0" maxlength="180">
									<button id="laserSendGcode"><span class="ico">&#10148;</span>Send</button>
										<button id="laserClearQueueBtn" class="warn"><span class="ico">&#128465;</span>Clear queue</button>
								</div>
									<div id="laserJogStatus" class="laser-jog-status">Jog: --</div>
							</div>
							<div style="display:grid; gap:6px;">
								<div class="laser-jog-wrap">
									<div style="color:var(--muted); font-size:0.85rem;">Manual Move</div>
									<div class="laser-jog-main">
										<div class="laser-jog-controls">
											<div class="laser-jog-step-row">
												<span class="laser-jog-label"><span>Move Step</span><span class="unit">mm</span></span>
												<input id="laserMoveStepMm" class="input-line" type="number" min="0.1" max="100" step="0.1" value="20">
											</div>
											<div class="laser-jog-step-row feed">
												<span class="laser-jog-label"><span>Move Speed</span><span class="unit">mm/sec</span></span>
												<input id="laserMoveFeedMmSec" class="input-line" type="number" min="0.2" max="80" step="0.1" value="10">
											</div>
										</div>
										<div class="laser-jog-pad">
											<div></div>
											<button id="laserJogUp" title="Move Up">&#8593;</button>
											<div></div>
											<button id="laserJogLeft" title="Move Left">&#8592;</button>
											<button id="laserJogHome" class="home" title="Homing">HOME</button>
											<button id="laserJogRight" title="Move Right">&#8594;</button>
											<div></div>
											<button id="laserJogDown" title="Move Down">&#8595;</button>
											<div></div>
										</div>
									</div>

	
								</div>
							</div>
							<div style="display:grid; gap:6px; margin-top:8px;">
								<div style="color:var(--muted); font-size:0.85rem;">Custom Position (mm)</div>
								<div style="display:grid; grid-template-columns:repeat(3, minmax(0, 1fr)); gap:6px; align-items:end;">
									<label style="display:grid; gap:4px; color:var(--muted); font-size:0.8rem;"><span>X</span><input id="laserCustomPosX" class="input-line" type="number" min="-1000" max="1000" step="0.1" placeholder="X"></label>
									<label style="display:grid; gap:4px; color:var(--muted); font-size:0.8rem;"><span>Y</span><input id="laserCustomPosY" class="input-line" type="number" min="-1000" max="1000" step="0.1" placeholder="Y"></label>
									<label style="display:grid; gap:4px; color:var(--muted); font-size:0.8rem;"><span>Z</span><input id="laserCustomPosZ" class="input-line" type="number" min="-1000" max="1000" step="0.1" placeholder="Z"></label>
								</div>
								<label class="inline" style="margin-top:2px; font-size:0.84rem; color:var(--muted);">
									<input id="laserCustomPosUseG0" type="checkbox"> Use G0 (fast move). Disable for G1 (controlled feed speed)
								</label>
								<div class="row" style="margin-top:2px;">
									<button id="laserSaveCustomPos"><span class="ico">&#128190;</span>Save Pos</button>
									<button id="laserGoCustomPos"><span class="ico">&#10148;</span>Go Custom Pos</button>
								</div>
							</div>
						</div>
					</details>
				</div>
			</div>
			</section>

			<section class=\"grid camera-column\">
			<div class=\"media\">
				<div class=\"laser-mini-status idle\" id=\"laserMiniStatus\">
					<span class=\"label\"><span class=\"dot\"></span><span id=\"laserMiniStatusText\">Laser: --</span></span>
				</div>
				<div class=\"tabs-row\">
					<a class=\"menu-tab active\" id=\"streamBadge\" href=\"#\"><span class=\"menu-tab-main\">Live Stream</span><span class=\"menu-tab-sub\">--</span></a>
					<a class=\"menu-tab\" id=\"streamHdBadge\" href=\"#\"><span class=\"menu-tab-main\">StreamHD</span><span class=\"menu-tab-sub\">--</span></a>
					<a class=\"menu-tab\" id=\"snapshotBadge\" href=\"#\"><span class=\"menu-tab-main\">Snapshot</span><span class=\"menu-tab-sub\">--</span></a>
				</div>
				<div class=\"media-panel active\" id=\"livePanel\">
					<div class=\"stream-wrap\">
						<button id=\"mediaFullscreenBtn\" class=\"fullscreen-btn\" type=\"button\" title=\"Fullscreen\">fullscreen</button>
						<div class=\"stream-loading\" id=\"streamLoading\">LOADING</div>
						<div class=\"stream-busy\" id=\"streamBusyNotice\">Stream is busy in another process.<br>The dashboard will resume automatically when the camera is free.</div>
						<img id=\"liveStream\" class=\"video\" src=\"\" alt=\"Live stream\">
					</div>
				</div>
				<div class=\"media-panel\" id=\"snapshotPanel\">
					<div class=\"stream-wrap snapshot-wrap\">
						<button id=\"snapshotFullscreenBtn\" class=\"fullscreen-btn\" type=\"button\" title=\"Fullscreen\">fullscreen</button>
						<div id=\"photoPlaceholder\" class=\"photo photo-placeholder\"><span id=\"photoPlaceholderText\">No snapshot yet</span></div>
						<img id=\"capturedPhoto\" class=\"photo\" src=\"\" alt=\"Latest photo\" style=\"display:none\">
					</div>
					<div class=\"row\" style=\"margin-top:10px; margin-bottom:10px\">
						<button id=\"takePhoto\"><span class=\"ico\">&#11044;</span>Take Photo</button>
						<button id=\"openDirectSnap\"><span class=\"ico\">&#128279;</span>Open /snap.jpg</button>
					</div>
					<div class=\"status\" id=\"photoStatus\"></div>
				</div>
			</div>
			<div class=\"quick-links in-camera\" id=\"quickLinksBox\" style=\"margin-top: -5px;\">
				<div class=\"quick-links-title\" style=\"text-align: center;\"><span class=\"ico\">&#128279;</span>Quick Links</div>
				<div class=\"quick-links-row\">
					<a class=\"quick-link-item\" id=\"quickStream\" href=\"#\" target=\"_blank\" rel=\"noopener noreferrer\"><span class=\"quick-link-prefix\"><span class=\"quick-link-icon\">&#9654;</span>Live</span></a>
					<a class=\"quick-link-item\" id=\"quickStreamHd\" href=\"#\" target=\"_blank\" rel=\"noopener noreferrer\"><span class=\"quick-link-prefix\"><span class=\"quick-link-icon\">&#9635;</span>HD</span></a>
					<a class=\"quick-link-item\" id=\"quickSnapshot\" href=\"#\" target=\"_blank\" rel=\"noopener noreferrer\"><span class=\"quick-link-prefix\"><span class=\"quick-link-icon\">&#9679;</span>Snap</span></a>
				</div>
			</div>
			</section>
	</main>

	<div class="fs-zoom-hud" id="fullscreenZoomHud">
		<button id="zoomOutBtn" class="fs-zoom-btn" type="button" title="Zoom Out">-</button>
		<div class="fs-zoom-indicator" id="zoomIndicator">Zoom 100%</div>
		<button id="zoomInBtn" class="fs-zoom-btn" type="button" title="Zoom In">+</button>
		<button id="zoomResetBtn" class="fs-zoom-btn" type="button" title="Reset Zoom">1:1</button>
	</div>

	<div class="modal" id="settingsMenuModal">
			<div class="modal-card" id="settingsMenuCard">
			<h3 class="modal-drag-handle" id="settingsMenuDragHandle"><span class="ico">&#9881;</span> Settings</h3>
			<p>Quick access to the main Laser AirCam panels.</p>
			<div class="settings-menu-grid">
				<button type="button" class="secondary settings-menu-title"><span class="ico">&#9678;</span>Laser AirCam v{APP_VERSION}</button>
				<button id="settingsMenuVideoBtn" type="button"><span class="ico">&#128249;</span>Video</button>
				<button id="settingsMenuScreenshotBtn" type="button"><span class="ico">&#128247;</span>Screenshot</button>
				<button id="settingsMenuV4l2Btn" type="button"><span class="ico">&#9881;</span>v4L2 Settings</button>
				<button id="settingsMenuLedBtn" type="button"><span class="ico">&#128161;</span>Led Management</button>
				<button id="settingsMenuButtonsBtn" type="button"><span class="ico">&#128295;</span>Buttons</button>
				<button id="settingsMenuAirAssistBtn" type="button"><span class="ico">&#128168;</span>AirAssist</button>
				<button id="settingsMenuGrblBtn" type="button"><span class="ico">&#128221;</span>G-CODE Commands</button>
			</div>
			<div class="row single-center" style="margin-top:12px">
				<button id="closeSettingsMenu" class="secondary"><span class="ico">&#10005;</span>Close</button>
			</div>
			</div>
	</div>

	<div class="modal" id="videoSettingsModal">
			<div class="modal-card" id="videoSettingsCard">
			<h3 class="modal-drag-handle" id="videoSettingsDragHandle">Stream Settings</h3>
			<p>Edit resolution and/or FPS, then press <b>Apply</b> to use the new values immediately.</p>
			<label for="videoResolutionSelect"><span class="ico">&#128208;</span>Resolution Preset</label>
			<select id="videoResolutionSelect"></select>
			<input id="videoResolutionInput" class="input-line" type="text" placeholder="1280x960" style="margin-top:6px">
			<label for="videoFpsSelect" style="margin-top:10px"><span class="ico">&#9201;</span>Preset FPS</label>
			<select id="videoFpsSelect"></select>
			<input id="videoFpsInput" class="input-line" type="number" min="1" max="120" placeholder="20" style="margin-top:6px">
			<div class="row" style="margin-top:12px">
				<button id="saveVideoSettings"><span class="ico">&#10227;</span>Apply and Restart</button>
				<button id="closeVideoSettings"><span class="ico">&#10005;</span>Close</button>
			</div>
			<div id="videoSettingsStatus" style="margin-top:8px; font-size:0.85rem; color:var(--muted);"></div>
			</div>
	</div>

	<div class="modal" id="v4l2SettingsModal">
			<div class="modal-card">
			<h3>Camera v4l2 Controls</h3>
			<p>Changes are applied to the driver immediately and saved into the systemd service.</p>
			<label for="v4l2HFlip" style="margin-top:8px"><span class="ico">&#8644;</span>Horizontal Flip</label>
			<div style="display:flex; align-items:center; gap:10px; margin-top:4px">
				<input type="checkbox" id="v4l2HFlip" style="width:20px;height:20px;cursor:pointer">
				<span style="color:var(--muted);font-size:0.9rem">Mirror the image horizontally</span>
			</div>
			<label for="v4l2VFlip" style="margin-top:12px"><span class="ico">&#8645;</span>Vertical Flip</label>
			<div style="display:flex; align-items:center; gap:10px; margin-top:4px">
				<input type="checkbox" id="v4l2VFlip" style="width:20px;height:20px;cursor:pointer">
				<span style="color:var(--muted);font-size:0.9rem">Mirror the image vertically</span>
			</div>
			<label for="v4l2Quality" style="margin-top:12px"><span class="ico">&#9783;</span>JPEG Compression Quality: <b id="v4l2QualityVal">90</b></label>
			<input type="range" id="v4l2Quality" min="1" max="100" value="90" style="margin-top:4px">
			<div class="row" style="margin-top:14px">
				<button id="saveV4l2Settings"><span class="ico">&#10004;</span>Apply</button>
				<button id="closeV4l2Settings"><span class="ico">&#10005;</span>Close</button>
			</div>
			<div id="v4l2SettingsStatus" style="margin-top:8px; font-size:0.85rem; color:var(--muted);"></div>
			</div>
	</div>

	<div class="modal" id="screenshotSettingsModal">
			<div class="modal-card" id="screenshotSettingsCard">
			<h3 class="modal-drag-handle" id="screenshotSettingsDragHandle">Screenshot Resolution</h3>
			<p>Requested format: WIDTHxHEIGHT, i.e. 3280x2464.</p>
			<label for="screenshotResolutionSelect"><span class="ico">&#128208;</span>Resolution Preset</label>
			<select id="screenshotResolutionSelect"></select>
			<input id="screenshotResolutionInput" class="input-line" type="text" placeholder="3280x2464">
			<label for="streamHdIntervalSelect" style="margin-top:10px"><span class="ico">&#9201;</span>StreamHD: 1 image every X seconds</label>
			<select id="streamHdIntervalSelect"></select>
			<input id="streamHdIntervalInput" class="input-line" type="number" min="1" max="60" placeholder="4" style="margin-top:6px">
			<div class="row" style="margin-top:10px">
				<button id="saveScreenshotResolution"><span class="ico">&#128190;</span>Save for Screenshot</button>
				<button id="saveStreamHdSettings"><span class="ico">&#128190;</span>Save for StreamHD</button>
			</div>
			<div class="row" style="margin-top:8px">
				<button id="closeScreenshotSettings"><span class="ico">&#10005;</span>Close</button>
				<div></div>
			</div>
			</div>
	</div>

	<div class="modal" id="ledPreviewModal">
			<div class="modal-card" id="ledPreviewCard">
			<h3 class="modal-drag-handle" id="ledPreviewDragHandle">Led Preview</h3>
			<p>Preview and tune LED output.</p>
			<div class="led-mgmt-stack">
				<div class="led-mgmt-section live-section">
					<div class="led-mgmt-section-title">Live animation</div>
					<div class="led-mgmt-3col">
						<div class="led-mgmt-field">
							<label for="effect"><span class="ico">&#10023;</span>Effect Mode</label>
							<select id="effect">
								<option value="static">Static</option>
								<option value="breathe">Breathe</option>
								<option value="pulse">Pulse</option>
								<option value="strobe">Strobe</option>
								<option value="flash">Flash</option>
								<option value="fire">Fire</option>
								<option value="disco">Disco</option>
								<option value="snake">Snake</option>
								<option value="twinkle">Twinkle</option>
							</select>
						</div>
						<div class="led-mgmt-field">
							<label for="colorMode"><span class="ico">&#9673;</span>Color Scheme</label>
							<select id="colorMode">
								<option value="cool_white">Cool White</option>
								<option value="warm_white">Warm White</option>
								<option value="amber_boost">Amber Boost</option>
								<option value="sunset_orange">Sunset Orange</option>
								<option value="laser_green">Laser Green</option>
								<option value="ruby_red">Ruby Red</option>
								<option value="ice_cyan">Ice Cyan</option>
								<option value="magenta_pink">Magenta pop</option>
								<option value="blue_intense">Blue Intense</option>
								<option value="blue_soft">Blue Soft</option>
								<option value="green_intense">Green Intense</option>
								<option value="green_soft">Green Soft</option>
								<option value="red_intense">Red Intense</option>
								<option value="red_soft">Red Soft</option>
								<option value="cyan_intense">Cyan Intense</option>
								<option value="cyan_soft">Cyan Soft</option>
								<option value="magenta_intense">Magenta Intense</option>
								<option value="magenta_soft">Magenta Soft</option>
								<option value="amber_intense">Amber Intense</option>
								<option value="amber_soft">Amber Soft</option>
								<option value="random_solid">Single Random Color</option>
								<option value="random_per_led">Random Color per LED</option>
								<option value="custom_solid">Custom Color</option>
							</select>
						</div>
						<div class="led-mgmt-field">
							<label for="presetMode"><span class="ico preset-icon">&#x1F3A8;&#xFE0E;</span>Preset Theme</label>
							<select id="presetMode">
								<option value="none">No Preset</option>
								<option value="ocean_wave">Ocean Wave</option>
								<option value="red_fire">Red Fire</option>
								<option value="green_forest">Green Forest</option>
								<option value="sunset_lava">Sunset Lava</option>
								<option value="ice_plasma">Ice Plasma</option>
							</select>
						</div>
					</div>
				</div>

				<div class="led-mgmt-section">
					<div class="slider-label-row" style="margin-top:2px">
						<label for="presetIntensity"><span class="ico">&#9650;</span>Preset Intensity</label>
						<span class="brightness-val" id="presetIntensityVal">100%</span>
					</div>
					<input id="presetIntensity" type="range" min="0" max="100" step="1" value="100">
					<div class="slider-label-row" style="margin-top:8px">
						<label for="ledDefaultBrightness"><span class="ico">&#9728;</span>Led default brightness</label>
						<span class="brightness-val" id="ledDefaultBrightnessVal">0.60</span>
					</div>
					<input id="ledDefaultBrightness" type="range" min="0" max="1" step="0.01" value="0.60">
					<div class="led-custom-inline">
						<label for="customColor"><span class="ico">&#11044;</span>Custom Color</label>
						<div class="color-picker-row">
							<input id="customColor" type="color" value="#d2ebff">
							<div id="customColorPreview" class="color-preview"><span id="customColorHex">#D2EBFF</span></div>
						</div>
					</div>
					<div class="led-mgmt-toggle-row" style="margin-top:2px;">
						<label style="display:flex; align-items:center; gap:10px;"><input type="checkbox" id="ledOnBootEnabled" style="width:20px;height:20px;cursor:pointer"><span style="color:var(--muted); font-size:0.88rem;">LED On at boot</span></label>
						<label style="display:flex; align-items:center; gap:10px;"><input type="checkbox" id="laserErrorAutoReset10s" style="width:20px;height:20px;cursor:pointer"><span style="color:var(--muted); font-size:0.88rem;">Reset LED error effect after 10s</span></label>
					</div>
				</div>

				<div class="led-mgmt-section powercycle-section">
					<div class="led-mgmt-section-title">Startup and shutdown animation</div>
					<div class="led-mgmt-3col">
						<div class="led-mgmt-field">
							<label for="startupLedEffect"><span class="ico">&#10023;</span>Startup Effect</label>
							<select id="startupLedEffect"></select>
						</div>
						<div class="led-mgmt-field">
							<label for="startupLedColor"><span class="ico">&#9673;</span>Startup Color</label>
							<select id="startupLedColor"></select>
						</div>
						<div class="led-mgmt-field">
							<label for="startupLedPreset"><span class="ico preset-icon">&#x1F3A8;&#xFE0E;</span>Startup Preset</label>
							<select id="startupLedPreset"></select>
						</div>
					</div>
					<div class="led-mgmt-3col" style="margin-top:6px;">
						<div class="led-mgmt-field">
							<label for="shutdownLedEffect"><span class="ico">&#10023;</span>Shutdown Effect</label>
							<select id="shutdownLedEffect"></select>
						</div>
						<div class="led-mgmt-field">
							<label for="shutdownLedColor"><span class="ico">&#9673;</span>Shutdown Color</label>
							<select id="shutdownLedColor"></select>
						</div>
						<div class="led-mgmt-field">
							<label for="shutdownLedPreset"><span class="ico preset-icon">&#x1F3A8;&#xFE0E;</span>Shutdown Preset</label>
							<select id="shutdownLedPreset"></select>
						</div>
					</div>
					<div class="slider-label-row" style="margin-top:8px">
						<label for="startupShutdownBrightness" style="margin-top: 12px;"><span class="ico">&#9728;</span>Startup/Shutdown Brightness</label>
						<span class="brightness-val" id="startupShutdownBrightnessVal">0.60</span>
					</div>
					<input id="startupShutdownBrightness" type="range" min="0" max="1" step="0.01" value="0.60">
				</div>
			</div>
			<div class="row single-center" style="margin-top:12px">
				<button id="closeLedPreview"><span class="ico">&#10005;</span>Close</button>
			</div>
			</div>
	</div>

	<div class="modal" id="airAssistModal">
			<div class="modal-card" id="airAssistCard">
			<h3 class="modal-drag-handle" id="airAssistDragHandle">&#128168; AirAssist</h3>
			<p style="color:var(--muted); font-size:0.88rem; margin:0 0 14px;">PWM control for the air-assist pump/fan.</p>
			<div style="display:grid; gap:12px;">
				<div style="display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap;">
					<div style="display:flex; align-items:center; gap:12px; flex-wrap:wrap;">
						<div style="display:flex; align-items:center; gap:8px;">
							<label for="airAssistListenEventsBtn" style="color:var(--muted); font-size:0.9rem;">Listen AirAssist events</label>
							<button id="airAssistListenEventsBtn" style="width:90px;">&#9711; OFF</button>
						</div>
						<div style="display:flex; align-items:center; gap:8px;">
							<span style="color:var(--muted); font-size:0.9rem;">Power</span>
						<button id="airAssistToggleBtn" style="width:90px;">&#9711; OFF</button>
						</div>
					</div>
				</div>
				<div>
					<div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:5px;">
						<span style="color:var(--muted); font-size:0.9rem;">Speed</span>
						<span id="airAssistSpeedVal" style="font-weight:700; color:var(--text);">100%</span>
					</div>
					<input id="airAssistSpeedSlider" type="range" min="0" max="100" step="1" value="100" style="width:100%;">
				</div>
				<hr style="border:none; border-top:1px solid var(--border); margin:8px 0 12px;">
				<div>
					<div style="display:flex; align-items:center; justify-content:space-between; gap:10px;">
						<span style="color:var(--muted); font-size:0.9rem;">Progressive AirAssist</span>
						<button id="airAssistAutoBtn" style="width:90px;">&#9711; OFF</button>
					</div>
				<div id="aaAutoRangeSection">
					<div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:6px;">
						<span style="color:var(--muted); font-size:0.9rem;">Laser power range</span>
					</div>
					<div class="aa-drs-wrap">
						<div class="aa-drs-track-bg"></div>
						<div class="aa-drs-fill" id="aaRangeFill"></div>
						<input type="range" id="aaRangeMin" min="0" max="100" step="1" value="0" class="aa-drs-input">
						<input type="range" id="aaRangeMax" min="0" max="100" step="1" value="100" class="aa-drs-input">
					</div>
					<div class="aa-drs-ticks">
						<span>0%</span><span>25%</span><span>50%</span><span>75%</span><span>100%</span>
					</div>
					<div style="display:flex; align-items:center; justify-content:space-between; margin:9px 0 5px;">
						<span style="color:var(--muted); font-size:0.9rem;">Min AirAssist PWM</span>
						<b id="aaMinPwmVal" style="color:var(--text); font-size:0.9rem;">0%</b>
					</div>
					<input id="aaMinPwm" type="range" min="0" max="100" step="1" value="0" style="width:100%;">
					<span style="color:var(--muted); font-size:0.82rem;">AirAssist starts @ <b id="aaRangeMinVal">0%</b> beam power with <b id="aaMinPwmHintVal">0%</b> PWM power. Max airflow @ <b id="aaRangeMaxVal">100%</b> beam power.</span>
				</div>
			</div>
					<div style="color:var(--muted); font-size:0.78rem; margin-top:5px;">Follow laser power &mdash; PWM tracks GCODE S value proportionally</div>
				</div>

						<div id="airAssistStatus" style="margin-top:10px; color:var(--muted); font-size:0.84rem; min-height:1.1rem;"></div>
			<div class="row" style="margin-top:14px">
				<button id="closeAirAssist" class="secondary"><span class="ico">&#10005;</span>Close</button>
			</div>
			</div>
	</div>

	<div class="modal" id="grblCommandsModal">
			<div class="modal-card" id="grblCommandsCard">
			<h3 class="modal-drag-handle" id="grblCommandsDragHandle">&#128221; G-CODE Commands</h3>
			<p style="color:var(--muted); font-size:0.88rem; margin:0 0 14px;">Send commands from LightBurn to control Bridge settings using GCode comments.</p>
			<div class="grbl-layout">
				<div class="grbl-grid">
				
				<!-- SYNTAX SECTION -->
				<div class="grbl-panel">
					<h4 style="color:var(--text); margin:0 0 8px; font-size:1rem;">📋 Syntax</h4>
					<code style="background:var(--bg-secondary); padding:8px; display:block; border-radius:4px; overflow-x:auto; font-size:0.85rem;">
						(BRIDGE:key=value key2=value2)
					</code>
					<p style="color:var(--muted); margin:8px 0 0; font-size:0.82rem;">Place in your Device GCode, Layer Start/End, or Material presets in LightBurn.</p>
				</div>

				<!-- AIR ASSIST SECTION -->
				<div class="grbl-panel">
					<h4 style="color:#90ee90; margin:0 0 12px; font-size:1rem;">💨 Air Assist Commands</h4>
					
					<div style="background:var(--bg-secondary); padding:10px; border-radius:4px; margin-bottom:10px; border-left:3px solid #90ee90;">
						<div style="display:flex; justify-content:space-between; align-items:start; gap:10px;">
							<div>
								<code style="color:#90ee90; font-weight:600;">aa_speed</code>
								<div style="color:var(--muted); font-size:0.82rem; margin-top:2px;"><strong>Values:</strong> 0-100 (percentage)</div>
								<div style="color:var(--muted); font-size:0.82rem; margin-top:2px;">Set air assist pump speed</div>
								<div style="color:var(--muted); font-size:0.75rem; margin-top:4px; font-style:italic;">Example: (BRIDGE:aa_speed=75)</div>
							</div>
						</div>
					</div>

					<div style="background:var(--bg-secondary); padding:10px; border-radius:4px; margin-bottom:10px; border-left:3px solid #90ee90;">
						<div>
							<code style="color:#90ee90; font-weight:600;">aa_progressive</code>
							<div style="color:var(--muted); font-size:0.82rem; margin-top:2px;"><strong>Values:</strong> on, off, true, false, 1, 0</div>
							<div style="color:var(--muted); font-size:0.82rem; margin-top:2px;">Enable/disable progressive (auto) mode</div>
							<div style="color:var(--muted); font-size:0.75rem; margin-top:4px; font-style:italic;">Example: (BRIDGE:aa_progressive=on)</div>
						</div>
					</div>

					<div style="background:var(--bg-secondary); padding:10px; border-radius:4px; border-left:3px solid #90ee90;">
						<code style="color:#90ee90; font-weight:600;">aa_tune</code>
						<div style="color:var(--muted); font-size:0.82rem; margin-top:2px;"><strong>Values:</strong> MIN_PERCENT,MAX_PERCENT[,MIN_PWM] (e.g., 20,90 or 20,90,35)</div>
						<div style="color:var(--muted); font-size:0.82rem; margin-top:2px;">Set progressive range and optional Min AirAssist PWM</div>
						<div style="color:var(--muted); font-size:0.75rem; margin-top:4px; font-style:italic;">Example: (BRIDGE:aa_tune=15,85,30)</div>
					</div>

					<div style="background:var(--bg-secondary); padding:10px; border-radius:4px; margin-top:10px; border-left:3px solid #90ee90;">
						<code style="color:#90ee90; font-weight:600;">aa_min_pwm</code>
						<div style="color:var(--muted); font-size:0.82rem; margin-top:2px;"><strong>Values:</strong> 0-100 (percentage)</div>
						<div style="color:var(--muted); font-size:0.82rem; margin-top:2px;">Set only Min AirAssist PWM for progressive mode</div>
						<div style="color:var(--muted); font-size:0.75rem; margin-top:4px; font-style:italic;">Example: (BRIDGE:aa_min_pwm=35)</div>
					</div>
				</div>

				<!-- LIGHT SECTION -->
				<div class="grbl-panel">
					<h4 style="color:#ffff99; margin:0 0 12px; font-size:1rem;">💡 Light Commands</h4>
					
					<div style="background:var(--bg-secondary); padding:10px; border-radius:4px; margin-bottom:10px; border-left:3px solid #ffff99;">
						<code style="color:#ffff99; font-weight:600;">light</code>
						<div style="color:var(--muted); font-size:0.82rem; margin-top:2px;"><strong>Values:</strong> on, off, true, false, 1, 0</div>
						<div style="color:var(--muted); font-size:0.82rem; margin-top:2px;">Turn LED ring on/off</div>
						<div style="color:var(--muted); font-size:0.75rem; margin-top:4px; font-style:italic;">Example: (BRIDGE:light=on)</div>
					</div>

					<div style="background:var(--bg-secondary); padding:10px; border-radius:4px; margin-bottom:10px; border-left:3px solid #ffff99;">
						<code style="color:#ffff99; font-weight:600;">light_brightness</code>
						<div style="color:var(--muted); font-size:0.82rem; margin-top:2px;"><strong>Values:</strong> 0.0-1.0 (decimal) or 0-100 (percentage)</div>
						<div style="color:var(--muted); font-size:0.82rem; margin-top:2px;">Set LED brightness</div>
						<div style="color:var(--muted); font-size:0.75rem; margin-top:4px; font-style:italic;">Example: (BRIDGE:light_brightness=0.8) or (BRIDGE:light_brightness=80)</div>
					</div>

					<div style="background:var(--bg-secondary); padding:10px; border-radius:4px; margin-bottom:10px; border-left:3px solid #ffff99;">
						<code style="color:#ffff99; font-weight:600;">light_color</code>
						<div style="color:var(--muted); font-size:0.82rem; margin-top:2px;"><strong>Values:</strong> red, green, blue, white, yellow, cyan, magenta, orange, purple</div>
						<div style="color:var(--muted); font-size:0.82rem; margin-top:2px;">Set LED custom color</div>
						<div style="color:var(--muted); font-size:0.75rem; margin-top:4px; font-style:italic;">Example: (BRIDGE:light_color=cyan)</div>
					</div>

					<div style="background:var(--bg-secondary); padding:10px; border-radius:4px; border-left:3px solid #ffff99;">
						<code style="color:#ffff99; font-weight:600;">light_effect</code>
						<div style="color:var(--muted); font-size:0.82rem; margin-top:2px;"><strong>Values:</strong> solid, blink, pulse, strobe, rainbow, wave, twinkle, fire, chase, scan, bounce</div>
						<div style="color:var(--muted); font-size:0.82rem; margin-top:2px;">Set LED animation effect</div>
						<div style="color:var(--muted); font-size:0.75rem; margin-top:4px; font-style:italic;">Example: (BRIDGE:light_effect=pulse)</div>
					</div>
				</div>

				<!-- EXAMPLES SECTION -->
				<div class="grbl-panel grbl-span-all">
					<h4 style="color:var(--text); margin:0 0 10px; font-size:1rem;">🔗 Combined Example</h4>
					<code style="background:var(--bg-secondary); padding:8px; display:block; border-radius:4px; overflow-x:auto; font-size:0.8rem;">
(BRIDGE:aa_speed=60 aa_progressive=on light=on light_brightness=0.9 light_color=cyan)
					</code>
				</div>

				<!-- HOW TO USE SECTION -->
				<div class="grbl-panel grbl-span-all">
					<h4 style="color:var(--text); margin:0 0 12px; font-size:1rem;">🎯 How to use in LightBurn</h4>
					<div class="grbl-howto-grid">
						<div class="grbl-howto-item">
							<div style="font-weight:600; color:#87ceeb; margin-bottom:4px;">Option A: Device GCode (every job)</div>
							<div style="color:var(--muted); font-size:0.82rem; margin-bottom:4px; font-weight:600;">Edit → Device Settings → GCode tab</div>
							<code style="background:var(--bg-secondary); padding:6px; display:block; border-radius:4px; overflow-x:auto; font-size:0.75rem;">
Start: (BRIDGE:aa_speed=60 aa_progressive=on light=on)<br/>
End: (BRIDGE:light=off)
							</code>
						</div>

						<div class="grbl-howto-item">
							<div style="font-weight:600; color:#87ceeb; margin-bottom:4px;">Option B: Material Library (per material)</div>
							<div style="color:var(--muted); font-size:0.82rem; margin-bottom:4px; font-weight:600;">Material Library → Select material → Cut settings</div>
							<code style="background:var(--bg-secondary); padding:6px; display:block; border-radius:4px; overflow-x:auto; font-size:0.75rem;">
(BRIDGE:aa_speed=75 light_color=cyan light_effect=solid)
							</code>
						</div>

						<div class="grbl-howto-item">
							<div style="font-weight:600; color:#87ceeb; margin-bottom:4px;">Option C: Layer Cut Settings (specific layer)</div>
							<div style="color:var(--muted); font-size:0.82rem; margin-bottom:4px; font-weight:600;">Cut layer → Advanced → Start/End GCode</div>
							<code style="background:var(--bg-secondary); padding:6px; display:block; border-radius:4px; overflow-x:auto; font-size:0.75rem;">
(BRIDGE:aa_tune=15,85,30 light=on)
							</code>
						</div>
					</div>
				</div>
				</div>
			</div>
			<div class="row" style="margin-top:14px">
				<button id="closeGrblCommands" class="secondary"><span class="ico">&#10005;</span>Close</button>
			</div>
			</div>
	</div>

	<div class="modal" id="buttonsSettingsModal">
			<div class="modal-card" id="buttonsSettingsCard">
			<h3 class="modal-drag-handle" id="buttonsSettingsDragHandle">Buttons Settings</h3>
			<p>Configure Mode button behavior for 1/2/3/4 presses, then assign LED/POWER actions for that selected mode.</p>
			<div class="buttons-settings-grid">
				<div class="buttons-settings-section">
					<div class="buttons-settings-title">Mode Profile</div>
					<div class="buttons-settings-row">
						<div class="buttons-settings-field">
							<label for="modePressCountSelect"><span class="ico">&#128273;</span>Mode button press count</label>
							<select id="modePressCountSelect">
								<option value="1">1 press</option>
								<option value="2">2 press</option>
								<option value="3">3 press</option>
								<option value="4">4 press</option>
							</select>
						</div>
						<div class="buttons-settings-field">
							<label for="modeEntryModeSelect"><span class="ico">&#9873;</span>Entry mode</label>
							<select id="modeEntryModeSelect"></select>
						</div>
					</div>
					<div class="buttons-settings-row">
						<div class="buttons-settings-field">
							<label for="modeLedColorSelect"><span class="ico">&#9673;</span>LED color mode</label>
							<select id="modeLedColorSelect"></select>
						</div>
						<div class="buttons-settings-field">
							<label for="modeLedEffectSelect"><span class="ico">&#10023;</span>LED effect</label>
							<select id="modeLedEffectSelect"></select>
						</div>
					</div>
					<div class="buttons-settings-row">
						<div class="buttons-settings-field">
							<label for="modeLedSingleActionSelect"><span class="ico">&#128161;</span>LED button single click action</label>
							<select id="modeLedSingleActionSelect"></select>
						</div>
						<div class="buttons-settings-field">
							<label for="modePowerSingleActionSelect"><span class="ico">&#9889;</span>POWER button single click action</label>
							<select id="modePowerSingleActionSelect"></select>
						</div>
					</div>
				</div>

				<div class="buttons-settings-section">
					<div class="buttons-settings-title">Static Assignments (2x / 3x)</div>
					<div class="buttons-settings-row">
						<div class="buttons-settings-field">
							<label for="ledDoublePressActionSelect"><span class="ico">&#128161;</span>LED button 2 press</label>
							<select id="ledDoublePressActionSelect"></select>
						</div>
						<div class="buttons-settings-field">
							<label for="ledTriplePressActionSelect"><span class="ico">&#128161;</span>LED 3 press</label>
							<select id="ledTriplePressActionSelect"></select>
						</div>
					</div>
					<div class="buttons-settings-row">
						<div class="buttons-settings-field">
							<label for="powerDoublePressActionSelect"><span class="ico">&#9889;</span>POWER button 2 press</label>
							<select id="powerDoublePressActionSelect"></select>
						</div>
						<div class="buttons-settings-field">
							<label for="powerTriplePressActionSelect"><span class="ico">&#9889;</span>POWER button 3 press</label>
							<select id="powerTriplePressActionSelect"></select>
						</div>
					</div>
					<div class="buttons-settings-hint">Available static actions: reboot, shutdown, clear status, light on/off, homing, custom position.</div>
					<label style="display:flex; align-items:center; gap:10px; margin-top:6px;"><input type="checkbox" id="buttonsResetModeOpeningDoor" style="width:20px;height:20px;cursor:pointer"><span style="color:var(--muted); font-size:0.86rem;">Reset buttons mode opening door</span></label>
				</div>
			</div>
			<div class="row" style="margin-top:12px">
				<button id="saveButtonsSettings"><span class="ico">&#10004;</span>Save</button>
				<button id="closeButtonsSettings"><span class="ico">&#10005;</span>Close</button>
			</div>
			<div class="buttons-settings-status" id="buttonsSettingsStatus"></div>
			</div>
	</div>

	<script>
			const statusEl = document.getElementById('status');
			const photoStatusEl = document.getElementById('photoStatus');
			const streamBadgeEl = document.getElementById('streamBadge');
			const streamHdBadgeEl = document.getElementById('streamHdBadge');
			const snapshotBadgeEl = document.getElementById('snapshotBadge');
			const livePanelEl = document.getElementById('livePanel');
			const snapshotPanelEl = document.getElementById('snapshotPanel');
			const effectEl = document.getElementById('effect');
			const colorModeEl = document.getElementById('colorMode');
			const presetModeEl = document.getElementById('presetMode');
			const presetIntensityEl = document.getElementById('presetIntensity');
			const presetIntensityValEl = document.getElementById('presetIntensityVal');
			const ledDefaultBrightnessEl = document.getElementById('ledDefaultBrightness');
			const ledDefaultBrightnessValEl = document.getElementById('ledDefaultBrightnessVal');
			const startupLedEffectEl = document.getElementById('startupLedEffect');
			const startupLedColorEl = document.getElementById('startupLedColor');
			const startupLedPresetEl = document.getElementById('startupLedPreset');
			const shutdownLedEffectEl = document.getElementById('shutdownLedEffect');
			const shutdownLedColorEl = document.getElementById('shutdownLedColor');
			const shutdownLedPresetEl = document.getElementById('shutdownLedPreset');
			const startupShutdownBrightnessEl = document.getElementById('startupShutdownBrightness');
			const startupShutdownBrightnessValEl = document.getElementById('startupShutdownBrightnessVal');
			const brightnessEl = document.getElementById('brightness');
			const brightnessValEl = document.getElementById('brightnessVal');
			const customColorEl = document.getElementById('customColor');
			const customColorPreviewEl = document.getElementById('customColorPreview');
			const customColorHexEl = document.getElementById('customColorHex');
			const togglePowerEl = document.getElementById('togglePower');
			const ledBulbIconEl = document.getElementById('ledBulbIcon');
			const ledStateLabelEl = document.getElementById('ledStateLabel');
			const capturedPhotoEl = document.getElementById('capturedPhoto');
						const photoPlaceholderEl = document.getElementById('photoPlaceholder');
						const photoPlaceholderTextEl = document.getElementById('photoPlaceholderText');
			const takePhotoBtn = document.getElementById('takePhoto');
			const liveStreamEl = document.getElementById('liveStream');
			const mediaFullscreenBtn = document.getElementById('mediaFullscreenBtn');
			const snapshotFullscreenBtn = document.getElementById('snapshotFullscreenBtn');
			const mqttImageEnabledEl = document.getElementById('mqttImageEnabled');
			const mqttImageHintEl = document.getElementById('mqttImageHint');
			const ledOnBootEnabledEl = document.getElementById('ledOnBootEnabled');
			const serialProxyEnabledEl = document.getElementById('serialProxyEnabled');
			const passthroughExtendOnRealtimeEl = document.getElementById('passthroughExtendOnRealtime');
			const laserLedSyncEnabledEl = document.getElementById('laserLedSyncEnabled');
			const laserRunningEffectEl = document.getElementById('laserRunningEffect');
			const laserRunningColorEl = document.getElementById('laserRunningColor');
			const laserIdleEffectEl = document.getElementById('laserIdleEffect');
			const laserIdleColorEl = document.getElementById('laserIdleColor');
			const laserHoldEffectEl = document.getElementById('laserHoldEffect');
			const laserHoldColorEl = document.getElementById('laserHoldColor');
			const laserDoorEffectEl = document.getElementById('laserDoorEffect');
			const laserDoorColorEl = document.getElementById('laserDoorColor');
			const laserErrorEffectEl = document.getElementById('laserErrorEffect');
			const laserErrorColorEl = document.getElementById('laserErrorColor');
			const laserCompleteEffectEl = document.getElementById('laserCompleteEffect');
			const laserCompleteColorEl = document.getElementById('laserCompleteColor');
			const laserStatusHintEl = document.getElementById('laserStatusHint');
			const laserClearErrorBtnEl = document.getElementById('laserClearErrorBtn');
			const laserErrorAutoReset10sEl = document.getElementById('laserErrorAutoReset10s');
			const openSettingsMenuEl = document.getElementById('openSettingsMenu');
			const openButtonsSettingsEl = document.getElementById('openButtonsSettings');
			const laserCustomGcodeEl = document.getElementById('laserCustomGcode');
			const laserSendGcodeEl = document.getElementById('laserSendGcode');
			const laserClearQueueBtnEl = document.getElementById('laserClearQueueBtn');
			const laserCustomPosXEl = document.getElementById('laserCustomPosX');
			const laserCustomPosYEl = document.getElementById('laserCustomPosY');
			const laserCustomPosZEl = document.getElementById('laserCustomPosZ');
			const laserCustomPosUseG0El = document.getElementById('laserCustomPosUseG0');
			const laserSaveCustomPosEl = document.getElementById('laserSaveCustomPos');
			const laserGoCustomPosEl = document.getElementById('laserGoCustomPos');
			const laserMoveStepMmEl = document.getElementById('laserMoveStepMm');
			const laserMoveFeedMmSecEl = document.getElementById('laserMoveFeedMmSec');
			const laserJogUpEl = document.getElementById('laserJogUp');
			const laserJogDownEl = document.getElementById('laserJogDown');
			const laserJogLeftEl = document.getElementById('laserJogLeft');
			const laserJogRightEl = document.getElementById('laserJogRight');
			const laserJogHomeEl = document.getElementById('laserJogHome');
			const laserJogStatusEl = document.getElementById('laserJogStatus');
			const laserSerialLinkHintEl = document.getElementById('laserSerialLinkHint');
			const laserSerialMessagesHintEl = document.getElementById('laserSerialMessagesHint');
			const laserSerialRxHintEl = document.getElementById('laserSerialRxHint');
			const laserSerialTxHintEl = document.getElementById('laserSerialTxHint');
			const serialProxyPortsHintEl = document.getElementById('serialProxyPortsHint');
			const laserMiniStatusEl = document.getElementById('laserMiniStatus');
			const laserMiniStatusTextEl = document.getElementById('laserMiniStatusText');
			const fullscreenZoomHudEl = document.getElementById('fullscreenZoomHud');
			const zoomOutBtn = document.getElementById('zoomOutBtn');
			const zoomInBtn = document.getElementById('zoomInBtn');
			const zoomResetBtn = document.getElementById('zoomResetBtn');
			const zoomIndicatorEl = document.getElementById('zoomIndicator');
			let photoTaken = false;
			let prevBlobUrl = null;
			const settingsMenuModalEl = document.getElementById('settingsMenuModal');
			const videoSettingsModalEl = document.getElementById('videoSettingsModal');
			const screenshotSettingsModalEl = document.getElementById('screenshotSettingsModal');
			const v4l2SettingsModalEl = document.getElementById('v4l2SettingsModal');
			const ledPreviewModalEl = document.getElementById('ledPreviewModal');
			const buttonsSettingsModalEl = document.getElementById('buttonsSettingsModal');
			const airAssistModalEl = document.getElementById('airAssistModal');
			const grblCommandsModalEl = document.getElementById('grblCommandsModal');
			const settingsMenuCardEl = document.getElementById('settingsMenuCard');
			const videoSettingsCardEl = document.getElementById('videoSettingsCard');
			const screenshotSettingsCardEl = document.getElementById('screenshotSettingsCard');
			const ledPreviewCardEl = document.getElementById('ledPreviewCard');
			const buttonsSettingsCardEl = document.getElementById('buttonsSettingsCard');
			const airAssistCardEl = document.getElementById('airAssistCard');
			const grblCommandsCardEl = document.getElementById('grblCommandsCard');
			const settingsMenuDragHandleEl = document.getElementById('settingsMenuDragHandle');
			const videoSettingsDragHandleEl = document.getElementById('videoSettingsDragHandle');
			const screenshotSettingsDragHandleEl = document.getElementById('screenshotSettingsDragHandle');
			const ledPreviewDragHandleEl = document.getElementById('ledPreviewDragHandle');
			const buttonsSettingsDragHandleEl = document.getElementById('buttonsSettingsDragHandle');
			const airAssistDragHandleEl = document.getElementById('airAssistDragHandle');
			const grblCommandsDragHandleEl = document.getElementById('grblCommandsDragHandle');
			const v4l2HFlipEl = document.getElementById('v4l2HFlip');
			const v4l2VFlipEl = document.getElementById('v4l2VFlip');
			const v4l2QualityEl = document.getElementById('v4l2Quality');
			const v4l2QualityValEl = document.getElementById('v4l2QualityVal');
			const v4l2SettingsStatusEl = document.getElementById('v4l2SettingsStatus');
			v4l2QualityEl.addEventListener('input', () => { v4l2QualityValEl.textContent = v4l2QualityEl.value; });
			const videoResolutionSelectEl = document.getElementById('videoResolutionSelect');
			const screenshotResolutionSelectEl = document.getElementById('screenshotResolutionSelect');
			const videoResolutionInputEl = document.getElementById('videoResolutionInput');
			const screenshotResolutionInputEl = document.getElementById('screenshotResolutionInput');
			const streamHdIntervalSelectEl = document.getElementById('streamHdIntervalSelect');
			const streamHdIntervalInputEl = document.getElementById('streamHdIntervalInput');
			const videoFpsSelectEl = document.getElementById('videoFpsSelect');
			const videoFpsInputEl = document.getElementById('videoFpsInput');
			const videoSettingsStatusEl = document.getElementById('videoSettingsStatus');
			const buttonsSettingsStatusEl = document.getElementById('buttonsSettingsStatus');
			const modePressCountSelectEl = document.getElementById('modePressCountSelect');
			const modeEntryModeSelectEl = document.getElementById('modeEntryModeSelect');
			const modeLedEffectSelectEl = document.getElementById('modeLedEffectSelect');
			const modeLedColorSelectEl = document.getElementById('modeLedColorSelect');
			const modeLedSingleActionSelectEl = document.getElementById('modeLedSingleActionSelect');
			const modePowerSingleActionSelectEl = document.getElementById('modePowerSingleActionSelect');
			const ledDoublePressActionSelectEl = document.getElementById('ledDoublePressActionSelect');
			const ledTriplePressActionSelectEl = document.getElementById('ledTriplePressActionSelect');
			const powerDoublePressActionSelectEl = document.getElementById('powerDoublePressActionSelect');
			const powerTriplePressActionSelectEl = document.getElementById('powerTriplePressActionSelect');
			const buttonsResetModeOpeningDoorEl = document.getElementById('buttonsResetModeOpeningDoor');
			const quickStreamEl = document.getElementById('quickStream');
			const quickStreamHdEl = document.getElementById('quickStreamHd');
			const quickSnapshotEl = document.getElementById('quickSnapshot');
			const streamUrl = '/stream';
			const streamHdUrl = '/streamhd';
			const streamLoadingEl = document.getElementById('streamLoading');
			const streamBusyEl = document.getElementById('streamBusyNotice');
			let currentStreamMode = 'stream';
			let liveReconnectTimer = null;
			let suppressStreamErrorsUntil = 0;
			let streamBusy = false;
			let lastCameraOwnerMode = null;
			let statePollBusy = false;
			let ledToggleBusy = false;
			let selectedCustomHex = '#d2ebff';
			let customColorDirty = false;
			let customColorApplyTimer = null;
			let customColorApplySeq = 0;
			let fullscreenZoom = 1;
			let fullscreenZoomTarget = null;
			const LASER_MOVE_STEP_MIN_MM = 0.1;
			const LASER_MOVE_STEP_MAX_MM = 100.0;
			const LASER_MOVE_FEED_MIN_MM_SEC = 0.2;
			const LASER_MOVE_FEED_MAX_MM_SEC = 80.0;
			const LASER_MOVE_INPUT_SYNC_HOLD_MS = 4000;
			let laserMoveStepSyncHoldUntil = 0;
			let laserMoveFeedSyncHoldUntil = 0;
			let laserMoveStepPersistPromise = null;
			let laserMoveFeedPersistPromise = null;
			const laserEffects = ['static','breathe','pulse','strobe','flash','fire','disco','snake','twinkle'];
			const laserColorModes = ['cool_white','warm_white','amber_boost','sunset_orange','laser_green','ruby_red','ice_cyan','magenta_pink','blue_intense','blue_soft','green_intense','green_soft','red_intense','red_soft','cyan_intense','cyan_soft','magenta_intense','magenta_soft','amber_intense','amber_soft','random_solid','random_per_led','custom_solid'];
			const ledPresets = ['none','ocean_wave','red_fire','green_forest','sunset_lava','ice_plasma'];
			const modeEntryModes = ['move_x','move_y','move_z','brightness','change_effect','select_preset','change_color'];
			const modeSingleClickActions = ['move_up','move_down','move_left','move_right','move_forward','move_backward','next_preset','previous_preset','next_effect','previous_effect','next_color','previous_color','brightness_plus','brightness_minus'];
			const staticButtonActions = ['reboot','shutdown','clear_status','light_toggle','homing','custom_position','none'];
			const defaultModeButtonProfiles = {
				'1': { entry_mode: 'move_x', led_effect: 'pulse', led_color_mode: 'laser_green', led_single_click_action: 'next_effect', power_single_click_action: 'next_color' },
				'2': { entry_mode: 'brightness', led_effect: 'breathe', led_color_mode: 'amber_boost', led_single_click_action: 'brightness_plus', power_single_click_action: 'brightness_minus' },
				'3': { entry_mode: 'change_effect', led_effect: 'twinkle', led_color_mode: 'ice_cyan', led_single_click_action: 'next_effect', power_single_click_action: 'previous_effect' },
				'4': { entry_mode: 'select_preset', led_effect: 'static', led_color_mode: 'cool_white', led_single_click_action: 'next_preset', power_single_click_action: 'previous_preset' },
			};
			const defaultStaticButtonActions = {
				led_double_press: 'light_toggle',
				led_triple_press: 'clear_status',
				power_double_press: 'reboot',
				power_triple_press: 'shutdown',
			};
			let modeButtonProfilesState = JSON.parse(JSON.stringify(defaultModeButtonProfiles));
			let staticButtonActionsState = Object.assign({}, defaultStaticButtonActions);
			let modePressCountCurrentKey = '1';

			function setupQuickLinks() {
				const rawHost = (window.location.hostname || 'localhost').trim();
				const base = 'http://' + rawHost;
				function applyLink(anchorEl, path) {
					const full = base + path;
					anchorEl.href = full;
				}

				applyLink(quickStreamEl, '/stream');
				applyLink(quickStreamHdEl, '/streamhd');
				applyLink(quickSnapshotEl, '/snapshot');
			}

			setupQuickLinks();

			const collapsibleBlocks = Array.from(document.querySelectorAll('details.collapsible-block'));
			
			function getCollapsibleState() {
				const state = {};
				collapsibleBlocks.forEach((detailsEl, idx) => {
					const id = detailsEl.id || ('collapsible-' + idx);
					state[id] = detailsEl.open;
				});
				return state;
			}
			
			function saveCollapsibleState() {
				try {
					sessionStorage.setItem('collapsibleState', JSON.stringify(getCollapsibleState()));
				} catch (e) {}
			}
			
			function restoreCollapsibleState() {
				try {
					const saved = sessionStorage.getItem('collapsibleState');
					if (!saved) return;
					const state = JSON.parse(saved);
					collapsibleBlocks.forEach((detailsEl, idx) => {
						const id = detailsEl.id || ('collapsible-' + idx);
						if (id in state) {
							detailsEl.open = state[id];
						}
					});
				} catch (e) {}
			}
			
			collapsibleBlocks.forEach((detailsEl) => {
				detailsEl.addEventListener('toggle', () => {
					saveCollapsibleState();
					if (!detailsEl.open) return;
					window.setTimeout(() => {
						detailsEl.scrollIntoView({ behavior: 'smooth', block: 'start', inline: 'nearest' });
					}, 120);
				});
			});
			
			restoreCollapsibleState();

			function showStreamLoading() { streamLoadingEl.classList.add('active'); }
			function hideStreamLoading() { streamLoadingEl.classList.remove('active'); }
			function showStreamBusy() { streamBusyEl.classList.add('active'); }
			function hideStreamBusy() { streamBusyEl.classList.remove('active'); }

			liveStreamEl.addEventListener('load', hideStreamLoading);
			liveStreamEl.addEventListener('error', hideStreamLoading);

			function startLiveStream(forceRestart) {
			if (streamBusy) {
				hideStreamLoading();
				showStreamBusy();
				if (lastCameraOwnerMode) {
					updateCameraNotice('Camera priority: ' + String(lastCameraOwnerMode).toUpperCase(), 'info');
				}
				return;
			}
			const baseUrl = currentStreamMode === 'streamhd' ? streamHdUrl : streamUrl;
			const nextUrl = baseUrl + '?t=' + Date.now();
			const sameModeActive = liveStreamEl.dataset.mode === currentStreamMode && !!liveStreamEl.src;
			if (forceRestart || !sameModeActive) {
				suppressStreamErrorsUntil = Date.now() + 1500;
				hideStreamBusy();
				showStreamLoading();
				liveStreamEl.dataset.mode = currentStreamMode;
				liveStreamEl.src = nextUrl;
			}
			}

			function scheduleLiveReconnect() {
			if (streamBusy) return;
			if (Date.now() < suppressStreamErrorsUntil) return;
			if (!livePanelEl.classList.contains('active')) return;
			if (!liveStreamEl.src) return;
			if (liveReconnectTimer !== null) return;
			liveReconnectTimer = setTimeout(() => {
				liveReconnectTimer = null;
				startLiveStream(true);
			}, 1200);
			}

			liveStreamEl.addEventListener('error', scheduleLiveReconnect);

			async function toggleMediaFullscreen() {
				if (!document.fullscreenElement) {
					const target = livePanelEl.classList.contains('active')
						? livePanelEl.querySelector('.stream-wrap')
						: ((capturedPhotoEl.style.display !== 'none' && capturedPhotoEl.src) ? capturedPhotoEl : photoPlaceholderEl);
					if (!target || !target.requestFullscreen) return;
					try {
						await target.requestFullscreen();
					} catch (err) {
						setStatus('Fullscreen is not available in this browser.');
					}
					return;
				}
				await document.exitFullscreen();
			}

			mediaFullscreenBtn.addEventListener('click', toggleMediaFullscreen);
			snapshotFullscreenBtn.addEventListener('click', toggleMediaFullscreen);
			liveStreamEl.addEventListener('dblclick', toggleMediaFullscreen);
			capturedPhotoEl.addEventListener('dblclick', toggleMediaFullscreen);
			photoPlaceholderEl.addEventListener('dblclick', toggleMediaFullscreen);

			function resolveZoomTarget() {
				if (livePanelEl.classList.contains('active')) {
					return liveStreamEl;
				}
				if (capturedPhotoEl.style.display !== 'none' && capturedPhotoEl.src) {
					return capturedPhotoEl;
				}
				return photoPlaceholderEl;
			}

			function setFullscreenZoom(value) {
				fullscreenZoom = Math.max(1, Math.min(8, Number(value) || 1));
				if (zoomIndicatorEl) {
					zoomIndicatorEl.textContent = 'Zoom ' + Math.round(fullscreenZoom * 100) + '%';
				}
				if (fullscreenZoomTarget) {
					fullscreenZoomTarget.style.transform = 'scale(' + fullscreenZoom.toFixed(2) + ')';
				}
			}

			function bindFullscreenZoomTarget() {
				const nextTarget = resolveZoomTarget();
				if (fullscreenZoomTarget && fullscreenZoomTarget !== nextTarget) {
					fullscreenZoomTarget.style.transform = '';
					fullscreenZoomTarget.classList.remove('zoom-target');
				}
				fullscreenZoomTarget = nextTarget || null;
				if (fullscreenZoomTarget) {
					fullscreenZoomTarget.classList.add('zoom-target');
					setFullscreenZoom(fullscreenZoom);
				}
			}

			zoomOutBtn.addEventListener('click', () => setFullscreenZoom(fullscreenZoom - 0.1));
			zoomInBtn.addEventListener('click', () => setFullscreenZoom(fullscreenZoom + 0.1));
			zoomResetBtn.addEventListener('click', () => setFullscreenZoom(1));

			document.addEventListener('wheel', (ev) => {
				if (!document.fullscreenElement) return;
				if (!document.fullscreenElement.contains(ev.target)) return;
				ev.preventDefault();
				const delta = ev.deltaY < 0 ? 0.12 : -0.12;
				setFullscreenZoom(fullscreenZoom + delta);
			}, { passive: false });

			document.addEventListener('fullscreenchange', () => {
				mediaFullscreenBtn.textContent = document.fullscreenElement ? 'exit' : 'fullscreen';
				const isFs = !!document.fullscreenElement;
				fullscreenZoomHudEl.classList.toggle('active', isFs);
				if (isFs) {
					fullscreenZoom = 1;
					bindFullscreenZoomTarget();
					setFullscreenZoom(1);
				} else {
					if (fullscreenZoomTarget) {
						fullscreenZoomTarget.style.transform = '';
						fullscreenZoomTarget.classList.remove('zoom-target');
					}
					fullscreenZoomTarget = null;
				}
			});

			function hexToRgb(hex) {
			const m = hex.replace('#', '');
			return {
				r: parseInt(m.slice(0, 2), 16),
				g: parseInt(m.slice(2, 4), 16),
				b: parseInt(m.slice(4, 6), 16)
			};
			}

			function rgbToHex(r, g, b) {
			const toHex = (v) => v.toString(16).padStart(2, '0');
			return '#' + toHex(r) + toHex(g) + toHex(b);
			}

			function normalizeHex(hex) {
				const raw = String(hex || '').trim().replace('#', '').toLowerCase();
				if (!/^[0-9a-f]{6}$/.test(raw)) return '#d2ebff';
				return '#' + raw;
			}

			function updateCustomColorPreview(hex) {
				const normalized = normalizeHex(hex);
				customColorPreviewEl.style.background = normalized;
				customColorHexEl.textContent = normalized.toUpperCase();
				const rgb = hexToRgb(normalized);
				const luma = (0.299 * rgb.r + 0.587 * rgb.g + 0.114 * rgb.b) / 255;
				customColorHexEl.style.color = luma > 0.62 ? '#0a1f33' : '#eef7ff';
			}

			function scheduleCustomColorApply(immediate) {
				const seq = ++customColorApplySeq;
				if (customColorApplyTimer !== null) {
					clearTimeout(customColorApplyTimer);
					customColorApplyTimer = null;
				}

				const runApply = async () => {
					try {
						const c = hexToRgb(selectedCustomHex);
						const state = await api('/api/color', c);
						if (seq !== customColorApplySeq) return;
						customColorDirty = false;
						if (state && Array.isArray(state.custom_color) && state.custom_color.length === 3) {
							const stateHex = rgbToHex(state.custom_color[0], state.custom_color[1], state.custom_color[2]);
							selectedCustomHex = normalizeHex(stateHex);
							customColorEl.value = selectedCustomHex;
							updateCustomColorPreview(selectedCustomHex);
						}
						if (state && state.color_mode) {
							colorModeEl.value = state.color_mode;
						}
					} catch (err) {
						if (seq !== customColorApplySeq) return;
						customColorDirty = false;
						setStatus('Color update error: ' + err.message);
						await refresh().catch(() => {});
					}
				};

				if (immediate) {
					runApply();
				} else {
					customColorApplyTimer = setTimeout(runApply, 140);
				}
			}

			async function api(path, payload) {
			const res = await fetch(path, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(payload || {})
			});
			let data = {};
			try {
				data = await res.json();
			} catch (err) {
				data = {};
			}
			if (!res.ok) {
				const detail = data.detail || data.error || ('HTTP ' + res.status);
				throw new Error(detail);
			}
			return data;
			}

			function setStatus(text) {
			statusEl.textContent = text;
			}

			function setPhotoStatus(text) {
			photoStatusEl.textContent = text;
			}

			function updateBrightnessValue(value) {
				const num = parseFloat(value);
				if (brightnessValEl) {
					brightnessValEl.textContent = isNaN(num) ? '--%' : (Math.round(num * 100) + '%');
				}
			}

			function updateDefaultBrightnessValue(value) {
				const num = parseFloat(value);
				ledDefaultBrightnessValEl.textContent = isNaN(num) ? '--' : num.toFixed(2);
			}

			function updateStartupShutdownBrightnessValue(value) {
				const num = parseFloat(value);
				startupShutdownBrightnessValEl.textContent = isNaN(num) ? '--' : num.toFixed(2);
			}

			function updatePresetIntensityValue(value) {
				const num = parseInt(value, 10);
				presetIntensityValEl.textContent = isNaN(num) ? '--' : (num + '%');
			}

			function updateLedState(isOn) {
				const active = !!isOn;
				if (ledBulbIconEl) {
					ledBulbIconEl.classList.toggle('on', active);
					ledBulbIconEl.classList.toggle('off', !active);
				}
				if (togglePowerEl) {
					togglePowerEl.setAttribute('aria-pressed', active ? 'true' : 'false');
					togglePowerEl.classList.toggle('light-on', active);
					togglePowerEl.classList.toggle('light-off', !active);
					togglePowerEl.textContent = active ? 'ON' : 'OFF';
					togglePowerEl.title = active ? 'LED on' : 'LED off';
				}
				if (ledStateLabelEl) {
					ledStateLabelEl.title = active ? 'LED on' : 'LED off';
				}
			}

			function startStateSyncPolling() {
				setInterval(async () => {
					if (statePollBusy) return;
					statePollBusy = true;
					try {
						await refresh();
					} catch (err) {
					} finally {
						statePollBusy = false;
					}
				}, 2000);
			}

			function showRightPanel(which) {
			const liveActive = which !== 'snapshot';
			const previousMode = currentStreamMode;
			if (which === 'streamhd') {
				currentStreamMode = 'streamhd';
			} else if (which === 'live') {
				currentStreamMode = 'stream';
			}
			livePanelEl.classList.toggle('active', liveActive);
			snapshotPanelEl.classList.toggle('active', !liveActive);
			streamBadgeEl.classList.toggle('active', which === 'live');
			streamHdBadgeEl.classList.toggle('active', which === 'streamhd');
			snapshotBadgeEl.classList.toggle('active', which === 'snapshot');
			if (liveActive) {
				startLiveStream(previousMode !== currentStreamMode || !liveStreamEl.src);
			} else {
				hideStreamBusy();
				suppressStreamErrorsUntil = Date.now() + 1500;
				liveStreamEl.dataset.mode = '';
				liveStreamEl.src = '';
			}
			if (document.fullscreenElement) {
				bindFullscreenZoomTarget();
				setFullscreenZoom(fullscreenZoom);
			}
			fetchSystemStats();
			}

			function updateStreamBusyState(ownerMode) {
				lastCameraOwnerMode = ownerMode || null;
				const busyNow = !!lastCameraOwnerMode && lastCameraOwnerMode !== currentStreamMode;
				if (busyNow === streamBusy) return;

				streamBusy = busyNow;
				if (streamBusy) {
					liveStreamEl.src = '';
					hideStreamLoading();
					if (livePanelEl.classList.contains('active')) showStreamBusy();
				} else {
					hideStreamBusy();
					if (livePanelEl.classList.contains('active')) {
						startLiveStream(true);
						setTimeout(() => {
							if (livePanelEl.classList.contains('active') && !streamBusy) {
								startLiveStream(true);
							}
						}, 1400);
					}
				}
			}

			function openModal(modalEl) {
			modalEl.classList.add('open');
			positionDraggableModal(modalEl, getModalCardFor(modalEl));
			}

			function closeModal(modalEl) {
			modalEl.classList.remove('open');
			}

			function getModalCardFor(modalEl) {
				if (modalEl === settingsMenuModalEl) return settingsMenuCardEl;
				if (modalEl === ledPreviewModalEl) return ledPreviewCardEl;
				if (modalEl === videoSettingsModalEl) return videoSettingsCardEl;
				if (modalEl === screenshotSettingsModalEl) return screenshotSettingsCardEl;
				if (modalEl === buttonsSettingsModalEl) return buttonsSettingsCardEl;
				if (modalEl === airAssistModalEl) return airAssistCardEl;
				if (modalEl === grblCommandsModalEl) return grblCommandsCardEl;
				return null;
			}

			function clampDraggableModalPosition(cardEl, left, top) {
				if (!cardEl) return { left: 12, top: 12 };
				const viewportWidth = window.innerWidth || document.documentElement.clientWidth || 0;
				const viewportHeight = window.innerHeight || document.documentElement.clientHeight || 0;
				const cardWidth = cardEl.offsetWidth || Math.min(420, Math.max(280, viewportWidth - 24));
				const cardHeight = cardEl.offsetHeight || 320;
				const maxLeft = Math.max(12, viewportWidth - cardWidth - 12);
				const maxTop = Math.max(12, viewportHeight - cardHeight - 12);
				return {
					left: Math.min(maxLeft, Math.max(12, Math.round(left))),
					top: Math.min(maxTop, Math.max(12, Math.round(top))),
				};
			}

			function applyDraggableModalPosition(cardEl, left, top) {
				if (!cardEl) return;
				const clamped = clampDraggableModalPosition(cardEl, left, top);
				cardEl.style.left = clamped.left + 'px';
				cardEl.style.top = clamped.top + 'px';
				cardEl.dataset.dragPositioned = '1';
			}

			function positionDraggableModal(modalEl, cardEl, forceCenter) {
				if (!cardEl) return;
				const viewportWidth = window.innerWidth || document.documentElement.clientWidth || 0;
				const viewportHeight = window.innerHeight || document.documentElement.clientHeight || 0;
				if (forceCenter || cardEl.dataset.dragPositioned !== '1') {
					const cardWidth = cardEl.offsetWidth || Math.min(420, Math.max(280, viewportWidth - 24));
					const cardHeight = cardEl.offsetHeight || 320;
					const centeredLeft = Math.max(12, (viewportWidth - cardWidth) / 2);
					const centeredTop = Math.max(12, Math.min(viewportHeight * 0.08, (viewportHeight - cardHeight) / 2));
					applyDraggableModalPosition(cardEl, centeredLeft, centeredTop);
					return;
				}
				const currentLeft = parseFloat(cardEl.style.left || '12');
				const currentTop = parseFloat(cardEl.style.top || '12');
				applyDraggableModalPosition(cardEl, currentLeft, currentTop);
			}

			function initModalDrag(modalEl, cardEl, dragHandleEl) {
				if (!modalEl || !cardEl || !dragHandleEl) return;
				let dragState = null;

				dragHandleEl.addEventListener('pointerdown', (ev) => {
					if (ev.button !== undefined && ev.button !== 0) return;
					positionDraggableModal(modalEl, cardEl);
					const startLeft = parseFloat(cardEl.style.left || '12');
					const startTop = parseFloat(cardEl.style.top || '12');
					dragState = {
						pointerId: ev.pointerId,
						startX: ev.clientX,
						startY: ev.clientY,
						startLeft: startLeft,
						startTop: startTop,
					};
					dragHandleEl.setPointerCapture(ev.pointerId);
					ev.preventDefault();
				});

				dragHandleEl.addEventListener('pointermove', (ev) => {
					if (!dragState || ev.pointerId !== dragState.pointerId) return;
					applyDraggableModalPosition(cardEl,
						dragState.startLeft + (ev.clientX - dragState.startX),
						dragState.startTop + (ev.clientY - dragState.startY)
					);
					ev.preventDefault();
				});

				function endDrag(ev) {
					if (!dragState || ev.pointerId !== dragState.pointerId) return;
					try {
						dragHandleEl.releasePointerCapture(ev.pointerId);
					} catch (err) {}
					dragState = null;
				}

				dragHandleEl.addEventListener('pointerup', endDrag);
				dragHandleEl.addEventListener('pointercancel', endDrag);
			}

			function fillResolutionSelect(selectEl, presets, currentValue) {
			const values = Array.isArray(presets) ? presets.slice() : [];
			if (!values.includes(currentValue)) values.push(currentValue);
			selectEl.innerHTML = values
				.map((v) => '<option value="' + v + '">' + v + '</option>')
				.join('');
			selectEl.value = currentValue;
			}

			function fillFpsSelect(selectEl, presets, currentValue) {
			const values = Array.isArray(presets) ? presets.slice() : [];
			if (!values.includes(currentValue)) values.push(currentValue);
			selectEl.innerHTML = values
				.map((v) => '<option value="' + v + '">' + v + ' fps</option>')
				.join('');
			selectEl.value = currentValue;
			}

			function fillIntervalSelect(selectEl, presets, currentValue) {
			const values = Array.isArray(presets) ? presets.slice() : [];
			if (!values.includes(currentValue)) values.push(currentValue);
			selectEl.innerHTML = values
				.map((v) => '<option value="' + v + '">1 image every ' + v + 's</option>')
				.join('');
			selectEl.value = currentValue;
			}

			function renderCameraSettings(settings) {
			const fps = settings.stream_fps || 20;
			const hdInterval = settings.streamhd_interval_s || 4;
			const mqttImageEnabled = Number(settings.mqtt_image_enabled || 0) === 1;
			if (settings.horizontal_flip !== undefined) v4l2HFlipEl.checked = settings.horizontal_flip === 1;
			if (settings.vertical_flip !== undefined) v4l2VFlipEl.checked = settings.vertical_flip === 1;
			if (settings.compression_quality !== undefined) { v4l2QualityEl.value = settings.compression_quality; v4l2QualityValEl.textContent = settings.compression_quality; }
			mqttImageEnabledEl.checked = mqttImageEnabled;
			mqttImageHintEl.textContent = mqttImageEnabled
				? 'MQTT Images (needs CPU)'
				: 'MQTT Images OFF (CPU save)';
			streamBadgeEl.innerHTML = '<span class="menu-tab-main">Live Stream</span><span class="menu-tab-sub">' + settings.stream_resolution + ' @' + fps + 'fps</span>';
			streamHdBadgeEl.innerHTML = '<span class="menu-tab-main">StreamHD</span><span class="menu-tab-sub">' + settings.screenshot_resolution + ' 1 frame every ' + hdInterval + 's</span>';
			snapshotBadgeEl.innerHTML = '<span class="menu-tab-main">Snapshot</span><span class="menu-tab-sub">' + settings.screenshot_resolution + '</span>';
			videoResolutionInputEl.value = settings.stream_resolution;
			screenshotResolutionInputEl.value = settings.screenshot_resolution;
			videoFpsInputEl.value = fps;
			streamHdIntervalInputEl.value = hdInterval;
			fillResolutionSelect(videoResolutionSelectEl, settings.resolution_presets, settings.stream_resolution);
			fillResolutionSelect(screenshotResolutionSelectEl, settings.resolution_presets, settings.screenshot_resolution);
			fillFpsSelect(videoFpsSelectEl, settings.fps_presets || [5,10,15,20,24,25,30], fps);
			fillIntervalSelect(streamHdIntervalSelectEl, settings.streamhd_interval_presets || [1,2,3,4,5,8,10], hdInterval);
			}

			function formatOptionLabel(value) {
				const text = String(value || '').trim();
				if (!text) return 'N/A';
				const labels = {
					cool_white: 'Cool White',
					warm_white: 'Warm White',
					amber_boost: 'Amber Boost',
					sunset_orange: 'Sunset Orange',
					laser_green: 'Laser Green',
					ruby_red: 'Ruby Red',
					ice_cyan: 'Ice Cyan',
					magenta_pink: 'Magenta Pink',
					blue_intense: 'Blue Intense',
					blue_soft: 'Blue Soft',
					green_intense: 'Green Intense',
					green_soft: 'Green Soft',
					red_intense: 'Red Intense',
					red_soft: 'Red Soft',
					cyan_intense: 'Cyan Intense',
					cyan_soft: 'Cyan Soft',
					magenta_intense: 'Magenta Intense',
					magenta_soft: 'Magenta Soft',
					amber_intense: 'Amber Intense',
					amber_soft: 'Amber Soft',
					random_solid: 'Random Solid',
					random_per_led: 'Random per LED',
					custom_solid: 'Custom Solid',
					brightness_plus: 'Brightness +',
					brightness_minus: 'Brightness -',
				};
				if (Object.prototype.hasOwnProperty.call(labels, text)) return labels[text];
				return text.replace(/_/g, ' ').replace(/\\b\\w/g, (m) => m.toUpperCase());
			}

			function setSelectOptions(selectEl, options, selectedValue) {
				selectEl.innerHTML = options.map((v) => '<option value="' + v + '">' + formatOptionLabel(v) + '</option>').join('');
				selectEl.value = selectedValue;
				if (!selectEl.value && options.length > 0) selectEl.value = options[0];
			}

			function renderModeProfileForSelectedPress() {
				const pressKey = String((modePressCountSelectEl && modePressCountSelectEl.value) || modePressCountCurrentKey || '1');
				modePressCountCurrentKey = pressKey;
				const profile = modeButtonProfilesState[pressKey] || defaultModeButtonProfiles[pressKey] || defaultModeButtonProfiles['1'];
				modeEntryModeSelectEl.value = profile.entry_mode || defaultModeButtonProfiles[pressKey].entry_mode;
				modeLedEffectSelectEl.value = profile.led_effect || defaultModeButtonProfiles[pressKey].led_effect;
				modeLedColorSelectEl.value = profile.led_color_mode || defaultModeButtonProfiles[pressKey].led_color_mode;
				modeLedSingleActionSelectEl.value = profile.led_single_click_action || defaultModeButtonProfiles[pressKey].led_single_click_action;
				modePowerSingleActionSelectEl.value = profile.power_single_click_action || defaultModeButtonProfiles[pressKey].power_single_click_action;
			}

			function updateModeProfileFromInputs(targetPressKey) {
				const pressKey = String(targetPressKey || modePressCountCurrentKey || (modePressCountSelectEl && modePressCountSelectEl.value) || '1');
				modeButtonProfilesState[pressKey] = {
					entry_mode: modeEntryModeSelectEl.value,
					led_effect: modeLedEffectSelectEl.value,
					led_color_mode: modeLedColorSelectEl.value,
					led_single_click_action: modeLedSingleActionSelectEl.value,
					power_single_click_action: modePowerSingleActionSelectEl.value,
				};
			}

			function renderButtonsSettings(config) {
				const cfg = config || {};
				const rawProfiles = (cfg.mode_button_profiles && typeof cfg.mode_button_profiles === 'object') ? cfg.mode_button_profiles : {};
				const mergedProfiles = {};
				['1', '2', '3', '4'].forEach((pressKey) => {
					const fallback = defaultModeButtonProfiles[pressKey];
					const raw = (rawProfiles[pressKey] && typeof rawProfiles[pressKey] === 'object') ? rawProfiles[pressKey] : {};
					mergedProfiles[pressKey] = {
						entry_mode: raw.entry_mode || fallback.entry_mode,
						led_effect: raw.led_effect || fallback.led_effect,
						led_color_mode: raw.led_color_mode || fallback.led_color_mode,
						led_single_click_action: raw.led_single_click_action || fallback.led_single_click_action,
						power_single_click_action: raw.power_single_click_action || fallback.power_single_click_action,
					};
				});
				modeButtonProfilesState = mergedProfiles;

				const rawStatic = (cfg.button_static_actions && typeof cfg.button_static_actions === 'object') ? cfg.button_static_actions : {};
				staticButtonActionsState = {
					led_double_press: rawStatic.led_double_press || defaultStaticButtonActions.led_double_press,
					led_triple_press: rawStatic.led_triple_press || defaultStaticButtonActions.led_triple_press,
					power_double_press: rawStatic.power_double_press || defaultStaticButtonActions.power_double_press,
					power_triple_press: rawStatic.power_triple_press || defaultStaticButtonActions.power_triple_press,
				};

				setSelectOptions(modeEntryModeSelectEl, modeEntryModes, modeEntryModes[0]);
				setSelectOptions(modeLedEffectSelectEl, laserEffects, laserEffects[0]);
				setSelectOptions(modeLedColorSelectEl, laserColorModes, laserColorModes[0]);
				setSelectOptions(modeLedSingleActionSelectEl, modeSingleClickActions, modeSingleClickActions[0]);
				setSelectOptions(modePowerSingleActionSelectEl, modeSingleClickActions, modeSingleClickActions[0]);
				setSelectOptions(ledDoublePressActionSelectEl, staticButtonActions, staticButtonActions[0]);
				setSelectOptions(ledTriplePressActionSelectEl, staticButtonActions, staticButtonActions[0]);
				setSelectOptions(powerDoublePressActionSelectEl, staticButtonActions, staticButtonActions[0]);
				setSelectOptions(powerTriplePressActionSelectEl, staticButtonActions, staticButtonActions[0]);

				if (!modePressCountSelectEl.value) modePressCountSelectEl.value = '1';
				modePressCountCurrentKey = String(modePressCountSelectEl.value || '1');
				renderModeProfileForSelectedPress();
				ledDoublePressActionSelectEl.value = staticButtonActionsState.led_double_press;
				ledTriplePressActionSelectEl.value = staticButtonActionsState.led_triple_press;
				powerDoublePressActionSelectEl.value = staticButtonActionsState.power_double_press;
				powerTriplePressActionSelectEl.value = staticButtonActionsState.power_triple_press;
				if (buttonsResetModeOpeningDoorEl) {
					buttonsResetModeOpeningDoorEl.checked = Number(cfg.buttons_reset_mode_opening_door || 0) === 1;
				}
			}

			function collectButtonsSettingsPatch() {
				updateModeProfileFromInputs();
				staticButtonActionsState = {
					led_double_press: ledDoublePressActionSelectEl.value,
					led_triple_press: ledTriplePressActionSelectEl.value,
					power_double_press: powerDoublePressActionSelectEl.value,
					power_triple_press: powerTriplePressActionSelectEl.value,
				};
				return {
					mode_button_profiles: modeButtonProfilesState,
					button_static_actions: staticButtonActionsState,
					buttons_reset_mode_opening_door: !!(buttonsResetModeOpeningDoorEl && buttonsResetModeOpeningDoorEl.checked),
				};
			}

			function renderLaserMonitor(data) {
				const cfg = (data && typeof data.config === 'object' && data.config) ? data.config : null;
				const safeCfg = cfg || {};
				if (!(buttonsSettingsModalEl && buttonsSettingsModalEl.classList.contains('open'))) {
					renderButtonsSettings(safeCfg);
				}
				setSelectOptions(laserRunningEffectEl, laserEffects, safeCfg.laser_led_running_effect || 'pulse');
				setSelectOptions(laserIdleEffectEl, laserEffects, safeCfg.laser_led_idle_effect || 'static');
				setSelectOptions(laserHoldEffectEl, laserEffects, safeCfg.laser_led_hold_effect || 'breathe');
				setSelectOptions(laserDoorEffectEl, laserEffects, safeCfg.laser_led_door_effect || 'strobe');
				setSelectOptions(laserErrorEffectEl, laserEffects, safeCfg.laser_led_error_effect || 'strobe');
				setSelectOptions(laserCompleteEffectEl, laserEffects, safeCfg.laser_led_engrave_complete_effect || 'twinkle');
				setSelectOptions(laserRunningColorEl, laserColorModes, safeCfg.laser_led_running_color_mode || 'laser_green');
				setSelectOptions(laserIdleColorEl, laserColorModes, safeCfg.laser_led_idle_color_mode || 'cool_white');
				setSelectOptions(laserHoldColorEl, laserColorModes, safeCfg.laser_led_hold_color_mode || 'amber_boost');
				setSelectOptions(laserDoorColorEl, laserColorModes, safeCfg.laser_led_door_color_mode || 'ruby_red');
				setSelectOptions(laserErrorColorEl, laserColorModes, safeCfg.laser_led_error_color_mode || 'ruby_red');
				setSelectOptions(laserCompleteColorEl, laserColorModes, safeCfg.laser_led_engrave_complete_color_mode || 'cool_white');
				setSelectOptions(startupLedEffectEl, laserEffects, safeCfg.led_startup_effect || 'strobe');
				setSelectOptions(startupLedColorEl, laserColorModes, safeCfg.led_startup_color_mode || 'laser_green');
				setSelectOptions(startupLedPresetEl, ledPresets, safeCfg.led_startup_preset || 'none');
				setSelectOptions(shutdownLedEffectEl, laserEffects, safeCfg.led_shutdown_effect || 'strobe');
				setSelectOptions(shutdownLedColorEl, laserColorModes, safeCfg.led_shutdown_color_mode || 'ruby_red');
				setSelectOptions(shutdownLedPresetEl, ledPresets, safeCfg.led_shutdown_preset || 'none');
				if (cfg) {
					const parsedDefaultBrightness = Number(cfg.led_default_brightness);
					const safeDefaultBrightness = Number.isFinite(parsedDefaultBrightness)
						? Math.max(0, Math.min(1, parsedDefaultBrightness))
						: 0.60;
					ledDefaultBrightnessEl.value = safeDefaultBrightness.toFixed(2);
					updateDefaultBrightnessValue(safeDefaultBrightness);
					const parsedStartupShutdownBrightness = Number(cfg.led_startup_shutdown_brightness);
					const safeStartupShutdownBrightness = Number.isFinite(parsedStartupShutdownBrightness)
						? Math.max(0, Math.min(1, parsedStartupShutdownBrightness))
						: 0.60;
					startupShutdownBrightnessEl.value = safeStartupShutdownBrightness.toFixed(2);
					updateStartupShutdownBrightnessValue(safeStartupShutdownBrightness);
					ledOnBootEnabledEl.checked = Number(cfg.led_on_boot || 0) === 1;
					serialProxyEnabledEl.checked = Number(cfg.serial_proxy_enabled || 0) === 1;
					if (passthroughExtendOnRealtimeEl) {
						passthroughExtendOnRealtimeEl.checked = Number(cfg.passthrough_extend_on_realtime || 0) === 1;
					}
					laserLedSyncEnabledEl.checked = Number(cfg.laser_led_sync_enabled || 0) === 1;
					if (laserErrorAutoReset10sEl) {
						laserErrorAutoReset10sEl.checked = Number(cfg.laser_led_error_auto_reset_10s || 0) === 1;
					}
					if (laserMoveStepMmEl) {
						const parsed = Number(cfg.laser_move_step_mm);
						const step = Number.isFinite(parsed) ? Math.max(LASER_MOVE_STEP_MIN_MM, Math.min(LASER_MOVE_STEP_MAX_MM, parsed)) : 20;
						laserMoveStepMmEl.dataset.lastValid = String(step);
						if (document.activeElement !== laserMoveStepMmEl && Date.now() >= laserMoveStepSyncHoldUntil) {
							laserMoveStepMmEl.value = String(step);
						}
					}
					if (laserMoveFeedMmSecEl) {
						const parsedFeed = Number(cfg.laser_move_feed_mm_sec);
						const feed = Number.isFinite(parsedFeed) ? Math.max(LASER_MOVE_FEED_MIN_MM_SEC, Math.min(LASER_MOVE_FEED_MAX_MM_SEC, parsedFeed)) : 10;
						laserMoveFeedMmSecEl.dataset.lastValid = String(Math.round(feed * 10) / 10);
						if (document.activeElement !== laserMoveFeedMmSecEl && Date.now() >= laserMoveFeedSyncHoldUntil) {
							laserMoveFeedMmSecEl.value = String(Math.round(feed * 10) / 10);
						}
					}
					if (laserCustomPosXEl && document.activeElement !== laserCustomPosXEl) {
						laserCustomPosXEl.value = String(Number(cfg.laser_custom_pos_x_mm || 0));
					}
					if (laserCustomPosYEl && document.activeElement !== laserCustomPosYEl) {
						laserCustomPosYEl.value = String(Number(cfg.laser_custom_pos_y_mm || 0));
					}
					if (laserCustomPosZEl && document.activeElement !== laserCustomPosZEl) {
						laserCustomPosZEl.value = String(Number(cfg.laser_custom_pos_z_mm || 0));
					}
					if (laserCustomPosUseG0El) {
						laserCustomPosUseG0El.checked = Number(cfg.laser_custom_pos_use_g0 || 0) === 1;
					}
				}
				const stateText = String(data.state || 'idle');
				const laserActive = !!data.laser_active;
				const lastErrorRaw = String(data.last_error || '').trim();
				const lastErrorTs = Number(data.last_error_ts || 0);
				const autoResetErrorUi = Number(safeCfg.laser_led_error_auto_reset_10s || 0) === 1;
				const errorExpired = autoResetErrorUi && lastErrorTs > 0 && ((Date.now() / 1000) - lastErrorTs) >= 10;
				const uiErrorRaw = errorExpired ? '' : lastErrorRaw;
				const cleanErrorParts = lastErrorRaw
					? lastErrorRaw
						.split('|')
						.map((part) => String(part || '').trim().replace(/^\\[[^\\]]+\\]\\s*/, '').replace(/\\s+/g, ' '))
						.filter(Boolean)
					: [];
				const errorCodePart = cleanErrorParts.find((part) => /^(?:ALARM|ERROR|ERR)\\s*:\\s*\\d+\\b/i.test(part)) || '';
				const errorDescriptionPart = cleanErrorParts.find((part) => /^(?:ALARM|ERROR|ERR)\\s*:\\s*(?!\\d+\\b).+/i.test(part)) || '';
				const cleanReason = errorCodePart && errorDescriptionPart
					? (errorCodePart + ' - ' + errorDescriptionPart)
					: (errorDescriptionPart || errorCodePart || cleanErrorParts[0] || '');
				const hasStickyError = !!uiErrorRaw;
				let uiState = ['idle', 'running', 'hold', 'door', 'error', 'engrave_complete'].includes(stateText) ? stateText : 'idle';
				if (uiState === 'running') {
					uiState = laserActive ? 'engraving' : 'moving';
				}
				if (hasStickyError && uiState !== 'door' && uiState !== 'engraving' && uiState !== 'moving') {
					uiState = 'error';
				}
				const stateLabel = uiState === 'engraving'
					? 'Engraving'
					: uiState === 'moving'
						? 'Moving'
						: uiState === 'engrave_complete'
							? 'Engrave completed'
							: uiState === 'hold'
								? 'HOLD'
								: uiState === 'door'
									? 'Door OPEN'
									: uiState === 'error'
										? 'ERROR'
										: 'Idle';
				const txRxStatus = (data.traffic_active || data.last_tx_command || data.last_rx_line) ? 'ON' : 'OFF';
				const laserSummary = stateLabel + ' | Laser = ' + (laserActive ? 'ON' : 'OFF') + ' | Tx/Rx = ' + txRxStatus;
				laserStatusHintEl.textContent = uiErrorRaw ? (laserSummary + '\\nerr: ' + uiErrorRaw) : laserSummary;
				if (laserMiniStatusEl) {
					const tone = uiState;
					laserMiniStatusEl.classList.remove('idle', 'running', 'moving', 'engraving', 'hold', 'door', 'error', 'engrave_complete');
					laserMiniStatusEl.classList.add(tone);
					laserMiniStatusEl.classList.remove('error-code-visible');
					if (laserMiniStatusTextEl) {
						if (uiState === 'error' && uiErrorRaw) {
							laserMiniStatusTextEl.textContent = cleanReason ? ('Error: ' + cleanReason) : 'Error';
						} else if (uiState === 'door') {
							laserMiniStatusTextEl.textContent = 'Door open';
						} else if (uiState === 'hold') {
							laserMiniStatusTextEl.textContent = 'Hold';
						} else if (uiState === 'engrave_complete') {
							laserMiniStatusTextEl.textContent = 'Engrave completed';
						} else if (uiState === 'idle') {
							laserMiniStatusTextEl.textContent = 'Idle';
						} else {
							laserMiniStatusTextEl.textContent = stateLabel;
						}
					}
				}
				const serial = (data && typeof data.serial_link === 'object' && data.serial_link) ? data.serial_link : {};
				const mode = String(serial.mode || 'disconnected');
				const clients = Number(serial.passthrough_clients || 0);
				const queued = Number(serial.queue_depth || 0);
				if (laserClearQueueBtnEl) {
					laserClearQueueBtnEl.disabled = queued <= 0;
				}
				if (laserSerialLinkHintEl) {
					laserSerialLinkHintEl.textContent = 'Serial link: mode=' + mode + ' | clients=' + clients + ' | queued=' + queued;
				}
				if (serialProxyPortsHintEl) {
					const targetPort = Number(safeCfg.serial_proxy_target_port || 2000);
					const listenPort = Number(safeCfg.serial_proxy_listen_port || 4001);
					serialProxyPortsHintEl.textContent = 'Serial monitor port target ' + targetPort + '; listen port ' + listenPort;
				}
				if (laserJogStatusEl) {
					const currentJogText = String(laserJogStatusEl.textContent || '');
					const hasJogPrefix = /^Jog:/i.test(currentJogText);
					const hasJogError = /^Jog:\\s*error/i.test(currentJogText);
					if (queued <= 0 && hasJogPrefix && !hasJogError) {
						laserJogStatusEl.textContent = 'Jog: ready, queue=0';
					}
				}
				if (laserSerialMessagesHintEl) {
					const rxLine = data.last_rx_line;
					const txLine = data.last_tx_command;
					const txText = formatSerialPreview('TX', txLine);
					const rxText = formatSerialPreview('RX', rxLine);
					if (laserSerialTxHintEl) laserSerialTxHintEl.textContent = txText;
					if (laserSerialRxHintEl) laserSerialRxHintEl.textContent = rxText;

				}
			}

			function parseNumericInput(rawValue) {
				const normalized = String(rawValue || '').trim().replace(',', '.');
				if (!normalized) return NaN;
				return Number(normalized);
			}

			function clampValue(value, minValue, maxValue) {
				return Math.min(maxValue, Math.max(minValue, value));
			}

			function formatSerialPreview(prefix, rawValue) {
				   let body = String(rawValue || '')
					   .split('\\r').join(' ')
					   .split('\\t').join(' ')
					   .split('\\n').join(' ')
					   .replace(/:(?! )/g, ': ')
					   .trim();
				if (!body) return prefix + ': --';
				const maxPreviewChars = 160;
				if (body.length <= maxPreviewChars) return prefix + ': ' + body;
				return prefix + ': ' + body.slice(0, maxPreviewChars) + '...';
			}

			function getCustomPositionValue(inputEl) {
				const raw = parseNumericInput(inputEl && inputEl.value);
				if (!Number.isFinite(raw)) return 0;
				return clampValue(raw, -1000, 1000);
			}

			function getLaserMoveStepMm() {
				const raw = parseNumericInput(laserMoveStepMmEl && laserMoveStepMmEl.value);
				if (!Number.isFinite(raw)) {
					const lastValid = parseNumericInput(laserMoveStepMmEl && laserMoveStepMmEl.dataset.lastValid);
					return Number.isFinite(lastValid) ? clampValue(lastValid, LASER_MOVE_STEP_MIN_MM, LASER_MOVE_STEP_MAX_MM) : 20;
				}
				return clampValue(raw, LASER_MOVE_STEP_MIN_MM, LASER_MOVE_STEP_MAX_MM);
			}

			function getLaserMoveFeedMmSec() {
				const raw = parseNumericInput(laserMoveFeedMmSecEl && laserMoveFeedMmSecEl.value);
				if (!Number.isFinite(raw)) {
					const lastValid = parseNumericInput(laserMoveFeedMmSecEl && laserMoveFeedMmSecEl.dataset.lastValid);
					return Number.isFinite(lastValid) ? clampValue(lastValid, LASER_MOVE_FEED_MIN_MM_SEC, LASER_MOVE_FEED_MAX_MM_SEC) : 10;
				}
				return clampValue(raw, LASER_MOVE_FEED_MIN_MM_SEC, LASER_MOVE_FEED_MAX_MM_SEC);
			}

			async function persistLaserMoveStepMm() {
				if (!laserMoveStepMmEl) return;
				if (laserMoveStepPersistPromise) return laserMoveStepPersistPromise;
				laserMoveStepSyncHoldUntil = Date.now() + LASER_MOVE_INPUT_SYNC_HOLD_MS;
				const run = (async () => {
					const step = getLaserMoveStepMm();
					laserMoveStepMmEl.dataset.lastValid = String(step);
					laserMoveStepMmEl.value = String(step);
					await patchLaserConfig({ laser_move_step_mm: step });
				})();
				laserMoveStepPersistPromise = run;
				try {
					await run;
				} finally {
					laserMoveStepPersistPromise = null;
					laserMoveStepSyncHoldUntil = Date.now() + 800;
				}
			}

			async function persistLaserMoveFeedMmSec() {
				if (!laserMoveFeedMmSecEl) return;
				if (laserMoveFeedPersistPromise) return laserMoveFeedPersistPromise;
				laserMoveFeedSyncHoldUntil = Date.now() + LASER_MOVE_INPUT_SYNC_HOLD_MS;
				const run = (async () => {
					const feed = getLaserMoveFeedMmSec();
					const roundedFeed = Math.round(feed * 10) / 10;
					laserMoveFeedMmSecEl.dataset.lastValid = String(roundedFeed);
					laserMoveFeedMmSecEl.value = String(roundedFeed);
					await patchLaserConfig({ laser_move_feed_mm_sec: roundedFeed });
				})();
				laserMoveFeedPersistPromise = run;
				try {
					await run;
				} finally {
					laserMoveFeedPersistPromise = null;
					laserMoveFeedSyncHoldUntil = Date.now() + 800;
				}
			}

			async function sendLaserJog(direction) {
				const dir = String(direction || '').toLowerCase();
				if (!dir) return;
				const step = getLaserMoveStepMm();
				const feed = getLaserMoveFeedMmSec();
				const jogButtons = [laserJogUpEl, laserJogDownEl, laserJogLeftEl, laserJogRightEl, laserJogHomeEl].filter(Boolean);
				jogButtons.forEach((btn) => { btn.disabled = true; });
				try {
					if (laserJogStatusEl) laserJogStatusEl.textContent = 'Jog: sending ' + dir + '...';
					const res = await api('/api/laser/jog', { direction: dir, step_mm: step, feed_mm_sec: feed, source: 'ui' });
					const deferred = !!res.deferred;
					const queued = Number(res.queue_depth || 0);
					const statusText = deferred
						? ('Jog ' + dir + ' queued (client active), queue=' + queued)
						: ('Jog ' + dir + ' sent, queue=' + queued);
					setStatus(statusText);
					if (laserJogStatusEl) laserJogStatusEl.textContent = 'Jog: ' + statusText;
					await refreshLaserMonitor();
				} catch (err) {
					setStatus('Jog error: ' + err.message);
					if (laserJogStatusEl) laserJogStatusEl.textContent = 'Jog error: ' + err.message;
				} finally {
					jogButtons.forEach((btn) => { btn.disabled = false; });
				}
			}

			async function sendCustomGcodeFromUi() {
				const command = String((laserCustomGcodeEl && laserCustomGcodeEl.value) || '').trim();
				if (!command) {
					setStatus('Enter a G-code command.');
					return;
				}
				if (!laserSendGcodeEl) return;
				laserSendGcodeEl.disabled = true;
				try {
					const res = await api('/api/laser/gcode', { command: command, source: 'ui' });
					const queued = Number(res.queue_depth || 0);
					const deferred = !!res.deferred;
					setStatus('G-code queued' + (deferred ? ' (active client, deferred sending).' : ' and sent.') + ' Queue=' + queued);
					if (laserCustomGcodeEl) laserCustomGcodeEl.value = '';
					await refreshLaserMonitor();
				} catch (err) {
					setStatus('G-code error: ' + err.message);
				} finally {
					laserSendGcodeEl.disabled = false;
				}
			}

			async function clearLaserQueueFromUi() {
				if (!laserClearQueueBtnEl) return;
				laserClearQueueBtnEl.disabled = true;
				try {
					const res = await api('/api/laser/queue/clear', { source: 'ui' });
					const cleared = Number(res.cleared || 0);
					setStatus('Queue cleared: removed ' + cleared + ' command(s).');
					await refreshLaserMonitor();
				} catch (err) {
					setStatus('Clear queue failed: ' + err.message);
				} finally {
					laserClearQueueBtnEl.disabled = false;
				}
			}

			async function persistCustomPositionFromUi() {
				const patch = {
					laser_custom_pos_x_mm: getCustomPositionValue(laserCustomPosXEl),
					laser_custom_pos_y_mm: getCustomPositionValue(laserCustomPosYEl),
					laser_custom_pos_z_mm: getCustomPositionValue(laserCustomPosZEl),
					laser_custom_pos_use_g0: !!(laserCustomPosUseG0El && laserCustomPosUseG0El.checked),
				};
				await patchLaserConfig(patch);
				if (laserCustomPosXEl) laserCustomPosXEl.value = String(patch.laser_custom_pos_x_mm);
				if (laserCustomPosYEl) laserCustomPosYEl.value = String(patch.laser_custom_pos_y_mm);
				if (laserCustomPosZEl) laserCustomPosZEl.value = String(patch.laser_custom_pos_z_mm);
				if (laserCustomPosUseG0El) laserCustomPosUseG0El.checked = !!patch.laser_custom_pos_use_g0;
			}

			async function runCustomPositionFromUi() {
				if (laserGoCustomPosEl) laserGoCustomPosEl.disabled = true;
				try {
					await persistCustomPositionFromUi();
					const res = await api('/api/laser/custom-position', { source: 'ui' });
					const queued = Number(res.queue_depth || 0);
					setStatus('Custom position queued/sent. Queue=' + queued);
					await refreshLaserMonitor();
				} catch (err) {
					setStatus('Custom position error: ' + err.message);
				} finally {
					if (laserGoCustomPosEl) laserGoCustomPosEl.disabled = false;
				}
			}

			async function clearLaserErrorFromUi() {
				if (!laserClearErrorBtnEl) return;
				laserClearErrorBtnEl.disabled = true;
				try {
					await api('/api/laser-monitor/clear-error', {});
					if (laserMiniStatusEl) {
						laserMiniStatusEl.classList.remove('running', 'moving', 'engraving', 'hold', 'door', 'error', 'engrave_complete');
						laserMiniStatusEl.classList.add('idle');
					}
					if (laserMiniStatusTextEl) {
						laserMiniStatusTextEl.textContent = 'Idle';
					}
					setStatus('Laser error/completed cleared.');
					await refreshLaserMonitor();
				} catch (err) {
					setStatus('Clear error failed: ' + err.message);
				} finally {
					laserClearErrorBtnEl.disabled = false;
				}
			}

			async function patchLaserConfig(patch) {
				const res = await api('/api/laser-monitor/config', patch);
				renderLaserMonitor(res);
				return res;
			}

			async function refreshLaserMonitor() {
				const res = await fetch('/api/laser-monitor');
				if (!res.ok) throw new Error('laser monitor error');
				const data = await res.json();
				renderLaserMonitor(data);
				restoreCollapsibleState();
			}

			async function refreshCameraSettings() {
			const res = await fetch('/api/camera/settings');
			if (!res.ok) throw new Error('camera settings error');
			const settings = await res.json();
			renderCameraSettings(settings);
			restoreCollapsibleState();
			}

			const cpuBarEl = document.getElementById('cpuBar');
			const ramBarEl = document.getElementById('ramBar');
			const tempBarEl = document.getElementById('tempBar');
			const cpuValEl = document.getElementById('cpuVal');
			const ramValEl = document.getElementById('ramVal');
			const tempValEl = document.getElementById('tempVal');
			const cameraNoticeEl = document.getElementById('cameraNotice');
			const cpuSparklineEl = document.getElementById('cpuSparkline');
			const cpuSparklineCtx = cpuSparklineEl.getContext('2d');
			const cpuHistory = [];
			const ramHistory = [];
			const tempHistory = [];
			const SYSSTAT_POLL_MS = 2000;
			const GRAPH_WINDOW_MS = 10 * 60 * 1000;
			const GRAPH_POINTS_MAX = Math.floor(GRAPH_WINDOW_MS / SYSSTAT_POLL_MS);

			function pushSystemSample(cpuValue, ramValue, tempValue) {
				cpuHistory.push(cpuValue);
				ramHistory.push(ramValue);
				tempHistory.push(tempValue);
				if (cpuHistory.length > GRAPH_POINTS_MAX) cpuHistory.shift();
				if (ramHistory.length > GRAPH_POINTS_MAX) ramHistory.shift();
				if (tempHistory.length > GRAPH_POINTS_MAX) tempHistory.shift();
				drawCpuSparkline();
			}

			function updateCameraNotice(message, level) {
				if (!message) {
					cameraNoticeEl.style.display = 'none';
					cameraNoticeEl.textContent = '';
					cameraNoticeEl.classList.remove('warn');
					return;
				}
				cameraNoticeEl.textContent = message;
				cameraNoticeEl.style.display = 'block';
				cameraNoticeEl.classList.toggle('warn', (level || '').toLowerCase() === 'warn');
			}

			function drawCpuSparkline() {
				if (!cpuSparklineCtx) return;
				const dpr = window.devicePixelRatio || 1;
				const cssWidth = cpuSparklineEl.clientWidth || 280;
				const cssHeight = cpuSparklineEl.clientHeight || 136;
				const pxWidth = Math.floor(cssWidth * dpr);
				const pxHeight = Math.floor(cssHeight * dpr);
				if (cpuSparklineEl.width !== pxWidth || cpuSparklineEl.height !== pxHeight) {
					cpuSparklineEl.width = pxWidth;
					cpuSparklineEl.height = pxHeight;
				}
				cpuSparklineCtx.setTransform(dpr, 0, 0, dpr, 0, 0);
				cpuSparklineCtx.clearRect(0, 0, cssWidth, cssHeight);
				cpuSparklineCtx.fillStyle = 'rgba(8, 33, 61, 0.28)';
				cpuSparklineCtx.fillRect(0, 0, cssWidth, cssHeight);

				const leftPad = 26;
				const rightPad = 28;
				const topPad = 8;
				const bottomPad = 16;
				const innerW = Math.max(1, cssWidth - leftPad - rightPad);
				const innerH = Math.max(1, cssHeight - topPad - bottomPad);

				cpuSparklineCtx.strokeStyle = 'rgba(214, 236, 255, 0.15)';
				cpuSparklineCtx.lineWidth = 1;
				[0, 50, 100].forEach((tick) => {
					const y = topPad + (1 - tick / 100) * innerH;
					cpuSparklineCtx.beginPath();
					cpuSparklineCtx.moveTo(leftPad, y);
					cpuSparklineCtx.lineTo(cssWidth - rightPad, y);
					cpuSparklineCtx.stroke();
				});

				cpuSparklineCtx.fillStyle = 'rgba(207, 230, 250, 0.72)';
				cpuSparklineCtx.font = '10px Segoe UI, sans-serif';
				cpuSparklineCtx.textAlign = 'right';
				cpuSparklineCtx.fillText('100%', leftPad - 3, topPad + 3);
				cpuSparklineCtx.fillText('50', leftPad - 3, topPad + innerH / 2 + 3);
				cpuSparklineCtx.fillText('0', leftPad - 3, topPad + innerH + 3);

				cpuSparklineCtx.textAlign = 'left';
				cpuSparklineCtx.fillStyle = 'rgba(255, 185, 126, 0.88)';
				cpuSparklineCtx.fillText('90°C', cssWidth - rightPad + 3, topPad + 3);
				cpuSparklineCtx.fillText('60', cssWidth - rightPad + 3, topPad + innerH / 2 + 3);
				cpuSparklineCtx.fillText('30', cssWidth - rightPad + 3, topPad + innerH + 3);

				cpuSparklineCtx.fillStyle = 'rgba(207, 230, 250, 0.72)';
				cpuSparklineCtx.textAlign = 'left';
				cpuSparklineCtx.fillText('-10m', leftPad, cssHeight - 3);
				cpuSparklineCtx.textAlign = 'center';
				cpuSparklineCtx.fillText('-5m', leftPad + innerW / 2, cssHeight - 3);
				cpuSparklineCtx.textAlign = 'right';
				cpuSparklineCtx.fillText('now', cssWidth - rightPad, cssHeight - 3);

				if (cpuHistory.length < 2) return;

				const step = innerW / Math.max(1, GRAPH_POINTS_MAX - 1);

				function drawSeries(series, color, minValue, maxValue) {
					let started = false;
					cpuSparklineCtx.beginPath();
					for (let i = 0; i < series.length; i++) {
						if (series[i] === null || series[i] === undefined) continue;
						const value = Math.min(maxValue, Math.max(minValue, series[i]));
						const norm = (value - minValue) / (maxValue - minValue);
						const x = leftPad + i * step;
						const y = topPad + (1 - norm) * innerH;
						if (!started) {
							cpuSparklineCtx.moveTo(x, y);
							started = true;
						} else {
							cpuSparklineCtx.lineTo(x, y);
						}
					}
					if (!started) return;
					cpuSparklineCtx.strokeStyle = color;
					cpuSparklineCtx.lineWidth = 1.8;
					cpuSparklineCtx.lineJoin = 'round';
					cpuSparklineCtx.lineCap = 'round';
					cpuSparklineCtx.stroke();
				}

				drawSeries(cpuHistory, '#74c2ff', 0, 100);
				drawSeries(ramHistory, '#c9b0ff', 0, 100);
				drawSeries(tempHistory, '#ffb570', 30, 90);

				cpuSparklineCtx.font = '10px Segoe UI, sans-serif';
			}

			window.addEventListener('resize', drawCpuSparkline);
			window.addEventListener('resize', () => {
				if (videoSettingsModalEl && videoSettingsModalEl.classList.contains('open')) {
					positionDraggableModal(videoSettingsModalEl, videoSettingsCardEl);
				}
				if (screenshotSettingsModalEl && screenshotSettingsModalEl.classList.contains('open')) {
					positionDraggableModal(screenshotSettingsModalEl, screenshotSettingsCardEl);
				}
				if (ledPreviewModalEl && ledPreviewModalEl.classList.contains('open')) {
					positionDraggableModal(ledPreviewModalEl, ledPreviewCardEl);
				}
				if (buttonsSettingsModalEl && buttonsSettingsModalEl.classList.contains('open')) {
					positionDraggableModal(buttonsSettingsModalEl, buttonsSettingsCardEl);
				}
				if (airAssistModalEl && airAssistModalEl.classList.contains('open')) {
					positionDraggableModal(airAssistModalEl, airAssistCardEl);
				}
				if (grblCommandsModalEl && grblCommandsModalEl.classList.contains('open')) {
					positionDraggableModal(grblCommandsModalEl, grblCommandsCardEl);
				}
			});
			initModalDrag(videoSettingsModalEl, videoSettingsCardEl, videoSettingsDragHandleEl);
			initModalDrag(settingsMenuModalEl, settingsMenuCardEl, settingsMenuDragHandleEl);
			initModalDrag(screenshotSettingsModalEl, screenshotSettingsCardEl, screenshotSettingsDragHandleEl);
			initModalDrag(ledPreviewModalEl, ledPreviewCardEl, ledPreviewDragHandleEl);
			initModalDrag(buttonsSettingsModalEl, buttonsSettingsCardEl, buttonsSettingsDragHandleEl);
			initModalDrag(airAssistModalEl, airAssistCardEl, airAssistDragHandleEl);
			initModalDrag(grblCommandsModalEl, grblCommandsCardEl, grblCommandsDragHandleEl);

			async function fetchSystemStats() {
			try {
				const res = await fetch('/api/system/stats');
				if (!res.ok) return;
				const s = await res.json();
				let cpuSample = null;
				let ramSample = null;
				let tempSample = null;
				if (s.cpu_percent !== null && s.cpu_percent !== undefined) {
					cpuBarEl.style.width = s.cpu_percent + '%';
					cpuValEl.textContent = s.cpu_percent + '%';
					cpuSample = s.cpu_percent;
				}
				if (s.ram_percent !== null && s.ram_percent !== undefined) {
					ramBarEl.style.width = s.ram_percent + '%';
					const ramUsed = s.ram_used_mb !== undefined ? Math.round(s.ram_used_mb) + 'M' : s.ram_percent + '%';
					ramValEl.textContent = ramUsed;
					ramSample = s.ram_percent;
				}
				if (s.cpu_temp !== null && s.cpu_temp !== undefined) {
					const pct = Math.min(Math.max((s.cpu_temp - 30) / 50 * 100, 0), 100);
					tempBarEl.style.width = pct + '%';
					tempValEl.textContent = s.cpu_temp + '\u00b0C';
					tempSample = s.cpu_temp;
				}
				updateStreamBusyState(s.camera_owner_mode);
				updateCameraNotice(s.camera_notice, s.camera_notice_level);
				if (cpuSample !== null || ramSample !== null || tempSample !== null) {
					pushSystemSample(cpuSample, ramSample, tempSample);
				}
			} catch (e) {}
			}

			fetchSystemStats();
			setInterval(fetchSystemStats, SYSSTAT_POLL_MS);

			let updatingBrightnessFromCode = false;

			async function refresh() {
			const res = await fetch('/api/state');
			const state = await res.json();
			effectEl.value = state.effect;
			colorModeEl.value = state.color_mode;
			presetModeEl.value = state.preset || 'none';
			presetIntensityEl.value = (state.preset_intensity !== undefined) ? state.preset_intensity : 100;
			updatePresetIntensityValue(presetIntensityEl.value);
			updatingBrightnessFromCode = true;
			brightnessEl.value = state.brightness;
			updatingBrightnessFromCode = false;
			updateBrightnessValue(state.brightness);
			updateLedState(state.is_on);
			const stateHex = rgbToHex(state.custom_color[0], state.custom_color[1], state.custom_color[2]);
			if (!customColorDirty) {
				selectedCustomHex = stateHex;
				customColorEl.value = stateHex;
			}
			updateCustomColorPreview(customColorDirty ? selectedCustomHex : stateHex);
			setStatus('Brightness: ' + parseFloat(state.brightness).toFixed(2));
			if (state.airassist !== undefined && typeof window.syncAirAssistState === 'function') {
				window.syncAirAssistState(state.airassist);
			}
			restoreCollapsibleState();
			}

			effectEl.addEventListener('change', async () => {
			await api('/api/effect', { effect: effectEl.value });
			await refresh();
			});

			colorModeEl.addEventListener('change', async () => {
			await api('/api/color-mode', { color_mode: colorModeEl.value });
			await refresh();
			});

			presetModeEl.addEventListener('change', async () => {
			await api('/api/preset', { preset: presetModeEl.value });
			await refresh();
			});

			presetIntensityEl.addEventListener('input', async () => {
			updatePresetIntensityValue(presetIntensityEl.value);
			await api('/api/preset-intensity', { intensity: parseInt(presetIntensityEl.value, 10) });
			});

			ledDefaultBrightnessEl.addEventListener('input', async () => {
				updateDefaultBrightnessValue(ledDefaultBrightnessEl.value);
			});

			ledDefaultBrightnessEl.addEventListener('change', async () => {
				try {
					await patchLaserConfig({ led_default_brightness: parseFloat(ledDefaultBrightnessEl.value) });
					setStatus('Led default brightness updated.');
				} catch (err) {
					await refreshLaserMonitor();
					setStatus('Led default brightness error: ' + err.message);
				}
			});

			startupShutdownBrightnessEl.addEventListener('input', async () => {
				updateStartupShutdownBrightnessValue(startupShutdownBrightnessEl.value);
			});

			startupShutdownBrightnessEl.addEventListener('change', async () => {
				try {
					await patchLaserConfig({ led_startup_shutdown_brightness: parseFloat(startupShutdownBrightnessEl.value) });
					setStatus('Startup/shutdown brightness updated.');
				} catch (err) {
					await refreshLaserMonitor();
					setStatus('Startup/shutdown brightness error: ' + err.message);
				}
			});

			brightnessEl.addEventListener('input', async () => {
				if (updatingBrightnessFromCode) return;
				await api('/api/brightness', { brightness: parseFloat(brightnessEl.value) });
				updateBrightnessValue(brightnessEl.value);
				setStatus('Brightness: ' + parseFloat(brightnessEl.value).toFixed(2));
			});

			customColorEl.addEventListener('input', () => {
				selectedCustomHex = normalizeHex(customColorEl.value);
				customColorEl.value = selectedCustomHex;
				customColorDirty = true;
				updateCustomColorPreview(selectedCustomHex);
				scheduleCustomColorApply(false);
			});

			customColorEl.addEventListener('change', () => {
				selectedCustomHex = normalizeHex(customColorEl.value);
				customColorEl.value = selectedCustomHex;
				customColorDirty = true;
				updateCustomColorPreview(selectedCustomHex);
				scheduleCustomColorApply(true);
			});

			togglePowerEl.addEventListener('click', async () => {
			if (ledToggleBusy) return;
			const previousIsOn = togglePowerEl.getAttribute('aria-pressed') === 'true';
			ledToggleBusy = true;
			togglePowerEl.disabled = true;
			updateLedState(!previousIsOn);
			try {
				await api('/api/power');
				await refresh();
			} catch (err) {
				updateLedState(previousIsOn);
				setStatus('LED toggle error: ' + err.message);
			} finally {
				ledToggleBusy = false;
				togglePowerEl.disabled = false;
			}
			});

			document.getElementById('shutdownPi').addEventListener('click', async () => {
			if (!confirm('Confirm Raspberry shutdown?')) return;
			await api('/api/shutdown', {});
			setStatus('Shutdown started...');
			});

			document.getElementById('rebootPi').addEventListener('click', async () => {
			if (!confirm('Confirm Raspberry reboot?')) return;
			await api('/api/reboot', {});
			setStatus('Reboot started...');
			});

			takePhotoBtn.addEventListener('click', async () => {
			takePhotoBtn.disabled = true;
			setPhotoStatus('');
			photoPlaceholderTextEl.textContent = 'Capturing...';
			photoPlaceholderEl.style.display = 'flex';
			capturedPhotoEl.style.display = 'none';
			const previousStreamSrc = liveStreamEl.src;
			liveStreamEl.src = '';
			try {
				const res = await fetch('/snapshot');
				if (!res.ok) throw new Error('HTTP ' + res.status);
				const blob = await res.blob();
				if (prevBlobUrl) { URL.revokeObjectURL(prevBlobUrl); }
				prevBlobUrl = URL.createObjectURL(blob);
				capturedPhotoEl.src = prevBlobUrl;
							photoPlaceholderEl.style.display = 'none';
							capturedPhotoEl.style.display = 'block';
				photoTaken = true;
				showRightPanel('snapshot');
				setPhotoStatus('Photo captured.');
			} catch (err) {
				photoPlaceholderTextEl.textContent = 'Capture error';
				setPhotoStatus('Error: ' + err.message);
			} finally {
				if (livePanelEl.classList.contains('active')) {
					startLiveStream(true);
				} else {
					liveStreamEl.src = previousStreamSrc;
				}
				takePhotoBtn.disabled = false;
			}
			});

			document.getElementById('openDirectSnap').addEventListener('click', () => {
			window.open('/snapshot', '_blank');
			});

			function openVideoSettingsModal() {
			openModal(videoSettingsModalEl);
			}

			function openScreenshotSettingsModal() {
			openModal(screenshotSettingsModalEl);
			}

			function openLedPreviewModal() {
			openModal(ledPreviewModalEl);
			}

			async function openButtonsSettingsModal() {
			buttonsSettingsStatusEl.textContent = '';
			await refreshLaserMonitor();
			openModal(buttonsSettingsModalEl);
			}

			function openAirAssistModal() {
			openModal(airAssistModalEl);
			loadAirAssistState();
			}

			if (openSettingsMenuEl) {
			openSettingsMenuEl.addEventListener('click', () => {
				openModal(settingsMenuModalEl);
			});
			}

			const openVideoSettingsEl = document.getElementById('openVideoSettings');
			if (openVideoSettingsEl) {
			openVideoSettingsEl.addEventListener('click', () => {
				openVideoSettingsModal();
			});
			}

			const openScreenshotSettingsEl = document.getElementById('openScreenshotSettings');
			if (openScreenshotSettingsEl) {
			openScreenshotSettingsEl.addEventListener('click', () => {
				openScreenshotSettingsModal();
			});
			}

			const openV4l2SettingsEl = document.getElementById('openV4l2Settings');
			if (openV4l2SettingsEl) {
			openV4l2SettingsEl.addEventListener('click', () => {
				window.location.href = '/camera-v4l2';
			});
			}

			const openLedPreviewEl = document.getElementById('openLedPreview');
			if (openLedPreviewEl) {
			openLedPreviewEl.addEventListener('click', () => {
				openLedPreviewModal();
			});
			}

			if (openButtonsSettingsEl) {
			openButtonsSettingsEl.addEventListener('click', async () => {
				await openButtonsSettingsModal();
			});
			}

			document.getElementById('settingsMenuVideoBtn').addEventListener('click', () => {
			closeModal(settingsMenuModalEl);
			openVideoSettingsModal();
			});

			document.getElementById('settingsMenuScreenshotBtn').addEventListener('click', () => {
			closeModal(settingsMenuModalEl);
			openScreenshotSettingsModal();
			});

			document.getElementById('settingsMenuV4l2Btn').addEventListener('click', () => {
			closeModal(settingsMenuModalEl);
			window.location.href = '/camera-v4l2';
			});

			document.getElementById('settingsMenuLedBtn').addEventListener('click', () => {
			closeModal(settingsMenuModalEl);
			openLedPreviewModal();
			});

			document.getElementById('settingsMenuButtonsBtn').addEventListener('click', async () => {
			closeModal(settingsMenuModalEl);
			await openButtonsSettingsModal();
			});

			document.getElementById('settingsMenuAirAssistBtn').addEventListener('click', () => {
			closeModal(settingsMenuModalEl);
			openAirAssistModal();
			});

			document.getElementById('settingsMenuGrblBtn').addEventListener('click', () => {
			closeModal(settingsMenuModalEl);
			openModal(grblCommandsModalEl);
			});

			document.getElementById('closeSettingsMenu').addEventListener('click', () => {
			closeModal(settingsMenuModalEl);
			});

			document.getElementById('closeVideoSettings').addEventListener('click', () => {
			closeModal(videoSettingsModalEl);
			});

			document.getElementById('closeScreenshotSettings').addEventListener('click', () => {
			closeModal(screenshotSettingsModalEl);
			});

			document.getElementById('closeV4l2Settings').addEventListener('click', () => {
			closeModal(v4l2SettingsModalEl);
			});

			document.getElementById('closeLedPreview').addEventListener('click', () => {
			closeModal(ledPreviewModalEl);
			});

			document.getElementById('closeButtonsSettings').addEventListener('click', () => {
			closeModal(buttonsSettingsModalEl);
			});

			const openAirAssistEl = document.getElementById('openAirAssist');
			if (openAirAssistEl) {
			openAirAssistEl.addEventListener('click', () => {
				openAirAssistModal();
			});
			}

			document.getElementById('closeAirAssist').addEventListener('click', () => {
			closeModal(airAssistModalEl);
			});

			document.getElementById('closeGrblCommands').addEventListener('click', () => {
			closeModal(grblCommandsModalEl);
			});

			airAssistModalEl.addEventListener('click', (ev) => {
			if (ev.target === airAssistModalEl) closeModal(airAssistModalEl);
			});

			grblCommandsModalEl.addEventListener('click', (ev) => {
			if (ev.target === grblCommandsModalEl) closeModal(grblCommandsModalEl);
			});

			(function() {
				const toggleBtn = document.getElementById('airAssistToggleBtn');
				const speedSlider = document.getElementById('airAssistSpeedSlider');
				const speedValEl = document.getElementById('airAssistSpeedVal');
				const autoBtn = document.getElementById('airAssistAutoBtn');
				const quickToggleBtn = document.getElementById('quickAirAssistToggle');
				const quickAutoBtn = document.getElementById('quickAirAssistAutoToggle');
				const quickSpeedSlider = document.getElementById('quickAirAssistSpeed');
				const quickSpeedValEl = document.getElementById('quickAirAssistSpeedVal');
				const quickAaMinPwmEl = document.getElementById('quickAaMinPwm');
				const quickAaMinPwmValEl = document.getElementById('quickAaMinPwmVal');
				const aaRangeMinEl = document.getElementById('aaRangeMin');
				const aaRangeMaxEl = document.getElementById('aaRangeMax');
				const aaMinPwmEl = document.getElementById('aaMinPwm');
				const aaRangeFillEl = document.getElementById('aaRangeFill');
				const aaRangeMinValEl = document.getElementById('aaRangeMinVal');
				const aaRangeMaxValEl = document.getElementById('aaRangeMaxVal');
				const aaMinPwmValEl = document.getElementById('aaMinPwmVal');
				const aaMinPwmHintValEl = document.getElementById('aaMinPwmHintVal');
				const statusEl = document.getElementById('airAssistStatus');
				const listenEventsBtn = document.getElementById('airAssistListenEventsBtn');
				let airAssistEnabled = false;
				let autoModeEnabled = false;
				let listenAirAssistEvents = false;
				let speedDebounceTimer = null;
				let autoRangeDebounceTimer = null;

				// Aggiorna lo stato AirAssist nel riquadro camera
				function updateAirAssistStatusText(enabled, auto) {
					const el = document.getElementById('airAssistStatusText');
					if (!el) return;
					let txt = enabled ? 'ON' : 'OFF';
					txt += auto ? ' (Auto)' : ' (Manual)';
					el.textContent = txt;
				}

				function updateToggleBtn(enabled) {
					airAssistEnabled = !!enabled;
					updateAirAssistStatusText(airAssistEnabled, autoModeEnabled);
					if (airAssistEnabled) {
						toggleBtn.textContent = '\u25CF ON';
						toggleBtn.style.background = 'linear-gradient(120deg, #1a7a3a, #2ecc71)';
						toggleBtn.style.color = '#fff';
						if (quickToggleBtn) {
							quickToggleBtn.textContent = 'ON';
							quickToggleBtn.classList.add('on');
							quickToggleBtn.setAttribute('aria-pressed', 'true');
						}
					} else {
						toggleBtn.textContent = '\u25CB OFF';
						toggleBtn.style.background = '';
						toggleBtn.style.color = '';
						if (quickToggleBtn) {
							quickToggleBtn.textContent = 'OFF';
							quickToggleBtn.classList.remove('on');
							quickToggleBtn.setAttribute('aria-pressed', 'false');
						}
					}
				}

				function updateAutoBtn(enabled) {
					autoModeEnabled = !!enabled;
					updateAirAssistStatusText(airAssistEnabled, autoModeEnabled);
					if (autoModeEnabled) {
						autoBtn.textContent = '\u25CF ON';
						autoBtn.style.background = 'linear-gradient(120deg, #1a4a7a, #2e9bcc)';
						autoBtn.style.color = '#fff';
						if (quickAutoBtn) {
							quickAutoBtn.textContent = 'ON';
							quickAutoBtn.classList.add('on');
							quickAutoBtn.setAttribute('aria-pressed', 'true');
						}
					} else {
						autoBtn.textContent = '\u25CB OFF';
						autoBtn.style.background = '';
						autoBtn.style.color = '';
						if (quickAutoBtn) {
							quickAutoBtn.textContent = 'OFF';
							quickAutoBtn.classList.remove('on');
							quickAutoBtn.setAttribute('aria-pressed', 'false');
						}
					}
				}

				function updateListenEventsBtn(enabled) {
					listenAirAssistEvents = !!enabled;
					if (listenAirAssistEvents) {
						listenEventsBtn.textContent = '\u25CF ON';
						listenEventsBtn.style.background = 'linear-gradient(120deg, #4a3a1a, #cc9b2e)';
						listenEventsBtn.style.color = '#fff';
					} else {
						listenEventsBtn.textContent = '\u25CB OFF';
						listenEventsBtn.style.background = '';
						listenEventsBtn.style.color = '';
					}
				}

				function updateSpeedControls(speed) {
					speedSlider.value = speed;
					speedValEl.textContent = speed + '%';
					if (quickSpeedSlider) quickSpeedSlider.value = speed;
					if (quickSpeedValEl) quickSpeedValEl.textContent = speed + '%';
				}

				function updateRangeFill() {
					const minVal = parseInt(aaRangeMinEl.value, 10);
					const maxVal = parseInt(aaRangeMaxEl.value, 10);
					const minPwm = parseInt(aaMinPwmEl.value, 10);
					const trackInsetPx = 2;
					const span = Math.max(0, maxVal - minVal);
					aaRangeFillEl.style.left = `calc(${minVal}% + ${trackInsetPx}px)`;
					aaRangeFillEl.style.width = span > 0 ? `calc(${span}% - ${trackInsetPx * 2}px)` : '0';
					aaRangeMinValEl.textContent = minVal + '%';
					aaRangeMaxValEl.textContent = maxVal + '%';
					aaMinPwmValEl.textContent = minPwm + '%';
					aaMinPwmHintValEl.textContent = minPwm + '%';
					if (quickAaMinPwmEl) quickAaMinPwmEl.value = minPwm;
					if (quickAaMinPwmValEl) quickAaMinPwmValEl.textContent = minPwm + '%';
				}

				window.syncAirAssistState = function(aa) {
					if (aa === undefined || aa === null) return;
					updateToggleBtn(aa.enabled);
					updateAutoBtn(aa.auto_mode);
					updateSpeedControls(aa.speed);
					if (aa.auto_range_min !== undefined) aaRangeMinEl.value = aa.auto_range_min;
					if (aa.auto_range_max !== undefined) aaRangeMaxEl.value = aa.auto_range_max;
					if (aa.auto_min_pwm !== undefined) aaMinPwmEl.value = aa.auto_min_pwm;
					updateRangeFill();
				};

				window.loadAirAssistState = async function() {
					statusEl.textContent = 'Loading...';
					try {
						const res = await fetch('/api/airassist');
						if (!res.ok) throw new Error('HTTP ' + res.status);
						const data = await res.json();
						updateToggleBtn(data.enabled);
						updateSpeedControls(data.speed);
						updateAutoBtn(data.auto_mode);
						updateListenEventsBtn(data.listen_events);
						aaRangeMinEl.value = data.auto_range_min !== undefined ? data.auto_range_min : 0;
						aaRangeMaxEl.value = data.auto_range_max !== undefined ? data.auto_range_max : 100;
						aaMinPwmEl.value = data.auto_min_pwm !== undefined ? data.auto_min_pwm : 0;
						updateRangeFill();
						statusEl.textContent = '';
					} catch (err) {
						statusEl.textContent = 'Failed to load state.';
					}
				};

				async function setAirAssistPower(newEnabled) {
					// Interlock: turning ON manual disables auto first
					if (newEnabled && autoModeEnabled) {
						await fetch('/api/airassist/auto', {
							method: 'POST',
							headers: { 'Content-Type': 'application/json' },
							body: JSON.stringify({ auto_mode: false }),
						});
						updateAutoBtn(false);
					}
					const res = await fetch('/api/airassist/power', {
						method: 'POST',
						headers: { 'Content-Type': 'application/json' },
						body: JSON.stringify({ enabled: newEnabled }),
					});
					if (!res.ok) throw new Error('HTTP ' + res.status);
					const data = await res.json();
					updateToggleBtn(data.enabled);
					statusEl.textContent = data.enabled ? 'Air Assist ON.' : 'Air Assist OFF.';
				}

				async function setAirAssistAuto(newAuto) {
					// Interlock: turning ON auto disables manual first
					if (newAuto && airAssistEnabled) {
						await fetch('/api/airassist/power', {
							method: 'POST',
							headers: { 'Content-Type': 'application/json' },
							body: JSON.stringify({ enabled: false }),
						});
						updateToggleBtn(false);
					}
					const res = await fetch('/api/airassist/auto', {
						method: 'POST',
						headers: { 'Content-Type': 'application/json' },
						body: JSON.stringify({ auto_mode: newAuto }),
					});
					if (!res.ok) throw new Error('HTTP ' + res.status);
					const data = await res.json();
					updateAutoBtn(data.auto_mode);
					statusEl.textContent = data.auto_mode ? 'Auto mode ON.' : 'Auto mode OFF.';
				}

				async function setAirAssistSpeed(speedValue) {
					const res = await fetch('/api/airassist/speed', {
						method: 'POST',
						headers: { 'Content-Type': 'application/json' },
						body: JSON.stringify({ speed: parseInt(speedValue, 10) }),
					});
					if (!res.ok) throw new Error('HTTP ' + res.status);
					const data = await res.json();
					updateSpeedControls(data.speed);
					statusEl.textContent = 'Speed set to ' + data.speed + '%.';
				}

				async function setListenAirAssistEvents(newListen) {
					const res = await fetch('/api/airassist/listen_events', {
						method: 'POST',
						headers: { 'Content-Type': 'application/json' },
						body: JSON.stringify({ listen_events: !!newListen }),
					});
					if (!res.ok) throw new Error('HTTP ' + res.status);
					const data = await res.json();
					updateListenEventsBtn(data.listen_events);
					statusEl.textContent = data.listen_events ? 'Listening to AirAssist events.' : 'Not listening to AirAssist events.';
				}

				toggleBtn.addEventListener('click', async () => {
					const newEnabled = !airAssistEnabled;
					toggleBtn.disabled = true;
					if (quickToggleBtn) quickToggleBtn.disabled = true;
					try {
						await setAirAssistPower(newEnabled);
					} catch (err) {
						statusEl.textContent = 'Power toggle failed.';
					} finally {
						toggleBtn.disabled = false;
						if (quickToggleBtn) quickToggleBtn.disabled = false;
					}
				});

				if (quickToggleBtn) {
					quickToggleBtn.addEventListener('click', async () => {
						const newEnabled = !airAssistEnabled;
						quickToggleBtn.disabled = true;
						toggleBtn.disabled = true;
						try {
							await setAirAssistPower(newEnabled);
						} catch (err) {
							statusEl.textContent = 'Power toggle failed.';
						} finally {
							quickToggleBtn.disabled = false;
							toggleBtn.disabled = false;
						}
					});
				}

				speedSlider.addEventListener('input', () => {
					updateSpeedControls(parseInt(speedSlider.value, 10));
					if (speedDebounceTimer) clearTimeout(speedDebounceTimer);
					speedDebounceTimer = setTimeout(async () => {
						try {
							await setAirAssistSpeed(speedSlider.value);
						} catch (err) {
							statusEl.textContent = 'Speed update failed.';
						}
					}, 200);
				});

				if (quickSpeedSlider) {
					quickSpeedSlider.addEventListener('input', () => {
						updateSpeedControls(parseInt(quickSpeedSlider.value, 10));
						if (speedDebounceTimer) clearTimeout(speedDebounceTimer);
						speedDebounceTimer = setTimeout(async () => {
							try {
								await setAirAssistSpeed(quickSpeedSlider.value);
							} catch (err) {
								statusEl.textContent = 'Speed update failed.';
							}
						}, 200);
					});
				}

				autoBtn.addEventListener('click', async () => {
					const newAuto = !autoModeEnabled;
					autoBtn.disabled = true;
					if (quickAutoBtn) quickAutoBtn.disabled = true;
					try {
						await setAirAssistAuto(newAuto);
					} catch (err) {
						statusEl.textContent = 'Auto mode toggle failed.';
					} finally {
						autoBtn.disabled = false;
						if (quickAutoBtn) quickAutoBtn.disabled = false;
					}
				});

				if (quickAutoBtn) {
					quickAutoBtn.addEventListener('click', async () => {
						const newAuto = !autoModeEnabled;
						quickAutoBtn.disabled = true;
						autoBtn.disabled = true;
						try {
							await setAirAssistAuto(newAuto);
						} catch (err) {
							statusEl.textContent = 'Auto mode toggle failed.';
						} finally {
							quickAutoBtn.disabled = false;
							autoBtn.disabled = false;
						}
					});
				}

				listenEventsBtn.addEventListener('click', async () => {
					const newListen = !listenAirAssistEvents;
					listenEventsBtn.disabled = true;
					try {
						await setListenAirAssistEvents(newListen);
					} catch (err) {
						statusEl.textContent = 'Failed to toggle listen events.';
					} finally {
						listenEventsBtn.disabled = false;
					}
				});

				function postAutoRange() {
					if (autoRangeDebounceTimer) clearTimeout(autoRangeDebounceTimer);
					autoRangeDebounceTimer = setTimeout(async () => {
						const minVal = parseInt(aaRangeMinEl.value, 10);
						const maxVal = parseInt(aaRangeMaxEl.value, 10);
						const minPwmVal = parseInt(aaMinPwmEl.value, 10);
						try {
							const res = await fetch('/api/airassist/auto', {
								method: 'POST',
								headers: { 'Content-Type': 'application/json' },
								body: JSON.stringify({ auto_range_min: minVal, auto_range_max: maxVal, auto_min_pwm: minPwmVal }),
							});
							if (!res.ok) throw new Error('HTTP ' + res.status);
							statusEl.textContent = 'Range: ' + minVal + '% \u2192 ' + maxVal + '%, Min PWM ' + minPwmVal + '%.';
						} catch (err) {
							statusEl.textContent = 'Range update failed.';
						}
					}, 300);
				}

				aaRangeMinEl.addEventListener('input', () => {
					if (parseInt(aaRangeMinEl.value, 10) >= parseInt(aaRangeMaxEl.value, 10)) {
						aaRangeMinEl.value = parseInt(aaRangeMaxEl.value, 10) - 1;
					}
					updateRangeFill();
					postAutoRange();
				});

				aaRangeMaxEl.addEventListener('input', () => {
					if (parseInt(aaRangeMaxEl.value, 10) <= parseInt(aaRangeMinEl.value, 10)) {
						aaRangeMaxEl.value = parseInt(aaRangeMinEl.value, 10) + 1;
					}
					updateRangeFill();
					postAutoRange();
				});

				aaMinPwmEl.addEventListener('input', () => {
					updateRangeFill();
					postAutoRange();
				});

				if (quickAaMinPwmEl) {
					quickAaMinPwmEl.addEventListener('input', () => {
						aaMinPwmEl.value = quickAaMinPwmEl.value;
						updateRangeFill();
						postAutoRange();
					});
				}



				updateRangeFill();
			})();

			v4l2SettingsModalEl.addEventListener('click', (ev) => {
			if (ev.target === v4l2SettingsModalEl) closeModal(v4l2SettingsModalEl);
			});

			settingsMenuModalEl.addEventListener('click', (ev) => {
			if (ev.target === settingsMenuModalEl) closeModal(settingsMenuModalEl);
			});

			ledPreviewModalEl.addEventListener('click', (ev) => {
			if (ev.target === ledPreviewModalEl) closeModal(ledPreviewModalEl);
			});

			buttonsSettingsModalEl.addEventListener('click', (ev) => {
			if (ev.target === buttonsSettingsModalEl) closeModal(buttonsSettingsModalEl);
			});

			modePressCountSelectEl.addEventListener('change', () => {
				const previousPressKey = modePressCountCurrentKey;
				updateModeProfileFromInputs(previousPressKey);
				modePressCountCurrentKey = String(modePressCountSelectEl.value || '1');
				renderModeProfileForSelectedPress();
			});
			modeEntryModeSelectEl.addEventListener('change', updateModeProfileFromInputs);
			modeLedEffectSelectEl.addEventListener('change', updateModeProfileFromInputs);
			modeLedColorSelectEl.addEventListener('change', updateModeProfileFromInputs);
			modeLedSingleActionSelectEl.addEventListener('change', updateModeProfileFromInputs);
			modePowerSingleActionSelectEl.addEventListener('change', updateModeProfileFromInputs);

			document.getElementById('saveButtonsSettings').addEventListener('click', async () => {
				buttonsSettingsStatusEl.textContent = 'Saving buttons settings...';
				try {
					const patch = collectButtonsSettingsPatch();
					await patchLaserConfig(patch);
					buttonsSettingsStatusEl.textContent = 'Buttons settings saved.';
					setStatus('Buttons settings updated.');
					setTimeout(() => closeModal(buttonsSettingsModalEl), 600);
				} catch (err) {
					buttonsSettingsStatusEl.textContent = 'Error: ' + err.message;
				}
			});

			document.getElementById('saveV4l2Settings').addEventListener('click', async () => {
			v4l2SettingsStatusEl.textContent = 'Applying settings...';
			try {
				const res = await api('/api/camera/settings/v4l2', {
					horizontal_flip: v4l2HFlipEl.checked ? 1 : 0,
					vertical_flip: v4l2VFlipEl.checked ? 1 : 0,
					compression_quality: parseInt(v4l2QualityEl.value),
				});
				renderCameraSettings(res);
				v4l2SettingsStatusEl.textContent = 'Settings applied.';
				setTimeout(() => closeModal(v4l2SettingsModalEl), 800);
			} catch (err) {
				v4l2SettingsStatusEl.textContent = 'Error: ' + err.message;
			}
			});

			document.getElementById('saveVideoSettings').addEventListener('click', async () => {
			const resolution = videoResolutionInputEl.value.trim();
			const fps = parseInt(videoFpsInputEl.value, 10);
			const payload = {};
			if (resolution) payload.resolution = resolution;
			if (!isNaN(fps)) payload.fps = fps;
			videoSettingsStatusEl.textContent = 'Updating stream settings...';
			try {
				const res = await api('/api/camera/settings/stream', payload);
				renderCameraSettings(res);
				videoSettingsStatusEl.textContent = 'Settings applied.';
				setTimeout(() => closeModal(videoSettingsModalEl), 800);
			} catch (err) {
				videoSettingsStatusEl.textContent = 'Error: ' + err.message;
			}
			});

			document.getElementById('saveScreenshotResolution').addEventListener('click', async () => {
			const resolution = screenshotResolutionInputEl.value.trim();
			try {
				const res = await api('/api/camera/settings/screenshot', { resolution: resolution });
				renderCameraSettings(res);
				closeModal(screenshotSettingsModalEl);
				setPhotoStatus('Screenshot resolution saved.');
			} catch (err) {
				setPhotoStatus('Screenshot update error: ' + err.message);
			}
			});

			document.getElementById('saveStreamHdSettings').addEventListener('click', async () => {
			const intervalSeconds = parseInt(streamHdIntervalInputEl.value, 10);
			if (isNaN(intervalSeconds) || intervalSeconds < 1 || intervalSeconds > 60) {
				setPhotoStatus('Invalid StreamHD value: use 1-60 seconds.');
				return;
			}
			try {
				const res = await api('/api/camera/settings/streamhd', { interval_seconds: intervalSeconds });
				renderCameraSettings(res);
				setPhotoStatus('StreamHD interval updated.');
			} catch (err) {
				setPhotoStatus('StreamHD update error: ' + err.message);
			}
			});

			videoSettingsModalEl.addEventListener('click', (ev) => {
			if (ev.target === videoSettingsModalEl) closeModal(videoSettingsModalEl);
			});

			screenshotSettingsModalEl.addEventListener('click', (ev) => {
			if (ev.target === screenshotSettingsModalEl) closeModal(screenshotSettingsModalEl);
			});

			videoResolutionSelectEl.addEventListener('change', () => {
			videoResolutionInputEl.value = videoResolutionSelectEl.value;
			});

			videoFpsSelectEl.addEventListener('change', () => {
			videoFpsInputEl.value = videoFpsSelectEl.value;
			});

			streamHdIntervalSelectEl.addEventListener('change', () => {
			streamHdIntervalInputEl.value = streamHdIntervalSelectEl.value;
			});

			screenshotResolutionSelectEl.addEventListener('change', () => {
			screenshotResolutionInputEl.value = screenshotResolutionSelectEl.value;
			});

			mqttImageEnabledEl.addEventListener('change', async () => {
				mqttImageEnabledEl.disabled = true;
				try {
					const res = await api('/api/camera/settings/mqtt-image', { enabled: mqttImageEnabledEl.checked });
					renderCameraSettings(res);
					setStatus(mqttImageEnabledEl.checked ? 'MQTT image feed enabled.' : 'MQTT image feed disabled (save CPU).');
				} catch (err) {
					mqttImageEnabledEl.checked = !mqttImageEnabledEl.checked;
					setStatus('MQTT image toggle error: ' + err.message);
				} finally {
					mqttImageEnabledEl.disabled = false;
				}
			});

			ledOnBootEnabledEl.addEventListener('change', async () => {
				try {
					await patchLaserConfig({ led_on_boot: ledOnBootEnabledEl.checked });
					await refreshLaserMonitor();
					setStatus('LED-on-boot updated.');
				} catch (err) {
					await refreshLaserMonitor();
					setStatus('LED on boot error: ' + err.message);
				}
			});

			serialProxyEnabledEl.addEventListener('change', async () => {
				try {
					await patchLaserConfig({ serial_proxy_enabled: serialProxyEnabledEl.checked });
					await refreshLaserMonitor();
					setStatus(serialProxyEnabledEl.checked ? 'Serial proxy enabled.' : 'Serial proxy disabled.');
				} catch (err) {
					await refreshLaserMonitor();
					setStatus('Serial proxy error: ' + err.message);
				}
			});

			if (passthroughExtendOnRealtimeEl) {
				passthroughExtendOnRealtimeEl.addEventListener('change', async () => {
					try {
						await patchLaserConfig({ passthrough_extend_on_realtime: passthroughExtendOnRealtimeEl.checked });
						await refreshLaserMonitor();
						setStatus('TCP bridge coexistence: ' + (passthroughExtendOnRealtimeEl.checked ? 'enabled' : 'disabled'));
					} catch (err) {
						await refreshLaserMonitor();
						setStatus('Bridge coexistence error: ' + err.message);
					}
				});
			}

			laserLedSyncEnabledEl.addEventListener('change', async () => {
				try {
					await patchLaserConfig({ laser_led_sync_enabled: laserLedSyncEnabledEl.checked });
					await refreshLaserMonitor();
					setStatus('Laser LED sync updated.');
				} catch (err) {
					await refreshLaserMonitor();
					setStatus('Laser LED sync error: ' + err.message);
				}
			});

			if (laserErrorAutoReset10sEl) {
			laserErrorAutoReset10sEl.addEventListener('change', async () => {
				try {
					await patchLaserConfig({ laser_led_error_auto_reset_10s: laserErrorAutoReset10sEl.checked });
					await refreshLaserMonitor();
					setStatus('Error effect auto reset updated.');
				} catch (err) {
					await refreshLaserMonitor();
					setStatus('Error effect auto reset error: ' + err.message);
				}
			});
			}

			laserRunningEffectEl.addEventListener('change', () => patchLaserConfig({ laser_led_running_effect: laserRunningEffectEl.value }).catch((err) => setStatus('Running profile error: ' + err.message)));
			laserRunningColorEl.addEventListener('change', () => patchLaserConfig({ laser_led_running_color_mode: laserRunningColorEl.value }).catch((err) => setStatus('Running profile error: ' + err.message)));
			laserIdleEffectEl.addEventListener('change', () => patchLaserConfig({ laser_led_idle_effect: laserIdleEffectEl.value }).catch((err) => setStatus('Idle profile error: ' + err.message)));
			laserIdleColorEl.addEventListener('change', () => patchLaserConfig({ laser_led_idle_color_mode: laserIdleColorEl.value }).catch((err) => setStatus('Idle profile error: ' + err.message)));
			laserHoldEffectEl.addEventListener('change', () => patchLaserConfig({ laser_led_hold_effect: laserHoldEffectEl.value }).catch((err) => setStatus('Hold profile error: ' + err.message)));
			laserHoldColorEl.addEventListener('change', () => patchLaserConfig({ laser_led_hold_color_mode: laserHoldColorEl.value }).catch((err) => setStatus('Hold profile error: ' + err.message)));
			laserDoorEffectEl.addEventListener('change', () => patchLaserConfig({ laser_led_door_effect: laserDoorEffectEl.value }).catch((err) => setStatus('Door profile error: ' + err.message)));
			laserDoorColorEl.addEventListener('change', () => patchLaserConfig({ laser_led_door_color_mode: laserDoorColorEl.value }).catch((err) => setStatus('Door profile error: ' + err.message)));
			laserErrorEffectEl.addEventListener('change', () => patchLaserConfig({ laser_led_error_effect: laserErrorEffectEl.value }).catch((err) => setStatus('Error profile error: ' + err.message)));
			laserErrorColorEl.addEventListener('change', () => patchLaserConfig({ laser_led_error_color_mode: laserErrorColorEl.value }).catch((err) => setStatus('Error profile error: ' + err.message)));
			laserCompleteEffectEl.addEventListener('change', () => patchLaserConfig({ laser_led_engrave_complete_effect: laserCompleteEffectEl.value }).catch((err) => setStatus('Complete profile error: ' + err.message)));
			laserCompleteColorEl.addEventListener('change', () => patchLaserConfig({ laser_led_engrave_complete_color_mode: laserCompleteColorEl.value }).catch((err) => setStatus('Complete profile error: ' + err.message)));
			startupLedEffectEl.addEventListener('change', () => patchLaserConfig({ led_startup_effect: startupLedEffectEl.value }).catch((err) => setStatus('Startup profile error: ' + err.message)));
			startupLedColorEl.addEventListener('change', () => patchLaserConfig({ led_startup_color_mode: startupLedColorEl.value }).catch((err) => setStatus('Startup profile error: ' + err.message)));
			startupLedPresetEl.addEventListener('change', () => patchLaserConfig({ led_startup_preset: startupLedPresetEl.value }).catch((err) => setStatus('Startup profile error: ' + err.message)));
			shutdownLedEffectEl.addEventListener('change', () => patchLaserConfig({ led_shutdown_effect: shutdownLedEffectEl.value }).catch((err) => setStatus('Shutdown profile error: ' + err.message)));
			shutdownLedColorEl.addEventListener('change', () => patchLaserConfig({ led_shutdown_color_mode: shutdownLedColorEl.value }).catch((err) => setStatus('Shutdown profile error: ' + err.message)));
			shutdownLedPresetEl.addEventListener('change', () => patchLaserConfig({ led_shutdown_preset: shutdownLedPresetEl.value }).catch((err) => setStatus('Shutdown profile error: ' + err.message)));
			laserClearErrorBtnEl.addEventListener('click', () => { clearLaserErrorFromUi().catch(() => {}); });
			laserSendGcodeEl.addEventListener('click', () => { sendCustomGcodeFromUi().catch(() => {}); });
			if (laserClearQueueBtnEl) {
				laserClearQueueBtnEl.addEventListener('click', () => { clearLaserQueueFromUi().catch(() => {}); });
			}
			if (laserSaveCustomPosEl) {
				laserSaveCustomPosEl.addEventListener('click', () => {
					persistCustomPositionFromUi()
						.then(() => setStatus('Custom position saved.'))
						.catch((err) => setStatus('Custom position save error: ' + err.message));
				});
			}
			if (laserGoCustomPosEl) {
				laserGoCustomPosEl.addEventListener('click', () => { runCustomPositionFromUi().catch(() => {}); });
			}
			laserJogUpEl.addEventListener('click', () => { sendLaserJog('up').catch(() => {}); });
			laserJogDownEl.addEventListener('click', () => { sendLaserJog('down').catch(() => {}); });
			laserJogLeftEl.addEventListener('click', () => { sendLaserJog('left').catch(() => {}); });
			laserJogRightEl.addEventListener('click', () => { sendLaserJog('right').catch(() => {}); });
			laserJogHomeEl.addEventListener('click', () => { sendLaserJog('home').catch(() => {}); });
			laserMoveStepMmEl.addEventListener('input', () => {
				laserMoveStepSyncHoldUntil = Date.now() + LASER_MOVE_INPUT_SYNC_HOLD_MS;
			});
			laserMoveStepMmEl.addEventListener('blur', () => {
				persistLaserMoveStepMm().catch((err) => setStatus('Move step error: ' + err.message));
			});
			laserMoveStepMmEl.addEventListener('keydown', (ev) => {
				if (ev.key === 'Enter') {
					ev.preventDefault();
					persistLaserMoveStepMm().catch((err) => setStatus('Move step error: ' + err.message));
				}
			});
			laserMoveFeedMmSecEl.addEventListener('input', () => {
				laserMoveFeedSyncHoldUntil = Date.now() + LASER_MOVE_INPUT_SYNC_HOLD_MS;
			});
			laserMoveFeedMmSecEl.addEventListener('blur', () => {
				persistLaserMoveFeedMmSec().catch((err) => setStatus('Move speed error: ' + err.message));
			});
			laserMoveFeedMmSecEl.addEventListener('keydown', (ev) => {
				if (ev.key === 'Enter') {
					ev.preventDefault();
					persistLaserMoveFeedMmSec().catch((err) => setStatus('Move speed error: ' + err.message));
				}
			});
			laserCustomGcodeEl.addEventListener('keydown', (ev) => {
				if (ev.key === 'Enter') {
					ev.preventDefault();
					sendCustomGcodeFromUi().catch(() => {});
				}
			});
			[laserCustomPosXEl, laserCustomPosYEl, laserCustomPosZEl].forEach((inputEl) => {
				if (!inputEl) return;
				inputEl.addEventListener('blur', () => {
					persistCustomPositionFromUi().catch(() => {});
				});
				inputEl.addEventListener('keydown', (ev) => {
					if (ev.key === 'Enter') {
						ev.preventDefault();
						persistCustomPositionFromUi().catch(() => {});
					}
				});
			});
			if (laserCustomPosUseG0El) {
				laserCustomPosUseG0El.addEventListener('change', () => {
					persistCustomPositionFromUi().catch((err) => setStatus('Custom position mode error: ' + err.message));
				});
			}

			streamBadgeEl.addEventListener('click', (ev) => {
			ev.preventDefault();
			showRightPanel('live');
			});

			streamHdBadgeEl.addEventListener('click', (ev) => {
			ev.preventDefault();
			showRightPanel('streamhd');
			});

			snapshotBadgeEl.addEventListener('click', (ev) => {
			ev.preventDefault();
			showRightPanel('snapshot');
			if (!photoTaken && !takePhotoBtn.disabled) takePhotoBtn.click();
			});

			selectedCustomHex = normalizeHex(customColorEl.value);
			updateCustomColorPreview(selectedCustomHex);

			showRightPanel('live');
			startStateSyncPolling();

			setInterval(() => {
				refreshLaserMonitor().catch(() => {});
			}, 2000);

			Promise.all([refresh(), refreshCameraSettings(), refreshLaserMonitor(), loadAirAssistState()])
			.catch(() => setStatus('API connection error'));
	</script>
</body>
</html>
"""
	return html.replace("{APP_VERSION}", str(app_version))
