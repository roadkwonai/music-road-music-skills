---
name: yue-style-engineer
description: YuE2 공식 가이드(장르·악기·보컬·언어·템포)와 공식 예시 배열(언어, 장르, 보컬, 악기, 선율·프레이징, BPM)로 Road Music 요청의 style·parts·cot·seed·abc를 작성·보정한다. Suno 스타일 프롬프트·Exclude Styles·메타태그를 YuE2 style로 바꿀 때, officialGuide advice를 고칠 때 사용. Builds YuE2 style prompts and mode options for Road Music (replaces suno-engineer).
---

# YuE2 스타일 엔지니어

원본 `suno-engineer`를 대체한다. [공통 규칙](../yue-music/references/common-rules.md)과 [CLI 연결](../yue-music/references/road-music-cli.md)을 먼저 적용한다. 근거: Road Music `docs/yue-prompt-guide.md#official-correction`, `#inputs`, `#planning`, `#limits`, `docs/yue-cli-workflow.md`, 공식 `docs/vendor/yue2/official/docs/generation.md`·`official/examples/song.json`.

## 핵심 원칙

1. **style은 음악 묘사만.** 공식 generation은 장르·악기·보컬 성격·언어·템포를 쓰라고 한다. 배열은 강제가 아니며, 이 묶음은 공식 `song.json` 예시의 배열(언어 → 장르 → 보컬 → 악기 → 선율·프레이징 → BPM)을 기본 출발점으로 쓴다. 공식 `generation-and-covers.md` 예시처럼 BPM을 앞쪽에 두는 배열도 있다.
   - 공식 예시 형태(`song.json`): `English, warm piano pop, expressive female voice, acoustic piano, rounded bass and light drums, lyrical memorable melody, unhurried phrasing, 88 BPM`
   - 한국어 예: `Korean, emotional piano ballad, solo female vocal, clear Korean phrasing, piano, cello, string ensemble, restrained verse and open chorus, 72 BPM`
   - 가사에 여러 언어가 섞이면 부르는 언어를 모두 쓴다: `Korean and English, dream pop, …`.
   - 박자가 특징이면 style에 **말로** 쓴다(`triple-meter waltz`, `compound six-eight sway`). Road Music 조합기는 style의 `/`를 `, `로 바꾸므로 `3/4 waltz`는 YuE2에 "3, 4 waltz"로 전달된다(2026-11-12 실측, notes에도 안 나옴). `R&B/soul` 같은 슬래시 태그도 `R&B and soul`처럼 쓴다. ABC를 줄 때는 `M:`·`Q:`와 같은 값.
2. **긍정형으로(Road Music 권장).** `negative_prompt` 필드는 없다(공식). 공식 예시 style에도 `no guitar`·`no vocals`가 있으므로 부정 문구를 "공식 위반"이라고 하지는 않지만, 제외는 보장되지 않으므로 Road Music은 긍정형을 권한다. `no drums`, `without autotune`, `빼고`는 `sparse piano and cello arrangement`, `natural unprocessed vocal`처럼 원하는 소리로 바꾼다. 완전 배제는 보장하지 않는다.
3. **명령문 금지.** "Generate…", "make a song…", "you are…", "만들어"를 넣지 않는다.
4. **실존 가수·밴드 이름 금지.** 참조 가수 필드가 없다. 특징을 음악 용어로 쓴다(`breathy airy female vocal`, `gritty baritone`).
5. **짧은 태그.** 쉼표 태그 하나가 공백 기준 10단어를 넘으면 조합기가 삭제하고 `song:prepare`가 `valid:false`를 낸다. 같은 뜻의 수식어를 겹쳐 쌓지 않고 긴 문장·충돌 태그·한 태그 안의 여러 구간 지시를 피한다(`docs/yue-cli-workflow.md` 편성 태그 예, `docs/genre-prompts.md#external-adaptation`).
6. **상충 지시 줄이기.** 또렷한 가사를 원하면 긴 잔향·두터운 더블링과 충돌하는지 본다. 장르 2개 이상을 섞을 때는 주 장르를 앞에 둔다.
7. **기본값 유지.** `cot:"full"`, `advanced`·`runtime` 생략(=CFG 1, ODE 32, yue-mlx 8bit 등). 바꾸면 실험이라고 밝히고 한 요소만. `parts.strict`+`parts.strong`은 CFG를 1.5로 바꾸므로 실험이다.

