# 공통 규칙 — 모든 yue-* 스킬에 적용

이 묶음의 모든 스킬은 아래 규칙을 먼저 적용한다. 근거의 정본은 Road Music 저장소다(`ROAD_MUSIC_HOME`, 이 사용자 환경의 기본값은 `/Users/freelife/youtube/music/music-road`이고, 다른 PC에서는 환경 변수로 지정한다). 이 파일은 그 규칙을 스킬에서 빠뜨리지 않게 묶은 요약이다. 내용이 다르면 **Road Music 문서와 실행 버전 `cli:schema`가 우선**한다. 이 스킬 묶음은 Road Music 저장소를 수정하지 않는다.

| 근거 | 경로(ROAD_MUSIC_HOME 기준) |
| --- | --- |
| YuE2 제작·공식 보정 | `docs/yue-prompt-guide.md` — `#official-correction`, `#official-report`, `#workflow`, `#inputs`, `#planning`, `#limits`, `#editing`, `#score-choice`, `#verification`, `#lyrics-verification`, `#rights` |
| 검토·승인·원문 보존·한국어 검수 | `docs/music-review.md` — `#mode`, `#preserve-input`, `#songwriting-design`, `#korean-review`, `#validation`, `#proposal`, `#approval`, `#retry-value`, `#micro-pronunciation`, `#delivery` |
| 가사 태그 정리 계약 | `docs/lyrics-tags.md`(Road Music 전처리 계약이며 원생 YuE의 태그 보장표가 아님) |
| CLI 고급 제작 | `docs/yue-cli-workflow.md`, `docs/yue-advanced-prompts.md` |
| 고정 공식 원문 | `docs/vendor/yue2/official/`(yue2-v0.1.6), `docs/vendor/yue2/current/`(main 2026-11-01), `docs/vendor/yue2/mlx/docs/usage.md` |
| 작업 지침 | `AGENTS.md`, `skills/road-music/SKILL.md` |

YuE 작업에서는 요청마다 위 가이드와 해당 작업의 고정 원문 절을 읽는다(AGENTS.md). "필요한 절만"은 작업과 무관한 절을 건너뛴다는 뜻이며 가이드 자체를 생략하라는 뜻이 아니다. `prompt:knowledge {"topic":"yue"}`는 `yue-prompt-guide.md`를 돌려줄 뿐 고정 공식 원문·`yue-cli-workflow.md`를 대신하지 않는다.

## 1. 엔진

- `yue-mlx` = Apple Silicon의 커뮤니티 MLX 포트(공식 YuE2 가중치 사용). `yue` = Windows NVIDIA의 공식 YuE2 워커. 사용자가 고른 엔진을 끝까지 유지한다.
- 미설치·실패를 이유로 다른 엔진(ACE 포함)으로 바꾸거나 모델을 내려받지 않는다. 미설치면 상태만 보고한다.
- 엔진 미지정이면 환경(`engines:list`, 플랫폼)에 맞는 값을 **가정값**으로 표시해 제안한다.
- ACE의 caption 512자·가사 4,096자 한계, Turbo 옵션을 YuE에 옮기지 않는다. 초기 YuE-v1 규칙(7B/1B 단계, `run_n_segments`, 섹션당 30초 등)을 YuE2 규칙으로 쓰지 않는다.
- `yue-mlx`의 실효 runtime 기본값은 `precision:"8bit"`, `memoryBudgetGiB:16`이다. 공식 표준 프리셋과 MLX 포트 기본 정밀도는 BF16이며, 8bit는 Road Music 호환 기본값이지 품질 기본값이 아니다(`#verification`). 보고서에 runtime을 함께 적는다.

## 2. YuE2 입력 계약

보고서의 "공식 근거" 열에는 아래 구분을 지켜 쓴다. 공식 원문에 없는 Road Music·원본 운영 규칙을 "공식"이라고 쓰지 않는다.

### 2-1. 공식 원문에 있는 사실

