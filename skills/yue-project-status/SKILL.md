---
name: yue-project-status
description: Road Music YuE2 작업의 현재 상태를 읽고 다음 할 일을 추천한다. 곡·앨범 이어 하기, 진행 현황 대시보드, 아이디어 목록, 새 프로젝트 만들기, 곡 이름 바꾸기, 완료 곡의 truncation·검수·마스터링 기록 확인을 Road Music projects/songs/production 명령으로 처리한다. Use when the user says "이어서", "어디까지 했지", "다음 뭐 해", "진행 상황", or names an existing song/album (replaces resume, next-step, album-dashboard, album-ideas, promote-idea, new-album, rename, validate-album, import-*).
---

# YuE2 작업 현황·이어 하기

원본은 자체 MCP 서버와 `~/.bitwize-music` 폴더 구조로 앨범 상태를 관리했다. Road Music에서는 **앱의 프로젝트·곡 목록과 제작 기록(SQLite 원장)**이 상태의 정본이다. 이 스킬은 그것을 읽어 요약하고 다음 단계를 추천하며, 별도 상태 파일을 만들지 않는다. [공통 규칙](../yue-music/references/common-rules.md)을 적용한다.

```bash
roadmusic() { node "${ROAD_MUSIC_HOME:-/Users/freelife/youtube/music/music-road}/cli/road-music.js" "$@"; }  # bash·zsh 공통. 셸 호출마다 다시 정의
```

## 읽기

먼저 서비스 없이 읽을 수 있는 것부터 본다.

| 알고 싶은 것 | 명령 | 구분 |
| --- | --- | --- |
| 서비스가 떠 있는지 | `roadmusic service:status` | 로컬(시작 안 함) |
| 제작 요청·작업·결과 파일(프로젝트 전체) | `production:projects`, `production:prompts`, `production:tasks --json '{"domain":"music"}'`, `production:files`, `production:dashboard` | 로컬 |
| 음악 그룹(작품) | `roadmusic works:list` | 로컬 |
| 대기열 | `roadmusic queue:list --no-start` | 로컬(서비스 없으면 연결 오류) |
| 프로젝트 목록·현재 프로젝트 | `roadmusic projects:list` | 서비스 |
| 현재 프로젝트의 곡(절대 `dir`·`audio`) | `roadmusic songs:list` | 서비스 |
| 곡 상세(요청·설정·`truncated`·파일) | `roadmusic song:detail --json '{"dir":"…"}'` | 서비스 |

- **제작 기록을 먼저 본다.** 원장에는 모든 프로젝트의 요청·생성·검수·마스터링 작업과 결과 파일 경로가 남아 있어 프로젝트를 바꾸지 않고도 찾을 수 있다. `songs:list`는 **현재 선택된 프로젝트의 곡만** 돌려준다. 다른 프로젝트 곡을 보려면 `projects:select`(앱 상태 변경)가 필요하므로 사용자가 원할 때만 한다.
- `songs:list`·`song:detail`은 서비스를 시작하고, 목록을 만들 때 프로젝트 폴더 안의 **오디오 없는 하위 폴더를 정리(삭제)**한다. 그래서 작업 파일은 곡 보관 폴더 밖에 둔다(공통 규칙). 옛 형식의 곡 파일명은 목록 시점에 바뀔 수 있으니 경로는 매번 다시 읽는다.
- 경로는 응답의 절대 경로를 그대로 쓴다. 다른 프로필·데이터 폴더의 결과로 현재 상태를 대신하지 않는다. 서비스 연결이 막히면 제작 기록만으로 답하고 `확인 불가(사유)`를 적는다.

## 이어 하기 (원본 resume)

사용자가 곡·앨범 이름이나 "어제 만든 …"을 말하면:

1. `production:prompts`·`production:tasks`·`works:list`에서 제목·요청 원문으로 찾는다(대소문자·띄어쓰기 무시). 여러 개면 후보를 보여주고 고르게 한다.
2. 곡이 현재 프로젝트에 있으면 `song:detail`로 승인된 요청, 결과 파일, `truncated`를 읽는다. 완료 곡의 `result.json`은 정리 단계에서 지워지므로 truncation은 `song:detail`(곡 `meta.json`)의 `truncated`로 본다. MLX 원본 `result.json`이 필요하면 `meta.attempt`(곡 폴더의 `yue-mlx/`) 아래에서 찾는다.
3. 같은 요청의 `review`·`mastering` 작업과 그 `files`를 확인해 검수·마스터링이 이미 됐는지 본다.
4. 아래 판단으로 추천 하나를 제시한다.

