const fill = document.getElementById('fill');
const volNumber = document.getElementById('volNumber');
const statusDot = document.getElementById('statusDot');
const statusText = document.getElementById('status-text');
const micIcon = document.getElementById('micIcon');
const peakVal = document.getElementById('peakVal');
const avgVal = document.getElementById('avgVal');
const rateVal = document.getElementById('rateVal');
const errorMsg = document.getElementById('error-msg');
const waveform = document.getElementById('waveform');
const ticksEl = document.getElementById('ticks');
const noiseFloorVal = document.getElementById('noiseFloorVal');

const BAR_COUNT = 32;
const CALIBRATION_FRAMES = 45;
const NOISE_MARGIN = 0.02;
const NOISE_ADAPT_ALPHA = 0.03;
const ATTACK_ALPHA = 0.42;
const RELEASE_ALPHA = 0.12;

const bars = [];
let peak = 0;
let history = [];
let updateCount = 0;
let waveHistory = new Array(BAR_COUNT).fill(0);
let noiseFloor = 0;
let smoothLevel = 0;
let calibratingFrames = 0;

for (let i = 0; i <= 20; i += 1) {
  const tick = document.createElement('div');
  tick.className = `tick${i % 5 === 0 ? ' major' : ''}`;
  ticksEl.appendChild(tick);
}

for (let i = 0; i < BAR_COUNT; i += 1) {
  const bar = document.createElement('div');
  bar.className = 'bar';
  waveform.appendChild(bar);
  bars.push(bar);
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function setStatus(state) {
  if (state === 'live') {
    statusDot.className = 'status-dot live';
    statusText.className = 'status-text live';
    statusText.textContent = 'LIVE MIC ACTIVE';
    errorMsg.style.display = 'none';
    return;
  }

  if (state === 'calibrating') {
    statusDot.className = 'status-dot';
    statusText.className = 'status-text';
    statusText.textContent = 'CALIBRATING ROOM NOISE';
    errorMsg.style.display = 'none';
    return;
  }

  statusDot.className = 'status-dot error';
  statusText.className = 'status-text error';
  statusText.textContent = 'MIC ACCESS ERROR';
  errorMsg.style.display = 'block';
  micIcon.classList.remove('active');
}

function updateWave(vol) {
  waveHistory.push(vol);
  if (waveHistory.length > BAR_COUNT) {
    waveHistory.shift();
  }

  bars.forEach((bar, i) => {
    const value = waveHistory[i];
    const height = Math.max(4, (value / 100) * 52);
    bar.style.height = `${height}px`;

    if (value > 70) {
      bar.style.background = 'var(--red)';
    } else if (value > 40) {
      bar.style.background = 'var(--amber)';
    } else if (value > 4) {
      bar.style.background = 'var(--cyan)';
    } else {
      bar.style.background = 'var(--dim)';
    }

    bar.style.opacity = String(0.35 + (i / BAR_COUNT) * 0.65);
  });
}

function applyVolume(vol) {
  updateCount += 1;

  fill.style.width = `${vol}%`;
  fill.className = `fill${vol > 70 ? ' high' : vol > 40 ? ' mid' : ''}`;

  volNumber.textContent = String(vol).padStart(2, '0');
  volNumber.className = `vol-number${vol > 70 ? ' high' : vol > 40 ? ' mid' : ''}`;

  micIcon.classList.toggle('active', vol > 5);

  if (vol > peak) {
    peak = vol;
    peakVal.textContent = String(peak).padStart(2, '0');
  }

  history.push(vol);
  if (history.length > 20) {
    history.shift();
  }

  const avg = Math.round(history.reduce((sum, v) => sum + v, 0) / history.length);
  avgVal.textContent = String(avg).padStart(2, '0');
  noiseFloorVal.textContent = String(Math.round(noiseFloor * 100)).padStart(2, '0');

  updateWave(vol);
}

function measureRms(timeDomainArray) {
  let sumSquares = 0;

  for (let i = 0; i < timeDomainArray.length; i += 1) {
    const centered = (timeDomainArray[i] - 128) / 128;
    sumSquares += centered * centered;
  }

  return Math.sqrt(sumSquares / timeDomainArray.length);
}

function processLevel(rms) {
  if (calibratingFrames < CALIBRATION_FRAMES) {
    calibratingFrames += 1;
    noiseFloor = noiseFloor === 0 ? rms : (noiseFloor * 0.9) + (rms * 0.1);
    setStatus('calibrating');
    applyVolume(0);
    return;
  }

  if (rms <= noiseFloor + NOISE_MARGIN) {
    noiseFloor = ((1 - NOISE_ADAPT_ALPHA) * noiseFloor) + (NOISE_ADAPT_ALPHA * rms);
  }

  const speech = Math.max(0, rms - (noiseFloor + NOISE_MARGIN));
  const alpha = speech > smoothLevel ? ATTACK_ALPHA : RELEASE_ALPHA;
  smoothLevel = ((1 - alpha) * smoothLevel) + (alpha * speech);

  const normalized = clamp((smoothLevel / 0.28) * 100, 0, 100);
  applyVolume(Math.round(normalized));
  setStatus('live');
}

async function startMicrophone() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        noiseSuppression: true,
        echoCancellation: true,
        autoGainControl: true
      }
    });

    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const source = audioContext.createMediaStreamSource(stream);
    const analyser = audioContext.createAnalyser();
    analyser.fftSize = 1024;
    analyser.smoothingTimeConstant = 0.45;

    source.connect(analyser);

    const timeData = new Uint8Array(analyser.fftSize);

    const loop = () => {
      analyser.getByteTimeDomainData(timeData);
      const rms = measureRms(timeData);
      processLevel(rms);
      requestAnimationFrame(loop);
    };

    requestAnimationFrame(loop);
  } catch (err) {
    setStatus('error');
  }
}

setInterval(() => {
  rateVal.textContent = String(updateCount);
  updateCount = 0;
}, 1000);

startMicrophone();