- `style`에 장르·악기·보컬 성격·언어·템포를 쓴다(generation.md). 배열 순서는 강제 규칙이 아니다. 공식 `examples/song.json`은 `언어, 장르, 보컬, 악기, 선율·프레이징, BPM` 순이고, `generation-and-covers.md`의 예시는 `English, warm female vocal, contemporary pop, 96 BPM, piano, …`처럼 다르다. 이 묶음은 첫 배열을 기본 출발점으로 쓴다.
- `lyrics`에는 부를 말과 `[Verse]`·`[Chorus]` 같은 구간 태그를 쓰고 구현 메모는 넣지 않는다. 가사에 넣은 발음·화자 주석은 별도 제어 채널이 아니다(main generation "What the score controls").
- `cot`: `full`(멜로디+코드 계획) / `melody`(멜로디만 계획) / `off`(악보 없이 직접 생성). `abc`는 `full`·`melody`에서만 쓴다.
- 원생 요청 필드는 `style`·`lyrics`·`cot`·`seed`·`abc`·`cfg_scale`·`id`(`tags`는 `style` 별칭)뿐이다. `negative_prompt`, `phonemes`, `bpm`, `reference_audio`, 편집 구간, 참조 가수 필드가 없다. 템포·박자는 ABC에 두고 style에도 같은 값으로 쓴다.
- 모드마다 원생 지시문이 따로 있으므로 style에 대체 지시문을 붙이지 않는다.
- `abc`는 planner를 우회한다. 악보는 `Vocal`·`Ins` 두 선율이며 세 번째 성부는 독립 제어되지 않는다. `cot:"melody"`는 입력 ABC의 코드를 자동 제거하지 않는다. 박자·템포·음 길이는 조건일 뿐 파형의 고정 타이밍이 아니다. 리듬·전사 오류는 샘플링보다 악보를 먼저 확인한다.
- 기본 CFG·샘플링은 바로 쓸 수 있는 값이며 바꾸면 품질이 달라질 수 있다. 한 번 호출하면 후보 하나가 나온다.
- 같은 seed라도 GPU·런타임·샘플링 설정이 다르면 결과가 달라질 수 있다. 재현에는 런타임 리비전·모델 식별자·실효 요청·원생 산출물이 필요하다.
- OOM을 숨기려고 요청한 곡을 조용히 줄이거나 추론 설정을 낮추지 않는다(공식 SKILL).

### 2-2. Road Music·이 묶음의 운영 규칙

- **긍정형 묘사:** 부정 필드가 없으므로(공식) 원하는 소리를 긍정형으로 쓰기를 권한다(Road Music `style-positive-description`). 공식 예시 style에도 `no guitar`, `no vocals` 같은 부정 문구가 있으므로 부정 문구 자체를 "공식 위반"이라고 쓰지 않는다. 다만 제외 효과는 보장되지 않는다. 근거 열에는 "negative_prompt 필드 없음(공식) → 긍정형 권장(Road Music)"처럼 나눠 쓴다.
- **명령문 금지:** "generate…", "make a song…"을 style에 넣지 않는다(`style-no-instruction`, 근거는 공식의 모드별 원생 지시문).
- **실존 가수·밴드 이름 금지:** 참조 가수 필드가 없고(공식) 권리 문제가 있다(원본·Road Music 원칙). 특징을 음악 용어로 묘사한다.
- **태그 길이:** 쉼표 태그 하나가 공백 기준 10단어를 넘으면 Road Music 조합기가 삭제하고 `song:prepare`가 `valid:false`를 낸다.
- **슬래시 금지:** 조합기는 style의 `/`를 `, `로 바꾼다(notes 없음). 박자는 `triple-meter waltz`처럼 말로, `R&B/soul`은 `R&B and soul`로 쓰고 `nativeRequest.style`에서 확인한다.
- **구간 태그 범위:** `[Pre-Chorus]`·`[Bridge]`·`[Intro]`·`[Interlude]`·`[Outro]`·`[instrumental]`은 Road Music 전처리가 유지하는 태그다. 공식 예시는 `[Verse]`·`[Chorus]`만 보여주므로 다른 태그의 음악적 효과를 YuE2가 보장한다고 쓰지 않는다.
- **여러 언어 가사:** 실제로 부르는 언어를 모두 style 앞에 쓴다(예: `Korean and English`).
- **기본값 유지:** `cot:"full"`, 기본 CFG·샘플링·ODE, runtime 기본값. 바꾸면 "실험"이라고 밝히고 한 번에 한 요소만 바꾼다. `parts.strict`+`parts.strong`을 함께 쓰면 CFG가 1.5로 바뀌므로 이것도 실험이다.
- **입력 범위:** YuE의 `targetSeconds`는 20~360(기록용), `bpm`은 40~220. `cot:"off"`는 `abc`·`mode:"plan"`과 함께 쓸 수 없다(CLI가 거부).
- **실패를 설정으로 숨기지 않기:** 메모리 부족·중단을 가사 단축, 설정 하향, 메모리 보호 해제로 덮지 않는다(공식 SKILL과 Road Music MLX 운영 규칙).
- **스타일 휴리스틱:** "악기 2~4개", "태그 10단어" 같은 수치는 Road Music 휴리스틱이므로 보고서의 공식 근거 열에 쓰지 않는다.

