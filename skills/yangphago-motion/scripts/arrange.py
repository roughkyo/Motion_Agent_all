# 범용 편곡기: 고른 곡 → 영상 길이에 맞춘 final.wav + beatmap.js (엔딩 정적·임팩트·마지막 한 방 포함)
# 실행: python arrange.py <곡.mp3> --seconds 30 [--beat 0.666685 --down0 0.1839] [--outro-bar 24]
#                         [--out music/final.wav] [--map beatmap.js]
#   --beat/--down0 생략 시 beat_grid로 자동 측정 (assets/music/library.json에 값이 있으면 그 값을 넘기면 빠름)
#   구조: [본문: 첫 다운비트부터] → 2박 정적 + 리버스 크래시 → 임팩트(원곡 outro-bar부터) → 1마디 뒤 마지막 한 방 → 페이드
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import librosa
from scipy.signal import butter, sosfilt, find_peaks
from scipy.io import wavfile

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, str(Path(__file__).parent))
import beat_grid                                       # noqa: E402

SR = 44100
rng = np.random.default_rng(3)


def filt(x, kind, f, order=2):
    return sosfilt(butter(order, f, btype=kind, fs=SR, output='sos'), x, axis=0)


def add(buf, t0, sig, gain=1.0):
    i = int(t0 * SR)
    if sig.ndim == 1:
        sig = np.stack([sig, sig], axis=1)
    n = min(len(sig), len(buf) - i)
    if n > 0:
        buf[i:i + n] += sig[:n] * gain


def crash(length):
    n = int(length * SR)
    return filt(rng.standard_normal(n), 'highpass', 3800, 3) * np.exp(-np.arange(n) / SR / 0.95)


def impact():
    # 서브 붐: 피치가 뚝 떨어지는 저음 '쾅'
    t = np.arange(int(2.0 * SR)) / SR
    f = 34 + 75 * np.exp(-t / 0.07)
    return np.tanh(2.0 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.7))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('--seconds', type=float, required=True)
    ap.add_argument('--beat', type=float, default=0)
    ap.add_argument('--down0', type=float, default=-1)
    ap.add_argument('--outro-bar', type=int, default=-1)
    ap.add_argument('--out', default='music/final.wav')
    ap.add_argument('--map', default='beatmap.js')
    a = ap.parse_args()

    y, _ = librosa.load(a.src, sr=SR, mono=False)
    y = y.T if y.ndim == 2 else np.stack([y, y], axis=1)
    src_dur = len(y) / SR

    # 박자: 인자로 받거나 자동 측정
    beat, down0 = a.beat, a.down0
    if not beat or down0 < 0:
        mono22 = beat_grid.load(a.src)
        beat, sph, r, _, _ = beat_grid.fit_backbeat(mono22)
        down0 = (sph - beat) % (beat * 4)
        print(f'측정: 1박 {beat:.5f}s ({60 / beat:.2f} BPM), 첫 다운비트 {down0:.4f}s, 위상 집중도 {r:.2f}')
    bar = beat * 4

    # 영상 구조 (박 단위): 마지막 한 방은 끝에서 0.6초 이상 여유를 둔 마디 경계
    fin_b = int((a.seconds - 0.6) // bar) * 4
    imp_b, gap_b = fin_b - 4, fin_b - 6
    t_gap, t_imp, t_fin = gap_b * beat, imp_b * beat, fin_b * beat
    if down0 + t_gap > src_dur:
        sys.exit('곡이 영상 본문보다 짧습니다. 더 긴 곡을 고르세요.')

    # 임팩트 뒤에 이어 붙일 원곡 마디: 지정 없으면 본문 이후에서 저음 에너지가 가장 큰 마디
    mono = y.mean(axis=1)
    lo = filt(mono, 'lowpass', 120, 4)
    nbar = int((src_dur - down0 - 2 * bar) // bar)
    energy = [np.sqrt(np.mean(lo[int((down0 + k * bar) * SR):int((down0 + (k + 1) * bar) * SR)] ** 2)) for k in range(nbar)]
    ob = a.outro_bar
    if ob < 0:
        start_k = gap_b // 4
        ob = start_k + int(np.argmax(energy[start_k:])) if start_k < nbar else int(np.argmax(energy))
    c0 = down0 + ob * bar

    def cut(t0, length):
        i = int(t0 * SR)
        seg = y[i:i + int(length * SR)].copy()
        n = int(0.008 * SR)                            # 자른 경계 '틱' 방지 8ms 페이드
        seg[:n] *= np.linspace(0, 1, n)[:, None]
        seg[-n:] *= np.linspace(1, 0, n)[:, None]
        return seg

    out = np.zeros((int(a.seconds * SR), 2))
    add(out, 0, cut(down0, t_gap))
    add(out, t_imp, cut(c0, a.seconds - t_imp + 0.05))
    rc = crash(1.3)[::-1]                              # 정적 동안 빨아들이는 리버스 크래시
    add(out, t_imp - len(rc) / SR, rc, 0.28)
    for t0, g in [(t_imp, 0.75), (t_fin, 0.9)]:
        add(out, t0, impact(), g)
        add(out, t0, crash(2.0), 0.3)
    fade_i = int((t_fin + 0.12) * SR)                  # 마지막 한 방 뒤에는 잔향만
    if fade_i < len(out):
        out[fade_i:] *= (np.linspace(1, 0, len(out) - fade_i) ** 2)[:, None]

    # 마스터: 소프트 클립 + 노멀라이즈
    out /= np.max(np.abs(out))
    out = np.tanh(1.3 * out) / np.tanh(1.3)
    out *= 0.93 / np.max(np.abs(out))
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    wavfile.write(a.out, SR, (out * 32767).astype(np.int16))

    # beatmap: 킥 = 원곡 저음 타격을 영상 시각으로 옮김, 스네어 = 2·4박 격자
    env = librosa.onset.onset_strength(y=filt(mono, 'lowpass', 110, 4), sr=SR, hop_length=256)
    env /= np.percentile(env, 99)
    tk = librosa.times_like(env, sr=SR, hop_length=256)
    pk, _ = find_peaks(env, height=0.55, distance=int(0.15 * SR / 256))
    kicks = []
    for s in tk[pk]:
        if down0 <= s < down0 + t_gap:
            kicks.append(s - down0)
        if c0 <= s < c0 + (t_fin - t_imp):
            kicks.append(s - c0 + t_imp)
    kicks.append(t_fin)
    snares = [b * beat for b in range(1, gap_b, 2)] + [t_imp + beat, t_imp + 3 * beat, t_fin]
    bm = {'bpm': round(60 / beat, 3), 'duration': a.seconds,
          'kicks': sorted(round(float(x), 4) for x in kicks), 'snares': sorted(round(float(x), 4) for x in snares),
          'impacts': [round(t_imp, 4), round(t_fin, 4)], 'gap': [round(t_gap, 4), round(t_imp, 4)]}
    Path(a.map).write_text('window.BEATMAP = ' + json.dumps(bm) + ';\n', encoding='utf-8')
    print(f'→ {a.out} + {a.map}: 본문 0~{t_gap:.2f}s · 정적 {t_gap:.2f}~{t_imp:.2f}s · '
          f'임팩트(원곡 {ob}마디) {t_imp:.2f}s · 마지막 한 방 {t_fin:.2f}s')


if __name__ == '__main__':
    main()
