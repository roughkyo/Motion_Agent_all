# 브라우저 스토리보드 생성기 (storyboard.json 하나로 장면 코드·키프레임·설명·음악 미리듣기를 모두 만듦)
# 실행: python make_storyboard.py storyboard.json [--page motion.html] [--out storyboard] [--beatmap beatmap.js]
#   1) scenes[].beats로 시작·끝 박을 누적 계산 → scenes.js (motion.html이 읽어서 그대로 그림)
#   2) 키프레임 자동 선택(장면당 2장 + 엔딩 3장, frames를 적으면 그 값 사용) → render.js stills
#   3) <out>/index.html (음악 카드 + 장면표) + <out>/contact.jpg (검수용 한 장 시트)
# storyboard.json 구조 (README: SKILL.md 5단계):
# {"title": "...", "style": "A 미니멀 키네틱",
#  "fonts": {"title": "P9", "body": "P6"},   ← 생략 시 D(티몬몬소리)/S(나눔스퀘어). 선택지: D S P5 P6 P7 P8 P9
#  "palette": {"bg": "#070707", "main": "#F4F4F0", "accent": "#B026FF", "sub": "#D9A3FF"},  ← 생략 시 기본 색감
#  "outro": "made by yangphago",   ← "" 이면 엔딩 없음
#  "music": [{"id": "m1", "label": "곡 — 작가", "src": "music/candidates/p1.mp3", "bpm": 90, "note": "...",
#             "contentId": false, "recommended": true, "source": "Pixabay | Lyria | 합성"}],
#  "scenes": [{"title": "훅", "desc": "...", "beats": 4, "bg": "black" | [[0,"white"],[1.25,"black"]],
#              "items": [{"fn": "typeT", "text": "센서가 말을 건다", "size": 110}], "motion": "...", "frames": [초…]}]}
import argparse
import html
import json
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.stdout.reconfigure(encoding='utf-8')
HERE = Path(__file__).parent

CSS = """
:root{--bg:#0b0b0d;--card:#151518;--line:#26262b;--fg:#f4f4f0;--mut:#8b8b93;--pu:#b026ff;--pu2:#d9a3ff}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.6 'Pretendard','Malgun Gothic',sans-serif}
.wrap{max-width:1280px;margin:0 auto;padding:32px 16px 80px}
h1{font-size:30px;margin:0 0 6px}h2{font-size:18px;margin:40px 0 14px;color:var(--pu2);letter-spacing:.04em}
.meta{color:var(--mut)}.meta b{color:var(--fg)}
.music{display:grid;grid-template-columns:repeat(auto-fill,minmax(360px,1fr));gap:14px}
.mc{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px}
.mc.rec{border-color:var(--pu);box-shadow:0 0 0 1px var(--pu) inset}
.mc .t{font-weight:700;font-size:16px}.mc .n{color:var(--mut);font-size:13px;margin:4px 0 10px}
.mc audio{width:100%}
.tag{display:inline-block;font-size:11px;padding:1px 8px;border-radius:99px;margin-right:4px;border:1px solid var(--line);color:var(--mut)}
.tag.pu{border-color:var(--pu);color:var(--pu2)}.tag.warn{border-color:#ff5a5a;color:#ff8a8a}.tag.ok{border-color:#3ddc84;color:#7ff0b0}
table{width:100%;border-collapse:collapse;background:var(--card);border-radius:12px;overflow:hidden}
th{background:#1d1d22;color:var(--pu2);font-size:13px;text-align:left;padding:10px 12px}
td{border-top:1px solid var(--line);padding:12px;vertical-align:top}
td.no{font-weight:800;font-size:22px;color:var(--pu);width:56px;text-align:center}
td.tm{white-space:nowrap;color:var(--mut);width:110px;font-variant-numeric:tabular-nums}
.th{display:flex;gap:8px;flex-wrap:wrap}
.th figure{margin:0;position:relative;cursor:zoom-in}
.th img{width:240px;aspect-ratio:16/9;object-fit:cover;border-radius:6px;display:block;border:1px solid var(--line)}
.th figcaption{position:absolute;left:6px;top:6px;background:var(--pu);color:#000;font:700 11px monospace;padding:1px 6px;border-radius:4px}
td.ds .tt{font-weight:700;font-size:16px;margin-bottom:4px}td.ds .mo{color:var(--mut);font-size:13px;margin-top:6px}
#lb{position:fixed;inset:0;background:#000d;display:none;align-items:center;justify-content:center;cursor:zoom-out}
#lb img{max-width:94vw;max-height:90vh}
@media(max-width:760px){.th img{width:100%}td.tm{width:auto}table,tbody,tr,td{display:block}th{display:none}td.no{text-align:left}}
"""

