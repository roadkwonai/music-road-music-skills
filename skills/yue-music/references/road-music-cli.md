# Road Music CLI 연결

```bash
ROAD_MUSIC_HOME="${ROAD_MUSIC_HOME:-/Users/freelife/youtube/music/music-road}"
RM="node $ROAD_MUSIC_HOME/cli/road-music.js"
```

최종 응답은 stdout JSON 한 줄(`{"ok":true,"result":…}`), `--events` 진행 JSONL은 stderr다. 입력 필드는 실행 버전의 `$RM schema`가 최종 기준이다(아래는 CLI 0.1.0 기준 요약).

## 명령 순서

| 단계 | 명령 | 모델 실행 | 승인 전 |
| --- | --- | --- | --- |
| 첫 연결 | `$RM cli:version`, `$RM cli:update:check` | 아니오 | 가능(읽기 전용, 업데이트 설치 안 함) |
| 상태 | `$RM app:state`, `$RM engines:list`, `$RM projects:list`, `$RM songs:list` | 아니오 | 가능 |
| 계약 | `$RM schema` | 아니오 | 가능 |
| 지식 | `$RM prompt:knowledge --json '{"topic":"yue"}'` (또는 `yue-advanced`, `lyrics`, `review`, `genres`) | 아니오 | 가능 |
| 엔진 범위 | `$RM yue:capabilities --json '{"engine":"yue-mlx"}'` | 아니오 | 가능 |
| 가사 정리 | `$RM lyrics:clean --json '{"text":"…"}'`, `$RM lyrics:check --json '{"text":"…","targetSeconds":180}'` | 아니오 | 가능 |
| style 조합 | `$RM prompt:compose --json '{…}'` | 아니오 | 가능 |
| 준비·공식 점검 | `$RM song:prepare --file song.json` | 아니오 | 가능 |
| 악보 점검 | `$RM score:check --json '{"text":"<abc>"}'`, `score:inspect`, `score:compare` | 아니오 | 가능 |
| 생성 | `$RM song:generate --file song.json` → `jobId` | **예** | **불가** |
| 완료 확인 | `$RM job:wait --json '{"jobId":"…"}'` | — | 생성 후 |

`song:generate --events --wait`로 한 번에 기다릴 수도 있지만, 반환된 `jobId`를 같은 프로필의 `job:wait`으로 확인하는 것이 기본이다. `uncertain:true`면 재제출하지 않는다.

## 생성 요청 JSON (`song:prepare`·`song:generate` 공통)

| 필드 | 값 | 비고 |
| --- | --- | --- |
| `title` | 문자열 ≤200 | 사람이 읽는 곡명. 원생 요청에는 전달되지 않음 |
| `engine` | `"yue-mlx"` / `"yue"` | CLI 기본값은 `ace`이므로 **반드시 지정** |
| `style` | 문자열 ≤2000 | 언어, 장르, 보컬, 악기, 선율·프레이징, (BPM) |
| `lyrics` | 문자열 ≤20000 | 부를 말 + 구간 태그 |
| `bpm` | 40~220 | style 끝에 `NNN BPM`으로 조합됨. 원생 bpm 필드 아님 |
| `parts` | `genre`, `instruments`(목록 값) 또는 `instrumentation`, `vocal`, `dynamics`, `mix`, `bpm`, `structure`, `strict`, `strong`, `instrumental` | `instruments`와 `instrumentation` 동시 사용 불가. 모두 style 태그로 조합됨 |
| `instrumental` | boolean | 무보컬 의도. 보장 아님 |
| `targetSeconds` | 숫자 | YuE는 기록용(`record-only-natural-eos`) |
| `seed` | 안전 정수 또는 십진 문자열 `"0"`~`"9223372036854775807"` | |
| `cot` | `full` / `melody` / `off` | 기본 `full` |
| `abc` | 문자열 | `cot:"off"`와 함께 쓸 수 없음 |
| `mode` | `song` / `plan` | `plan`은 악보 모델 추론(실제 생성 작업) |
| `advanced` | camelCase 16개(`temperature`, `topP`, …, `cfgScale`, `odeSteps`) | 생략 = 엔진 기본값. 원생 `cfg_scale` 등을 최상위에 넣지 않음 |
| `runtime` | `yue:capabilities`가 표시한 키만 | 임의 변경 금지 |
| `count` | 1~8 | 같은 설정의 후보만 |

`coverAudio`·`recording`·`soundEffect`는 ACE 경로이며 YuE 요청에 붙이지 않는다. 최상위에 정의되지 않은 필드는 schema가 거부한다.

## `song:prepare` 결과 읽기

| 키 | 확인할 것 |
| --- | --- |
| `valid`, `errors` | `false`면 생성 불가. 예: 10단어 넘는 style 태그 삭제 |
| `notes` | 조합기가 바꾼 내용 |
| `changes.style` | `original` → `prepared`(BPM·악기 추가), `dropped` |
| `changes.lyrics` | `original` → `prepared`, `changed` |
| `officialGuide` | `advice` 수, `checks[]`의 `id`·`status`(`pass`/`advice`/`not-applicable`)·`advice` 문구 |
| `effective` | 실효 advanced(기본 CFG1·ODE32 등)·runtime |
| `nativeRequest` | 원생 YuE2로 가는 style·lyrics·cot·seed·cfg_scale·샘플링 |
| `validation` | `targetSeconds: record-only-natural-eos`, `synthesis: not-run` |

### officialGuide 점검 ID

| ID | 의미 | 보정 방향 |
| --- | --- | --- |
| `style-language` | style에 가창 언어 | 맨 앞에 `Korean` 등 |
| `style-genre-instruments` | 장르와 주요 악기 | 장르 뒤 악기 2~4개(영어) |
| `style-vocal` | 보컬 성격 | `solo female vocal` 등 |
| `style-tempo` | 템포 | `bpm` 필드 또는 `NN BPM` |
| `style-positive-description` | 부정·제외 문구 없음 | `no drums` → `sparse piano and cello arrangement` |
| `style-no-instruction` | 명령문 없음 | "make a song…" 삭제, 음악 묘사만 |
| `lyrics-sections` | `[Verse]`/`[Chorus]`/`[Pre-Chorus]`/`[Bridge]` 중 하나 이상 | 구간으로 나눔 |
| `lyrics-no-annotations` | 괄호·`/발음/` 주석 없음 | 주석은 검수 메모로 옮김 |
| `abc-tempo-consistency` | ABC `Q:`와 style BPM ±2 | 같은 값 |
| `melody-abc-chord-free` | melody 모드 ABC에 코드 없음 | `score:strip-chords` 사본 |

`instrumental`이면 언어·보컬·가사 점검은 `not-applicable`이다. CLI가 스스로 붙이는 문구는 사용자 원문 점검 대상이 아니다.
