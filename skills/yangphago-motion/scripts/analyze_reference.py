# 레퍼런스 모션그래픽 분석기
# 실행: python analyze_reference.py <영상 파일 또는 폴더> <출력 폴더>
# 결과: 영상마다 <이름>.json(컷·히트·박자·움직임 수치) + <이름>_sheet.jpg(1초 간격 타임코드 시트) + <이름>_hits.jpg(히트 직후 프레임)
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import librosa
from PIL import Image, ImageDraw, ImageFont
sys.stdout.reconfigure(encoding='utf-8')     # Windows 콘솔(cp949)에서 한글 출력이 깨지지 않도록

TW, TH = 320, 180            # 시트 칸 크기
SCENE = 0.30                 # 컷 판정 문턱값 (ffmpeg scene 점수)


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')


def probe(f):
    out = run(['ffprobe', '-v', 'error', '-select_streams', 'v', '-show_entries',
               'stream=r_frame_rate:format=duration', '-of', 'json', str(f)]).stdout
    j = json.loads(out)
    num, den = j['streams'][0]['r_frame_rate'].split('/')
    return float(j['format']['duration']), float(num) / float(den)


def cuts_of(f):
    # 화면이 크게 바뀌는 순간 = 컷 (모션그래픽은 와이프도 컷으로 잡힘)
    err = run(['ffmpeg', '-hide_banner', '-i', str(f), '-vf', f"select='gt(scene,{SCENE})',showinfo",
               '-an', '-f', 'null', '-']).stderr
    ts = []
    for line in err.splitlines():
        if 'pts_time:' in line:
            ts.append(float(line.split('pts_time:')[1].split()[0]))
    # 0.15초 안에 연달아 잡힌 것은 하나의 전환으로 합침
    merged = []
    for x in ts:
        if not merged or x - merged[-1] > 0.15:
            merged.append(x)
    return merged


def hits_of(g, fps):
    # 프레임 변화량이 튀는 순간 = 히트 (컷·와이프·글자가 박히는 순간 모두 포함)
    d = np.abs(np.diff(g, axis=0)).mean(axis=(1, 2))
    thr = max(6.0, float(np.median(d) + 3 * d.std()))
    hits = []
    for i in range(1, len(d) - 1):
        if d[i] > thr and d[i] >= d[i - 1] and d[i] >= d[i + 1]:
            t = (i + 1) / fps
            if not hits or t - hits[-1] > 0.15:
                hits.append(t)
    return hits


def frames(f, fps, w, h):
    # 작은 회색조 프레임 배열 (움직임 측정용)
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(f), '-vf', f'fps={fps},scale={w}:{h},format=gray',
                          '-f', 'rawvideo', '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(np.float32)


def grab(f, t, w=TW, h=TH):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t:.3f}', '-i', str(f), '-frames:v', '1',
                          '-vf', f'scale={w}:{h}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
    if len(raw) < w * h * 3:
        return Image.new('RGB', (w, h))
    return Image.frombytes('RGB', (w, h), raw[:w * h * 3])


def sheet(f, times, path, cols=8):
    # 타임코드를 붙인 프레임 격자
    try:
        font = ImageFont.truetype('arial.ttf', 18)
    except OSError:
        font = ImageFont.load_default()
    rows = max(1, (len(times) + cols - 1) // cols)
    img = Image.new('RGB', (cols * TW, rows * TH), (20, 20, 20))
    d = ImageDraw.Draw(img)
    for i, t in enumerate(times):
        x, y = (i % cols) * TW, (i // cols) * TH
        img.paste(grab(f, t), (x, y))
        d.rectangle([x, y, x + 74, y + 24], fill=(176, 38, 255))
        d.text((x + 5, y + 2), f'{t:5.2f}s', fill=(0, 0, 0), font=font)
    img.save(path, quality=82)


def analyze(f, out):
    dur, fps = probe(f)
    g30 = frames(f, 30, 160, 90)
    hits = hits_of(g30, 30)
    cuts = cuts_of(f)
    lens = np.diff([0] + cuts + [dur])
    info = {'file': f.name, 'duration': round(dur, 2), 'fps': round(fps, 2), 'cuts': [round(c, 3) for c in cuts], 'hits': [round(h, 3) for h in hits],
            'hit_gap': round(float(np.median(np.diff(hits))), 2) if len(hits) > 1 else None,
            'cut_len': {'mean': round(float(lens.mean()), 2), 'median': round(float(np.median(lens)), 2),
                        'min': round(float(lens.min()), 2), 'max': round(float(lens.max()), 2)}}
    # 음악: BPM과 박 위치 → 컷이 박자(반박 포함)에 맞는 비율
    try:
        sr = 22050
        pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(f), '-ac', '1', '-ar', str(sr), '-f', 's16le', '-'],
                             capture_output=True).stdout
        y = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr, units='time')
        bpm = float(np.atleast_1d(tempo)[0])
        if bpm > 140:                        # 힙합은 8분음표를 박으로 세는 경우가 많음 → 절반으로
            bpm /= 2
            beats = beats[::2]
        half = np.sort(np.concatenate([beats, beats[:-1] + np.diff(beats) / 2]))
        on = [c for c in hits if len(half) and np.min(np.abs(half - c)) < 0.07]
        rms = librosa.feature.rms(y=y)[0]
        tr = librosa.times_like(rms, sr=sr)
        energy = [round(float(20 * np.log10(rms[(tr >= s) & (tr < s + 1)].mean() + 1e-9)), 1) for s in range(int(dur))]
        info.update({'bpm': round(bpm, 1), 'beat': round(60 / bpm, 3),
                     'hit_on_beat': round(len(on) / max(1, len(hits)), 2), 'energy_db_per_sec': energy})
    except Exception as e:                  # 무음 영상 등
        info['audio_error'] = str(e)
    # 움직임: 10fps 프레임 차이 → 초당 움직임 지수, 정지 구간 비율
    diff = np.abs(np.diff(g30, axis=0)).mean(axis=(1, 2))
    per_sec = [round(float(diff[i * 30:(i + 1) * 30].mean()), 1) for i in range(len(diff) // 30)]
    info.update({'motion_per_sec': per_sec, 'holds': round(float((diff < 1.0).mean()), 2)})
    # 시트 2장
    sheet(f, list(np.arange(0.5, dur, 1.0)), out / f'{f.stem}_sheet.jpg')
    sheet(f, [min(h + 0.1, dur - 0.05) for h in hits[:48]], out / f'{f.stem}_hits.jpg')
    (out / f'{f.stem}.json').write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding='utf-8')
    return info


if __name__ == '__main__':
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    files = sorted(src.glob('*.mp4')) if src.is_dir() else [src]
    for f in files:
        i = analyze(f, out)
        print(f"{i['file']}: {i['duration']}s, 컷 {len(i['cuts'])}개, 히트 {len(i['hits'])}개(간격 중앙값 {i['hit_gap']}s), "
              f"BPM {i.get('bpm')}, 히트-박자 일치 {i.get('hit_on_beat')}, 정지 비율 {i['holds']}")
