# music-road-music-skills 작업 지침

한국어로 응답한다. 이 저장소는 Road Music(YuE2 `yue-mlx`/`yue`)용 음악 스킬 묶음이다. Codex·Claude Code 모두 같은 `skills/<이름>/SKILL.md`를 쓴다.

## 스킬을 쓸 때

- YuE2 음악 요청은 `skills/yue-music/SKILL.md`에서 시작하고, 거기서 연결하는 스킬과 `skills/yue-music/references/common-rules.md`를 따른다. Codex에서는 `$yue-music`처럼 부르거나 해당 `SKILL.md`를 직접 읽는다.
- Road Music 위치는 `ROAD_MUSIC_HOME`(기본 `/Users/freelife/youtube/music/music-road`)이다. CLI는 셸 함수 `roadmusic() { node "${ROAD_MUSIC_HOME:-…}/cli/road-music.js" "$@"; }`로 부른다. zsh는 `RM="node …"; $RM` 형태를 단어로 나누지 않으므로 쓰지 않는다.
- 음악 생성(`song:generate`·`song:render`·`song:resume`·`song:replay`), 엔진·모델 설치, 업데이트는 사용자가 요청·승인한 범위에서만 한다. 테스트는 `ROADMUSIC_DATA_DIR`를 임시 폴더로 분리하고, 그 폴더로 시작된 서비스는 같은 값으로 `cli:stop`한다.
- Road Music 저장소는 읽기만 한다.

## 이 저장소를 고칠 때

- 스킬을 바꾸면 `node scripts/verify-examples.mjs`(Road Music CLI 필요)와 `node --test tests/*.test.cjs`를 실행한다.
- 스킬을 추가·삭제하면 `manifest.json`, `README.md`의 스킬 표, `docs/skills.md`, `docs/upstream-coverage.md`를 함께 고친다.
- 버전은 `VERSION`과 `manifest.json`을 같이 올리고 `release/YYYY-MM-DD-title.md` 노트를 하나 쓴다. 태그 `vX.Y.Z`를 push하면 `.github/workflows/release.yml`이 Release를 만든다. 기존 태그·Release는 덮어쓰지 않는다.
- GitHub 인증은 상위 `.envrc`를 셸 추적을 끄고 `set -a; source …; set +a`로 적용한다. 원문·토큰을 출력하거나 커밋하지 않는다.
