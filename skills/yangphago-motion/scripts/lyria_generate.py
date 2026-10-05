# Gemini Lyria 음악 생성 (선택지 ① AI 생성)
# 실행: python lyria_generate.py --out music/lyria_a.mp3 [--model lyria-3-clip-preview | lyria-3.5] [--prompt "..."]
#       python lyria_generate.py --check   → 키가 준비됐는지만 확인 (키 값은 절대 출력하지 않음)
#   API 키: 스킬 폴더의 .env (GEMINI_API_KEY=...) → 없으면 환경변수 GEMINI_API_KEY
#   사용자가 .env에 직접 붙여넣는다. 채팅으로 키를 받거나 .env 내용을 열어 보지 말 것
#   요금: clip(약 30초) $0.04 / song $0.08, 무료 등급 없음 · 결과물에 SynthID 워터마크 포함
#   BPM은 파라미터가 아님 → 프롬프트에 "90 BPM"을 쓰고, 생성 후 beat_grid.py로 실제 박자를 측정
import argparse
import base64
import os
import subprocess
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')     # Windows 콘솔(cp949)에서 한글 출력이 깨지지 않도록

DEFAULT_PROMPT = (
    "Instrumental urban hip hop beat, 90 BPM, heavy boom bap drums, punchy kick, crisp snare, "
    "deep sub bass, dark minimal synth, vinyl texture, trendy and confident, no vocals. "
    "[0:00-0:04] intro with filtered drums, [0:04-0:26] full beat, [0:26-0:28] drop out silence, "
    "[0:28-0:30] one final heavy hit."
)


def find_audio(obj):
    # 응답 구조가 버전마다 조금 달라서, output_audio → outputs[*] 순서로 오디오 데이터를 찾음
    au = getattr(obj, 'output_audio', None)
    if au is not None and getattr(au, 'data', None):
        return au.data
    for o in getattr(obj, 'outputs', None) or []:
        if getattr(o, 'type', '') == 'audio' and getattr(o, 'data', None):
            return o.data
    return None


ENV = Path(__file__).resolve().parent.parent / '.env'


def load_key():
    # 스킬 폴더 .env 우선, 비어 있으면 환경변수
    if ENV.exists():
        for line in ENV.read_text(encoding='utf-8').splitlines():
            k, _, v = line.partition('=')
            if k.strip() == 'GEMINI_API_KEY' and v.strip():
                return v.strip().strip('"\'')
    return os.environ.get('GEMINI_API_KEY', '').strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out')
    ap.add_argument('--model', default='lyria-3-clip-preview')
    ap.add_argument('--prompt', default=DEFAULT_PROMPT)
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()

    key = load_key()
    if not key:
        print(f'KEY MISSING → 사용자에게 안내: "{ENV}" 파일을 메모장으로 열어 GEMINI_API_KEY= 뒤에 키를 붙여넣고 저장해 주세요.')
        sys.exit(1)
    if a.check:
        print('KEY READY')
        return
    if not a.out:
        sys.exit('--out 경로가 필요합니다')

    from google import genai
    client = genai.Client(api_key=key)
    print(f'생성 중… model={a.model}')
    it = client.interactions.create(model=a.model, input=a.prompt)
    data = find_audio(it)
    if data is None:
        sys.exit(f'응답에서 오디오를 찾지 못함: {str(it)[:500]}')
    raw = base64.b64decode(data) if isinstance(data, str) else data

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(raw)
    print(f'저장: {out} ({len(raw) / 1024:.0f} KB)')

    # 바로 박자 측정 → 스토리보드의 bpm 칸과 편곡 기준값으로 사용
    beat_grid = Path(__file__).with_name('beat_grid.py')
    subprocess.run([sys.executable, str(beat_grid), str(out)])


if __name__ == '__main__':
    main()
