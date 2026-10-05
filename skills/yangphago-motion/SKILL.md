---
name: yangphago-motion
description: 양파고(정보 교사) 스타일 모션그래픽 영상 제작. 키네틱 타이포+도형, 색감 3택(기본 블랙·화이트·형광 퍼플 / AI 추천 / 사용자 지정 4색), 16:9, 어반 힙합/붐뱁 비트 동기화, 엔딩 문구(기본 "made by yangphago", 시작 시 질문). 수업 자료(PPTX·PDF·DOCX)나 주제를 받아 브라우저 스토리보드(키프레임 이미지+설명+음악 미리듣기)로 승인받은 뒤 mp4로 렌더링한다. "모션그래픽 만들어줘", "키네틱 타이포 영상", "수업 소개 영상", 레퍼런스 영상을 주며 "이런 느낌으로" 같은 요청에 사용.
---

# yangphago-motion

**내가 쓰는 파일은 `storyboard.json` 하나.** 나머지(장면 코드·키프레임·스토리보드 페이지·검수 시트·편곡·mp4)는 스크립트가 만든다.
측정치(30초 영상): 편곡 2초 · 스토리보드 2초 · 렌더 18초.

## 고정 요구사항 (사용자가 바꾸라고 하기 전까지)
1. 키네틱 타이포 + 도형 (+필요 시 벡터·아이콘·3D 이미지: `references/sites.md`, 재채색 `python "$SK/scripts/tone_vectors.py" <png들> --palette storyboard.json` → `*_duo.png`, 영상 palette와 같은 색으로 맞춰짐)
2. 색감은 **접수 때 3가지 중 선택** (아래 '색감' 참고). 기본 = 블랙 `#070707` · 화이트 `#F4F4F0` · 형광 퍼플 `#B026FF` · 연보라 `#D9A3FF`. 어떤 색감이든 **한 화면 강조색 한 곳**
3. 16:9, 1920×1080, 30fps
4. 어반 힙합/붐뱁, 묵직하고 트렌디. 상업적 무료 음원 또는 생성
5. 엔딩 문구는 **접수 때 반드시 질문** (기본 `made by yangphago`, storyboard.json `outro`에 기록. beatmap의 gap·impacts로 자동 배치)
6. 영상 길이는 **반드시 질문** · 7. 레퍼런스 영상을 주면 최대한 비슷하게 · 8. **스토리보드 승인 전 최종 렌더 금지**

## 빠른 작업 순서 (`$SK` = 이 SKILL.md가 있는 폴더 = 스킬 로드 시 표시되는 Base directory. 개인 설치는 `~/.claude/skills/yangphago-motion`, 플러그인 설치는 플러그인 폴더 안)

**1. 접수** — AskUserQuestion은 한 번에 **최대 4문항** → 두 번에 나눠 묻는다.
- 1차: 길이 · 음악 · 스타일+글꼴 · 엔딩 문구
- 2차: **색감**(① 기본 색감: 블랙·화이트·퍼플 / ② AI 추천 색감: 주제에 맞춰 4색 제안 / ③ 직접 지정: 배경·주·강조·보조 색) · 레퍼런스 영상 유무
  - ③을 고르면 채팅으로 이렇게 받는다: "배경 / 주 색깔(글자) / 강조 / 보조 색을 HEX(#1A1A2E)나 색 이름(남색, 크림색…)으로 알려 주세요. 예) 배경 남색, 주 크림색, 강조 주황, 보조 하늘색". 색 이름은 HEX로 바꿔 json에 적고, 무엇으로 바꿨는지 한 줄로 알린다
  - ②는 자료 주제·분위기에서 4색을 골라 **이름+HEX+고른 이유 한 줄**로 제안하고, 스토리보드에서 확인받는다

