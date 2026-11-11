---
name: yue-setup-check
description: Road Music YuE2 작업을 시작할 때 CLI 버전·업데이트 알림·필수 도구·엔진 설치 상태·YuE 엔진 지원 범위·이 스킬 묶음의 최신 Release 여부를 점검하고, 처음 쓰는 사용자에게 사용법을 안내한다. 설치·업데이트·생성은 하지 않는다. Use at session start, for "설정 확인", "설치됐어?", "지금 곡 만들 수 있어?", "도움말", "처음 써봐" with YuE2 in Road Music (replaces session-start, setup, configure, health-check, help, tutorial, about).
---

# YuE2 작업 환경 점검·안내

원본의 `session-start`·`setup`·`configure`·`health-check`·`help`·`tutorial`·`about`을 Road Music CLI 기준으로 바꿨다. 원본은 Python 가상환경·MCP 서버·설정 파일을 점검했지만, 이 묶음은 별도 서버가 없고 Road Music CLI를 그대로 쓴다. [공통 규칙](../yue-music/references/common-rules.md)을 적용한다.

**점검은 읽기만 한다.** 엔진·모델 설치, CLI·앱 업데이트, 스킬 업데이트, 생성은 사용자가 요청했을 때만 Road Music 문서(`docs/cli-install.md`, `docs/updates.md`, `docs/yue-mlx.md`)나 `yue-skills-update`의 절차로 한다.

```bash
ROAD_MUSIC_HOME="${ROAD_MUSIC_HOME:-/Users/freelife/youtube/music/music-road}"
roadmusic() { node "${ROAD_MUSIC_HOME:-/Users/freelife/youtube/music/music-road}/cli/road-music.js" "$@"; }  # bash·zsh 공통. 셸 호출마다 다시 정의
```

## 점검 순서

1~7은 로컬(서비스를 시작하지 않음), 8~9는 서비스 명령이다.

| # | 점검 | 명령 | 통과 기준 |
| --- | --- | --- | --- |
| 1 | Road Music 위치 | `test -f "$ROAD_MUSIC_HOME/cli/road-music.js"` | 파일 있음. 없으면 `ROAD_MUSIC_HOME` 설정 안내 |
| 2 | Node.js | `node --version` | 실행됨(Road Music 문서 기준 Node.js 24 LTS 권장) |
| 3 | CLI 버전·업데이트 알림 | `roadmusic cli:version`, `roadmusic cli:update:check` | 새 버전은 알리기만 함. 0.1.1보다 낮으면 `song:prepare`의 `officialGuide` 공식 점검이 없다고 함께 알림 |
| 4 | 스킬 묶음 업데이트 | `node "<yue-skills-update 폴더>/scripts/check-update.mjs"` | `status`에 따라 알림(`yue-skills-update`) |
| 5 | YuE 지원 범위 | `roadmusic yue:capabilities --json '{"engine":"yue-mlx"}'` | `platformMatches`, 설치 파일 감지, 기본값(CFG·ODE·runtime). 파일 감지는 실행 준비 확인이 아님 |
| 6 | 입력 계약 | `roadmusic cli:schema` | `song:prepare`·`song:generate`에 `engine`·`cot`·`abc`·`parts` 필드 존재 |
| 7 | 서비스 | `roadmusic service:status` | 떠 있는지만 확인 |
| 8 | 필수 도구 | `roadmusic setup:check` | ffmpeg·ffprobe 등 결과 |
| 9 | 엔진 준비 | `roadmusic engines:list`, `roadmusic app:state` | 사용할 엔진(`yue-mlx`/`yue`)의 설치 여부, 현재 프로젝트 |

- **서비스 시작 판단:** 사용자가 환경 점검이나 "지금 만들 수 있어?"를 직접 물었다면 읽기용 서비스 시작(8~9)은 그 요청 범위로 본다. 세션 시작 때 스스로 하는 자동 점검이라면 1~7만 하고, 8~9는 "미실행(서비스 시작 필요)"으로 적는다.
- 서비스 연결이 막히면(샌드박스·권한 오류 등) 8~9를 `확인 불가(사유)`로 적고, 5의 파일 감지만으로 "바로 생성 가능"이라고 단정하지 않는다.
- 임시 `ROADMUSIC_DATA_DIR`나 다른 프로필에서 본 "미설치"를 사용자 실제 환경의 상태로 보고하지 않는다.
- (선택) 묶음 자체 검증: `node <묶음 루트>/scripts/verify-examples.mjs`(임시 `ROADMUSIC_DATA_DIR`).

## 보고

```text
## 작업 환경 점검
| # | 항목 | 결과 | 메모 |
- 지금 할 수 있는 것: (예: 생성 가능 / 초안·검수·song:prepare만 가능)
- 사용자 결정이 필요한 것: (예: 엔진 설치, CLI 업데이트, 스킬 업데이트)
```

"지금 바로 곡을 만들 수 있나?"에는 8~9까지 확인한 경우에만 "예"라고 답한다.

## 처음 쓰는 사용자 안내 (원본 tutorial·help)

1. 원하는 곡을 말한다: "YuE MLX로 한국어 여성 발라드 1곡 준비해줘."
2. AI가 가사·style·요청 JSON과 `## YuE2 공식 가이드 보정 보고`를 보여준다(생성 전).
3. 확인하고 "그대로 생성해줘"라고 하면 생성한다. 처음부터 "가사와 프롬프트까지 전부 자동으로 정하고 생성해줘"라고 하면 검토 없이 진행한다.
4. 생성 뒤 결과 검수(`yue-result-review`), 마스터링(`yue-mastering`), 공개 준비(`yue-release`)를 이어서 할 수 있다.

전체 스킬 목록은 묶음 루트의 `README.md`와 `docs/skills.md`를 가리킨다.
