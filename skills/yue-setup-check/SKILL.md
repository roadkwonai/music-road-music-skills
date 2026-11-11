---
name: yue-setup-check
description: Road Music YuE2 작업을 시작할 때 CLI 버전·업데이트 알림·필수 도구·엔진 설치 상태·YuE 엔진 지원 범위·이 스킬 묶음 버전을 읽기 전용으로 점검하고, 처음 쓰는 사용자에게 사용법을 안내한다. 설치·업데이트·생성은 하지 않는다. Use at session start, for "설정 확인", "설치됐어?", "도움말", "처음 써봐" with YuE2 in Road Music (replaces session-start, setup, configure, health-check, help, tutorial, about).
---

# YuE2 작업 환경 점검·안내

원본의 `session-start`·`setup`·`configure`·`health-check`·`help`·`tutorial`·`about`을 Road Music CLI 기준으로 바꿨다. 원본은 Python 가상환경·MCP 서버·설정 파일을 점검했지만, 이 묶음은 별도 서버가 없고 Road Music CLI를 그대로 쓴다. [공통 규칙](../yue-music/references/common-rules.md)을 적용한다.

**모든 단계는 읽기 전용이다.** 엔진·모델 설치, CLI·앱 업데이트, 서비스 시작은 사용자가 요청했을 때만 Road Music 문서(`docs/cli-install.md`, `docs/updates.md`, `docs/yue-mlx.md`)의 절차로 한다.

## 점검 순서

```bash
ROAD_MUSIC_HOME="${ROAD_MUSIC_HOME:-/Users/freelife/youtube/music/music-road}"
roadmusic() { node "${ROAD_MUSIC_HOME:-/Users/freelife/youtube/music/music-road}/cli/road-music.js" "$@"; }  # bash·zsh 공통. 셸 호출마다 다시 정의
```

| # | 점검 | 명령 | 통과 기준 |
| --- | --- | --- | --- |
| 1 | Road Music 위치 | `test -f "$ROAD_MUSIC_HOME/cli/road-music.js"` | 파일 있음. 없으면 `ROAD_MUSIC_HOME` 설정 안내 |
| 2 | Node.js | `node --version` | 실행됨(Road Music 문서 기준 Node.js 24 LTS 권장) |
| 3 | CLI 버전 | `roadmusic cli:version` | `ok:true` |
| 4 | 업데이트 알림 | `roadmusic cli:update:check` | 새 버전은 알리기만 함. 설치하지 않음 |
| 5 | 필수 도구 | `roadmusic setup:check`(서비스 시작) | ffmpeg·ffprobe 등 결과를 그대로 보고 |
| 6 | 엔진 | `roadmusic engines:list`(서비스 시작) | 사용자가 쓸 엔진(`yue-mlx`/`yue`)의 상태. 미설치면 보고만 |
| 7 | YuE 지원 범위 | `roadmusic yue:capabilities --json '{"engine":"yue-mlx"}'` | `platformMatches`, 기본값(CFG·ODE), runtime 기본값 |
| 8 | 입력 계약 | `roadmusic cli:schema`(로컬) | `song:prepare`·`song:generate`에 `engine`·`cot`·`abc`·`parts` 필드 존재 |
| 9 | 이 묶음 버전 | 묶음 루트의 `VERSION` | 버전 표시. 최신 확인은 `gh release view --repo roadkwonai/music-road-music-skills`(사용자가 원할 때) |
| 10 | 예시 검증(선택) | `node <묶음 루트>/scripts/verify-examples.mjs` | 예시 요청이 모두 기대와 일치. `ROADMUSIC_DATA_DIR`는 임시 폴더 |

점검용으로 데이터를 쓰는 명령은 `ROADMUSIC_DATA_DIR`를 임시 폴더로 분리한다. 단, **엔진 설치 상태는 데이터 폴더·프로필에 따라 다르게 보일 수 있다.** 임시 폴더에서 본 "미설치"를 사용자 실제 환경의 상태로 보고하지 않는다. 실제 상태를 보려면 사용자의 기본 프로필로 `engines:list`를 읽는다(읽기 전용).

## 보고

```text
## 작업 환경 점검
| # | 항목 | 결과 | 메모 |
- 바로 할 수 있는 것: (예: 초안·검수·song:prepare는 가능, 생성은 yue-mlx 설치 후)
- 사용자 결정이 필요한 것: (예: 엔진 설치, CLI 업데이트)
```

## 처음 쓰는 사용자 안내 (원본 tutorial·help)

짧게 이렇게 안내한다.

1. 원하는 곡을 말한다: "YuE MLX로 한국어 여성 발라드 1곡 준비해줘."
2. AI가 가사·style·요청 JSON과 `## YuE2 공식 가이드 보정 보고`를 보여준다(생성 전).
3. 확인하고 "그대로 생성해줘"라고 하면 생성한다. 처음부터 "가사와 프롬프트까지 전부 자동으로 정하고 생성해줘"라고 하면 검토 없이 진행한다.
4. 생성 뒤 결과 검수(`yue-result-review`), 마스터링(`yue-mastering`), 공개 준비(`yue-release`)를 이어서 할 수 있다.

전체 스킬 목록은 묶음 루트의 `README.md`와 `docs/skills.md`를 가리킨다.
