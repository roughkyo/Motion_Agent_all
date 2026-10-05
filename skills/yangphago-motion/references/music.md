# 음악 준비 (4가지 선택지)

공통 목표: 어반 힙합 / 붐뱁, 묵직하고 트렌디, **보컬 없음**, 85~95 BPM(기본 90). 결과물은 `music/final.wav` + `beatmap.js`.
후보는 모두 `music/candidates/`에 저장하고 스토리보드 페이지의 🎧 미리듣기 카드로 보여 준 뒤 사용자가 고른다.

| 선택지 | 소요 | 토큰 | 비용 | 박자 정확도 | 음악 품질 | 저작권 |
|---|---|---|---|---|---|---|
| ⓪ 스킬 라이브러리 곡 (`assets/music/library.json`) | **수 초** | 약 1천 | 무료 | 측정값 저장됨 | 검증된 곡 | 검증 완료 (콘텐츠 ID 없음) |
| ① Pixabay 검색 | 3~5분 | 5천~8천 | 무료 | beat_grid로 측정 (r ≥ 0.4면 신뢰, 후보 절반 탈락 사례) | **가장 풍부** (실제 프로듀서 곡) | Pixabay 라이선스, **콘텐츠 ID 등록 곡은 유튜브 알림 가능** |
| ② Gemini Lyria 생성 | 1~3분 | 약 3천 | 클립 $0.04 · 곡 $0.08 | beat_grid로 측정 | 높음, 분위기를 글로 주문 | 생성물 사용 가능, SynthID 워터마크 |
| ③ Python 합성 (`synth_beat.py`) | 수 초~1분 | 약 1천 | 무료 | **완벽** (박자를 직접 만듦) | 단순 반복, 길수록 단조로움 | 완전 자유 |
| ④ 레퍼런스 영상 음원 그대로 | 즉시 | 약 1천 | — | beat_grid로 측정 | 원곡 그대로 | **라이선스 확인된 경우만**. 교실 수업 내 상영은 저작권법 제25조 범위일 수 있으나 공개 게시(유튜브 등)는 불가 |
(시간·토큰은 30초 영상, 사용자 응답 대기 제외 대략치 — 2026-10-05 실측 기반. SKILL.md 접수 질문의 description과 같은 값을 유지)

## ① Pixabay 검색
1. 내장 브라우저로 `https://pixabay.com/ko/music/search/boom%20bap/` 열기 → 쿠키 배너는 **"모두 거부"**
2. 같은 탭에서 아래 JS 실행 → 검색 결과 링크 수집 → 곡 페이지마다 콘텐츠 ID 검사 + mp3 주소 추출
```js
const qs = ['boom%20bap', 'urban%20hip%20hop', 'hip%20hop%20beat%20dark'];
const links = new Map();
await Promise.all(qs.flatMap(q => [1, 2].map(async pg => {
  const h = await (await fetch(`/ko/music/search/${q}/?pagi=${pg}`)).text();
  for (const m of h.matchAll(/href="(\/ko\/music\/[^"\/]+-(\d+)\/)"/g)) links.set(m[2], m[1]);
})));
const clean = [];
await Promise.all([...links].slice(0, 60).map(async ([id, u]) => {
  try {
    const h = await (await fetch(u)).text();
    if (h.includes('콘텐츠 ID 등록됨')) return;               // 유튜브 저작권 알림 위험 곡 제외
    const title = (h.match(/<title>([^<]+)/) || [, ''])[1].split('|')[0].trim();
    const mp3 = (h.match(/https:\/\/cdn\.pixabay\.com\/(?:download\/)?audio\/[^"'\s]+\.mp3/) || [])[0];
    clean.push({ id, title, u: decodeURIComponent(u), mp3 });
  } catch (e) {}
}));
clean
```
3. 제목·길이·분위기로 3~5곡 추리기 (영상 길이보다 긴 곡, 보컬 없는 곡). mp3가 비어 있으면 곡 페이지의 다운로드 버튼 주소를 확인
4. 후보 다운로드 (사용자에게 "후보 N곡을 미리듣기용으로 내려받겠다"고 한 줄 알리고 진행):
   `curl -sSL -A "Mozilla/5.0" -o music/candidates/p1.mp3 "<mp3 주소>"`
