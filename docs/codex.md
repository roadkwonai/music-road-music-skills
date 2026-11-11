# Codex에서 쓰기

[README](../README.md) · [시작하기](getting-started.md) · [테스트](testing.md)

이 묶음은 Codex와 Claude Code에서 같은 `SKILL.md`를 쓴다. Codex용으로 스킬마다 `agents/openai.yaml`(표시 이름·짧은 설명·기본 프롬프트)을 붙였다. Road Music 자체 스킬과 같은 형식이다.

## 설치

```bash
for d in ~/music-road-music-skills/skills/*/; do ln -s "${d%/}" "${CODEX_HOME:-$HOME/.codex}/skills/"; done
```

확인:

```bash
codex exec --skip-git-repo-check --ephemeral -s read-only \
  "Do not run commands. List every available skill whose name starts with 'yue-'."
```

2026-11-12에 codex-cli 0.167.0에서 심볼릭 링크로 설치한 13개 스킬을 모두 인식하는 것을 확인했다.

## 부르는 법

- 자연어로 요청하면 description을 보고 `yue-music`이 선택된다: "YuE MLX로 한국어 발라드 1곡 준비해줘."
- 명시하려면 `$yue-music`, `$yue-style-engineer`처럼 앞에 붙인다. 각 스킬의 `default_prompt`가 예시다.
- 이 저장소 안에서 Codex를 열면 루트 [AGENTS.md](../AGENTS.md)가 함께 적용된다.

## Codex에서 특히 지킬 것

| 항목 | 이유 | 스킬의 대응 |
| --- | --- | --- |
| zsh 셸 | `RM="node …"; $RM cmd`가 zsh에서 깨진다 | 모든 스킬이 `roadmusic()` 셸 함수를 쓴다 |
| 매 명령이 새 셸 | 함수·환경 변수가 이어지지 않는다 | 함수 정의와 `ROADMUSIC_DATA_DIR`를 명령마다 함께 쓴다 |
| 참고 문서를 덜 여는 경향 | 1차 Codex 테스트에서 보고서 표 머리글·승인 질문·검수 판정어가 빠졌다 | 필수 출력 골격을 `yue-music` 본문에 직접 넣었다 |
| 샌드박스 | `workspace-write`에서는 작업 폴더 밖에 쓸 수 없다 | 테스트용 `ROADMUSIC_DATA_DIR`를 작업 폴더 안에 둔다. 생성은 Road Music 서비스·엔진이 필요하므로 사용자의 실제 환경에서 실행한다 |
| 승인 정책 `never` | 묻지 않고 실행할 수 있다 | 스킬이 생성 명령을 모드별 승인 뒤로 묶는다. 생성·설치는 요청 범위에서만 |

## 테스트 결과

[테스트 문서](testing.md#codex)에 Codex 1차·2차 결과와 바꾼 점을 정리했다.
