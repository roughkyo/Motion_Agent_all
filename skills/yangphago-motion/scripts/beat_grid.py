# 음원 박자 분석기: BPM · 첫 다운비트 · 킥/스네어 · 마디별 에너지 → beatmap.js
# 실행: python beat_grid.py <음원(mp3/wav/mp4)> [--start 초] [--length 초] [--map beatmap.js]
#   --start/--length: 영상에 쓸 구간만 잘라서 쓸 때, 그 구간 기준(0초 시작)으로 타이밍을 변환
#   출력 표의 마디별 에너지(low=저음, hi=고음)로 '풀비트 / 브레이크 / 히트' 구간을 골라 편곡
import sys
import argparse
import json
import subprocess

import numpy as np
import librosa
from scipy.signal import butter, sosfilt, find_peaks
sys.stdout.reconfigure(encoding='utf-8')     # Windows 콘솔(cp949)에서 한글 출력이 깨지지 않도록

SR = 22050
H = 128


def load(path):
    # mp4·mp3 모두 ffmpeg로 읽음 (librosa 단독으로는 mp4를 못 읽음)
    pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'],
                         capture_output=True).stdout
    return np.frombuffer(pcm, np.int16).astype(np.float32) / 32768


def band_env(y, kind, f):
    z = sosfilt(butter(4, f, kind, fs=SR, output='sos'), y)
    e = librosa.onset.onset_strength(y=z, sr=SR, hop_length=H)
    return e / (np.percentile(e, 99) + 1e-9)


def fit_backbeat(y):
    # 스네어(2·4박)는 2박 간격 → 주기·위상을 원형 평균으로 찾고 최소제곱으로 다듬음
    # (첫 피크를 기준으로 잡으면 그 피크가 격자 밖일 때 전부 실패함 → 위상 히스토그램 방식)
    e = band_env(y, 'bandpass', [1800, 6000])
    t = librosa.times_like(e, sr=SR, hop_length=H)
    p, _ = find_peaks(e, height=1.0, distance=int(.25 * SR / H))
    S = t[p]
    tempo = float(np.atleast_1d(librosa.beat.beat_track(y=y, sr=SR)[0])[0])
    if tempo > 140:
        tempo /= 2
    best = None
    for bpm in np.arange(tempo * .9, tempo * 1.1, 0.01):
        P = 120 / bpm
        z = np.exp(2j * np.pi * S / P).mean()
        if best is None or abs(z) > best[0]:
            best = (abs(z), P, (np.angle(z) / (2 * np.pi) * P) % P)
    r, P, ph = best
    k = np.round((S - ph) / P)
    m = np.abs(S - (ph + k * P)) < .05
    if m.sum() >= 4:
        P, ph = np.polyfit(k[m], S[m], 1)
    return P / 2, ph, r, int(m.sum()), len(S)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('--start', type=float, default=0)
    ap.add_argument('--length', type=float, default=0)
    ap.add_argument('--map', default='')
    a = ap.parse_args()
    y = load(a.src)
    dur = len(y) / SR
    beat, snare_ph, r, inl, ns = fit_backbeat(y)
    bar = beat * 4
    down0 = (snare_ph - beat) % bar                   # 스네어가 2박이므로 한 박 앞이 1박
    print(f'BPM {60 / beat:.3f} · 1박 {beat:.5f}s · 첫 다운비트 {down0:.4f}s · 위상 집중도 {r:.2f} · 스네어 정렬 {inl}/{ns}')
    if r < .4:
        print('⚠ 백비트가 뚜렷하지 않음 → 결과를 귀로 확인하거나 librosa beat_track 결과와 비교할 것')
    # 마디별 에너지 표
    lo = sosfilt(butter(4, 120, 'lowpass', fs=SR, output='sos'), y)
    hi = sosfilt(butter(4, 2000, 'highpass', fs=SR, output='sos'), y)
    db = lambda z: 20 * np.log10(np.sqrt(np.mean(z ** 2)) + 1e-9)
    n = 0
    while down0 + (n + 1) * bar <= dur:
        i0, i1 = int((down0 + n * bar) * SR), int((down0 + (n + 1) * bar) * SR)
        L = db(lo[i0:i1])
        print(f'bar{n:3d} {down0 + n * bar:8.3f}s  all {db(y[i0:i1]):6.1f}  low {L:6.1f}  hi {db(hi[i0:i1]):6.1f}  ' + '#' * int(max(0, 32 + L)))
        n += 1
    # 킥: 저음 대역 실제 타격 / 스네어: 격자의 2·4박
    e = band_env(y, 'lowpass', 110)
    tk = librosa.times_like(e, sr=SR, hop_length=H)
    pk, _ = find_peaks(e, height=.55, distance=int(.15 * SR / H))
    kicks = tk[pk]
    snares = np.arange(down0 + beat, dur, 2 * beat)
    if a.map:
        s0 = a.start
        s1 = s0 + (a.length or dur - s0)
        sel = lambda arr: sorted(round(float(x - s0), 4) for x in arr if s0 <= x < s1)
        bm = {'bpm': round(60 / beat, 3), 'duration': round(s1 - s0, 3), 'kicks': sel(kicks), 'snares': sel(snares),
              'impacts': [], 'downbeat': round(float((down0 - s0) % bar), 4)}
        with open(a.map, 'w', encoding='utf-8') as fp:
            fp.write('window.BEATMAP = ' + json.dumps(bm) + ';\n')
        print(f'→ {a.map}: 킥 {len(bm["kicks"])} · 스네어 {len(bm["snares"])} (impacts는 편곡 후 직접 추가)')


if __name__ == '__main__':
    main()
