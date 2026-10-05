# Motion Agent — 수업 자료를 30초 모션그래픽으로

PDF·PPTX·DOCX 수업 자료를 넣고 질문 몇 개에 답하면, 음악 비트에 맞춘 **키네틱 타이포그래피 영상(mp4, 1920×1080, 30fps)** 을 만들어 주는 Claude Code 플러그인입니다.
플러그인 안에는 `yangphago-motion` 스킬 하나가 들어 있습니다.

- 자료에서 핵심 문구를 뽑아 장면을 설계함 (30초에 문구 35개 이상, 박 단위 교체)
- 브라우저 스토리보드(키프레임 + 음악 미리듣기)로 먼저 확인받은 뒤에만 최종 렌더
- 색감 3가지 선택: 기본 / AI 추천 / 직접 지정(배경·주·강조·보조), 색 대비 자동 검사
- 음악 4가지 선택: 라이브러리 곡 / 파이썬 합성(`--mood boombap|japan`) / Pixabay 검색 / Lyria AI 생성
- 엔딩 문구 선택 (기본 `made by yangphago`, 엔딩 없이도 가능)

## 설치

### 1) 플러그인으로 설치 (권장)
Claude Code에서:
```
/plugin marketplace add roughkyo/Motion_Agent_all
/plugin install motion-agent@motion-agent-all
```

### 2) 스킬 폴더만 복사
```bash
git clone https://github.com/roughkyo/Motion_Agent_all.git
cp -r Motion_Agent_all/skills/yangphago-motion ~/.claude/skills/
```

## 필요한 프로그램
| 프로그램 | 용도 |
|---|---|
| Python 3.10+ | 텍스트 추출·음악 합성·스토리보드 생성 (`pip install -r requirements.txt`) |
| Node.js 18+ | mp4 렌더 (`playwright-core`는 작업 폴더에 자동 설치) |
| ffmpeg | 영상 인코딩·음원 분석 (PATH에 등록) |
| Chrome 또는 Edge | 렌더용 브라우저 (자동 탐색, 못 찾으면 `CHROME_PATH` 환경변수) |

## 저장소에 포함하지 않은 파일 (라이선스)
| 파일 | 이유 | 없을 때 동작 / 직접 넣는 방법 |
|---|---|---|
| 티몬몬소리 Black, 나눔스퀘어 ExtraBold | 이 저장소에서는 페이퍼로지만 재배포 | 페이퍼로지로 자동 대체. 원래 글꼴을 쓰려면 각 배포처에서 받아 `assets/fonts/KRD.ttf`(티몬몬소리), `assets/fonts/KRS.ttf`(나눔스퀘어)로 저장 |
| Pixabay 음원 2곡 (`library.json` 참고) | Pixabay 라이선스상 음원 파일 단독 재배포 불가 | 자체 합성곡 `boombap.wav`·파이썬 합성 사용. 원하면 Pixabay에서 같은 제목으로 받아 `assets/music/`에 같은 파일명으로 저장 |
| 레퍼런스 샘플 영상 10편과 캡처 | Envato Elements 라이선스 | 분석 수치(`references/analysis/*.md, *.csv`)만 포함. 레퍼런스 영상은 사용자가 직접 제공 |
| `.env` | API 키 | `.env.example`을 `.env`로 복사 후 키 입력 (Lyria를 쓸 때만) |

## 사용 예
```
양파고 모션 스킬로 이 PDF를 30초 영상으로 만들어줘  (파일 첨부)
```
접수 질문(길이·음악·스타일·엔딩·색감·레퍼런스) → 미리보기 → 승인 → `outputs/<프로젝트명>/<프로젝트명>.mp4`

## 폴더 구조
```
.claude-plugin/           플러그인·마켓플레이스 정보
skills/yangphago-motion/
  SKILL.md                에이전트 작업 지시서
  scripts/                스토리보드·음악 합성·편곡·렌더 스크립트
  references/             스타일 가이드, 함정 기록, 음악·참조 사이트, 분석 수치
  assets/fonts/           페이퍼로지 (SIL OFL 1.1, OFL.txt)
  assets/music/           자체 합성곡 boombap.wav, library.json
```

## 만든 사람
양파고 (Yang Phago)