## 3. 사용자 원문 보존

- 사용자가 준 가사·프롬프트·명시 옵션이 기준이다. 임의로 개사·번역·확장·축약·교체·장르/성별 변경을 하지 않는다.
- AI가 쓴 부분은 규칙대로 바로 보정한다. 사용자 원문은 **원문 → 보정안 → 근거 → 예상 영향 → 적용 여부**로 제안하고 승인받은 부분만 반영한다.
- 전체 자동 위임도 별도로 제공된 원문을 고칠 권한이 아니다.
- **승인이 필요한 차이와 보고만 할 차이:** CLI 조합은 BPM 문구 추가, 악기 요약 추가, 태그 이름 정리(`[Verse 1]`→`[Verse]`), 연주곡 골격 생성 같은 차이를 늘 만든다. 이런 차이는 보고만 한다. **부르는 문장이 삭제·잘림·치환**되거나 사용자가 정한 장르·보컬·악기의 뜻이 바뀌는 차이만 승인 대상이며, 해결 전에는 생성하지 않는다.
- **advice가 사용자 원문에 남을 때:** `officialGuide`는 생성을 막지 않는 권고다. 제공안 승인·전체 자동 위임에서는 원문을 그대로 제출하고, 보고서에 `유지(사용자 원문)`와 보정안을 적고, 결과 검수에서 그 부분(예: 괄호 주석이 불렸는지)을 확인 항목으로 올린다. 기본 검토 모드에서는 보정안을 검토안에 넣어 함께 묻는다. 태그 수식어의 의도(`[Chorus - 힘차게]`)는 AI가 정하는 style로 옮길 수 있다.
- `lyrics:clean`·`prompt:compose`·`song:prepare`의 정리본은 **별도 점검본**이다. 원문 파일을 정리본으로 덮어쓰지 않는다.

## 4. 제목·가사 언어 검수

- **한국어** 제목이나 가사가 있으면 생성 전에 `docs/music-review.md#korean-review` 기준으로 해당 한국어 항목을 검수한다(자동 위임도 생략하지 않음).
  - 제목·문장(조사·주어·서술어·시제·호칭)·전곡 내용(화자/대상/흐름)·용어·비유·장면·가창 문구(어순·호흡)·제목과 후렴의 모든 반복 위치를 읽는다.
  - AI 초안은 보완 후 다시 읽는다. 사용자 원문은 제안만 한다. 부분 수정은 지정 구절과 그 반복 위치만 다룬다.
- **한국어가 없는 항목**은 한국어 검수 `해당 없음`이다. 다른 언어를 번역하거나 한국어 기준(조사·번역투 등)으로 교정하지 않으며, 그 언어의 자연스러움을 검증했다고 보고하지 않는다. 한글 제목 + 영어 가사면 제목만 한국어 검수한다.
- 판정: `검토 완료 / 보완 필요 / 원문 보존·제안만 / 확인 불가 / 해당 없음`. 독립 검수인지 자체 검수인지 밝힌다.
- 도구 통과(`lyrics:check` 등)를 자연스러움 검수로 대신하지 않는다. 연주곡은 가사 검수 해당 없음, 제목만 검수한다.
- 제목·가사 표현만 검토하는 요청에는 엔진 조회·생성 준비 자료·보정 보고를 요구하지 않는다(`#korean-review`, `yue-prompt-guide.md#workflow` 2단계).

## 5. 요청 모드와 승인

