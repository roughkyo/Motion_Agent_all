# 부품 사전 (storyboard.json `items[].fn`)

엔진: `scripts/motion_template.html` (v2). **motion.html은 고치지 않는다** — 모든 연출은 이 표의 부품을 json에 적어서 만든다.
측정 근거: `analysis/iot30_motion_grammar.md` (레퍼런스 IoT 30초를 1/600초 간격으로 계측한 값)
완성 예시: `examples/iot30.storyboard.json` (레퍼런스와 프레임별 상관 0.95~1.00)

## 공통 규칙
| 키 | 뜻 | 기본 |
|---|---|---|
| `at` | 장면 안에서 등장하는 박 | 0 |
| `until` | 사라지는 박 (그 박에 컷) | 장면 끝까지 |
| `exit` | until 직전 0.25박 퇴장 `fade` · `drop` · `zoom` | 컷 |
| `pos` | 자리 이름 `C` `L` `R` `T` `B` `LT` `LB` `RT` `RB` `CT` `CB` `HOOK` | (960, 540) |
| `x` `y` | 좌표(1920×1080). pos보다 우선. 대부분 **중심**, `align: "left"`면 왼쪽 끝 | |
| `size` | 글자 크기(px) 또는 아이콘·부품 크기 | 120 |
| `color` | `ink`(배경 반대색) `pu`(강조) `pl`(보조) `gr`(회색) `wh` `bk` `#hex` | ink |
| `font` | `D`(제목체) `S`(본문체) `M`(고정폭·코드) `P5`~`P9` | 제목체 |
| `align` | `left` `center` `right` | center |
| `o` | 함수 세부 옵션 (아래 표의 o.*) | |

자리(pos) 좌표: C(960,600) · L(520,600) · R(1400,600) · T(960,340) · B(960,880) · LT(520,420) · LB(520,820) · RT(1400,420) · RB(1400,820) · CT(960,440) · CB(960,800) · HOOK(140,540)
머리글이 있으면 위 250px까지는 머리글 자리 → 본문은 y 300~960에 배치.

## 장면 키
```json
{"title": "역할 분담", "label": "01 역할 분담", "desc": "스토리보드 설명", "beats": 6,
 "head": {"text": "역할 분담", "sub": "4단계 릴레이", "tag": "1단계", "align": "left|right", "color": "pu"},
 "transition": "slash|curtain|shutter|iris|split|flash|none", "glitch": false, "calm": false,
 "bg": "black|white|glow" 또는 [[0,"black"],[2,"white"]], "items": [...]}
```
- `head`: 왼쪽 위 제목이 **쾅(slam)** + 부제가 0.3박 뒤 마스크 상승. `tag`가 있으면 강조색 알약이 먼저 튀고 제목은 72px. `align: "right"`면 오른쪽 위 제목 + 아래 회색 부제
- `transition`: 장면 시작 경계에 0.34초 와이프. 생략하면 slash → curtain → shutter 순환 (레퍼런스와 동일)
- `glitch: true`: 이 장면에서 스네어마다 화면 찢김 (경고·위험 장면)
- `calm: true`: 역동성 검사 제외 (의도적으로 멈추는 장면)
- `label`: HUD 왼쪽 아래 장면 라벨. 생략 시 `"NN title"`

## 전역 키
```json
"fx": {"hud": "상단 작은 제목", "dots": true, "grain": true, "vignette": true, "flash": true, "glitch": true,
       "shake": 1, "zoom": 1, "punch": 0, "wipe": true, "strobe": true},
"assets": {"laptop": "assets/laptop_duo.png"},
"outro_sub": "엔딩 밑줄 아래 작은 글"
```
- 생략하면 레퍼런스 값 그대로 (모두 켜짐, 흔들림 스네어 7px·임팩트 28px, 킥 줌 1.2%·임팩트 줌 4%)
- `fx.hud`: 문자열이면 왼쪽 위 제목, `false`면 HUD 끔 (A안 미니멀일 때)
- `fx.punch`: 장면 컷 순간 줌 펀치(0.06 권장). 와이프를 끈(`wipe:false`) A안에서 사용

---