**음악 질문은 옵션 description에 아래 비교를 그대로 넣는다** (착오 방지: 시간·토큰·품질·저작권을 고르는 순간 보이게. 사용자 응답 대기 시간 제외, 30초 영상 기준 실측)
| 옵션(label) | description |
|---|---|
| 라이브러리 곡 (추천) | 수 초 · 토큰 약 1천 · `library.json`의 검증된 곡(현재 3곡: 331music 밝은 붐뱁 / boombap 묵직한 합성 붐뱁 / DesiFreeMusic LP 질감 붐뱁) 중 주제에 맞는 2곡을 편곡해 스토리보드에서 들어 보고 선택 · 박자값 저장됨 · 저작권 확인 완료 |
| 파이썬 합성 | 수 초~1분 · 토큰 약 1천 · 박자 완벽 동기화 · 저작권 완전 자유 · 단, 드럼+코드 단순 반복이라 길수록 단조롭고 '만든 티'가 남 |
| Pixabay 검색 | 3~5분 · 토큰 5천~8천 · 실제 프로듀서 곡이라 질감·분위기 선택 폭이 가장 넓음 · 단, 콘텐츠 ID 확인 필요, 곡에 따라 박자 측정 불안정(후보 절반 탈락 사례) |
| Lyria AI 생성 | 1~3분 · 토큰 약 3천 · **유료**(곡당 약 $0.04~0.08) · Gemini API 키 필요 · 원하는 분위기를 글로 주문 가능, 박자 측정 필요 |
- 질문 문구 예: "음악은 어떻게 할까요? (시간·토큰은 30초 영상 기준 대략치)"
- Pixabay·Lyria로 쓴 곡은 렌더 후 "라이브러리에 추가할까요?"를 묻고, 동의하면 `assets/music/`에 복사 + `library.json`에 beat·down0·outro_bar·라이선스 기록 → 다음부터 수 초

세부 선택지: 길이(15/30/60초) · 음악(위 표) · 스타일(A 미니멀 키네틱 기본 / B 정보형) · 글꼴(기본 티몬몬소리+나눔스퀘어 / 페이퍼로지 — 고르기 어려우면 `assets/fonts/preview.jpg`를 보여 줌) · 레퍼런스 영상 유무 · **"마지막 문구는 무엇으로 해드릴까요?"**(옵션: `made by yangphago`(기본) / 엔딩 없이 본문만 / 직접 입력은 Other로). 요청에 이미 답이 있으면 생략.

**2. 준비** (한 번에 실행)
```bash
mkdir -p fonts music/candidates out && cp "$SK/assets/fonts/"*.ttf fonts/ && cp "$SK/scripts/motion_template.html" motion.html && (npm ls playwright-core >/dev/null 2>&1 || npm i playwright-core)
```
- 세션 폴더에 이전 작업물(motion.html·music/final.wav 등)이 있으면 덮어쓰지 말고 하위 폴더(`<작업명>/`)를 만들어 그 안에서 위 명령 실행
- 자료 텍스트는 **반드시** `python "$SK/scripts/extract_text.py" <자료들> --out source.txt` (PDF·PPTX·DOCX → UTF-8 파일, 화면엔 요약만. 직접 `print`하면 Windows cp949 콘솔이 `\xa0` 등에서 죽는다) → `source.txt`를 Read로 필요한 부분만 읽고 핵심 문장만 추출(**Wi-Fi 비밀번호·키·개인정보 제외**)

**3. 음악 → `music/final.wav` + `beatmap.js`**
- ⓪ 라이브러리: (GitHub 배포본에는 Pixabay 곡 파일이 없을 수 있음 — `assets/music/`에 파일이 없으면 그 곡은 후보에서 빼고 자체 합성곡 `boombap.wav`를 쓰거나, 사용자가 Pixabay에서 같은 제목으로 받아 넣게 안내) `assets/music/library.json`의 저장값(beat·down0·outro_bar)을 **반드시** 넘겨서 (자동 측정은 합성곡에서 실패함) `python "$SK/scripts/arrange.py" "$SK/assets/music/<file>" --seconds <길이> --beat <beat> --down0 <down0> --outro-bar <outro_bar>`
  - 2곡 편곡: 첫 곡은 기본 출력(`music/final.wav`+`beatmap.js`), 둘째 곡은 `--out music/alt.wav --map music/alt_beatmap.js` → storyboard.json music에 m1·m2로 올림. m2가 선택되면 alt 두 파일을 final.wav·beatmap.js로 복사 후 make_storyboard 재실행
  - **BPM이 같은 곡끼리 짝지으면 장면 박 수를 그대로 쓸 수 있다** (90BPM: 331music·boombap / 88BPM: DesiFreeMusic). BPM이 다르면 make_storyboard 경고를 보고 beats 재조정