## 입력 구성

| 의도 | 쓰는 곳 | 메모 |
| --- | --- | --- |
| 장르·분위기 한 줄 | `style` 또는 `parts.genre` | 둘 다 주면 `parts.genre`가 우선(`changes.style.overridden` 확인) |
| 악기 | style 안 영어 악기명, 또는 `parts.instruments`(공개 목록 값) / `parts.instrumentation`(악기·role·technique·section) | 둘 중 하나만. 멀티트랙·볼륨·완전 배제 아님 |
| 보컬 | style 또는 `parts.vocal`(≤8개) | 곡 전체 성향. 구간별 창법 고정 아님. 성량·고음 요청 예: `powerful female rock vocal`, `bright piercing high belting`, `wide vocal range`, `sustained high notes`, `raspy edge`. 실존 가수 비교 대신 이런 묘사를 쓰고, 고음이 어느 줄에서 나올지는 정할 수 없다 |
| 전개·에너지 | `parts.dynamics` | `gradual build`, `chorus lift` |
| 믹스 의도 | `parts.mix` | `lead vocal forward`. 믹서 값 아님 |
| 템포 | `bpm`(40~220) 또는 `parts.bpm` | style에 `NN BPM` 추가(끝 또는 악기 요약 앞, 기존 BPM 문구는 대체). 정확한 템포 아님 |
| 길이 | `targetSeconds` | 기록용. 가사 분량과 자연 EOS가 실제 길이를 정함 |
| 무보컬 | `instrumental:true`(+ 선택 `parts.structure`) | 가사는 생략한다. CLI가 가사를 `[Intro][instrumental]…` 골격으로 바꾸고 style에 `no vocals…` 목록을 붙인다. 청취 확인 필요 |
| 편성 고정 | `parts.strict` | style에 `only the instruments listed above and nothing else, no drum kit, … no synthesizers` 목록을 붙인다. 사용자가 편성 고정을 원할 때만, 보고서에 밝힘 |
| 연주곡 골격 | `parts.structure`: `pop`/`short`/`theme`/`loop` | style 태그가 아니라 연주곡 가사 골격 선택 |

`parts.*`는 결국 원생 `style` 문자열로 조합된다. 조합 순서는 Road Music 조합기가 정하므로(예: parts 예시는 `언어·장르 → 편성 → 보컬 → 전개 → BPM → 악기 요약` 순으로 나왔다) 공식 예시 순서를 정확히 지키려면 `style` 한 줄로 직접 쓴다. `instrumental:true`에서 CLI가 덧붙이는 `no vocals…` 문구는 사용자 원문이 아니므로 보정 대상이 아니다. **최종 결과는 `song:prepare`의 `changes.style.prepared`/`nativeRequest.style`로 확인**하고, 그 결과를 다시 `style`에 넣어 같은 parts를 중복 조합하지 않는다.

장르별 출발점은 Road Music `docs/genre-prompts.md#genre-catalog`(또는 `prompt:knowledge {"topic":"genres"}`)를 참고하되 사용자가 지정한 값(보컬 성별 등)이 레시피 기본값보다 우선한다. 레시피에 언어 태그가 `Korean emotional ballad`처럼 장르와 붙어 있어도 그대로 써도 된다(`style-language` 통과). 나누는 것은 취향이며 공식 요구가 아니다.

## 모드 선택 (`cot`, `abc`)

