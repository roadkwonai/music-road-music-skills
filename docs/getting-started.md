# 시작하기 — 설치와 첫 곡

[README](../README.md) · [작업 흐름](workflow.md) · [Codex에서 쓰기](codex.md) · [문제 해결](troubleshooting.md)

## 1. 준비물

| 항목 | 필요한 이유 | 확인 |
| --- | --- | --- |
| Road Music 소스 키트 | 스킬이 Road Music CLI로 준비·생성한다 | `node "$ROAD_MUSIC_HOME/cli/road-music.js" cli:version` |
| Node.js(Road Music 권장 24 LTS) | CLI 실행 | `node --version` |
| `npm ci --include=dev`를 마친 키트 | CLI가 Electron을 개발 의존성으로 쓴다 | Road Music `docs/cli-install.md` |
| ffmpeg·ffprobe | 길이 확인·마스터링·내보내기 | `ffmpeg -version` |
| YuE2 엔진 | 실제 생성(`yue-mlx`는 Apple Silicon, `yue`는 Windows NVIDIA) | Road Music `docs/yue-mlx.md`. 이 묶음은 엔진을 설치하지 않는다 |
| Claude Code 또는 Codex | 스킬을 읽고 실행하는 에이전트 | — |

엔진이 없어도 가사·style 작성, 검수, `song:prepare` 점검까지는 할 수 있다. 생성만 엔진이 필요하다.

## 2. 설치

### Release ZIP으로 설치(권장)

```bash
gh release download --repo roadkwonai/music-road-music-skills --pattern 'MusicRoad-YuE2-Skills-*.zip' --pattern SHA256SUMS.txt
shasum -a 256 -c SHA256SUMS.txt
unzip MusicRoad-YuE2-Skills-*.zip -d ~/music-road-music-skills-release
```

압축을 푼 폴더의 `skills/*`를 아래 방법으로 연결한다.

### 저장소를 받아 링크로 설치

```bash
git clone https://github.com/roadkwonai/music-road-music-skills.git ~/music-road-music-skills
```

Claude Code:

```bash
for d in ~/music-road-music-skills/skills/*/; do ln -s "${d%/}" ~/.claude/skills/; done
```

Codex:

```bash
for d in ~/music-road-music-skills/skills/*/; do ln -s "${d%/}" "${CODEX_HOME:-$HOME/.codex}/skills/"; done
```

- 같은 이름의 스킬이 이미 있으면 `ln -s`가 실패한다. 기존 것을 덮어쓰지 않는다.
- 스킬끼리 `../yue-music/references/…`로 서로 참조하므로 폴더 구조를 유지한 채 링크한다(링크의 실제 위치 기준으로 풀린다).
- 링크 방식이라 저장소를 `git pull`하면 설치본도 바로 바뀐다.

### Road Music 위치 알려주기

기본값은 이 사용자 환경의 `/Users/freelife/youtube/music/music-road`다. 다른 곳이면 셸 설정에 넣는다.

```bash
export ROAD_MUSIC_HOME=/path/to/music-road
```

Windows PowerShell:

```powershell
setx ROAD_MUSIC_HOME "C:\path\to\music-road"
```

## 3. 설치 확인

에이전트에게 "YuE2 작업 환경을 점검해줘"라고 하면 `yue-setup-check`가 읽기 전용으로 점검한다. 직접 확인하려면:

```bash
roadmusic() { node "${ROAD_MUSIC_HOME:-/Users/freelife/youtube/music/music-road}/cli/road-music.js" "$@"; }
roadmusic cli:version
roadmusic yue:capabilities --json '{"engine":"yue-mlx"}'
```

묶음 자체 검사:

```bash
node --test tests/*.test.cjs
ROADMUSIC_DATA_DIR="$(mktemp -d)" node scripts/verify-examples.mjs
```

## 4. 첫 곡

```text
YuE MLX로 한국어 여성 보컬 발라드 1곡 준비해줘. 이별 후 혼자 남은 방이 주제야. 생성 전에 보여줘.
```

에이전트는 가사·style·요청 JSON·한국어 검수·`## YuE2 공식 가이드 보정 보고`를 한 번에 보여주고 멈춘다. 마음에 들면:

```text
그대로 생성해줘.
```

처음부터 맡기려면:

```text
가사와 프롬프트까지 전부 자동으로 정해서 yue-mlx로 트로트 1곡 생성해줘.
```

생성 뒤에는 "결과 검수해줘", "-14 LUFS로 마스터링해줘", "유튜브에 올리기 전 점검해줘"로 이어 간다. 자세한 흐름은 [작업 흐름](workflow.md).

## 5. 업데이트·제거

- 업데이트 확인: 스킬을 처음 쓸 때 `yue-skills-update`가 자동으로 최신 Release를 확인해 알려 준다. 직접 확인은 `node ~/music-road-music-skills/skills/yue-skills-update/scripts/check-update.mjs --force`.
- 업데이트: 저장소 링크 설치면 `git -C ~/music-road-music-skills pull --ff-only`. Release 설치면 새 ZIP을 받아 체크섬 확인 후 교체한다. 최신 버전은 [Releases](https://github.com/roadkwonai/music-road-music-skills/releases)와 [릴리스 노트](../release/README.md).
- 제거: `~/.claude/skills/yue-*`, `~/.codex/skills/yue-*` 링크만 지운다. 저장소·Road Music·곡은 그대로다.