| 요청 | 모드 | 생성 |
| --- | --- | --- |
| "곡 만들어줘", "가사는 네가 써줘" | 기본 검토 | 검토안 제시 후 승인 대기 |
| "가사·프롬프트만 먼저 제안해줘" | 초안만 | 생성하지 않음. 자동 작사를 요청했어도 생성 권한이 아님 |
| 한쪽만 자동 위임 | 부분 위임 | 검토안 제시 후 대기 |
| "가사와 프롬프트까지 전부 자동으로 정하고 생성해줘" | 전체 자동 위임 | 검수·검증 후 바로 생성, 결과 보고 |
| "이 가사와 프롬프트 그대로 생성해줘" | 제공안 승인 | 재승인 없이 생성 |
| "기존 곡의 어색한 가사를 고쳐 새 음원까지 재제작해줘" | 지정 수정·재생성 | 허용한 범위만 보완·검수하고 보존 조건으로 생성. 같은 수정·생성의 재승인 없음 |
| "후렴을 바꿔줘"(생성 언급 없음) | 수정만 | 수정안 제시, 생성하지 않음 |
| 승인된 안에 "그대로 진행해" | 승인 후 실행 | 승인 범위대로 생성 |

- 승인 전에는 `song:generate`·`song:render`·`song:resume`·`song:replay`·`mode:"plan"` 제출을 하지 않는다. 무응답·시간 경과는 승인이 아니다.
- 같은 작업에서 받은 위임은 유지하되, 사용자가 나중에 "먼저 보여줘"·"초안만"이라고 하면 그 제한이 우선한다.
- 승인 후 AI 판단으로 가사·장르·보컬·길이·곡 수·핵심 편성의 **의미를 바꾸면** 다시 검토받는다(그 변경까지 위임받았으면 그 범위에서 진행). 같은 안의 기술적 재검증, 이미 보여준 정리 결과 적용, 기본 seed 선택에는 재승인을 요구하지 않는다.
- 곡 수 미지정은 1곡(`count:1`). `count`는 같은 설정의 후보에만 쓰고, 다른 장르는 별도 요청으로 나눈다.

### 로컬 명령과 서비스 명령

Road Music CLI 명령 중 일부는 **서비스(백그라운드 앱)를 시작**한다. 초안만·제목/가사 검토만 요청받았을 때는 서비스를 시작하지 않는다(`music-review.md#validation`).

| 구분 | 명령 |
| --- | --- |
| 로컬(서비스·모델 없음) | `cli:version`, `cli:update:check`, `cli:schema`, `prompt:knowledge`, `song:prepare`, `yue:capabilities`, `score:inspect`, `score:compare`, `score:strip-chords`, `production:*`, `works:list`, `service:status`, 그리고 `--no-start`를 붙인 명령 |
| 서비스 시작 | `cli:status`, `schema`, `app:state`, `setup:check`, `engines:list`, `projects:*`, `songs:list`, `song:detail`, `song:score`, `lyrics:clean`, `lyrics:check`, `prompt:compose`, `score:check`, `queue:list`, `job:wait`, 생성 명령 |

초안만 모드의 정리 확인은 `song:prepare`의 `changes.lyrics.prepared`·`changes.style.prepared`·`notes`로 한다. 서비스 명령은 생성 준비 단계(검토안 제시 직전 또는 승인 후)에서 쓴다. `score:transcribe`는 로컬이지만 별도 SheetSage2 환경이 필요하다. 헤드리스 실행에서는 `ROADMUSIC_STUDIO_AUTO_OPEN=0`을 쓴다.

## 6. 보장하지 않는 것 (모든 보고에 적용)

다음은 프롬프트·보정으로 **해결됐다고 쓰지 않는다**: 정확한 길이(`targetSeconds`는 기록용, 자연 EOS로 끝남), 정확한 템포, 특정 가수·음색, 정확한 발음·한국어 완창, 무보컬(`instrumental:true`도 청취 확인 필요), 구간별 창법, 악기 완전 배제. ABC 검사·ASR 일치·작업 완료를 청취 품질로 바꾸지 않는다. 듣지 않았으면 `미청취`라고 쓴다.

## 7. 공식 가이드 보정 보고

YuE·`yue-mlx`의 프롬프트를 쓰거나 생성을 준비할 때마다(초안만 요청한 경우 포함) `song:prepare`(로컬)의 `officialGuide`로 점검·보정하고 [보고 형식](report-template.md)의 `## YuE2 공식 가이드 보정 보고` 절을 **보정이 없어도** 포함한다. `song:prepare`를 실행하지 못했으면 정적 점검 결과와 `미실행`을 적는다.

## 8. 확인한 사실만 쓰기

시각은 한국 시간(KST)으로 적고, UTC 원문을 옮기면 `UTC`를 붙인다.