- ③ 합성: `python "$SK/scripts/synth_beat.py" --seconds <길이> [--mood japan] --out music/final.wav --map beatmap.js`
  - **주제에 맞는 mood를 고른다**: `boombap`(기본, Fm9 전자피아노+비브라폰) / `japan`(미야코부시 음계 코드 + 코토 리드 + 타이코). mood가 달라도 박 구조·gap은 같아 장면 박 수 그대로
- ①② 검색·생성: `references/music.md` (후보는 `music/candidates/`에 로컬 저장 → 미리듣기 카드) → 고른 곡을 arrange.py
- ② Lyria를 고르면 먼저 `python "$SK/scripts/lyria_generate.py" --check` → `KEY MISSING`이면 사용자에게
  "`$SK/.env` 파일을(없으면 `.env.example`을 복사해 만들고) 메모장으로 열어 `GEMINI_API_KEY=` 뒤에 키를 붙여넣고 저장해 주세요 (발급: https://aistudio.google.com/apikey)"라고 안내하고 기다린다.
  **키를 채팅으로 받지 말고, .env를 직접 열어 보지 않는다** (`--check`의 KEY READY/MISSING만 사용)

**4. storyboard.json 작성** → `python "$SK/scripts/make_storyboard.py" storyboard.json`
- 장면은 `beats`만 쓰면 시간·키프레임·엔딩 행이 자동. 장면 beats 합계 = 엔딩 시작 박(넘치거나 모자라면 스크립트가 경고)
  - 30초·90BPM(arrange): 본문 **38박** · 15초: 14박 · 60초: 82박 / 30초·88BPM: 34박 (synth_beat는 출력된 gap[0]÷1박). 엔딩 없음(`outro: ""`)이면 길이÷1박 전체 (30초 90BPM 45박 · 88BPM 44박)
- `storyboard/contact.jpg` **한 장만** 열어 검수(겹침·잘림·가독성) → 고칠 곳은 json 수정 후 재실행
- 미리보기: **세션 루트에서** `python "$SK/scripts/preview.py" <작업 폴더(루트면 .)>` (루트 `.claude/launch.json`에 `storyboard` 설정을 합침. preview_start는 루트 launch.json만 읽으므로 하위 폴더에 만들면 인식 안 됨) → `preview_start {name:"storyboard"}` → `/storyboard/` 보여 주고 **음악 번호 + 수정할 장면**을 묻는다

**5. 승인 후 렌더** → 결과물은 **세션 루트의 `outputs/<프로젝트명>/`** 에 저장 (프로젝트명 = 작업 폴더명처럼 짧은 영문, 폴더는 render.js가 자동 생성)
`node "$SK/scripts/render.js" video motion.html music/final.wav <세션루트>/outputs/<프로젝트명>/<프로젝트명>.mp4`
- 같은 폴더의 `<프로젝트명>_qa.jpg`(1초 1장 격자) **한 장만** 확인 → SendUserFile로 mp4 전달 + 음원·라이선스 한 줄

