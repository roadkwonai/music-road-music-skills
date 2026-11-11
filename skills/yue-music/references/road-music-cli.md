# Road Music CLI 연결

```bash
ROAD_MUSIC_HOME="${ROAD_MUSIC_HOME:-/Users/freelife/youtube/music/music-road}"
roadmusic() { node "${ROAD_MUSIC_HOME:-/Users/freelife/youtube/music/music-road}/cli/road-music.js" "$@"; }  # bash·zsh 공통. 셸 호출마다 다시 정의
```

Windows PowerShell 예: `$env:ROAD_MUSIC_HOME="C:\path\to\music-road"; node "$env:ROAD_MUSIC_HOME\cli\road-music.js" cli:version`.

최종 응답은 stdout JSON 한 줄(`{"ok":true,"result":…}` 또는 `{"ok":false,"error":{…}}`), `--events` 진행 JSONL은 stderr다. 입력 필드는 실행 버전의 `roadmusic cli:schema`(로컬)가 최종 기준이다(아래는 CLI 0.1.0, protocol 2 기준 요약). `schema`도 같은 내용을 주지만 서비스를 시작한다.

## 명령 순서

"구분"의 **로컬**은 서비스·모델 없이 실행되고, **서비스**는 Road Music 백그라운드 서비스를 시작한다. 초안만·가사 검토만 요청에는 로컬 명령만 쓴다.

| 단계 | 명령 | 구분 | 승인 전 |
| --- | --- | --- | --- |
| 첫 연결 | `roadmusic cli:version`, `roadmusic cli:update:check` | 로컬 | 가능(업데이트 설치 안 함) |
| 계약 | `roadmusic cli:schema` | 로컬 | 가능 |
| 지식 | `roadmusic prompt:knowledge --json '{"topic":"yue"}'`(`yue-advanced`, `lyrics`, `review`, `genres`, `models`, `hymn-remake` 등) | 로컬 | 가능 |
| 엔진 범위 | `roadmusic yue:capabilities --json '{"engine":"yue-mlx"}'` | 로컬 | 가능 |
| 준비·공식 점검 | `roadmusic song:prepare --file song.json` | 로컬 | 가능 |
| 악보 검사(오프라인) | `score:inspect`, `score:compare`, `score:strip-chords` | 로컬 | 가능 |
| 상태 | `app:state`, `setup:check`, `engines:list`, `projects:list`, `songs:list`, `song:detail` | 서비스 | 생성 준비 단계에서 |
| 가사 정리·분량 | `lyrics:clean --json '{"text":"…"}'`, `lyrics:check --json '{"text":"…","targetSeconds":180}'` | 서비스 | 생성 준비 단계에서 |
| style 조합 | `prompt:compose --json '{…}'` | 서비스 | 생성 준비 단계에서 |
| 악보 검사(런타임) | `score:check --json '{"text":"<abc>"}'` | 서비스 + YuE 런타임 | 런타임이 없으면 실패 → `score:inspect`로 대체하고 `미실행(사유)` 보고 |
| 생성 | `roadmusic song:generate --file song.json` → `jobId` | 서비스·모델 | **불가** |
| 완료 확인 | `roadmusic job:wait --json '{"jobId":"…","timeoutMs":3600000}'` | 서비스 | 생성 후 |

- `song:generate --events --wait`로 한 번에 기다릴 수도 있지만, 반환된 `jobId`를 같은 프로필의 `job:wait`으로 확인하는 것이 기본이다. `job:wait`이 시간 초과로 끝나면 같은 `jobId`로 다시 기다린다. 새로 제출하지 않는다.
- `uncertain:true`면 재제출하지 않고 `service:status`(=`cli:status`, 자동 시작 없음)·`queue:list`·`songs:list`로 실행 여부부터 확인한다.
- 임시 `ROADMUSIC_DATA_DIR`로 서비스를 띄웠다면 작업 뒤 같은 값으로 `roadmusic cli:stop`을 실행해 정리한다.

## 생성 요청 JSON (`song:prepare`·`song:generate` 공통)