## 텍스트 부품 (역동 타이포)
| fn | 필수 | 옵션 | 동작 · 측정값 |
|---|---|---|---|
| `slam` | text | o.from(2.2) o.d(.22) | **쾅**: 2.2배 → 1배, 0.15박(100ms) 안에 정착, 불투명 1프레임. 레퍼런스 모든 제목 |
| `stack` | lines[[글,색]] | step(1) lh(1.2) fly(줄번호) flyAt(1.3) | 여러 줄이 박마다 쾅쾅 쌓임 + 킥 펌프. `fly` 줄은 잔상 남기며 날아감 (레퍼런스 훅) |
| `fly` | text | o.flyAt(1.3) o.dist o.trail | 쾅 → flyAt 박에 가속하며 잔상 3겹 + 스피드 라인 |
| `reveal` | text | o.by:"word" o.st(.08) o.d(.3) | 마스크 안에서 아래→위로 올라옴. 부제·설명 줄 기본 |
| `punch` | words[] | step(.5) hot(강조 순번) kinds[] | 같은 자리에서 단어 연타, 등장 방식이 slam·flipIn·splitIn·zoomThrough로 순환 |
| `letterDrop` | text | o.st(.12) | 글자가 위에서 떨어져 세로로 늘었다 정착 (엔딩과 같은 동작) |
| `flipIn` | text | o.st(.05) | 글자가 세로로 뒤집히며 차례로 섬 |
| `splitIn` | text | o.d(.45) | 위·아래 반쪽이 반대 방향에서 밀려와 맞물림 |
| `zoomThrough` | text | o.out(퇴장 박) | 작게→정착, out 박에 카메라를 통과하듯 커지며 사라짐 |
| `glitchText` | text | o.loop(true) | 색수차 등장 + 스네어마다 떨림 |
| `marquee` | text | o.speed(260) o.dir(-1) o.alpha(.1) | 배경을 가로지르는 거대 외곽선 글자 (깊이감) |
| `counter` | to | from d(1) prefix suffix dec label | 숫자 카운트업 → 도달 순간 펀치 |
| `typeT` | text | o.cps(5.5) | 타이핑 + 세로 커서 (왼쪽 고정) |
| `typeP` | text | d(박) | 진행형 타이핑 + 블록 커서 (코드) |
| `blurIn` `shrinkIn` `trackIn` `scatter` `wordSeq` `swap` `lines` `outlineFill` `highlight` `richLine` `text` | | | v1 동작 그대로 (style-guide.md A안 표) |

## 비주얼 부품
| fn | 필수 | 주요 옵션 | 모습 (레퍼런스 장면) |
|---|---|---|---|
| `icon` | name | style: badge·box·plain, hot, label, sub, spin, blink | 아이콘이 튀어나오며 선이 그려짐. badge = 원 배지 |
| `icons` | items[{icon,label,hot}] | gap step(.25) style size | 아이콘 줄이 차례로 등장 (열쇠 3개) |
| `flow` | nodes[{icon,label,sub,hot}] | y x0 x1 r step(.5) st0(.5) packet{text,at,every,n,d} numbered | **노드 릴레이**: 배지가 반 박마다 + 점선 연결 + 데이터 칩이 흐름 (01 역할 분담) |
| `cards` | cards[{head,body,sub,icon,num,hot}] | y w h gap step(.8) st0(.3) font lastHot | 카드가 1.5배에서 내려앉으며 기울기 복원, 마지막은 강조 채움 (06 주의 3) |
| `gauge` | value 또는 loop | r(130) lw(22) d(.8) unit text label | 원형 게이지 + 숫자 카운트 / loop=박 주기로 도는 타이머 (50%, 5초) |
| `bars` | items[[라벨,값,hot]] | w h max unit step | 막대가 차례로 자라며 값 카운트 |
| `table` | rows[{v:[],at,hot}] | head[] cols[] w top check rh | 표: 머리행 강조 + 행이 at 박마다 추가 + ✓ (구글 시트) |
| `terminal` | lines[[글,at,색]] | input[[글,at]] title w h | 창 + 입력줄 타이핑 + 로그 줄 추가 (시리얼 모니터) |
| `urlbar` | pre mid post | label sub hl(.5) x0 y | 주소창 가운데 조각이 강조 박스로 칠해짐 (열쇠 3개) |
| `codebox` | code | label w h hot | 작은 제목 + 코드 한 줄 상자, 아래에서 올라옴 |
| `device` | device: laptop·monitor·phone | url typeD result resultAt resultSub icon w | 기기 화면 속 주소창 타이핑 → 결과 쾅 (03 웹 앱 시험) |
| `steps` | items[[글,부제]] | step(.5) gap w hot | 번호 상자 + 글이 밀려 들어오는 단계 목록 |
| `timeline` | items[[글,부제]] | step(.5) w hot | 가로 시간축, 점·라벨이 위아래 교대 |
| `tags` | words[] | step(.25) size hot w | 키워드 알약이 줄바꿈하며 톡톡 |
| `vs` | left{icon,label,sub,hot} right{} | mid("VS") midAt(1) dx r | 비교: 양쪽 배지 + 가운데 VS 충격파 |
| `orbit` | icons[] | r tilt speed hot br | 가운데 주제 주위로 아이콘 공전 |
| `packet` | text | to[x,y] n every d | 데이터 칩이 날아감 |
| `arrow` | pts[[x,y]…] | d lw dash head | 화살표가 그려져 나감 |
| `check` `cross` | | size · cross: text(도장) sub | ✓ 그려짐 / ✕ + 흔들림 + INVALID 도장 |
| `pill` | text | style: solid·outline | 알약 태그 튀어나옴 |
| `focus` | | w h | 대상에 조여드는 모서리 브래킷 |
| `band` | | angle(-.32) h alpha | 비스듬히 가로지르는 반투명 띠 (훅 배경) |
| `rings` `burst` `sparkle` `ring` `poly` `bar` `line` | | r n seed | 충격파 · 파편 · 반짝 · 도형 |
| `speedlines` `particles` | | n h dir alpha | 가로 속도선 · 떠다니는 도형 (연속 앰비언트) |
| `img` | key | w slide glow | storyboard.json `assets`의 이미지 (tone_vectors.py로 재채색) |

