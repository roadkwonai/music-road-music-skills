---
name: yue-skills-update
description: 이 YuE2 스킬 묶음(music-road-music-skills)의 설치 버전과 GitHub 최신 Release를 비교해 새 버전을 알리고, 사용자가 원할 때 최신 Release로 업데이트하는 방법을 안내·실행한다. yue-* 스킬을 처음 쓸 때 한 번 자동으로 확인하며(12시간 캐시), "스킬 업데이트", "최신 버전이야?", "yue 스킬 버전" 요청에 사용한다. Checks for and guides updates of the music-road-music-skills bundle, like Road Music's cli:update:check.
---

# YuE2 스킬 묶음 업데이트 확인

Road Music CLI의 `cli:update:check`처럼 이 스킬 묶음도 새 Release를 확인한다. **확인은 읽기 전용이고, 설치·교체는 사용자가 요청했을 때만 한다.** [공통 규칙](../yue-music/references/common-rules.md)을 적용한다.

## 1. 확인 (사용 시 자동, 세션당 한 번)

```bash
node "<이 SKILL.md가 있는 폴더>/scripts/check-update.mjs"          # 12시간 캐시 사용
node "<이 SKILL.md가 있는 폴더>/scripts/check-update.mjs" --force  # 사용자가 "지금 확인"을 요청했을 때
```

- 스크립트는 링크 설치여도 실제 묶음 루트의 `VERSION`을 읽고, GitHub 공개 API로 `roadkwonai/music-road-music-skills`의 최신 Release와 태그 커밋을 조회한다. 인증 토큰이나 사용자 정보를 보내지 않는다. 결과는 `~/.cache/music-road-music-skills/update-check.json`에 12시간 저장한다.
- 출력은 JSON 한 줄이다. `status`에 따라 다음처럼 알린다.

| `status` | 뜻 | 사용자에게 |
| --- | --- | --- |
| `up-to-date`, `local-ahead` | 최신(또는 개발 중인 체크아웃이 더 앞섬) | 알리지 않고 작업 계속 |
| `update-available` | 더 높은 버전의 Release가 있음 | 현재·최신 버전, 제목, Release 링크를 한두 줄로 알리고 작업 계속 |
| `same-version-different-commit` | 같은 번호로 다시 배포된 Release(예: 0.1.0 유지 기간)이고 git 설치본이 그 커밋을 포함하지 않음 | 같은 버전의 수정본이 있다고 알림 |
| `local-newer` | 설치본 번호가 Release보다 높음 | 알리지 않음(개발본) |
| `no-release`, `check-failed`, `local-version-unknown` | 확인 불가 | 묻지 않으면 알리지 않음. 사용자가 확인을 요청했으면 사유를 그대로 보고 |

- 알림은 작업을 막지 않는다. 음악 요청 중에 업데이트를 설치하지 않는다.
- Release 설치본(ZIP)은 버전 번호로만 비교한다. 같은 번호의 재배포는 Release 노트의 날짜로만 짐작할 수 있다고 밝힌다.

확인만 요청받았으면 git·설치 명령은 실행하지 않는다(스크립트가 필요한 정보를 낸다). 사용자가 "업데이트 방법"을 물으면 결과의 `installMode`·`root`·`latest`를 채운 **실제 명령**을 아래에서 골라 보여준다(실행은 하지 않음).

## 2. 업데이트 (사용자가 요청했을 때만)

설치 방식은 확인 결과의 `installMode`로 고른다. 실행 전 현재 버전·최신 버전·바뀌는 위치를 한 줄로 밝힌다.

### git 체크아웃(`installMode: "git"`)

```bash
git -C "<root>" status --porcelain     # 로컬 수정이 있으면 멈추고 보고(덮어쓰지 않음)
git -C "<root>" fetch --tags origin
git -C "<root>" pull --ff-only
node "<root>/skills/yue-skills-update/scripts/check-update.mjs" --force
```

`~/.claude/skills`·`~/.codex/skills`의 링크는 그대로 새 내용을 가리킨다. fast-forward가 안 되면 멈추고 보고한다.

### Release ZIP(`installMode: "release"`)

```bash
NEW="$HOME/music-road-music-skills-<최신버전>"            # 기존 폴더와 다른 새 폴더
mkdir "$NEW" && cd "$NEW"
gh release download v<최신버전> --repo roadkwonai/music-road-music-skills
shasum -a 256 -c SHA256SUMS.txt                           # 실패하면 중단
unzip -q MusicRoad-YuE2-Skills-<최신버전>.zip
```

체크섬이 맞으면 `~/.claude/skills/yue-*`, `${CODEX_HOME:-~/.codex}/skills/yue-*` 링크를 새 폴더의 `skills/*`로 바꾼다. 기존 링크가 이 묶음의 이전 폴더를 가리키는지 먼저 확인하고, 다른 스킬·다른 경로의 링크는 건드리지 않는다. 이전 폴더는 지우지 않고 사용자에게 남겨 둔다. `gh`가 없으면 Release 페이지에서 ZIP과 `SHA256SUMS.txt`를 받는 방법을 안내한다.

업데이트 뒤 `check-update.mjs --force`로 `up-to-date`인지, `node --test tests/*.test.cjs`가 통과하는지 확인하고 보고한다. 체크섬·압축·확인 중 하나라도 실패하면 업데이트 완료라고 하지 않는다.

## 보고 예

```text
YuE2 스킬 묶음 새 버전이 있습니다: 현재 0.1.0 → 최신 0.2.0 (「…」, https://github.com/roadkwonai/music-road-music-skills/releases/tag/v0.2.0). 업데이트를 원하시면 말씀해 주세요.
```
