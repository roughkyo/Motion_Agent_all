---
name: yangphago-motion
description: 양파고(정보 교사) 스타일 모션그래픽 영상 제작. 키네틱 타이포 + 내용과 연결된 아이콘·다이어그램·표·게이지·카드·기기 화면이 박자에 맞춰 유기적으로 등장하는 정보형 영상(HUD·와이프·글리치·카메라 흔들림), 색감 3택(기본 블랙·화이트·형광 퍼플 / AI 추천 / 사용자 지정 4색), 16:9, 어반 힙합/붐뱁 비트 동기화, 엔딩 문구(기본 "made by yangphago", 시작 시 질문). 수업 자료(PPTX·PDF·DOCX)나 주제를 받아 브라우저 스토리보드(키프레임 이미지+설명+음악 미리듣기)로 승인받은 뒤 mp4로 렌더링한다. "모션그래픽 만들어줘", "키네틱 타이포 영상", "수업 소개 영상", "인포그래픽 영상", 레퍼런스 영상을 주며 "이런 느낌으로" 같은 요청에 사용.
---

# yangphago-motion (v2 정보형 키네틱 엔진)

**내가 쓰는 파일은 `storyboard.json` 하나.** 장면 코드·키프레임·스토리보드 페이지·검사·편곡·mp4는 스크립트가 만든다. motion.html은 고치지 않는다.
측정치(30초): 편곡 2초 · 스토리보드+검사 4초 · 렌더 50초. 품질 기준 = `references/analysis/iot30_motion_grammar.md` (레퍼런스를 1/600초 간격 계측)

## 고정 요구사항 (사용자가 바꾸라고 하기 전까지)
1. **텍스트만 나오는 화면 금지.** 장면마다 문구 + 그 문구와 연결된 비주얼(아이콘·노드 흐름·표·게이지·카드·기기 화면·막대·타임라인)이 함께 움직인다. 비주얼 없는 장면은 전체의 20% 이하
2. 색감은 **접수 때 3가지 중 선택** (아래 '색감'). 기본 = 블랙 `#070707` · 화이트 `#F4F4F0` · 형광 퍼플 `#B026FF` · 연보라 `#D9A3FF`. 강조색은 한 화면의 주인공 한두 곳에만
3. 16:9, 1920×1080, 30fps
4. 어반 힙합/붐뱁, 묵직하고 트렌디. 상업적 무료 음원 또는 생성
5. 엔딩 문구는 **접수 때 반드시 질문** (기본 `made by yangphago`, storyboard.json `outro`)
6. 영상 길이는 **반드시 질문** · 7. 레퍼런스 영상을 주면 최대한 비슷하게 · 8. **스토리보드 승인 전 최종 렌더 금지**

## 빠른 작업 순서 (`$SK` = 이 SKILL.md가 있는 폴더 = 스킬 로드 시 표시되는 Base directory)

**1. 접수** — AskUserQuestion은 한 번에 **최대 4문항** → 두 번에 나눠 묻는다.
- 1차: 길이 · 음악 · 스타일+글꼴 · 엔딩 문구
- 2차: **색감**(① 기본 색감: 블랙·화이트·퍼플 / ② AI 추천 색감: 주제에 맞춰 4색 제안 / ③ 직접 지정: 배경·주·강조·보조 색) · 레퍼런스 영상 유무
  - ③을 고르면 채팅으로 이렇게 받는다: "배경 / 주 색깔(글자) / 강조 / 보조 색을 HEX(#1A1A2E)나 색 이름(남색, 크림색…)으로 알려 주세요. 예) 배경 남색, 주 크림색, 강조 주황, 보조 하늘색". 색 이름은 HEX로 바꿔 json에 적고, 무엇으로 바꿨는지 한 줄로 알린다
  - ②는 자료 주제·분위기에서 4색을 골라 **이름+HEX+고른 이유 한 줄**로 제안하고, 스토리보드에서 확인받는다

