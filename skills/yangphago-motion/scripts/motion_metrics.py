"""렌더된 mp4의 역동성 측정 → 레퍼런스(IoT 30초) 기준과 비교

사용: python motion_metrics.py <영상.mp4> [--until 25.3] [--ref 레퍼런스.mp4]
  --until : 본문 끝(초). 엔딩은 기준이 달라 빼고 잰다 (beatmap.js gap[0], 30초·90BPM이면 25.33)
  --ref   : 비교할 영상이 있으면 같은 지표를 나란히 출력하고 프레임별 상관을 계산

지표 (640×360으로 줄여서 매 프레임 측정):
  요소 수   화면에 떨어져 있는 덩어리(글자 묶음·아이콘·도형) 개수의 중앙값 → 텍스트만 있으면 1~2
  윤곽 밀도 경계선 픽셀 비율 → 도형·아이콘·표가 많을수록 높음
  정지 비율 직전 프레임과 거의 같은 프레임 비율 → 높을수록 멈춰 있음
  빈 구간   요소 3개 이하가 1초 넘게 이어진 구간
기준값 = 레퍼런스 실측(요소 16 · 윤곽 2.78% · 정지 37%)에서 여유를 둔 선. 스킬 v1 텍스트형 결과는 요소 1 · 윤곽 0.86% · 정지 76%
"""
import argparse
import subprocess
import sys

import numpy as np
from scipy import ndimage

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
W, H = 640, 360
TARGET = {'comps': 10, 'edge': .02, 'still': .45}


def frames(src):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', src, '-vf', f'scale={W}:{H}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)


def measure(src, until):
    fr = frames(src)
    n = len(fr) if not until else min(len(fr), int(until * 30))
    comps, edge, diff, pur = [], [], [], []
    prev = None
    for f in fr[:n].astype(np.float32):
        R, G, B = f[..., 0], f[..., 1], f[..., 2]
        luma = .299 * R + .587 * G + .114 * B
        fg = luma > 45 if luma.mean() < 128 else luma < 200       # 흰 배경이면 어두운 것이 전경
        lab, k = ndimage.label(ndimage.binary_dilation(fg[::2, ::2], iterations=2))
        sizes = ndimage.sum(np.ones_like(lab), lab, range(1, k + 1)) if k else []
        comps.append(int(np.sum(np.asarray(sizes) > 30)))
        gy, gx = np.gradient(luma)
        edge.append(float((np.hypot(gx, gy) > 40).mean()))
        mx, mn = f.max(axis=2), f.min(axis=2)
        pur.append(float(((mx - mn) > 110).mean()))          # 채도 높은 픽셀 = 강조색 (팔레트와 무관)
        diff.append(float(np.abs(luma - prev).mean()) if prev is not None else 0)
        prev = luma
    comps = np.array(comps)
    # 빈 구간: 요소 3개 이하가 30프레임(1초) 넘게
    empty, run = [], 0
    for i, c in enumerate(list(comps) + [99]):
        if c <= 3: run += 1
        else:
            if run > 30: empty.append(((i - run) / 30, i / 30))
            run = 0
    return dict(comps=float(np.median(comps)), comps75=float(np.percentile(comps, 75)), edge=float(np.mean(edge)),
                still=float(np.mean(np.array(diff[1:]) < .3)), pur=float(np.mean(pur)), empty=empty,
                series=dict(comps=comps, edge=np.array(edge), diff=np.array(diff), pur=np.array(pur)))


def show(name, m):
    ok = lambda b: '✓' if b else '⚠'
    print(f'{name}')
    print(f'  {ok(m["comps"] >= TARGET["comps"])} 요소 수(중앙) {m["comps"]:.0f}  (75% {m["comps75"]:.0f}) · 기준 {TARGET["comps"]} 이상')
    print(f'  {ok(m["edge"] >= TARGET["edge"])} 윤곽 밀도 {m["edge"]:.2%} · 기준 {TARGET["edge"]:.0%} 이상')
    print(f'  {ok(m["still"] <= TARGET["still"])} 정지 비율 {m["still"]:.0%} · 기준 {TARGET["still"]:.0%} 이하')
    print(f'  · 강조색(고채도) 면적 {m["pur"]:.1%}')
    if m['empty']:
        print('  ⚠ 빈 구간(요소 3개 이하 1초+): ' + ', '.join(f'{a:.1f}~{b:.1f}s' for a, b in m['empty']))
    passed = m['comps'] >= TARGET['comps'] and m['edge'] >= TARGET['edge'] and m['still'] <= TARGET['still'] and not m['empty']
    print('  → ' + ('통과: 레퍼런스 수준의 밀도·움직임' if passed else '미달: 비주얼 부품을 늘리거나 정지 구간에 동작을 추가'))
    return passed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('video')
    ap.add_argument('--until', type=float, default=0)
    ap.add_argument('--ref')
    a = ap.parse_args()
    m = measure(a.video, a.until)
    show(a.video, m)
    if a.ref:
        r = measure(a.ref, a.until)
        show(a.ref, r)
        n = min(len(m['series']['comps']), len(r['series']['comps']))
        for k in ('pur', 'edge', 'diff', 'comps'):
            c = np.corrcoef(m['series'][k][:n], r['series'][k][:n])[0, 1]
            print(f'  프레임별 상관 {k}: {c:.3f}')


if __name__ == '__main__':
    main()
