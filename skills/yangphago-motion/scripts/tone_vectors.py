# 컬러 벡터(Pixabay 등)를 영상 색감에 맞는 3색 그라데이션(그림자 → 강조색 → 하이라이트)으로 재채색
# 실행: python tone_vectors.py 이미지1.png 이미지2.png ... [--palette storyboard.json]  →  같은 폴더에 *_duo.png
#   --palette 생략 시 기본 색감(어두운 보라 → 형광 퍼플 → 화이트)
#   palette가 있으면: 하이라이트 = bg·main 중 밝은 색, 그림자 = 어두운 색을 강조색 쪽으로 24% 섞은 색
import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image
sys.stdout.reconfigure(encoding='utf-8')     # Windows 콘솔(cp949)에서 한글 출력이 깨지지 않도록

DEFAULT_STOPS = [(0.0, (42, 8, 70)), (0.5, (176, 38, 255)), (1.0, (244, 244, 240))]


def hex_rgb(h):
    h = h.strip().lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def palette_stops(path):
    # storyboard.json의 palette로 그라데이션 3색을 만든다 (palette가 없으면 기본값)
    pal = json.loads(Path(path).read_text(encoding='utf-8')).get('palette')
    if not pal:
        print('palette 없음 → 기본 색감 사용')
        return DEFAULT_STOPS
    bg, main, accent = hex_rgb(pal['bg']), hex_rgb(pal['main']), hex_rgb(pal['accent'])
    # 밝기 순으로 그림자·하이라이트를 정해야 밝은 배경 테마에서도 네거티브처럼 뒤집히지 않는다
    lum = lambda c: 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]
    dark, light = sorted((bg, main), key=lum)
    shadow = tuple(round(d + (a - d) * 0.24) for d, a in zip(dark, accent))
    return [(0.0, shadow), (0.5, accent), (1.0, light)]


def gradient(v, stops):
    # 밝기(0~1)를 3색 그라데이션으로 변환
    out = np.zeros(v.shape + (3,))
    for (a, ca), (b, cb) in zip(stops, stops[1:]):
        m = (v >= a) & (v <= b)
        k = ((v[m] - a) / (b - a))[:, None]
        out[m] = np.array(ca) * (1 - k) + np.array(cb) * k
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('files', nargs='+')
    ap.add_argument('--palette', help='storyboard.json 경로 (palette 항목 사용)')
    args = ap.parse_args()
    stops = palette_stops(args.palette) if args.palette else DEFAULT_STOPS
    print('stops', [c for _, c in stops])

    for f in map(Path, args.files):
        im = np.asarray(Image.open(f).convert('RGBA')).astype(float) / 255
        rgb, a = im[..., :3], im[..., 3]
        lum = rgb @ np.array([0.299, 0.587, 0.114])
        # 불투명한 부분의 밝기 범위를 0~1로 늘려서 대비 확보
        vis = a > 0.5
        lo, hi = np.percentile(lum[vis], 2), np.percentile(lum[vis], 98)
        v = np.clip((lum - lo) / max(hi - lo, 1e-3), 0, 1)
        col = gradient(v, stops)
        out = np.dstack([col, a * 255]).astype(np.uint8)
        Image.fromarray(out, 'RGBA').save(f.with_name(f.stem + '_duo.png'))
        # 가장 밝은 영역(노트북 화면 등)의 위치 → 그 안에 글자를 띄울 때 좌표로 사용 (키보드가 섞이면 수동 보정)
        ys, xs = np.where(vis & (v > 0.9))
        if len(xs):
            print(f.name, 'bright bbox (x0,y0,x1,y1)', xs.min(), ys.min(), xs.max(), ys.max(), '/ size', im.shape[1], im.shape[0])
        print('saved', f.stem + '_duo.png', 'lum range', round(lo, 3), round(hi, 3))


if __name__ == '__main__':
    main()
