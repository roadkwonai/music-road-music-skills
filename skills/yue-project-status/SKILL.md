---
name: yue-project-status
description: Road Music YuE2 작업의 현재 상태를 읽고 다음 할 일을 추천한다. 곡·앨범 이어 하기, 진행 현황 대시보드, 아이디어 목록, 새 프로젝트 만들기, 곡 이름 바꾸기, 완료 곡의 truncation·검수 누락 확인을 Road Music projects/songs/production 명령으로 처리한다. Use when the user says "이어서", "어디까지 했지", "다음 뭐 해", "진행 상황", or names an existing song/album (replaces resume, next-step, album-dashboard, album-ideas, promote-idea, new-album, rename, validate-album, import-*).
---

# YuE2 작업 현황·이어 하기

원본은 자체 MCP 서버와 `~/.bitwize-music` 폴더 구조로 앨범 상태를 관리했다. Road Music에서는 **앱의 프로젝트·곡 목록과 제작 기록**이 상태의 정본이다. 이 스킬은 그것을 읽어 요약하고 다음 단계를 추천하며, 별도 상태 파일을 만들지 않는다. [공통 규칙](../yue-music/references/common-rules.md)을 적용한다.

```bash
roadmusic() { node "${ROAD_MUSIC_HOME:-/Users/freelife/youtube/music/music-road}/cli/road-music.js" "$@"; }  # bash·zsh 공통. 셸 호출마다 다시 정의
```

## 읽기 (모두 읽기 전용)

| 알고 싶은 것 | 명령 |
| --- | --- |
| 앱·서비스 상태 | `roadmusic service:status`(서비스를 시작하지 않음), `roadmusic app:state`(서비스 시작). 일반 `cli:status`는 서비스를 시작하므로 상태 확인에는 `service:status` 또는 `--no-start`를 붙인다 |
| 프로젝트 | `roadmusic projects:list` |
| 곡 목록(절대 `dir`) | `roadmusic songs:list` |
| 곡 상세(요청·설정·파일) | `roadmusic song:detail --json '{"dir":"…"}'` |
| 대기열 | `roadmusic queue:list --no-start` |
| 음악 그룹(작품) | `roadmusic works:list` |
| 제작 기록·시간 | `roadmusic production:tasks --json '{"domain":"music"}'`, `roadmusic production:dashboard --json '{"domain":"music"}'` |

경로는 응답의 절대 `dir`·`path`를 그대로 쓴다. 이름으로 경로를 추측하지 않는다. 다른 프로필·데이터 폴더의 결과로 현재 상태를 대신하지 않는다.

## 이어 하기 (원본 resume)

사용자가 곡·앨범 이름을 말하면:

1. `songs:list`·`projects:list`에서 대소문자·띄어쓰기를 무시하고 찾는다. 여러 개면 후보를 보여주고 고르게 한다.
2. `song:detail`로 승인된 요청(가사·style·엔진·seed·옵션), 결과 파일, `result.json`의 truncation을 읽는다.
3. 아래 "다음 단계 판단"으로 추천 하나를 제시한다.

## 다음 단계 판단 (원본 next-step)

| 상태 | 추천 |
| --- | --- |
| 가사·style 초안만 있고 승인 없음 | 검토안 다시 제시(`yue-pre-generation-check`) |
| 사실 기반 곡인데 출처 확인 대기 | `yue-research`의 사람 확인 |
| 대기열·실행 중 | 기다림. 새 제출 금지. `job:wait` 또는 `queue:list` |
| 실패·`uncertain` | 실행 여부 확인 후 원인 조사(`yue-result-review`). 자동 재제출 금지 |
| 완료, truncation 참 | 완주 아님. 원인 조사 |
| 완료, 검수 기록 없음 | `yue-result-review` |
| 검수 완료, 청취 미실행 | 사용자 청취 요청 |
| 청취 승인 | 마스터링(`yue-mastering`) → 공개 준비(`yue-release`) |

추천은 하나만 먼저 제시하고 이유를 한 줄로 쓴다. 추가 생성을 기본 추천으로 삼지 않는다(재제작은 효율 기준을 먼저 적용).

## 진행 현황 (원본 album-dashboard)

여러 곡·앨범은 다음 표로 요약한다.

```text
## 진행 현황 — <프로젝트>
| # | 제목 | 엔진 | 단계 | 결과 파일 | truncation | 검수 | 청취 | 다음 |
- 완료 n / 진행 n / 대기 n / 실패 n
- 막힌 항목:
```

단계 값: `초안` → `승인` → `생성 중` → `생성 완료` → `검수 완료` → `청취 승인` → `마스터링` → `공개 준비`. Road Music에 기록되지 않은 단계(예: 청취)는 대화·사용자 기록에서 확인되지 않으면 `미확인`으로 둔다.

## 아이디어·새 프로젝트 (원본 album-ideas, promote-idea, new-album)

- 아이디어 목록은 사용자가 정한 파일(없으면 작업 폴더의 `IDEAS.md`)에 `제목 / 한 줄 콘셉트 / 장르 / 상태(대기·진행·보류)`로 적는다. 기존 파일은 덮어쓰지 않고 추가한다.
- 아이디어를 실제 작업으로 옮길 때: `roadmusic projects:create --json '{"name":"…"}'`로 프로젝트를 만들고(사용자가 원할 때), 기획은 `yue-album-planner`로 넘긴다. 프로젝트를 만든다고 곡을 생성하지 않는다.
- 제작 요청 원문은 `song:generate`의 `requestPrompt`로 넘기면 Road Music이 실제 곡 폴더에 연결해 자동 기록한다. 생성이 아닌 요청(기획·가사만)을 기록할 때만 `production:request`를 쓴다.

## 이름 바꾸기·정리 (원본 rename, validate-album, import-*)

- 곡 제목 변경: `roadmusic song:rename --json '{"dir":"…","title":"…"}'`. 제목만 바뀌며 음원·가사는 그대로다. 제목을 바꿔도 모델이 부른 가사는 바뀌지 않는다.
- 외부 음원 가져오기: Road Music `songs:import`(실행 버전 schema 확인). 원본 파일은 보존한다.
- 구조 점검: 곡 `dir`에 오디오·`result.json`·(full/melody면) `score.abc`가 있는지, 기존 곡이 덮어써지지 않았는지 확인한다. 파일을 옮기거나 지우는 정리는 Road Music 저장공간 스킬(`road-music-storage`)의 미리보기·확인 절차로만 한다.
