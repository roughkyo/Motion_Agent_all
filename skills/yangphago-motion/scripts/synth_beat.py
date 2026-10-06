# 붐뱁 힙합 비트 자작 생성기 (외부 샘플 0개 → 저작권 100% 자작)
# 실행: python synth_beat.py --seconds 30 [--bpm 90] [--mood boombap|japan] [--tapestop 마디] [--out music/beat.wav] [--map beatmap.js]
#   --mood japan: 미야코부시 음계(D·Eb·G·A·Bb) 코드 + 코토(현 튕김) 리드 + 타이코 북 (일본 주제용)
#   영상 길이(초)에 맞춰 마디 수를 정하고, 끝은 '2박 정적 → made by 임팩트 → 1마디 뒤 마지막 한 방' (arrange.py와 같은 박 구조)
import sys
import argparse
import json
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile
sys.stdout.reconfigure(encoding='utf-8')     # Windows 콘솔(cp949)에서 한글 출력이 깨지지 않도록

SR = 44100
ap = argparse.ArgumentParser()
ap.add_argument('--seconds', type=float, default=30)
ap.add_argument('--bpm', type=float, default=90)
ap.add_argument('--tapestop', type=int, default=-1)       # 이 마디 후반 2박에 테이프스톱 (-1이면 없음)
ap.add_argument('--mood', default='boombap', choices=['boombap', 'japan'])   # 곡 분위기
ap.add_argument('--out', default='music/beat.wav')
ap.add_argument('--map', default='beatmap.js')
args = ap.parse_args()
BPM = args.bpm
BEAT = 60 / BPM          # 한 박 = 0.6667초
STEP = BEAT / 4          # 16분음표
BAR = BEAT * 4
# arrange.py와 같은 구조: 마지막 한 방 = 끝에서 0.6초 이상 남긴 마디 경계, 임팩트는 그 1마디 전, 정적은 임팩트 직전 2박
# (30초·90BPM → 본문 38박 · 정적 25.33s · 임팩트 26.67s · 마지막 한 방 29.33s)
BARS = max(4, int((args.seconds - 0.6) // BAR))   # 마지막 한 방은 BARS마디 첫 박
OUTRO = BARS - 1                                  # made by 임팩트 마디 (그 직전 2박은 정적)
LEAD_FROM = BARS // 2                             # 리드 벨 시작 마디
TAIL = args.seconds - BARS * 240 / BPM
N = int((BARS * BAR + TAIL) * SR)
SWING = 0.16 * STEP      # 홀수 16분음표를 살짝 늦춰서 붐뱁 특유의 그루브

rng = np.random.default_rng(7)


# ===== 기본 유틸 =====
def tt(n):
    return np.arange(n) / SR


def filt(x, kind, f, order=2):
    # 버터워스 필터 (lowpass / highpass / bandpass)
    sos = butter(order, f, btype=kind, fs=SR, output='sos')
    return sosfilt(sos, x, axis=0)


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def when(bar, step):
    # 마디·16분 위치 → 초 (스윙 반영)
    t = bar * BAR + step * STEP
    if step % 2 == 1:
        t += SWING
    return t


def add(buf, t0, sig, gain=1.0, pan=0.0):
    # 모노/스테레오 신호를 버스에 더하기 (pan: -1 왼쪽 ~ +1 오른쪽)
    i = int(t0 * SR)
    if i >= len(buf):
        return
    if sig.ndim == 1:
        l = np.sqrt(0.5 * (1 - pan))
        r = np.sqrt(0.5 * (1 + pan))
        sig = np.stack([sig * l, sig * r], axis=1) * np.sqrt(2)
    n = min(len(sig), len(buf) - i)
    buf[i:i + n] += sig[:n] * gain


# ===== 악기 합성 =====
def kick(vel=1.0):
    n = int(0.7 * SR)
    t = tt(n)
    f = 46 + 115 * np.exp(-t / 0.032)             # 피치가 뚝 떨어지는 '쿵'
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.34)
    click = filt(rng.standard_normal(n), 'highpass', 2500) * np.exp(-t / 0.003) * 0.35
    return np.tanh(2.4 * (body + click)) * vel


def snare(vel=1.0):
    n = int(0.55 * SR)
    t = tt(n)
    noise = filt(rng.standard_normal(n), 'bandpass', [900, 8500]) * np.exp(-t / 0.14)
    tone = np.sin(2 * np.pi * 182 * t) * np.exp(-t / 0.07) + 0.5 * np.sin(2 * np.pi * 320 * t) * np.exp(-t / 0.04)
    return np.tanh(1.9 * (1.1 * noise + 0.8 * tone)) * vel


def hat(vel=1.0, open_=False):
    n = int((0.45 if open_ else 0.12) * SR)
    t = tt(n)
    x = filt(rng.standard_normal(n), 'highpass', 7200, 4)
    return x * np.exp(-t / (0.17 if open_ else 0.022)) * vel


def rhodes(m, dur, vel=1.0):
    # FM 합성 전자피아노: 때리는 순간 금속성 → 부드럽게 사라짐, 좌우로 흔들리는 트레몰로
    f = mtof(m)
    n = int((dur + 1.0) * SR)
    t = tt(n)
    idx = 1.3 * np.exp(-t / 0.3) + 0.12
    car = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * t))
    tine = 0.18 * np.sin(2 * np.pi * f * 7.02 * t) * np.exp(-t / 0.04)
    amp = np.exp(-t / 1.7) * (1 - np.exp(-t / 0.004))
    rel = np.where(t > dur, np.exp(-(t - dur) / 0.22), 1.0)
    s = (car + tine) * amp * rel * vel
    trem = 0.12 * np.sin(2 * np.pi * 4.2 * t)
    return np.stack([s * (1 + trem), s * (1 - trem)], axis=1)