## storyboard.json
```json
{"title": "IoT 첫걸음", "style": "A 미니멀 키네틱", "fonts": {"title": "P9", "body": "P6"},
 "music": [{"id": "m1", "label": "Urban Hip Hop Beat — 331music", "src": "music/final.wav", "bpm": 90,
            "note": "올드스쿨, 밝음", "contentId": false, "recommended": true, "source": "Pixabay"}],
 "scenes": [
  {"title": "훅", "desc": "타이핑", "beats": 4, "motion": "typeT",
   "items": [{"fn": "typeT", "text": "센서가 말을 건다", "size": 110}]},
  {"title": "키워드", "desc": "흰 배경 블러 등장 → 배경만 검정 컷", "beats": 4, "bg": [[0, "white"], [1.25, "black"]],
   "items": [{"fn": "blurIn", "text": "온습도", "size": 240, "o": {"out": 2.8}}, {"fn": "ring", "at": 1.25, "r": 380, "color": "pu"}]}
 ]}
```
**글꼴** `fonts`(생략 가능): `title`·`body`에 `D`(티몬몬소리 Black, 기본 제목) `S`(나눔스퀘어 ExtraBold, 기본 본문) `P5`~`P9`(페이퍼로지 Medium·SemiBold·Bold·ExtraBold·Black). 엔딩 큰 글자도 title 글꼴을 따름
**색감** `palette`(생략 시 기본 색감): `{"bg": 배경, "main": 주(글자색 = 반전 화면의 배경), "accent": 강조(item color `pu`, glow 배경, 엔딩), "sub": 보조(`pl`)}` — 모두 `#RRGGBB`. 회색 `gr`은 bg·main을 섞어 자동. item 색 이름(`ink` `pu` `pl` `gr` `wh` `bk`)은 그대로 쓰면 팔레트를 따라간다 (`wh`=main, `bk`=bg)
- make_storyboard가 대비율을 출력(⚠ 표시): 글자 main/bg **4.5 이상**, 강조 accent/bg·accent/main **3 이상** 권장. ⚠면 색을 조정해 다시 제안
- AI 추천 예: 일본 여행 → 먹색 `#1B1B1F` · 한지 `#F3EDE2` · 주홍(도리이) `#E8452C` · 벚꽃 `#F4A7B9` / 코딩 → 다크 `#0D1117` · `#E6EDF3` · 터미널 그린 `#3FB950` · `#58A6FF`
**엔딩** `outro`(생략 시 `made by yangphago`): `"made by ○○"` → 윗줄 made by + 큰 글자 ○○ · `"윗줄|큰 글자"` → 직접 두 줄 · 그 외 → 큰 글자 한 줄. 긴 문구는 폭에 맞게 자동 축소 · `""` → **엔딩 없음**: 본문 장면이 영상 끝까지(본문 박 = 길이÷1박, 예 30초·90BPM 45박). 음악의 2박 정적·임팩트는 그대로 있으므로 마지막 장면을 정적 박에서 시작해 임팩트에 핵심 문구가 터지게 배치 (make_storyboard가 정적·임팩트 박 위치를 출력)
**장면**: `beats` · `bg`(`black`/`white`/`glow` 또는 `[[박,모드],…]` — 배경은 문구와 독립적으로 한 프레임 컷) · `items` · 선택 `frames`(초), `draw`(motion.html에 직접 만든 JS 함수 이름, B안·특수 장면용)
**item 공통**: `fn` · `at`(장면 안 시작 박) · `until`(사라지는 박) · `x`(기본 960) `y`(540) `size`(120) · `color`(`ink`=배경 반대색 기본, `pu` `pl` `gr` `wh` `bk` `#hex`) · `font`(`S`=본문 글꼴, `D`·`P5`~`P9`=특정 글꼴) · `o`(함수 옵션)

| fn | 필수 | 주요 옵션 | 용도 (근거 샘플) |
|---|---|---|---|
| `typeT` | text | o.cps(5.5) | 타이핑+커서, 왼쪽 고정 (63211445) |
| `blurIn` | text | o.out(퇴장 박), o.d, o.st | 글자별 블러 등장·퇴장 (11971627) |
| `shrinkIn` | text | o.from(1.6) | 큰 반투명→축소·선명 (62295607) |
| `trackIn` | text | o.from | 자간 수축 (62999763) |
| `wordSeq` | text | o.st(1), o.hc | 단어 순차, 현재 단어만 보라 |
| `scatter` | text | o.d, o.out | 흩어진 글자 조립 (62999763) |
| `swap` | words[] | step | 같은 자리 문구 확장 |
| `lines` | lines[[글,크기,색]] | o.st, o.gap | 줄별 엇갈림 조립 (57523104) |
| `outlineFill` | text | d(박), o.lc | 외곽선→채움 스캔 (60944035) |
| `highlight` | text | d, o.bc | 선택 박스 (63211445) |
| `richLine` | parts[[글,색]] | | 한 단어만 보라 |
| `text` | text | | 정적 글자 |
| `sparkle` | | r | 4각 별 반짝 |
| `ring` `poly` `bar` `line` | (line: pts) | r, n, lw, spin, w, h, d | 도형 |
| `img` | key | w | 벡터 (motion.html의 IMG에 등록) |

## 예상 소요 (30초 영상, 사용자 응답 대기 제외 — 2026-10-05 실측 기반 대략치)
사용자가 시간·비용을 물으면 이 표로 답한다. 음악 선택에 따라 ①단계가 크게 달라진다.
| 구간 | 시간 | 토큰 | 가장 오래/많이 드는 것 |
|---|---|---|---|
| ① 접수 → 미리보기 | 라이브러리·합성 **5~8분** / Pixabay **10~15분** | 2만~4만 | 시간: 음악 검색(Pixabay)·storyboard.json 설계 / 토큰: 자료 본문 읽기·Pixabay 결과 목록·검수 이미지 |
| ② 승인 → mp4 | **2~3분** (60초 영상은 렌더 약 2배) | 3천~5천 | 시간: 렌더(프레임 캡처+인코딩) — 토큰은 거의 안 씀 |
| 수정 1회 | 3~5분 | 5천~1만 | json 수정 → 키프레임 재생성 → 재렌더 |
- gateguard 첫 시도 차단마다 재시도 1회분 시간·토큰이 추가된다