### 아이콘 이름 (77종, 24칸 선화 · 강조색 한 군데)
기기·IT: `sensor` `chip` `board` `laptop` `monitor` `phone` `server` `database` `cloud` `wifi` `network` `code` `terminal` `robot` `ai` `gear` `link` `upload` `download` `battery` `bolt`
보안: `key` `lock` `unlock` `shield` `eye`
학교·사람: `user` `users` `school` `book` `pencil` `doc` `folder` `mail` `chat` `bell` `megaphone` `mic` `video` `camera` `image` `music`
시간·데이터: `clock` `timer` `hourglass` `calendar` `chart` `pie` `trend` `target`
세계·생활: `globe` `pin` `home` `car` `plane` `cart` `coin` `bulb` `heart` `star` `flag` `trophy` `rocket` `search`
과학·자연: `thermo` `drop` `sun` `leaf` `atom` `flask`
기호: `play` `check` `x` `warning` `question` `plus` `dot`
- `sensor`는 LED 칸이 깜박임(`blink`). 없는 이름은 점으로 그려지고 make_storyboard가 ⚠로 알려 줌
- 주제에 딱 맞는 그림이 필요하면 Pixabay 벡터 → `tone_vectors.py` → `assets` + `img` (references/sites.md)

---

## 장면 설계 패턴 (레퍼런스에서 뽑은 골격 6가지)
| 패턴 | 구성 | 예시 json (요약) |
|---|---|---|
| **훅** | 반투명 띠 + 왼쪽 큰 글 3줄 stack(마지막 줄 fly) + 오른쪽 상징 아이콘 + 데이터 칩 발사 | `band` · `stack`(190px) · `icon`(plain 320) · `packet` |
| **흐름(릴레이)** | 머리글 + flow 4노드 + 패킷 + 아래 요약 reveal | `head` · `flow` · `reveal` |
| **조각 강조** | 머리글 옆 아이콘 줄 + urlbar 2개 + 코드 상자 2개 + `=` slam + 알약 | `icons` · `urlbar` · `codebox` · `slam` · `pill` |
| **시연** | 오른쪽 머리글 + 왼쪽 기기 타이핑 → 결과 쾅 + 오른쪽 표 한 행 + 게이지 + 결론 slam | `device` · `table` · `gauge` · `slam` |
| **입력→검증** | 태그 머리글 + 왼쪽 터미널 + 오른쪽 표(✓) + 실패 ✕ 도장 | `terminal` · `table(check)` · `cross` |
| **경고** | 강조색 머리글 + 카드 3장 0.8박 간격 + `glitch: true` | `cards` |
| (추가) **숫자** | counter 큰 숫자 + bars 또는 gauge | `counter` · `bars` |
| (추가) **비교** | vs + arrow + check | `vs` · `arrow` · `check` |
| (추가) **목차·단계** | steps 또는 timeline + tags | `steps` · `timeline` · `tags` |

장면 안 리듬 (레퍼런스 실측): 0박 머리글 쾅 → 0.2~0.5박 첫 비주얼 → 이후 **0.3~0.5박마다** 요소 추가 → 장면 마지막 1~1.5박에 **결론 한 방**(slam 강조색: "여기까지 오면 50% 성공!", "INVALID", "3회 이상 저장 ✓")
