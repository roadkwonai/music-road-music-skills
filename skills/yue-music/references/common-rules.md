# 공통 규칙 — 모든 yue-* 스킬에 적용

이 묶음의 모든 스킬은 아래 규칙을 먼저 적용한다. 근거의 정본은 Road Music 저장소(`ROAD_MUSIC_HOME`, 기본 `/Users/freelife/youtube/music/music-road`)이며, 이 파일은 그 규칙을 스킬에서 빠뜨리지 않게 묶은 요약이다. 내용이 다르면 **Road Music 문서와 실행 버전 `schema`가 우선**한다. 이 스킬 묶음은 Road Music 저장소를 수정하지 않는다.

| 근거 | 경로(ROAD_MUSIC_HOME 기준) |
| --- | --- |
| YuE2 제작·공식 보정 | `docs/yue-prompt-guide.md` — `#official-correction`, `#official-report`, `#planning`, `#limits`, `#score-choice`, `#lyrics-verification` |
| 검토·승인·원문 보존·한국어 검수 | `docs/music-review.md` — `#mode`, `#preserve-input`, `#korean-review`, `#validation`, `#proposal`, `#approval`, `#retry-value` |
| 가사 태그 정리 계약 | `docs/lyrics-tags.md` |
| CLI 고급 제작 | `docs/yue-cli-workflow.md` |
| 고정 공식 원문 | `docs/vendor/yue2/official/` (yue2-v0.1.6), `docs/vendor/yue2/current/` (main 2026-11-01), `docs/vendor/yue2/mlx/docs/usage.md` |
| 작업 지침 | `AGENTS.md`, `skills/road-music/SKILL.md` |

## 1. 엔진

- `yue-mlx` = Apple Silicon의 커뮤니티 MLX 포트(공식 YuE2 가중치 사용). `yue` = Windows NVIDIA의 공식 YuE2 워커. 사용자가 고른 엔진을 끝까지 유지한다.
- 미설치·실패를 이유로 다른 엔진(ACE 포함)으로 바꾸거나 모델을 내려받지 않는다. 미설치면 상태만 보고한다.
- 엔진 미지정이면 환경(`engines:list`, 플랫폼)에 맞는 값을 **가정값**으로 표시해 제안한다.
- ACE의 caption 512자·가사 4,096자 한계, Turbo 옵션을 YuE에 옮기지 않는다. 초기 YuE-v1 규칙(7B/1B 단계, `run_n_segments`, 섹션당 30초 등)을 YuE2 규칙으로 쓰지 않는다.

## 2. YuE2 입력 계약 (공식 가이드 기준)

- `style`: 공식 예시 순서 **언어, 장르, 보컬, 악기, 선율·프레이징, BPM**. 쉼표로 나눈 짧은 태그. 한 태그가 공백 기준 10단어를 넘으면 Road Music 조합기가 삭제하므로 나눈다.
- `lyrics`: **실제로 부를 말 + `[Verse]`·`[Pre-Chorus]`·`[Chorus]`·`[Bridge]` 같은 구간 태그만.** 구현 메모·발음 표기·화자·연출 주석·괄호 지시는 넣지 않는다(그대로 불릴 수 있다).
- `cot`: `full`(기본, 멜로디+코드 계획) / `melody`(멜로디만 계획) / `off`(악보 없이 직접 생성, `abc` 불가).
- `seed`: 재현 추적용. 같은 seed라도 런타임·엔진이 다르면 같은 곡을 보장하지 않는다.
- `abc`: 외부 악보. planner를 우회한다. `Vocal`·`Ins` 두 선율뿐이며 악기별 트랙이 아니다. `cot:"melody"`는 코드를 자동 제거하지 않는다. 템포는 ABC `Q:`와 style BPM을 같게 둔다.
- **없는 필드:** `negative_prompt`, `phonemes`, `bpm`(원생), 참조 가수, 참조 음원, 구간별 가수, 길이(초). 만들지 않는다. 제외하고 싶은 소리는 원하는 소리의 **긍정형 묘사**로 바꾼다.
- style에 "generate…", "make a song…" 같은 명령문을 넣지 않는다(모드별 원생 지시문이 따로 있다).
- 실존 가수·밴드 이름을 style에 넣지 않는다(참조 가수 필드가 없고 권리 문제가 있다). 원하는 특징을 음악 용어로 묘사한다.
- 기본값(`cot:"full"`, 기본 CFG·샘플링·ODE)을 유지한다. 바꾸면 "실험"이라고 밝히고 한 번에 한 요소만 바꾼다.

## 3. 사용자 원문 보존