JS = """
// 로컬 음원은 http.server가 Range 요청을 지원하지 않아 탐색(seek)이 안 됨 → blob으로 받아서 재생
document.querySelectorAll('audio[data-local]').forEach(a=>{
  fetch(a.dataset.local).then(r=>r.blob()).then(b=>{a.src=URL.createObjectURL(b)}).catch(()=>{a.src=a.dataset.local});
});
// 한 곡을 재생하면 나머지는 멈춤
document.addEventListener('play',e=>{document.querySelectorAll('audio').forEach(a=>{if(a!==e.target)a.pause()})},true);
const lb=document.getElementById('lb');
document.querySelectorAll('.th img').forEach(i=>i.onclick=()=>{lb.querySelector('img').src=i.src;lb.style.display='flex'});
lb.onclick=()=>lb.style.display='none';
"""


def contrast(a, b):
    # WCAG 대비율 (1~21). 글자 4.5 이상, 큰 글자·강조 3 이상이면 읽힘
    def lum(h):
        cs = []
        for i in (1, 3, 5):
            c = int(h[i:i + 2], 16) / 255
            cs.append(c / 12.92 if c <= .03928 else ((c + .055) / 1.055) ** 2.4)
        return .2126 * cs[0] + .7152 * cs[1] + .0722 * cs[2]
    hi, lo = sorted((lum(a), lum(b)), reverse=True)
    return (hi + .05) / (lo + .05)


def check_palette(pal):
    # 4색을 #RRGGBB로 정리하고, 가독성이 떨어지는 조합은 경고만 한다
    out = {}
    for k in ('bg', 'main', 'accent', 'sub'):
        h = str(pal.get(k, '')).strip()
        if re.fullmatch(r'#[0-9a-fA-F]{3}', h):
            h = '#' + ''.join(c * 2 for c in h[1:])
        if not re.fullmatch(r'#[0-9a-fA-F]{6}', h):
            # stderr는 cp949 콘솔에서 한글이 깨지므로 stdout으로 출력 후 종료
            print(f'✗ palette.{k} = "{h}" → #RRGGBB 형식으로 적어 주세요 (bg·main·accent·sub 4개 모두 필요)')
            sys.exit(1)
        out[k] = h.upper()
    # main은 글자색이자 반전 배경이므로 bg·main 양쪽 위에서 강조색이 보여야 한다
    checks = [('main', 'bg', 4.5, '본문 글자'), ('accent', 'bg', 3, '배경 위 강조색'),
              ('accent', 'main', 3, '반전 배경 위 강조색'), ('sub', 'bg', 3, '배경 위 보조색')]
    for a, b, need, what in checks:
        r = contrast(out[a], out[b])
        mark = '✓' if r >= need else '⚠'
        print(f'{mark} 대비 {what} {a}/{b} = {r:.1f} (권장 {need} 이상)')
    return out


def esc(s):
    return html.escape(str(s if s is not None else ''))


def mmss(sec):
    return f'{int(sec // 60)}:{sec % 60:05.2f}'


def music_html(m, up):
    src = m.get('src', '')
    # 원격(CDN) 음원은 탐색이 안 될 수 있음 → 가능하면 music/candidates/에 내려받아 로컬로 사용
    if src.startswith('http'):
        audio = f'<audio controls preload="none" src="{esc(src)}"></audio>'
    else:
        audio = f'<audio controls data-local="{esc(up + src)}"></audio>'
    tags = []
    if m.get('source'):
        tags.append(f'<span class="tag">{esc(m["source"])}</span>')
    if m.get('bpm'):
        tags.append(f'<span class="tag">{esc(m["bpm"])} BPM</span>')
    if m.get('contentId') is True:
        tags.append('<span class="tag warn">콘텐츠 ID 등록됨</span>')
    elif m.get('contentId') is False:
        tags.append('<span class="tag ok">콘텐츠 ID 없음</span>')
    if m.get('recommended'):
        tags.append('<span class="tag pu">추천</span>')
    cls = 'mc rec' if m.get('recommended') else 'mc'
    return (f'<div class="{cls}"><div class="t">{esc(m.get("id", ""))}. {esc(m.get("label", ""))}</div>'
            f'<div>{"".join(tags)}</div><div class="n">{esc(m.get("note", ""))}</div>{audio}</div>')


