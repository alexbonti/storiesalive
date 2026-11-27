#!/usr/bin/env node
/* Esporta trailer.html in video.mp4 (1280x720, 24 fps, senza audio).
   Uso: node render.js [video.mp4]   (richiede Playwright e ffmpeg; avvia da solo un server locale) */
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');
const out = path.resolve(process.argv[2] || 'video.mp4');
const FPS = 24, PORT = 8791;
(async () => {
  const srv = spawn('python3', ['-m', 'http.server', String(PORT)], { cwd: path.resolve(__dirname, '..'), stdio: 'ignore' });
  await new Promise(r => setTimeout(r, 1200));
  const ff = spawn('ffmpeg', ['-nostdin', '-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-',
    '-vf', 'scale=1280:720:flags=neighbor', '-c:v', 'libx264', '-preset', 'slow', '-crf', '24', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 640, height: 360 } });
  page.on('pageerror', e => console.error('ERRORE pagina:', e));
  await page.goto(`http://localhost:${PORT}/trailer/trailer.html?render`);
  await page.waitForFunction(() => window.ready, null, { timeout: 20000 });
  const dur = await page.evaluate(() => window.DUR), n = Math.round(dur * FPS);
  for (let i = 0; i < n; i++) {
    const b64 = await page.evaluate(t => { draw(t); return document.getElementById('c').toDataURL('image/png').split(',')[1]; }, i / FPS);
    if (!ff.stdin.write(Buffer.from(b64, 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 120 === 0) console.log(`fotogramma ${i}/${n}`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await browser.close(); srv.kill();
  console.log('video scritto in', out);
})();