**음악 질문은 옵션 description에 아래 비교를 그대로 넣는다** (사용자 응답 대기 시간 제외, 30초 영상 기준 실측)
| 옵션(label) | description |
|---|---|
| 라이브러리 곡 (추천) | 수 초 · 토큰 약 1천 · `library.json`의 검증된 곡(현재 3곡: 331music 밝은 붐뱁 / boombap 묵직한 합성 붐뱁 / DesiFreeMusic LP 질감 붐뱁) 중 주제에 맞는 2곡을 편곡해 스토리보드에서 들어 보고 선택 · 박자값 저장됨 · 저작권 확인 완료 |
| 파이썬 합성 | 수 초~1분 · 토큰 약 1천 · 박자 완벽 동기화 · 저작권 완전 자유 · 단, 드럼+코드 단순 반복이라 길수록 단조롭고 '만든 티'가 남 |
| Pixabay 검색 | 3~5분 · 토큰 5천~8천 · 실제 프로듀서 곡이라 질감·분위기 선택 폭이 가장 넓음 · 단, 콘텐츠 ID 확인 필요, 곡에 따라 박자 측정 불안정(후보 절반 탈락 사례) |
| Lyria AI 생성 | 1~3분 · 토큰 약 3천 · **유료**(곡당 약 $0.04~0.08) · Gemini API 키 필요 · 원하는 분위기를 글로 주문 가능, 박자 측정 필요 |
- 질문 문구 예: "음악은 어떻게 할까요? (시간·토큰은 30초 영상 기준 대략치)"
- Pixabay·Lyria로 쓴 곡은 렌더 후 "라이브러리에 추가할까요?"를 묻고, 동의하면 `assets/music/`에 복사 + `library.json`에 beat·down0·outro_bar·라이선스 기록

세부 선택지: 길이(15/30/60초) · 음악(위 표) · **스타일(B 정보형 키네틱 — 기본, 아이콘·도표·HUD / A 미니멀 키네틱 — 큰 글자 위주, HUD 없음)** · 글꼴(기본 티몬몬소리+나눔스퀘어 / 페이퍼로지 — 고르기 어려우면 `assets/fonts/preview.jpg`를 보여 줌) · 레퍼런스 영상 유무 · **"마지막 문구는 무엇으로 해드릴까요?"**(옵션: `made by yangphago`(기본) / 엔딩 없이 본문만 / 직접 입력은 Other로). 요청에 이미 답이 있으면 생략.

**2. 준비** (한 번에 실행)
```bash
mkdir -p fonts music/candidates out && cp "$SK/assets/fonts/"*.ttf fonts/ && cp "$SK/scripts/motion_template.html" motion.html && (npm ls playwright-core >/dev/null 2>&1 || npm ls --prefix "$SK" playwright-core >/dev/null 2>&1 || npm i playwright-core)
```
- 세션 폴더에 이전 작업물이 있으면 덮어쓰지 말고 하위 폴더(`<작업명>/`)를 만들어 그 안에서 실행
- 자료 텍스트는 **반드시** `python "$SK/scripts/extract_text.py" <자료들> --out source.txt` (화면엔 요약만. 직접 `print`하면 Windows cp949 콘솔이 죽는다) → 필요한 부분만 Read (**Wi-Fi 비밀번호·키·개인정보 제외**)

**3. 음악 → `music/final.wav` + `beatmap.js`**
- ⓪ 라이브러리: (GitHub 배포본에는 Pixabay 곡 파일이 없을 수 있음 — `assets/music/`에 없으면 그 곡은 빼고 `boombap.wav`를 쓰거나 사용자가 같은 제목으로 받아 넣게 안내) `library.json` 저장값을 **반드시** 넘긴다: `python "$SK/scripts/arrange.py" "$SK/assets/music/<file>" --seconds <길이> --beat <beat> --down0 <down0> --outro-bar <outro_bar>`
  - 2곡 편곡: 둘째 곡은 `--out music/alt.wav --map music/alt_beatmap.js` → music에 m1·m2. m2가 선택되면 alt 두 파일을 final.wav·beatmap.js로 복사 후 make_storyboard 재실행
  - BPM이 같은 곡끼리 짝지으면 장면 박 수를 그대로 쓸 수 있다 (90BPM: 331music·boombap / 88BPM: DesiFreeMusic)