| 목적 | `cot` | `abc` |
| --- | --- | --- |
| 새 곡(기본) | `full` | 생략 → 모델이 멜로디·코드 계획 |
| 멜로디만 계획, 반주 자유 | `melody` | 생략 또는 검증한 코드 없는 멜로디 ABC |
| 악보 없이 직접 생성 | `off` | 넣을 수 없음 |
| 화성·멜로디·형식 수정 | `full`/`melody` | 원본이 아닌 **수정 사본** |
| 악보 기반 커버 | `melody` | `score:strip-chords`로 코드 뺀 ABC. 원곡 권리 확인 |

- 외부 ABC는 planner를 우회한다. `Vocal`·`Ins` 두 선율뿐이고 세 번째 성부는 독립 제어가 안 된다. `score:inspect`(로컬)로 확인한다. `score:check`는 YuE 런타임이 있어야 동작하므로 실패하면 `미실행(사유)`로 보고하고 inspect 결과를 쓴다. 편집은 `yue-score-editor`.
- ABC가 있으면 `Q:` 템포와 style BPM을 같게(`abc-tempo-consistency`).
- `mode:"plan"`은 악보 모델 추론이라 생성 작업이다. 승인 범위에서만.
- 가사 수정 후 악보 선택은 Road Music `docs/yue-prompt-guide.md#score-choice`를 따른다. 기존 ABC 재사용을 기본으로 삼지 않는다.

## Suno 프롬프트를 받았을 때

[대응표](../yue-music/references/suno-to-yue2.md)로 변환한다. 요약:

- `Male baritone, gritty. Heavy rock, distorted guitars. Modern production.` → `English, heavy rock, gritty male baritone vocal, distorted electric guitar, bass guitar, drums, driving riffs, polished modern production, 140 BPM`. 이때 원문에 없던 `English`·`bass guitar, drums`·`driving riffs`·`140 BPM`은 **AI가 더한 가정값**으로 표시하고, 원문의 `Modern production`도 빠뜨리지 않는다. 변환표에 원문 → 변환 → 추가/삭제 항목을 모두 적는다.
- Exclude Styles → 긍정형 묘사. Variety·Weirdness·Style Influence·Max Mode·Persona·Voice → 대응 없음으로 보고하고 넣지 않는다.
- **사용자가 준 Suno 프롬프트도 사용자 원문이다.** 변환안을 원문 옆에 제시하고 승인받은 뒤 반영한다.

## 자주 생기는 문제 (YuE2 기준)

| 증상 | 먼저 확인 | 조치 |
| --- | --- | --- |
| 장르가 다르게 나옴 | style 첫 장르 태그, 상충 태그 | 주 장르를 앞으로, 겹치는 장르 줄이기 |
| 보컬이 묻힘 | `parts.mix`, 잔향·두꺼운 편성 태그 | `lead vocal forward`, 반주 단순화. 보장 아님 |
| 곡이 일찍 끝남 / 길다 | `result.json` `truncated`, 가사 분량 | 길이는 가사·EOS가 결정. 잘림이면 원인 조사(`yue-result-review`) |
| 리듬·박자가 이상함 | 악보(ABC)부터 | 샘플링을 바꾸기 전에 악보 확인(공식 main generation) |
| 원치 않는 악기 | 부정어 사용 여부 | 원하는 편성만 긍정형으로. 배제 보장 없음 |
| 발음 문제 | 가사 표기 | 철자 변형·주석 금지. `yue-result-review`의 미세 발음 판단 |

## 보정 절차

1. 초안 style·옵션으로 요청 JSON을 만들고 `song:prepare`를 실행한다.
2. `officialGuide.checks`의 `advice`마다 [점검 ID 표](../yue-music/references/road-music-cli.md#officialguide-점검-id)로 보정한다. AI 작성분은 바로, 사용자 원문은 제안만.
3. 다시 `song:prepare` → `valid:true`, 남은 advice와 유지 이유를 기록한다.
4. [보정 보고](../yue-music/references/report-template.md)의 style 행을 채운다.
