const fill       = document.getElementById('fill');
const volNumber  = document.getElementById('volNumber');
const statusDot  = document.getElementById('statusDot');
const statusText = document.getElementById('status-text');
const micIcon    = document.getElementById('micIcon');
const peakVal    = document.getElementById('peakVal');
const avgVal     = document.getElementById('avgVal');
const rateVal    = document.getElementById('rateVal');
const errorMsg   = document.getElementById('error-msg');
const waveform   = document.getElementById('waveform');
const ticksEl    = document.getElementById('ticks');

for (let i = 0; i <= 20; i++) {
  const t = document.createElement('div');
  t.className = 'tick' + (i % 5 === 0 ? ' major' : '');
  ticksEl.appendChild(t);
}