- ③ 합성: `python "$SK/scripts/synth_beat.py" --seconds <길이> [--mood japan] --out music/final.wav --map beatmap.js` (mood: `boombap` 기본 / `japan`. 박 구조는 arrange와 같음)
- ①② 검색·생성: `references/music.md` → 고른 곡을 arrange.py
- ② Lyria: 먼저 `python "$SK/scripts/lyria_generate.py" --check` → `KEY MISSING`이면 "`$SK/.env` 파일을(없으면 `.env.example`을 복사해 만들고) 메모장으로 열어 `GEMINI_API_KEY=` 뒤에 키를 붙여넣고 저장해 주세요 (발급: https://aistudio.google.com/apikey)"라고 안내하고 기다린다. **키를 채팅으로 받지 말고, .env를 직접 열어 보지 않는다**

**4. 비주얼 기획 → storyboard.json** (가장 중요 — 여기서 '텍스트만'이 되느냐가 갈린다)
1) 자료에서 장면 5~8개 뼈대를 잡는다 (30초 기준 본문 38박 → **장면당 4~6박**, 훅 4박 + 본문 + 결론/경고 4박)
2) 장면마다 **키워드 → 비주얼 비유**를 먼저 정한다 (아래 표). 문구를 정하기 전에 "이 장면에서 무엇이 움직이나"를 고른다
3) `references/components.md`의 **장면 설계 패턴**(훅 · 흐름 · 조각 강조 · 시연 · 입력→검증 · 경고 · 숫자 · 비교 · 단계)에 대입. 완성 예시: `references/examples/iot30.storyboard.json`
4) `python "$SK/scripts/make_storyboard.py" storyboard.json` → **역동성 검사 표**가 나온다. ⚠(비주얼 없음 · 1박에 새 요소 1개 미만 · 2박 넘게 멈춤 · 없는 아이콘)가 있으면 json을 고쳐 재실행 (`--lint`면 키프레임 없이 검사만, 1초)
5) `storyboard/contact.jpg` **한 장만** 열어 겹침·잘림·빈 화면 검수
6) 미리보기: **세션 루트에서** `python "$SK/scripts/preview.py" <작업 폴더(루트면 .)>` → `preview_start {name:"storyboard"}` → `/storyboard/` 보여 주고 **음악 번호 + 수정할 장면**을 묻는다

| 내용 | 비주얼 비유 (부품) |
|---|---|
| 순서·과정·데이터 이동 | `flow` 노드 릴레이 + packet / `steps` / `timeline` / `arrow` |
| 장치·도구·서비스 | `icon`(badge) · `device`(노트북·모니터·휴대폰 화면 타이핑) |
| 기록·결과·목록 | `table`(행 추가 + ✓) · `terminal`(로그 줄) · `tags` |
| 비율·진행·시간 | `gauge`(%, loop 타이머) · `counter` · `bars` |
| 주의·규칙·오류 | `cards` + `glitch` · `cross`(INVALID 도장) · `focus` |
| 비교·선택 | `vs` · 좌우 `icon` + `arrow` |
| 코드·주소·설정값 | `urlbar`(조각 하이라이트) · `codebox` · `typeP` |
| 감정·임팩트 한 방 | `stack`/`fly`/`punch`/`letterDrop` + `rings`·`burst` |

**5. 승인 후 렌더 → 역동성 측정** — 결과물은 **세션 루트의 `outputs/<프로젝트명>/`**
`node "$SK/scripts/render.js" video motion.html music/final.wav <세션루트>/outputs/<프로젝트명>/<프로젝트명>.mp4`
`python "$SK/scripts/motion_metrics.py" <mp4> --until <gap[0]초>` → 요소 수 10↑ · 윤곽 2%↑ · 정지 45%↓ · 빈 구간 없음 (레퍼런스 16 · 2.78% · 37%)
- 미달이면 지적된 구간의 장면에 부품을 추가하고 재렌더. 통과하면 `<프로젝트명>_qa.jpg` **한 장만** 확인 → SendUserFile로 mp4 전달 + 음원·라이선스 한 줄