## 다음 단계 판단 (원본 next-step)

| 상태 | 추천 |
| --- | --- |
| 가사·style 초안만 있고 승인 없음 | 검토안 다시 제시(`yue-pre-generation-check`) |
| 사실 기반 곡인데 출처 확인 대기 | `yue-research`의 사람 확인 |
| 대기열·실행 중 | 기다림. 새 제출 금지. `job:wait` 또는 `queue:list --no-start` |
| 실패·`uncertain` | 실행 여부 확인 후 원인 조사(`yue-result-review`). 자동 재제출 금지 |
| 완료, truncation 참 | 완주 아님. 원인 조사 |
| 완료, 검수 기록 없음 | `yue-result-review` |
| 검수 완료, 청취 미실행 | 사용자 청취 요청 |
| 청취 승인, 마스터 기록 없음 | 마스터링(`yue-mastering`) |
| 마스터 있음 | 공개 준비(`yue-release`) |

추천은 하나만 먼저 제시하고 이유를 한 줄로 쓴다. 추가 생성을 기본 추천으로 삼지 않는다(재제작은 효율 기준을 먼저 적용).

## 진행 현황 (원본 album-dashboard)

```text
## 진행 현황 — <프로젝트>
| # | 제목 | 엔진 | 단계 | 결과 파일 | truncation | 검수 | 청취 | 마스터 | 다음 |
- 완료 n / 진행 n / 대기 n / 실패 n
- 막힌 항목:
```

단계 값: `초안` → `승인` → `생성 중` → `생성 완료` → `검수 완료` → `청취 승인` → `마스터링` → `공개 준비`. 기록되지 않은 단계(예: 청취)는 대화·사용자 기록에서 확인되지 않으면 `미확인`으로 둔다. 가져온 곡(`imported`)과 `cot:"off"` 곡은 `score.abc`가 없는 것이 정상이다.

## 아이디어·새 프로젝트 (원본 album-ideas, promote-idea, new-album)

- 아이디어 목록은 사용자가 정한 파일(없으면 곡 보관 폴더 밖 작업 폴더의 `IDEAS.md`)에 `제목 / 한 줄 콘셉트 / 장르 / 상태(대기·진행·보류)`로 적는다. 기존 파일은 덮어쓰지 않고 추가한다.
- 아이디어를 실제 작업으로 옮길 때: `roadmusic projects:create --json '{"name":"…"}'`(사용자가 원할 때). **create는 새 프로젝트를 바로 현재 프로젝트로 선택한다**(앱 상태 변경). 기획은 `yue-album-planner`로 넘긴다. 프로젝트를 만든다고 곡을 생성하지 않는다.
- 생성 요청 원문은 `song:generate`의 `requestPrompt`가 자동 기록한다. 생성이 아닌 기획·가사 요청만 따로 남길 때 `production:request`를 쓴다.

## 이름 바꾸기·가져오기 (원본 rename, import-*)

- 곡 제목 변경은 사용자가 요청했을 때만: `roadmusic song:rename --json '{"dir":"…","title":"…","requestPrompt":"<요청 원문>"}'`. **제목과 함께 오디오 파일명도 바뀌므로**(`audio.wav`→`<제목>.wav` 등) 이전에 알려 준 경로를 다시 읽어 알린다. 제목을 바꿔도 모델이 부른 가사는 바뀌지 않는다.
- 외부 음원 가져오기: `roadmusic songs:import --input /abs/file`(현재 프로젝트로 복사). 원본 파일은 보존한다.
- 구조 점검: 곡 `dir`에 오디오와 `meta.json`이 있는지, (full/melody면) `score.abc`가 있는지, 기존 곡이 덮어써지지 않았는지 본다. `result.json`은 완료 곡에 없는 것이 정상이다. 파일을 옮기거나 지우는 정리는 Road Music 저장공간 스킬(`road-music-storage`)의 미리보기·확인 절차로만 한다.