def bass(m, dur, vel=1.0):
    f = mtof(m)
    n = int((dur + 0.2) * SR)
    t = tt(n)
    s = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t) + 0.12 * np.sin(6 * np.pi * f * t)
    amp = (1 - np.exp(-t / 0.006)) * np.exp(-t / 1.1)
    rel = np.where(t > dur, np.exp(-(t - dur) / 0.05), 1.0)
    return np.tanh(1.6 * s * amp * rel) * vel


def bell(m, dur, vel=1.0):
    # 비브라폰 느낌의 리드 (FM 비율 3.5)
    f = mtof(m)
    n = int((dur + 1.4) * SR)
    t = tt(n)
    idx = 2.2 * np.exp(-t / 0.12)
    s = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * 3.5 * t))
    return s * np.exp(-t / 0.9) * (1 - np.exp(-t / 0.002)) * vel


def koto(m, dur, vel=1.0):
    # 코토 느낌: 배음이 높을수록 빨리 사라지는 현 튕김 + 튕기는 순간 음정이 살짝 높았다가 내려옴
    f = mtof(m)
    n = int((dur + 1.2) * SR)
    t = tt(n)
    bend = 1 + 0.012 * np.exp(-t / 0.05)
    ph = 2 * np.pi * np.cumsum(f * bend) / SR
    s = np.zeros(n)
    for k in range(1, 9):
        s += np.sin(k * ph) * np.exp(-t * (1.5 + 1.8 * k)) / k
    return s * (1 - np.exp(-t / 0.001)) * vel


def taiko(vel=1.0):
    # 타이코: 낮은 가죽 북 '둥' (피치가 조금 내려가며 길게 울림)
    n = int(0.9 * SR)
    t = tt(n)
    f = 62 + 38 * np.exp(-t / 0.06)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.38)
    skin = filt(rng.standard_normal(n), 'lowpass', 900) * np.exp(-t / 0.03) * 0.5
    return np.tanh(1.8 * (body + skin)) * vel


def crash(length=3.0):
    n = int(length * SR)
    t = tt(n)
    x = filt(rng.standard_normal(n), 'highpass', 3800, 3)
    return x * np.exp(-t / 0.95)


def impact():
    # 서브 붐: '쾅' 하는 장면 전환용
    n = int(2.4 * SR)
    t = tt(n)
    f = 32 + 70 * np.exp(-t / 0.08)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.9)
    return np.tanh(2.0 * sub)


# ===== 편곡 =====
drums = np.zeros((N, 2))
music = np.zeros((N, 2))
keys = np.zeros((N, 2))                     # 코드 전용 버스 (저역 정리용)
intro = np.zeros((N, 2))
fx = np.zeros((N, 2))
send = np.zeros((N, 2))                     # 리버브로 보내는 버스

# 코드: Fm9 | Dbmaj9 | Bbm9 | C7(b9)  (도입부 0~1마디는 Bbm9 → C7 → 2마디에서 Fm9로 해결)
CH = [[56, 60, 63, 67], [53, 56, 60, 63], [56, 60, 61, 65], [52, 58, 61, 67]]
ROOT = [41, 37, 34, 36]
LEAD = [
    [(0, 72, 3), (3, 75, 3), (6, 77, 3), (10, 79, 5)],
    [(0, 77, 3), (3, 75, 3), (6, 72, 3), (10, 68, 6)],
    [(0, 73, 3), (3, 72, 3), (6, 70, 3), (10, 72, 5)],
    [(0, 72, 3), (3, 76, 3), (6, 79, 3), (10, 73, 6)],
]