## storyboard.json (v2)
```json
{"title": "IoT 첫걸음 · 온습도 데이터 온라인 저장", "style": "B 정보형 키네틱", "fonts": {"title": "D", "body": "S"},
 "outro": "made by yangphago", "outro_sub": "IoT 첫걸음 · 온습도 데이터 온라인 저장", "fx": {"hud": "IoT 첫걸음 / 온습도 저장"},
 "music": [{"id": "m1", "label": "Urban Hip Hop Beat — 331music", "src": "music/final.wav", "bpm": 90, "contentId": false, "recommended": true, "source": "라이브러리"}],
 "scenes": [
  {"title": "HOOK", "beats": 4, "items": [
    {"fn": "band"},
    {"fn": "stack", "x": 140, "y": 560, "size": 190, "lines": [["센서값이"], ["구글 시트로", "pu"], ["날아간다"]], "fly": 2},
    {"fn": "icon", "name": "sensor", "x": 1600, "y": 380, "size": 320, "style": "plain"},
    {"fn": "packet", "text": "26·61", "x": 1600, "y": 560, "to": [2100, 300], "n": 1, "d": 1.6, "at": 2}]},
  {"title": "역할 분담", "beats": 6, "head": {"text": "역할 분담", "sub": "4단계 릴레이"}, "items": [
    {"fn": "flow", "y": 480, "nodes": [{"icon": "sensor", "label": "DHT11", "sub": "온습도 측정"}, {"icon": "board", "label": "UNO R4 WiFi", "sub": "Wi-Fi로 전송"},
      {"icon": "cloud", "label": "Apps Script", "sub": "받아서 검사"}, {"icon": "database", "label": "Google Sheet", "sub": "한 줄 기록"}],
     "packet": {"text": "25·60", "at": 2.5}},
    {"fn": "reveal", "text": "센서 값 → Wi-Fi → 구글 서버 → 시트에 한 줄", "y": 900, "size": 46, "font": "S", "at": 3}]}
 ]}
```
- 장면 시간은 `beats`만 쓰면 자동. 장면 beats 합계 = 엔딩 시작 박 (30초·90BPM **38박** · 15초 14박 · 60초 82박 / 88BPM 30초 34박 — arrange·synth 공통). 엔딩 없음(`outro: ""`)이면 길이÷1박 전체(30초 90BPM 45박)
- 부품·옵션·아이콘 77종·자리 이름: **`references/components.md`** (작성 전에 한 번 읽는다)
- **글꼴** `fonts.title`·`fonts.body`: `D`(티몬몬소리) `S`(나눔스퀘어) `P5`~`P9`(페이퍼로지). item `font`는 여기에 `M`(고정폭·코드)
- **색감** `palette`: `{"bg","main","accent","sub"}` 모두 `#RRGGBB`. make_storyboard가 대비율 출력(글자 4.5↑, 강조 3↑ 권장, ⚠면 재제안). AI 추천 예: 일본 여행 → `#1B1B1F` `#F3EDE2` `#E8452C` `#F4A7B9` / 코딩 → `#0D1117` `#E6EDF3` `#3FB950` `#58A6FF`
- **엔딩** `outro`: `"made by ○○"` → 윗줄 + 큰 글자 · `"윗줄|큰 글자"` · 그 외 큰 글자 한 줄 · `""` 엔딩 없음(마지막 장면을 make_storyboard가 출력하는 임팩트 박에 맞춤)

