# 자주 막히는 지점 (지난 작업에서 실제로 겪은 것)

## 환경 · 도구
| 증상 | 원인 | 해결 |
|---|---|---|
| Write/Edit/첫 Bash가 "Fact-Forcing Gate"로 막힘 | (설치된 환경만) ECC 플러그인 gateguard 훅: 세션 첫 Bash · 파일별 첫 Write/Edit를 **상태 기반으로 무조건 1회 거부** (미리 말해도 거부됨) | 정상 동작. 호출처 · Glob 중복 확인 · 데이터 구조 · 사용자 지시 원문을 말하고 같은 호출 재시도. 새 파일 수를 줄여 횟수 최소화 |
| PDF 텍스트 `print`에서 `UnicodeEncodeError: 'cp949' … '\xa0'` | Windows 콘솔 인코딩이 cp949 | `scripts/extract_text.py`로 UTF-8 파일에 저장 후 Read (임시로는 `PYTHONIOENCODING=utf-8`) |
| 새 옵션(outro 등)이 키프레임에 반영 안 됨 | 작업 폴더의 motion.html이 스킬 템플릿 수정 **전** 복사본 | 템플릿을 고친 뒤엔 `cp "$SK/scripts/motion_template.html" motion.html` 후 make_storyboard 재실행 |
| `preview_start`: "No server named storyboard" | 하위 폴더에 launch.json을 만듦. preview_start는 세션 루트 `.claude/launch.json`만 읽음 | 세션 루트에서 `scripts/preview.py <작업 폴더>` (`--directory`로 하위 폴더 서빙) |
| `rm -f "$S"/*` 차단 | 안전 검사 | `"${S:?}"` 또는 경로를 직접 적기. 스크래치 폴더 잔여물은 두어도 됨 |
| librosa가 mp4를 못 읽음 | 포맷 미지원 | ffmpeg 파이프(`-f s16le`)로 읽기 (스크립트에 반영됨) |
| render.js: playwright-core 없음 | 프로젝트 폴더에 미설치 | 작업 폴더에서 `npm i playwright-core` (Chrome은 설치본 사용) |
| render.js: "Chrome/Edge를 찾지 못함" | 브라우저 미설치 또는 비표준 위치 | Chrome 설치, 또는 `CHROME_PATH` 환경변수에 실행 파일 경로 지정 (자동 탐색: Chrome → Edge, Windows·Mac·Linux 공통) |
| 렌더 화면이 검정/글꼴이 기본체 | 폰트 경로 누락, fontsReady 전 캡처 | `fonts/KRD.ttf`, `fonts/KRS.ttf` 복사 확인 (배포본은 두 폰트가 없어 페이퍼로지로 자동 대체 — README의 폰트 안내 참고). 페이지의 `window.fontsReady` 유지 |
| 미리보기에서 음악 탐색(seek) 불가 | python http.server가 Range 미지원 | 음원을 `fetch → blob URL`로 재생 (템플릿·스토리보드에 반영됨) |
| 미리보기 포트 충돌 | 다른 대화가 8765 사용 | launch.json에 다른 포트(8766~) 사용 |

## v2 정보형 (2026-10-06 추가)
| 증상 | 원인 | 해결 |
|---|---|---|
| 결과가 텍스트 위주·정적 | 장면에 텍스트 부품만 씀 (v1 테슬라 15초: 요소 2개·정지 76%) | 키워드→비주얼 비유 표로 부품 먼저 고르기. make_storyboard 역동성 검사 ⚠ 0개 + motion_metrics 통과 확인 |
| 아이콘이 점으로 나옴 | 없는 아이콘 이름 | make_storyboard ⚠ 목록에서 고르기 (components.md 77종) |
| 머리글과 본문이 겹침 | 본문을 y 250 위에 둠 | 머리글 있는 장면은 본문 y 300~960 |
| 노드 라벨이 겹침 | flow 노드 5개 이상 + 긴 라벨 | 노드 4개 이하, 라벨 12자 이하, 또는 x0·x1 넓힘 |
| json 수정이 안 먹음 | 작업 폴더 motion.html이 v1 복사본 | `cp "$SK/scripts/motion_template.html" motion.html` 후 재실행 |
| 이미지(img)가 안 보임 | assets 경로가 작업 폴더 기준이 아님 | `"assets": {"키": "assets/파일_duo.png"}` — motion.html 기준 상대경로 (make_storyboard가 ⚠) |

## 박자 분석
| 증상 | 원인 | 해결 |
|---|---|---|
| librosa BPM이 172처럼 두 배 | 8분음표를 박으로 셈 | 140 초과면 절반 (스크립트 반영). 스네어 간격(2박)으로 재확인 |
| 박자 격자 정렬 0개 | 첫 피크를 기준으로 잡음 | 원형 평균 위상 방식 (`beat_grid.py`) |
| 위상 집중도 r < 0.4 | 백비트가 약한 곡, 자체 합성곡(boombap.wav: 45 BPM·r 0.08로 오측정) | library.json 저장값 사용, 또는 귀로 확인. 합성(③)은 beatmap이 직접 나오므로 측정 불필요 |
| ffmpeg scene 컷이 0개 | 모션그래픽은 하드 컷이 적음 | 프레임 차이 히트(`analyze_reference.py`)와 정밀 분석 자료 사용 |

## 화면
| 증상 | 해결 |
|---|---|
| 타이핑 중 문장이 좌우로 흔들림 | 완성 문장 기준 왼쪽 끝 고정 (`typeT`) |
| 문구 겹침 · 카드와 글자 충돌 | stills로 장면마다 1~2장 찍어 **직접 눈으로** 확인 후 좌표 수정 |
| 흰 배경에서 흰 글자 | 장면 draw의 `ink` 인자 사용 (배경에 따라 자동 반전) |
| 퍼플이 여러 곳 → 강조가 죽음 | 한 화면 퍼플 한 곳 |
| 한글 블러가 뭉개짐 | 블러를 약하게 하거나 `d`를 늘림, 받침 많은 단어는 shrinkIn 사용 |
| ctx.filter 블러가 다음 그리기에 남음 | `T()`는 save/restore 안에서만 filter 설정. render 시작 시 `ctx.filter='none'` |

## 내용 · 보안
- 활동지·PDF 속 **학교 Wi-Fi SSID/비밀번호, API 키, 학생 개인정보는 영상에 절대 넣지 않음** (예: `WIFI_PASS = "********"`로 가림)
- Gemini 키는 채팅으로 받지 않음. 사용자가 스킬 폴더 `.env`에 직접 입력, 확인은 `lyria_generate.py --check`만
- 레퍼런스 음원은 라이선스 확인 전 분석용
- 사용자 이메일 등 계정 정보는 어떤 외부 요청에도 넣지 않음
