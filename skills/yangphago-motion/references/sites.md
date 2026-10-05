# 모션그래픽 제작 참조 사이트

**언제 여기를 보나** — 스킬 기본 자산(라이브러리 곡·내장 폰트·도형)으로 부족할 때만. 사이트 이용은 내장 브라우저로, 쿠키 배너는 "모두 거부", 다운로드 전 파일명·출처를 사용자에게 한 줄 알림.

| 상황 | 볼 곳 |
|---|---|
| 음악 ① Pixabay 검색을 골랐을 때 | 무료 음원 (`music.md` ① 절차) |
| 음악 ② Lyria 생성을 골랐을 때 / API 오류·모델명 확인 | Gemini 음악 생성 문서 |
| 임팩트·전환에 효과음을 더하고 싶을 때 (사용자 요청 시) | 무료 음향 효과 |
| 장면에 아이콘·그림이 필요할 때 (`img` item) | 간단 아이콘 → 무료 벡터 → 3D 이미지 순으로 |
| 사용자가 내장 폰트(티몬몬소리·나눔스퀘어·페이퍼로지) 외 글꼴을 원할 때 | 무료 폰트 · 한글 무료 폰트 (상업적 이용 가능 여부 확인 후 `fonts/`에 ttf 추가) |
| 레퍼런스 영상이 없는데 "이런 느낌" 아이디어가 필요할 때 | 모션그래픽 레퍼런스 (참고만, 다운로드·복제 금지) |

## 소리
| 용도 | 사이트 | 메모 |
|---|---|---|
| 무료 음원 | https://pixabay.com/ko/music/ | 곡 페이지에 **"콘텐츠 ID 등록됨"** 표시가 있으면 유튜브 업로드 시 저작권 알림 가능 → 미등록 곡 우선 |
| Gemini 음악 생성 (Lyria) | https://ai.google.dev/gemini-api/docs/music-generation | `scripts/lyria_generate.py`의 근거 문서. 모델명·요청 형식이 바뀌면 여기서 확인 |
| 무료 음향 효과 | https://pixabay.com/ko/sound-effects/ | 임팩트·스크래치·리버스 크래시 등 |

## 이미지 · 아이콘
| 용도 | 사이트 | 메모 |
|---|---|---|
| 무료 벡터 | https://pixabay.com/ko/vectors/search/computer/ | 컬러 원본은 `tone_vectors.py <png들> --palette storyboard.json`으로 영상 색감에 맞춰 재채색 (그림자→강조→하이라이트, 생략 시 기본 퍼플 톤) |
| 간단 아이콘 | https://fonts.google.com/icons | Material Symbols |
| 3D 이미지 | https://shapefest.com/#new | |

## 폰트
| 용도 | 사이트 |
|---|---|
| 무료 폰트 | https://fonts.google.com/?lang=ko_Kore |
| 한글 무료 폰트 | https://noonnu.cc/font_page/1456 |

## 모션그래픽 레퍼런스
| 사이트 | 메모 |
|---|---|
| [Pinterest '모션그래픽' 검색](https://kr.pinterest.com/search/pins/?q=%EB%AA%A8%EC%85%98%EA%B7%B8%EB%9E%98%ED%94%BD&rs=typed) | 스타일·구도 아이디어 |
| https://elements.envato.com/video-templates | 템플릿 연출 참고 (유료 구독 서비스) |

## 제작 흐름
SKILL.md의 '빠른 작업 순서' 참고 (storyboard.json → make_storyboard.py → 승인 → render.js video)