## 박진감 규칙 v2 (레퍼런스 실측 기반 — 반드시 지킴)
- **화면 구성**: 머리글(왼쪽 위 제목 쾅 + 부제) + 본문 비주얼 1~3개 + 작은 라벨들. 큰 글자(100px+)는 화면당 하나, 나머지는 26~46px로 작고 많게 (레퍼런스 글자 크기 중앙 34px)
- **장면 안 리듬**: 0박 머리글 → 0.2~0.5박 첫 비주얼 → **0.3~0.5박마다 새 요소** → 마지막 1~1.5박에 **결론 한 방**(강조색 slam). 2박 넘게 아무것도 새로 나오지 않으면 안 된다
- **장면 길이**: 4~6박. 장면 경계마다 와이프가 자동으로 들어가 컷 리듬을 만든다 (`transition`으로 종류 지정)
- **훅(첫 4박)**: 큰 글자 2~3줄을 박마다 쾅(stack) + 상징 아이콘 + 움직이는 소품(packet·fly). 첫 프레임 플래시는 자동
- **강조색**: 마지막 노드·마지막 카드·결론 문구·핵심 숫자처럼 "도착점"에만
- 흰 배경(`bg: white`)은 전환용으로 짧게만. 레퍼런스 정보형은 0%
- 한 장면에 텍스트 부품만 있으면 make_storyboard가 ⚠ — 의도적으로 멈춘 장면만 `calm: true`

## 스타일
- **B 정보형 키네틱(기본)**: 위 규칙 + fx 기본값(HUD·점 격자·그레인·비네트·와이프·플래시·글리치·흔들림)
- **A 미니멀 키네틱**: `"fx": {"hud": false, "wipe": false, "dots": false, "punch": 0.06}`, 장면마다 큰 글자 한 문구 + 보조 비주얼 1개(icon·rings·sparkle·band) 이상, `bg` 흑백 반전으로 컷 리듬. 텍스트 동작 근거는 `references/style-guide.md` A안 표

## 레퍼런스 영상을 받았을 때
`python "$SK/scripts/analyze_reference.py" ref.mp4 out/ref` → `_sheet.jpg` 한 장 + JSON(hit_gap·holds·bpm) → 장면 골격을 `components.md` 패턴에 매핑
`python "$SK/scripts/motion_metrics.py" <내 결과.mp4> --ref ref.mp4 --until <본문 끝>` → 요소 수·윤곽·정지 비율과 프레임별 상관으로 얼마나 가까운지 확인
샘플 원본 10편은 `assets/samples/videos/` (Envato 라이선스, 배포본에는 없음 → `references/analysis/` 측정값 사용). 음원은 라이선스 확인 전 분석용

## 예상 소요 (30초, 사용자 응답 대기 제외)
| 구간 | 시간 | 토큰 | 가장 많이 드는 것 |
|---|---|---|---|
| ① 접수 → 미리보기 | 라이브러리·합성 **6~10분** / Pixabay **11~17분** | 3만~5만 | storyboard.json 설계(비주얼 기획)·자료 읽기 |
| ② 승인 → mp4 + 측정 | **2~3분** (60초 영상은 약 2배) | 3천~5천 | 렌더 50초 + 측정 20초 |
| 수정 1회 | 2~4분 | 5천~1만 | json 수정 → 검사·키프레임 → 재렌더 |

## 토큰·시간 절약 규칙
- 이미지 검수는 **contact.jpg / _qa.jpg 한 장씩**. 개별 stills는 문제 장면을 확대할 때만
- 수정은 json만 고치고 make_storyboard 재실행 (motion.html은 건드리지 않음). 검사만 볼 때는 `--lint`
- 참고 문서는 필요할 때만: 부품 `references/components.md`(작성 전 1회) · 측정 근거 `references/analysis/iot30_motion_grammar.md` · A안 텍스트 동작 `references/style-guide.md` · 음악 `references/music.md` · 오류 `references/pitfalls.md` · 외부 자산 `references/sites.md`
- (gateguard 훅이 설치된 환경에서만) 첫 시도 차단은 정상 동작 → 사실을 말하고 같은 호출 재시도. 내가 Write하는 파일은 storyboard.json 하나로 유지