| 필드 | 값 | 비고 |
| --- | --- | --- |
| `title` | 문자열 ≤200 | 사람이 읽는 곡명. 원생 요청에는 전달되지 않음 |
| `engine` | `"yue-mlx"` / `"yue"` | CLI 기본값은 `ace`이므로 **반드시 지정** |
| `style` | 문자열 ≤2000 | 언어, 장르, 보컬, 악기, 선율·프레이징, (BPM) |
| `lyrics` | 문자열 ≤20000 | 부를 말 + 구간 태그. 연주곡이면 생략 |
| `bpm` | 40~220 | 원생 bpm 필드가 아니라 style에 `NN BPM`으로 조합됨(style에 이미 있던 `NN BPM`은 이 값으로 바뀜). 위치는 style 끝이거나 악기 요약 앞이므로 `changes.style.prepared`로 확인 |
| `parts.genre` | 문자열 | 있으면 `style`보다 우선 |
| `parts.instruments` | 공개 목록 값 ≤16 | 조합기가 끝에 악기 요약(`piano and cello duet` 등)을 붙임. style 안 악기명과 중복될 수 있음 |
| `parts.instrumentation` | `{instrument, role, technique?, section?}` ≤16 | `instruments`와 동시 사용 불가(오류) |
| `parts.vocal`·`dynamics`·`mix` | 짧은 태그 ≤8 | style 태그로 조합. 가수·믹서 값 고정 아님 |
| `parts.bpm` | 40~220 | `bpm`과 같음 |
| `parts.strict` | boolean | style 끝에 `only the instruments listed above and nothing else, no additional instruments, no drum kit, … no synthesizers …` 부정문 목록을 붙임. 사용자가 편성 고정을 요청했을 때만 쓰고 보고서에 밝힘 |
| `parts.strong` | boolean | 단독으로는 변화 없음. `strict`와 함께면 `cfgScale` 1.5(실험) |
| `parts.structure` | `""`/`pop`/`short`/`theme`/`loop` | style 태그가 아니라 **연주곡 가사 골격**을 고름 |
| `instrumental` | boolean | 사용자 `lyrics`를 버리고 `[Intro][instrumental]…` 골격으로 바꾸며 style 끝에 `no vocals, no singing, …` 목록을 붙임. 무보컬 보장 아님. 공식 main의 Vocal→Ins 연주곡 절차와 같지 않음 |
| `targetSeconds` | YuE 20~360 | 기록용(`record-only-natural-eos`) |
| `seed` | 안전 정수 또는 십진 문자열 `"0"`~`"9223372036854775807"` | 생략하면 제출 시 배정(`nativeRequest.seed`는 null) |
| `cot` | `full` / `melody` / `off` | 기본 `full` |
| `abc` | 문자열 | `cot:"off"`와 함께 쓸 수 없음 |
| `mode` | `song` / `plan` | `plan`은 악보 모델 추론(실제 생성 작업). `cot:"off"`와 함께 쓸 수 없음 |
| `advanced` | camelCase 16개(`temperature`, `topP`, …, `cfgScale`, `odeSteps`) | 생략 = 엔진 기본값. 원생 `cfg_scale` 등을 최상위에 넣지 않음 |
| `runtime` | `yue:capabilities`가 표시한 키만 | 임의 변경 금지 |
| `count` | 1~8 | 같은 설정의 후보만 |

`coverAudio`·`recording`·`soundEffect`는 ACE 경로이며 YuE 요청에 붙이지 않는다. 정의되지 않은 필드는 schema가 거부한다.

조합기의 자동 처리(`renderer/prompt.js`): 가사에 한글이 있고 style에 Korean이 없으면 맨 앞에 `Korean`을 넣는다. style의 대괄호·`Style:` 같은 라벨·따옴표는 지운다(notes에 기록). 10단어를 넘는 태그는 삭제하고 `valid:false`가 된다.

## `song:prepare` 결과 읽기

두 가지 실패 경로를 구분한다.

| 결과 | 뜻 | 예 |
| --- | --- | --- |
| `ok:false`, `error.code:"INVALID_ARGUMENT"` | 입력 자체가 거부됨(준비 결과 없음) | YuE `targetSeconds`가 20~360 밖, `cot:"off"`+`abc`/`plan`, `instruments`+`instrumentation`, 가사도 `instrumental`도 없음, seed 범위 초과 |
| `ok:true`, `result.valid:false` | 준비는 됐지만 생성 불가 | 10단어 넘는 style 태그 삭제 |

| 키 | 확인할 것 |
| --- | --- |
| `valid`, `errors` | `false`면 생성 불가 |
| `notes` | 조합기가 바꾼 내용 |
| `changes.style` | `original` → `prepared`(BPM·악기·Korean·no vocals 추가), `dropped`, `overridden` |
| `changes.lyrics` | `original` → `prepared`, `changed` |
| `officialGuide` | `advice` 수, `checks[]`의 `id`·`status`(`pass`/`advice`/`not-applicable`)·`advice` 문구, `notice` |
| `effective` | 실효 `advanced`(CFG·샘플링·ODE)와 `runtime`(yue-mlx: precision 8bit, memoryBudgetGiB 16 …) |
| `nativeRequest` | 원생 YuE2로 가는 style·lyrics·cot·seed·cfg_scale·샘플링 |
| `validation` | `targetSeconds: record-only-natural-eos`, `synthesis: not-run`, `context: requires-runtime-tokenizer`(토큰 예산은 실행 때 확인) |

### officialGuide 점검 ID

| ID | 의미 | 보정 방향 | 근거 구분 |
| --- | --- | --- | --- |
| `style-language` | style에 가창 언어 | `Korean` 등 | 공식 |
| `style-genre-instruments` | 장르와 주요 악기 | 장르 뒤 주요 악기(영어) | 공식(개수는 Road Music 휴리스틱) |
| `style-vocal` | 보컬 성격 | `solo female vocal` 등 | 공식 |
| `style-tempo` | 템포 | `bpm` 필드 또는 `NN BPM` | 공식 |
| `style-positive-description` | 부정·제외 문구 없음 | `no drums` → `sparse piano and cello arrangement` | 필드 부재는 공식, 긍정형 권장은 Road Music |
| `style-no-instruction` | 명령문 없음 | "make a song…" 삭제, 음악 묘사만 | 공식(모드별 원생 지시문) |
| `lyrics-sections` | `[Verse]`/`[Chorus]`/`[Pre-Chorus]`/`[Bridge]` 중 하나 이상 | 구간으로 나눔 | 공식 |
| `lyrics-no-annotations` | 괄호·`/발음/` 주석 없음 | 주석은 검수 메모로 옮김 | 공식(main) |
| `abc-tempo-consistency` | ABC `Q:`와 style BPM ±2 | 같은 값 | 공식 |
| `melody-abc-chord-free` | melody 모드 ABC에 코드 없음 | `score:strip-chords` 사본 | 공식 |

`instrumental`이면 언어·보컬·가사 점검은 `not-applicable`이다. CLI가 스스로 붙이는 문구(`no vocals…`, strict 목록)는 사용자 원문 점검 대상이 아니다(`userStyle`은 `parts.genre`/`style`과 vocal·dynamics·mix만 본다).