- 사용자가 준 가사·프롬프트·명시 옵션이 기준이다. 임의로 개사·번역·확장·축약·교체·장르/성별 변경을 하지 않는다.
- AI가 쓴 부분은 공식 규칙대로 바로 보정한다. 사용자 원문은 **원문 → 보정안 → 근거 → 예상 영향 → 적용 여부**로 제안하고 승인받은 부분만 반영한다.
- 전체 자동 위임도 별도로 제공된 원문을 고칠 권한이 아니다.
- `lyrics:clean`·`prompt:compose`·`song:prepare`의 정리본은 **별도 점검본**이다. 원문 파일을 정리본으로 덮어쓰지 않는다. 정리로 의미가 바뀌면 해당 부분만 보고하고 해결 전에는 생성하지 않는다.

## 4. 한국어 제목·가사 검수

한국어 제목이나 가사가 있으면 생성 전에 `docs/music-review.md#korean-review` 기준으로 검수한다(자동 위임도 생략하지 않음).

- 제목·문장(조사·주어·서술어·시제·호칭)·전곡 내용(화자/대상/흐름)·용어·비유·가창 문구(어순·호흡)·제목과 후렴 반복 위치를 읽는다.
- AI 초안은 보완 후 다시 읽는다. 사용자 원문은 제안만 한다. 부분 수정은 지정 구절과 그 반복 위치만 다룬다.
- 판정: `검토 완료 / 보완 필요 / 원문 보존·제안만 / 확인 불가 / 해당 없음`. 독립 검수인지 자체 검수인지 밝힌다.
- 도구 통과(`lyrics:check` 등)를 자연스러움 검수로 대신하지 않는다. 연주곡은 가사 검수 해당 없음, 제목만 검수한다.

## 5. 요청 모드와 승인

| 요청 | 모드 | 생성 |
| --- | --- | --- |
| "곡 만들어줘", "가사는 네가 써줘" | 기본 검토 | 검토안 제시 후 승인 대기 |
| "가사·프롬프트만 먼저 제안해줘" | 초안만 | 생성하지 않음 |
| 한쪽만 자동 위임 | 부분 위임 | 검토안 제시 후 대기 |
| "가사와 프롬프트까지 전부 자동으로 정하고 생성해줘" | 전체 자동 위임 | 검수·검증 후 바로 생성, 결과 보고 |
| "이 가사와 프롬프트 그대로 생성해줘" | 제공안 승인 | 재승인 없이 생성 |
| 승인된 안에 "그대로 진행해" | 승인 후 실행 | 승인 범위대로 생성 |

- 승인 전에는 `song:generate`·`song:render`·`song:resume`·`song:replay`를 제출하지 않는다. 무응답·시간 경과는 승인이 아니다.
- 조회·`lyrics:clean`·`prompt:compose`·`yue:capabilities`·`song:prepare`는 승인 전에도 실행할 수 있다(모델·서비스 없이 로컬 실행).
- 곡 수 미지정은 1곡(`count:1`). `count`는 같은 설정의 후보에만 쓰고, 다른 장르는 별도 요청으로 나눈다.

## 6. 보장하지 않는 것 (모든 보고에 적용)

다음은 프롬프트·보정으로 **해결됐다고 쓰지 않는다**: 정확한 길이(`targetSeconds`는 기록용, 자연 EOS로 끝남), 정확한 템포, 특정 가수·음색, 정확한 발음·한국어 완창, 무보컬(`instrumental:true`도 청취 확인 필요), 구간별 창법, 악기 완전 배제. ABC 검사·ASR 일치·작업 완료를 청취 품질로 바꾸지 않는다. 듣지 않았으면 `미청취`라고 쓴다.

## 7. 공식 가이드 보정 보고

YuE·`yue-mlx`의 프롬프트를 쓰거나 생성을 준비할 때마다(초안만 요청한 경우 포함) `song:prepare`의 `officialGuide`로 점검·보정하고 [보고 형식](report-template.md)의 `## YuE2 공식 가이드 보정 보고` 절을 **보정이 없어도** 포함한다. `song:prepare`를 실행하지 못했으면 정적 점검 결과와 `미실행`을 적는다.

## 8. 안전 경계

- 음악 생성, 엔진·모델 설치, 업데이트, 대기열 삭제, 진행 중 작업 종료는 사용자가 요청한 범위에서만 한다.
- 테스트·검증에서 데이터 폴더가 필요하면 `ROADMUSIC_DATA_DIR`를 임시 폴더로 분리한다.
- 곡·프로젝트 경로는 `songs:list`·`projects:list`가 돌려준 절대 경로를 그대로 쓴다. 기존 파일을 덮어쓰지 않는다.
- `uncertain:true`면 재제출하지 말고 `service:status`·`queue:list`·`songs:list`로 실행 여부부터 확인한다.
- 실제 생성·수정은 Road Music의 제작 기록 스킬(`skills/road-music-production-records`)을 함께 적용한다.
