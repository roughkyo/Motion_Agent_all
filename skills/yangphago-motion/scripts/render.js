// 범용 렌더러 (Canvas render(t) 페이지 → PNG / mp4)
//   node render.js stills <page.html> <outdir> 1.5 4 7.25 ...   → <outdir>/s_<초>.png
//   node render.js video  <page.html> <audio.wav> <out.mp4>      → 30fps mp4 (오디오 포함) + <out>_qa.jpg 검수 시트
// 페이지 조건: window.BEATMAP.duration, render(t), 캔버스 변수 cv, window.fontsReady(Promise)
// 경로는 현재 작업 폴더 기준. playwright-core는 작업 폴더 또는 스킬 폴더에 설치 (npm i playwright-core)
const { spawn, spawnSync } = require('child_process');
const fs = require('fs');
const path = require('path');

let chromium;
try {
  ({ chromium } = require(require.resolve('playwright-core', { paths: [process.cwd(), __dirname, path.resolve(__dirname, '..'), ...(process.env.NODE_PATH || '').split(path.delimiter).filter(Boolean)] })));
} catch {
  console.error('playwright-core 없음 → 작업 폴더 또는 스킬 폴더에서 npm i playwright-core');
  process.exit(1);
}

const FPS = 30;
const [mode, page_, ...rest] = process.argv.slice(2);
const abs = p => path.resolve(process.cwd(), p);

// ffmpeg: FFMPEG_PATH → PATH → winget 설치 폴더 탐색 (터미널을 다시 열기 전엔 PATH에 없을 수 있음)
function findFfmpeg() {
  if (process.env.FFMPEG_PATH && fs.existsSync(process.env.FFMPEG_PATH)) return process.env.FFMPEG_PATH;
  try { if (spawnSync('ffmpeg', ['-version']).status === 0) return 'ffmpeg'; } catch {}
  const base = path.join(process.env.LOCALAPPDATA || '', 'Microsoft', 'WinGet', 'Packages');
  try {
    for (const pkg of fs.readdirSync(base).filter(d => /ffmpeg/i.test(d))) {
      for (const sub of fs.readdirSync(path.join(base, pkg))) {
        const exe = path.join(base, pkg, sub, 'bin', 'ffmpeg.exe');
        if (fs.existsSync(exe)) return exe;
      }
    }
  } catch {}
  return 'ffmpeg';
}

// 브라우저: CHROME_PATH 환경변수 → 설치된 Chrome → Edge 순 (OS별 설치 경로는 playwright가 찾음)
async function launch() {
  const args = ['--allow-file-access-from-files'];
  if (process.env.CHROME_PATH) return chromium.launch({ executablePath: process.env.CHROME_PATH, args });
  for (const channel of ['chrome', 'msedge']) {
    try { return await chromium.launch({ channel, args }); } catch {}
  }
  console.error('Chrome/Edge를 찾지 못함 → Chrome을 설치하거나 CHROME_PATH 환경변수에 실행 파일 경로를 지정');
  process.exit(1);
}

(async () => {
  const browser = await launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  page.on('pageerror', e => console.error('페이지 오류:', e.message));
  await page.goto(require('url').pathToFileURL(abs(page_)).href);
  await page.evaluate(() => window.fontsReady);
  const DUR = await page.evaluate(() => window.BEATMAP.duration);
  const grab = t => page.evaluate(t => { render(t); return cv.toDataURL('image/png').split(',')[1]; }, t);

  if (mode === 'stills') {
    const dir = abs(rest[0]);
    fs.mkdirSync(dir, { recursive: true });
    for (const t of rest.slice(1)) {
      fs.writeFileSync(path.join(dir, `s_${t}.png`), Buffer.from(await grab(parseFloat(t)), 'base64'));
    }
    console.log(`stills ${rest.length - 1}장 → ${dir}`);
  } else if (mode === 'video') {
    const FF = findFfmpeg();
    const [audio, out] = rest.map(abs);
    fs.mkdirSync(path.dirname(out), { recursive: true });
    const ff = spawn(FF, [
      '-y', '-framerate', String(FPS), '-f', 'image2pipe', '-c:v', 'png', '-i', '-',
      '-i', audio, '-t', String(DUR),
      '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p',
      '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart', out,
    ], { stdio: ['pipe', 'inherit', 'inherit'] });
    const total = Math.round(FPS * DUR);
    for (let i = 0; i < total; i++) {
      if (!ff.stdin.write(Buffer.from(await grab(i / FPS), 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
      if (i % 150 === 0) console.log(`frame ${i}/${total}`);
    }
    ff.stdin.end();
    await new Promise(r => ff.on('close', r));
    // 검수 시트: 1초에 1장씩 6열 격자 한 장 (<out>_qa.jpg) → 이미지 한 번만 열어 전체 확인
    const qa = out.replace(/\.mp4$/i, '_qa.jpg');
    spawnSync(FF, ['-y', '-v', 'error', '-i', out, '-vf', `fps=1,scale=384:-1,tile=6x${Math.ceil(DUR / 6)}`, '-frames:v', '1', qa]);
    console.log('done', out, '| 검수 시트', qa);
  } else {
    console.error('mode는 stills 또는 video');
  }
  await browser.close();
})();