LEAD_SYN = bell
if args.mood == 'japan':
    # 미야코부시(D·Eb·G·A·Bb) 위의 코드: Dm7 | Ebmaj7 | Gm7 | A7(b9)
    CH = [[57, 60, 62, 65], [55, 58, 62, 63], [58, 62, 65, 67], [55, 58, 61, 64]]
    ROOT = [38, 39, 43, 45]
    LEAD = [
        [(0, 74, 3), (3, 75, 3), (6, 74, 2), (8, 70, 2), (10, 69, 6)],
        [(0, 67, 3), (3, 70, 3), (6, 75, 3), (10, 74, 5)],
        [(0, 70, 2), (2, 69, 2), (4, 67, 4), (10, 62, 6)],
        [(0, 63, 3), (3, 62, 3), (6, 69, 3), (10, 70, 6)],
    ]
    LEAD_SYN = koto
    LEAD_FROM = 2                           # 코토는 본문 시작부터

kicks, snares, impacts = [], [], []


def is_silent(bar, step):
    # 29마디 후반 2박: 전부 끊고 정적 → 30마디 'made by' 임팩트
    return bar == OUTRO - 1 and step >= 8


for bar in range(BARS):
    k = (bar - 2) % 4                       # 2마디가 Fm9가 되도록 정렬
    full = bar >= 2

    # --- 코드 (전자피아노) ---
    for step, d, v in [(0, 9, 0.8), (10, 6, 0.55)]:
        if is_silent(bar, step):
            continue
        for j, m in enumerate(CH[k]):
            sig = rhodes(m, d * STEP, v * (0.9 + 0.1 * j / 3))
            add(intro if not full else keys, when(bar, step) + j * 0.006, sig, 0.1)
            add(send, when(bar, step), sig, 0.05)

    if not full:
        continue

    # --- 드럼 ---
    kick_steps = [0, 10] + ([7] if bar % 2 == 1 else [])
    snare_steps = [(4, 1.0), (12, 1.0)] + ([(15, 0.25)] if bar % 2 == 1 else [])
    if bar % 8 == 1 and bar > 2 or bar == BARS - 1:   # 필인: 8마디마다 마지막 박에 스네어 롤
        snare_steps = [(4, 1.0), (12, 1.0), (13, 0.55), (14, 0.7), (15, 0.85)]
        kick_steps = [0, 10, 14]
    for s in kick_steps:
        if is_silent(bar, s):
            continue
        add(drums, when(bar, s), kick(0.95 if s == 0 else 0.8))
        kicks.append(when(bar, s))
    for s, v in snare_steps:
        if is_silent(bar, s):
            continue
        sig = snare(v)
        add(drums, when(bar, s), sig, 0.72)
        add(send, when(bar, s), sig, 0.2)
        if v >= 1.0:
            snares.append(when(bar, s))
    for s in range(0, 16, 2):
        if is_silent(bar, s):
            continue
        open_ = (bar % 4 == 1 and s == 14)
        add(drums, when(bar, s), hat(0.6 if s % 4 == 0 else 0.38, open_), 0.28, 0.25)
    if bar % 4 == 3:
        add(drums, when(bar, 15), hat(0.3), 0.25, -0.2)

    # --- 타이코 (japan): 마디 첫 박 '둥' + 짝수 마디 끝 '둥둥' ---
    if args.mood == 'japan':
        for s in [0] + ([12, 14] if bar % 2 == 1 else []):
            if not is_silent(bar, s):
                add(drums, when(bar, s), taiko(0.8), 0.55, -0.15)

    # --- 베이스 ---
    for s, d, iv in [(0, 5, 0), (7, 2, 0), (10, 4, 0), (14, 2, 7 if k == 3 else 12)]:
        if is_silent(bar, s):
            continue
        add(music, when(bar, s), bass(ROOT[k] + iv, d * STEP, 0.9), 0.5)

    # --- 리드 벨 (최종미션~LCD 구간, 그리고 엔딩) ---
    if LEAD_FROM <= bar < OUTRO - 1 or bar >= OUTRO:
        for s, m, d in LEAD[k]:
            sig = LEAD_SYN(m, d * STEP, 0.8)
            add(music, when(bar, s), sig, 0.11 if LEAD_SYN is bell else 0.2, 0.3)
            add(send, when(bar, s), sig, 0.12)

# --- 장면 전환 효과 ---
TS = args.tapestop
for b in sorted({2, OUTRO} | ({TS + 1} if TS > 0 else set())):   # 리버스 크래시로 빨아들이고 → 크래시
    rc = crash(1.4)[::-1]
    add(fx, b * BAR - len(rc) / SR, rc, 0.32)
    add(fx, b * BAR, crash(), 0.38)