5. 각 후보 `python beat_grid.py music/candidates/p1.mp3` → BPM·첫 다운비트·마디 에너지 표 확인
- 경험치: 붐뱁 태그 곡은 콘텐츠 ID 등록 비율이 높음. "urban hip hop", "lofi hip hop beat"까지 넓히면 미등록 곡을 찾기 쉬움
- 지난 작업 채택곡: Urban Hip Hop Beat — 331music (90 BPM, 111초)

## ② Gemini Lyria 생성
- 공식 문서: https://ai.google.dev/gemini-api/docs/music-generation (모델명·요청 형식 변경 시 확인)
- 키: 스킬 폴더 **`.env`** 의 `GEMINI_API_KEY=` (비어 있으면 환경변수 GEMINI_API_KEY 사용)
  - 확인: `python scripts/lyria_generate.py --check` → `KEY READY` / `KEY MISSING` (키 값은 출력하지 않음)
  - MISSING이면 사용자에게 안내: `.env`를 메모장으로 열어 `GEMINI_API_KEY=` 뒤에 키 붙여넣고 저장 (발급: https://aistudio.google.com/apikey)
  - **채팅으로 키를 받지 말고, .env 내용을 열어 보지 말 것**
- 실행: `python scripts/lyria_generate.py --out music/candidates/l1.mp3 [--model lyria-3-clip-preview | lyria-3.5] --prompt "..."`
  - `lyria-3-clip-preview`: 약 30초 클립 · `lyria-3.5`: 더 긴 곡
  - 프롬프트에 BPM·악기·분위기·**no vocals**·구간 태그 `[0:00-0:04] intro ...` 를 넣음 (BPM 파라미터는 없음 → 측정 필수)
  - 출력 44.1kHz 스테레오. 응답 구조는 `interaction.output_audio.data`(base64). 생성 직후 beat_grid 자동 실행
- 2~3개 프롬프트로 후보를 만들어 미리듣기 카드에 올림 (비용 미리 알림: 클립 3개 ≈ $0.12)

## ③ Python 합성
`python scripts/synth_beat.py --seconds 30 [--bpm 90] [--tapestop 마디] --out music/final.wav --map beatmap.js`
- 마디 수 = round((초−2)/(240/BPM)), 8마디마다 필, 중간부터 리드, 엔딩 2박 정적(gap) → 임팩트 → 2마디 뒤 마지막 한 방
- beatmap에 kicks·snares·impacts·gap이 정확히 들어감 → 편곡 없이 바로 템플릿 사용
- 미리듣기 후보로도 올릴 수 있음 (예: 85/90/95 BPM 세 가지를 candidates/에 생성)

## ④ 레퍼런스 음원
`ffmpeg -i ref.mp4 -vn -ac 2 -ar 44100 music/candidates/ref.wav` → beat_grid. 라이선스 확인 전에는 **분석용으로만** 사용.

## 편곡: 고른 곡 → 영상 길이에 맞추기 (①②④) — 명령 한 줄
`python scripts/arrange.py <곡> --seconds <길이> [--beat B --down0 D --outro-bar N]` → `music/final.wav` + `beatmap.js`
- 구조: 첫 다운비트부터 본문 → 2박 정적 + 리버스 크래시 → 임팩트(원곡의 저음이 가장 센 마디, `--outro-bar`로 지정 가능) → 1마디 뒤 마지막 한 방 → 페이드
- `--beat/--down0`을 생략하면 beat_grid로 자동 측정 (약 +2초). 라이브러리 곡은 library.json 값을 넘김
- 새로 검증한 곡은 `assets/music/`에 복사하고 `library.json`에 한 줄 추가 → 다음부터 검색 생략
- 클리핑 확인이 필요하면: `ffmpeg -i music/final.wav -af volumedetect -f null -` (max_volume > -0.5dB면 문제)