def scene_html(no, s):
    # 키프레임마다 타임코드 배지
    figs = ''.join(f'<figure><img src="frames/s_{f}.png" alt=""><figcaption>{float(f):.2f}s</figcaption></figure>'
                   for f in s['frames'])
    extra = ' · '.join(x for x in [s.get('motion'), s.get('beat')] if x)
    mo = f'<div class="mo">{esc(extra)}</div>' if extra else ''
    return (f'<tr><td class="no">{no}</td><td class="tm">{esc(s["time"])}</td>'
            f'<td><div class="th">{figs}</div></td>'
            f'<td class="ds"><div class="tt">{esc(s.get("title", ""))}</div>{esc(s.get("desc", ""))}{mo}</td></tr>')


def read_beatmap(path):
    m = re.search(r'=\s*(\{.*\})', Path(path).read_text(encoding='utf-8'), re.S)
    return json.loads(m.group(1))


def contact(paths, out, cols=6, w=384):
    # 검수용 한 장 시트: 이미지 여러 장을 따로 여는 것보다 토큰이 훨씬 적음
    h = w * 9 // 16
    rows = (len(paths) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * w, rows * h), (40, 40, 40))
    d = ImageDraw.Draw(sheet)
    for i, (label, p) in enumerate(paths):
        x, y = i % cols * w, i // cols * h
        if Path(p).exists():
            sheet.paste(Image.open(p).convert('RGB').resize((w, h)), (x, y))
        d.rectangle([x, y, x + 70, y + 18], fill=(176, 38, 255))
        d.text((x + 4, y + 3), label, fill=(0, 0, 0))
    sheet.save(out, quality=80)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('json')
    ap.add_argument('--page', default='motion.html')
    ap.add_argument('--out', default='storyboard')
    ap.add_argument('--beatmap', default='beatmap.js')
    a = ap.parse_args()
    sb = json.loads(Path(a.json).read_text(encoding='utf-8'))
    bm = read_beatmap(a.beatmap)
    bt = 60 / bm['bpm']
    out = Path(a.out)
    (out / 'frames').mkdir(parents=True, exist_ok=True)

    # 1) 장면 시간 누적 계산 → scenes.js
    scenes, cur = [], 0.0
    for s in sb.get('scenes', []):
        s = dict(s)
        s['from'], s['to'] = cur, cur + s['beats']
        cur = s['to']
        s['time'] = f'{mmss(s["from"] * bt)}-{mmss(s["to"] * bt)}'
        if not s.get('frames'):
            ln = s['beats']
            s['frames'] = [round((s['from'] + ln * .5) * bt, 2), round((s['from'] + ln * .8) * bt, 2)]   # 퇴장 전 상태가 보이도록
        scenes.append(s)
    gap0 = bm.get('gap', [bm['duration'] - 10 * bt])[0]
    # outro가 ""(또는 false)이면 엔딩 없음 → 본문이 영상 끝까지
    no_outro = sb.get('outro', 'made by yangphago') in ('', False, None)
    end0 = bm['duration'] if no_outro else gap0
    if no_outro:
        imps = ', '.join(f'{x / bt:.1f}박' for x in bm.get('impacts', []))
        print(f'ℹ 엔딩 없음: 본문 {end0 / bt:.1f}박 · 음악 정적 {gap0 / bt:.1f}박~ · 임팩트 {imps} → 마지막 장면을 임팩트에 맞추세요')
    if cur * bt > end0 + .01:
        print(f'⚠ 장면 합계 {cur}박({cur * bt:.2f}s)이 본문 끝({end0:.2f}s)을 넘음 → 넘친 부분은 잘림. beats를 줄이세요')
    elif end0 - cur * bt > bt:
        print(f'ℹ 본문 끝까지 {end0 - cur * bt:.2f}s 남음 → 마지막 장면이 그만큼 길게 유지됨')
    js = [{k: s[k] for k in ('from', 'to', 'bg', 'items', 'draw') if k in s} for s in scenes]
    for s in js:
        s.setdefault('bg', 'black')
        s.setdefault('items', [])
    # 글꼴 선택(fonts.title / fonts.body: D·S·P5~P9)도 함께 기록 → 템플릿이 읽음
    fonts = sb.get('fonts', {})
    head = ''.join(f'window.FONT_{k.upper()} = {json.dumps(fonts[k])};\n' for k in ('title', 'body') if fonts.get(k))
    # 엔딩 문구(outro): "윗줄|큰 글자" 또는 "made by ○○" → 두 줄, 그 외는 큰 글자 한 줄
    outro = sb.get('outro', 'made by yangphago')
    if not isinstance(outro, str):
        outro = 'made by yangphago'
    if '|' in outro:
        top, word = outro.split('|', 1)
    elif outro.lower().startswith('made by '):
        top, word = outro[:7], outro[8:]
    else:
        top, word = '', outro
    head += f'window.OUTRO_TOP = {json.dumps(top.strip(), ensure_ascii=False)};\n'
    head += f'window.OUTRO_WORD = {json.dumps(word.strip(), ensure_ascii=False)};\n'
    if no_outro:
        head += 'window.NO_OUTRO = true;\n'
    # 색감(palette): 생략하면 템플릿 기본 색(블랙·화이트·퍼플)
    if sb.get('palette'):
        head += f'window.PALETTE = {json.dumps(check_palette(sb["palette"]))};\n'
    Path(a.page).with_name('scenes.js').write_text(head + 'window.SCENES = ' + json.dumps(js, ensure_ascii=False) + ';\n', encoding='utf-8')

    # 엔딩 행 자동 추가 (gap → 임팩트 → 마지막 한 방)
    imps = bm.get('impacts') or [gap0 + 2 * bt, bm['duration'] - .5]
    if not no_outro:
        scenes.append({'title': '엔딩', 'desc': f'2박 정적 → 임팩트 → "{outro.replace("|", " ")}" 낙하 → 마지막 한 방',
                       'time': f'{mmss(gap0)}-{mmss(bm["duration"])}', 'motion': 'outro (고정)',
                       'frames': [round(imps[0] + .6, 2), round(imps[0] + 3.2 * bt, 2), round(imps[-1] + .2, 2)]})

    # 2) 키프레임 캡처 (파일명 = 초 문자열 → img src와 일치)
    times = [str(f) for s in scenes for f in s['frames']]
    subprocess.run(['node', str(HERE / 'render.js'), 'stills', a.page, str(out / 'frames'), *times], check=True)
    contact([(f'{s_i + 1}-{f}', out / 'frames' / f's_{f}.png') for s_i, s in enumerate(scenes) for f in s['frames']],
            out / 'contact.jpg')

    # 3) 스토리보드 페이지
    up = '../' * len(out.parts)                        # index.html → 프로젝트 루트
    music = sb.get('music', [])
    title = esc(sb.get('title', '스토리보드'))
    music_sec = ''
    if music:
        music_sec = f'<h2>🎧 음악 후보 미리듣기</h2><div class="music">{"".join(music_html(m, up) for m in music)}</div>'
    doc = f"""<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title>
<style>{CSS}</style></head><body><div class="wrap">
<h1>{title}</h1>
<div class="meta">길이 <b>{bm['duration']:g}초</b> · {bm['bpm']:g} BPM · 16:9 · 스타일 <b>{esc(sb.get('style', ''))}</b> · 장면 <b>{len(scenes)}개</b></div>
{music_sec}
<h2>🎬 스토리보드</h2>
<table><thead><tr><th>장면</th><th>시간</th><th>키프레임</th><th>설명</th></tr></thead>
<tbody>{''.join(scene_html(i + 1, s) for i, s in enumerate(scenes))}</tbody></table>
<p class="meta" style="margin-top:24px">음악 번호와 수정할 장면 번호를 채팅으로 알려 주세요. 승인 후 최종 렌더를 시작합니다.</p>
</div><div id="lb"><img alt=""></div><script>{JS}</script></body></html>"""
    (out / 'index.html').write_text(doc, encoding='utf-8')
    print(f'→ {out / "index.html"} · scenes.js · 검수 시트 {out / "contact.jpg"} (키프레임 {len(times)}장)')


if __name__ == '__main__':
    main()