for b in sorted({OUTRO} | ({TS + 1} if TS > 0 else set())):
    add(fx, b * BAR, impact(), 0.8)
    impacts.append(b * BAR)

# 마지막 한 방 (32마디 첫 박)
END = BARS * BAR
add(fx, END, impact(), 0.9)
add(fx, END, crash(3.4), 0.45)
add(drums, END, kick(1.0))
add(drums, END, snare(1.0), 0.7)
for j, m in enumerate(CH[0]):
    add(keys, END + j * 0.01, rhodes(m, 2.6, 0.9), 0.12)
add(music, END, bass(ROOT[0], 2.4, 1.0), 0.5)
kicks.append(END)
snares.append(END)
impacts.append(END)

# ===== 믹싱 =====
# 도입부: 먹먹한 로우패스 (라디오에서 흘러나오는 느낌)
keys += filt(intro, 'lowpass', 650)
keys = filt(keys, 'highpass', 170)        # 킥·베이스 자리를 비워줌
music += keys

# 사이드체인: 킥이 칠 때 음악을 살짝 눌러서 펌핑감
duck = np.ones(N)
for tk in kicks:
    i = int(tk * SR)
    n = min(int(0.35 * SR), N - i)
    duck[i:i + n] -= 0.35 * np.exp(-tt(n) / 0.11)
music *= duck[:, None]

# 리버브: 지수 감쇠 노이즈를 임펄스 응답으로 사용
irn = int(1.8 * SR)
ir = rng.standard_normal((irn, 2)) * np.exp(-tt(irn) / 0.45)[:, None]
ir = filt(ir, 'lowpass', 5000)
wet = np.stack([fftconvolve(send[:, c], ir[:, c])[:N] for c in range(2)], axis=1) * 0.06

# 바이닐 노이즈: 지글지글 + 틱틱
crk = np.zeros(N)
pops = rng.integers(0, N, int(N / SR * 18))
crk[pops] = rng.standard_normal(len(pops)) * 0.6
crk = filt(crk, 'highpass', 1200) + filt(rng.standard_normal(N), 'bandpass', [2000, 7000]) * 0.012
vinyl = np.stack([crk, np.roll(crk, 37)], axis=1) * 0.09

drums = filt(drums, 'lowpass', 11000)
music = filt(music, 'lowpass', 7500)       # 먼지 낀 붐뱁 톤
mix = drums * 1.25 + music + fx + wet + vinyl
mix = filt(mix, 'highpass', 28)

# 테이프스톱: 13마디 후반 2박 동안 테이프가 멈추듯 음정·속도가 떨어짐
t0 = t1 = -1.0
if TS > 0:
    t0 = TS * BAR + 2 * BEAT
    t1 = (TS + 1) * BAR
    i0, i1 = int(t0 * SR), int(t1 * SR)
    tau = np.arange(i1 - i0) / (i1 - i0)
    rate = (1 - tau) ** 1.6
    pos = i0 + np.cumsum(rate)
    for c in range(2):
        mix[i0:i1, c] = np.interp(pos, np.arange(N), mix[:, c]) * (1 - tau ** 3)

# 마스터: 소프트 클립 + 노멀라이즈 + 마지막 한 방 뒤 잔향만 페이드아웃
mix /= np.max(np.abs(mix))
mix = np.tanh(1.4 * mix) / np.tanh(1.4)
fade = max(1, N - int((END + 0.12) * SR))
mix[-fade:] *= np.linspace(1, 0, fade)[:, None] ** 2
mix *= 0.93 / np.max(np.abs(mix))
wavfile.write(args.out, SR, (mix * 32767).astype(np.int16))

# ===== 영상 싱크용 비트맵 =====
beatmap = {
    'bpm': BPM,
    'duration': round(N / SR, 3),
    'kicks': sorted(round(x, 4) for x in kicks if not (t0 <= x < t1)),
    'snares': sorted(round(x, 4) for x in snares if not (t0 <= x < t1)),
    'impacts': [round(x, 4) for x in impacts],
    'tapeStop': [round(t0, 4), round(t1, 4)],
    'gap': [round((OUTRO - 0.5) * BAR, 4), round(OUTRO * BAR, 4)],
}
with open(args.map, 'w', encoding='utf-8') as fp:
    fp.write('window.BEATMAP = ' + json.dumps(beatmap) + ';\n')
print('ok', beatmap['duration'], 's,', len(kicks), 'kicks,', len(snares), 'snares')