생성 소요 시간, 다운로드 용량, 메모리 요구량, 모델 라이선스, 설치 상태는 이번에 실제로 읽은 문서나 CLI 응답에 있을 때만 적고 출처를 함께 쓴다. 확인하지 못했으면 "미확인"이라고 쓴다. 공식 코드·문서 라이선스(고정판 CC BY-NC 4.0, main Apache-2.0)와 모델 가중치 라이선스는 서로 다르다(`docs/yue-prompt-guide.md#rights`). `engines:list`의 설치 상태는 그 조회의 `ROADMUSIC_DATA_DIR`·프로필 기준이므로, 임시 데이터 폴더에서 본 "미설치"를 사용자 실제 환경의 상태로 단정하지 않는다.

## 9. 사용자 선호 파일 (선택)

원본의 override 기능을 대신한다. `MUSIC_ROAD_SKILLS_PREFS`(기본 `~/.config/music-road-music-skills/preferences.md`)가 있으면 읽어 장르 매핑·자주 쓰는 보컬·피하고 싶은 표현 같은 취향을 참고한다. 우선순위는 **이번 요청의 사용자 지시 > 선호 파일 > 장르 레시피**이며, 선호 파일이 공식 계약·안전 경계를 바꾸지 못한다. 파일이 없으면 조용히 건너뛴다.

## 10. 안전 경계

- 음악 생성, 엔진·모델 설치, 업데이트, 대기열 삭제, 진행 중 작업 종료는 사용자가 요청한 범위에서만 한다.
- Road Music 공개 카탈로그 명령만 쓴다. UI 내부 IPC·임의 JavaScript·공식 원생 명령(`yue2 generate`, `yue2 validate` 등)으로 우회하지 않는다.
- 외부 전송·브라우저 열기·피드백 전송은 사용자의 명시적 요청 없이 하지 않는다.
- 테스트·검증에서 데이터 폴더가 필요하면 `ROADMUSIC_DATA_DIR`를 임시 폴더로 분리하고, 그 폴더로 시작한 서비스는 끝나면 같은 `ROADMUSIC_DATA_DIR`로 `cli:stop`해 정리한다.
- 곡·프로젝트 경로는 `songs:list`·`projects:list`가 돌려준 절대 경로를 그대로 쓴다. 기존 파일을 덮어쓰지 않으며 `--overwrite`는 사용자가 요청했을 때만 쓴다.
- **작업 파일은 곡 보관 폴더 밖에:** 조사 기록, 수정 악보, 마스터, 납품물, 임시 요청 JSON은 Road Music 곡 보관 폴더(`app:state.songsDir`의 상위 Songs 폴더와 그 아래 프로젝트·곡 폴더) **밖**에 쓴다. `songs:list`는 프로젝트 폴더 안에서 오디오가 없는 하위 폴더를 정리(삭제)하고, 곡 폴더 안의 추가 `.wav`/`.mp3`는 곡 오디오로 잘못 집힐 수 있다. 사용자가 정한 곳이 없으면 Songs와 나란한 폴더(예: `~/Documents/YueStudio/Work/<곡>/`, 마스터는 `~/Documents/YueStudio/Masters/<곡>/`)를 쓴다.
- `uncertain:true`면 재제출하지 말고 `service:status`·`queue:list --no-start`·`songs:list`로 실행 여부부터 확인한다.
- 실제 생성·수정 요청은 Road Music 제작 기록 스킬(`skills/road-music-production-records`)을 적용한다. 생성·렌더·리플레이는 `requestPrompt`에 사용자 요청 원문을 넣으면 Road Music이 실제 곡 폴더에 연결해 자동 기록하므로 `production:request`를 따로 중복 기록하지 않는다.
- **새 곡은 새 프로젝트에:** 생성 전에 `app:state`의 `songsDir`·`projects:list`의 `current`를 확인한다. 현재 프로젝트가 이 곡과 관계없는 다른 작업이면 새 프로젝트를 만든 뒤 생성한다(`projects:create`는 만든 프로젝트를 바로 현재 프로젝트로 선택한다. 기존 프로젝트로 돌아갈 때만 `projects:select`). 같은 곡의 수정·재제작은 원래 프로젝트를 쓴다. 선택은 앱의 현재 프로젝트를 바꾸므로 보고에 적는다. 저장공간 정리는 `skills/road-music-storage`의 미리보기·확인 절차로만 한다.