## 토큰·시간 절약 규칙
- 이미지 검수는 **contact.jpg / _qa.jpg 한 장씩**. 개별 stills·브라우저 스크린샷은 문제 장면을 확대할 때만
- 스토리보드 페이지 확인은 `get_page_text`·JS 점검으로. 스크린샷은 사용자에게 보여 줄 때만
- **외부 참조 사이트** `references/sites.md` (무료 음원·Gemini 음악 생성 문서·효과음·벡터·아이콘·3D 이미지·폰트·모션 레퍼런스 10곳 + "어떤 상황에 어디를 보나" 표): 기본 자산으로 부족할 때만 연다
- 참고 문서는 필요할 때만 읽는다: 동작 세부 `references/style-guide.md`, 레퍼런스 대조 `references/analysis/report.md`(26KB, 레퍼런스 영상이 있을 때만), 음악 검색 `references/music.md`, 오류 `references/pitfalls.md`
- 수정 요청은 json만 고치고 make_storyboard 재실행 (motion.html은 건드리지 않음)
- (gateguard 훅이 설치된 환경에서만, "Fact-Forcing Gate" 메시지로 확인) 이 훅은 **첫 시도를 무조건 한 번 막는다**(세션 첫 Bash · 새 파일 첫 Write · 기존 파일 첫 Edit, 미리 사실을 말해도 동일). 오류가 아니라 정상 동작 → 사실(요청 원문·명령 목적·호출처·데이터 구조)을 말하고 **같은 호출을 그대로 재시도**. 다른 방법으로 우회하지 않는다
  - 차단을 줄이려면: 내가 Write하는 파일은 storyboard.json 하나 · launch.json은 preview.py로 · 첫 Bash는 2단계 준비 명령 하나로 몰아서

## 레퍼런스 영상을 받았을 때
샘플 원본 10편: `assets/samples/videos/` (Envato Elements 라이선스라 GitHub 배포본에는 없음 — 폴더가 비어 있으면 `references/analysis/`의 측정값만 사용. "샘플 ○○처럼" 요청 시 이 파일로 분석. 기존 측정값은 `references/analysis/`에 있으니 재분석은 필요할 때만)
`python "$SK/scripts/analyze_reference.py" ref.mp4 out/ref` → `_sheet.jpg` 한 장 + JSON(hit_gap·holds·bpm)으로 문구 길이·배경 비율·동작을 위 fn 표에 매핑. 표에 없는 동작만 motion.html에 함수로 추가하고 `draw`로 연결. 음원은 라이선스 확인 전 분석용.

## 스타일
- A안(기본): 한 화면 한 문구 · 정중앙 · 등장 반 박 · 흰 배경 약 20%
- **박진감 규칙 (반드시 지킴)** — 느슨하면 바로 지루해진다
  - 자료에서 **키워드를 넉넉히 뽑는다**: 30초에 화면 문구 **35개 이상**(15초 18+, 60초 70+). 목차·소제목·고유명사·숫자 목록을 통째로 활용
  - 단어는 **1박**, 나열은 **반 박 연타**(`swap` step .5, `wordSeq` st .5), 문장(8자+)만 2박. **한 문구를 3박 넘게 붙잡지 않는다**
  - 장면 하나에 items 여러 개를 `at`/`until`로 **박마다 교체** (예: 테마 8개 → 8박 장면에 item 8개, fn을 blurIn·scatter·trackIn·shrinkIn으로 번갈아)
  - 배경 반전(`bg` 배열)을 2박마다 섞어 컷 리듬을 만든다. 킥 펌프·컷 줌 펀치는 템플릿에 내장
  - 피날레는 `swap`으로 임팩트·마지막 한 방마다 문구를 한 덩어리씩 추가 (예: `일본,` → `일본, 지금` → `일본, 지금 떠나자`)
- B안(정보형: 회로·코드·표가 많은 설명): `references/example_infostyle_iot30.html`의 장면 함수를 motion.html에 옮겨 `draw`로 사용
