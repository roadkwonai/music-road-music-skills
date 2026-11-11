# Music Road YuE2 Skills

**Road Music으로 YuE2 음악을 만드는 Claude Code·Codex용 스킬 묶음입니다.** 대화로 원하는 곡을 말하면 기획, 작사, style 프롬프트, 생성 전 공식 가이드 점검, 생성, 결과 검수, 악보 편집, 마스터링, 공개 준비까지 이어서 처리합니다. 모든 단계는 YuE2 공식 가이드와 Road Music 규칙을 따릅니다.

Suno용으로 만들어진 [claude-ai-music-skills](https://github.com/bitwize-music-studio/claude-ai-music-skills)(스킬 53개, CC0)를 분석해 YuE2 모델에 맞게 다시 썼습니다. Suno의 슬라이더·Exclude Styles·Persona·구간 교체처럼 YuE2에 없는 기능은 비슷한 옵션으로 흉내 내지 않고 "대응 없음"으로 밝힙니다.

[![Release](https://img.shields.io/github/v/release/roadkwonai/music-road-music-skills?label=release)](https://github.com/roadkwonai/music-road-music-skills/releases/latest)

| 항목 | 내용 |
| --- | --- |
| 대상 엔진 | `yue-mlx`(Apple Silicon, 커뮤니티 MLX 포트) · `yue`(Windows NVIDIA, 공식 YuE2 워커) |
| 기준 | YuE2 공식 `yue2-v0.1.6` 고정판, 공식 main(2026-11-01), Road Music CLI 0.1.0(protocol 2) |
| 에이전트 | Claude Code, Codex(codex-cli 0.167.0에서 확인) |
| 스킬 | 13개 ([레퍼런스](docs/skills.md)) |
| 라이선스 | MIT ([LICENSE](LICENSE)) |

---

## 이런 식으로 씁니다

```text
나:   맥에서 YuE MLX로 한국어 여성 보컬 락발라드 1곡 만들고 싶어. 이별 후 혼자 남은 방을 정리하는 내용, 150초, 피아노랑 일렉기타 중심. 가사는 네가 써줘.
AI:   기본 검토 모드로 진행합니다. 생성 전에 확인받습니다.
      - 가사(Verse·Pre-Chorus·Chorus·Bridge)와 한국어 검수 판정
      - style: Korean, emotional rock ballad, solo female vocal, piano, electric guitar, … 76 BPM
      - 요청 JSON과 song:prepare 결과(valid, 공식 점검 pass 8 · advice 0)
      - ## YuE2 공식 가이드 보정 보고(보정 전후 표)
      이 가사·프롬프트·옵션으로 생성할까요?

나:   그대로 생성해줘.
AI:   song:generate → job:wait. 결과 파일, truncation, 실제 길이, 가사 반영(전사/청취 구분)을 보고합니다.

나:   유튜브용으로 -14 LUFS 마스터링하고 올리기 전에 점검해줘.
AI:   원본은 보존하고 새 WAV를 만든 뒤 측정 전후 표를 보여줍니다. 이어서 권리·AI 고지·메타데이터 점검표를 줍니다.
```

Suno에서 쓰던 프롬프트도 그대로 붙여 넣으면 원문은 보존하고, YuE2용 보정안과 실행 JSON(원문판·보정판)을 따로 줍니다.

## 지키는 원칙

- **사용자 원문 보존:** 준 가사·프롬프트·옵션은 임의로 고치지 않습니다. 고칠 점은 `원문 → 보정안 → 근거 → 적용 여부`로 제안하고, 승인받은 것만 반영합니다.
- **생성 전 승인:** 기본은 다 보여주고 묻습니다. "가사와 프롬프트까지 전부 자동으로 정하고 생성해줘"처럼 전체를 맡긴 경우에만 묻지 않고 진행합니다.
- **매번 공식 가이드 보정 보고:** 프롬프트를 쓰거나 생성을 준비할 때마다 `song:prepare`의 공식 점검으로 보정하고 `## YuE2 공식 가이드 보정 보고`와 보정 전후 표를 붙입니다. 보정이 없어도 "보정 없음"이라고 씁니다.
- **한국어 검수:** 한국어 제목·가사는 생성 전에 자연스러움을 검수합니다. 한국어가 없는 항목은 해당 없음입니다.
- **보장하지 않는 것은 보장한다고 쓰지 않음:** 정확한 길이·템포, 특정 가수 음색, 발음, 무보컬, 악기 완전 배제는 청취로만 확인합니다.
- **엔진 유지·설치 안 함:** 고른 엔진을 바꾸거나 모델을 몰래 내려받지 않습니다.

자세한 규칙은 [공통 규칙](skills/yue-music/references/common-rules.md)에 있습니다.

## 스킬 13개

| 단계 | 스킬 | 하는 일 | 원본 대응 |
| --- | --- | --- | --- |
| 진입 | [`yue-music`](skills/yue-music/SKILL.md) | 요청 모드 판정, 엔진 유지, 단계 연결, 필수 출력 골격 | session-start, help, next-step |
| 기획 | [`yue-album-planner`](skills/yue-album-planner/SKILL.md) | 여러 곡의 순서·에너지·곡별 요청 설계 | album-conceptualizer |
| 조사 | [`yue-research`](skills/yue-research/SKILL.md) | 실화·다큐 곡의 1차 자료 조사, 사람 출처 확인 관문 | researcher 외 13개 |
| 작사 | [`yue-lyric-writer`](skills/yue-lyric-writer/SKILL.md) | 부를 말 + 구간 태그만 쓰는 YuE2 가사 | lyric-writer, lyric-refiner |
| 프롬프트 | [`yue-style-engineer`](skills/yue-style-engineer/SKILL.md) | style·parts·cot·seed·abc 작성과 보정 | suno-engineer |
| 검수 | [`yue-lyric-reviewer`](skills/yue-lyric-reviewer/SKILL.md) | 한국어·계약·발음 위험·AI 투·차용 점검 | lyric-reviewer, pronunciation-specialist, voice-checker, explicit-checker |
| 관문 | [`yue-pre-generation-check`](skills/yue-pre-generation-check/SKILL.md) | G0~G10, `song:prepare` 2회, 승인 후 생성 | pre-generation-check |
| 결과 | [`yue-result-review`](skills/yue-result-review/SKILL.md) | truncation·길이·전사·청취 구분, 재제작 판단 | Regeneration Workflow |
| 악보 | [`yue-score-editor`](skills/yue-score-editor/SKILL.md) | ABC 편집·재화성·악보 기반 커버·악보 내보내기 | sheet-music-publisher, Song Editor·Cover |
| 후처리 | [`yue-mastering`](skills/yue-mastering/SKILL.md) | 원본 보존 마스터링·QC·내보내기 | mastering-engineer, mix-engineer |
| 공개 | [`yue-release`](skills/yue-release/SKILL.md) | 권리·라이선스·AI 고지·메타데이터·아트·홍보 문구 | release-director, promo-*, album-art-director, plagiarism-checker |
| 관리 | [`yue-project-status`](skills/yue-project-status/SKILL.md) | 이어 하기·다음 단계·진행 현황·이름 변경 | resume, next-step, album-dashboard 외 |
| 점검 | [`yue-setup-check`](skills/yue-setup-check/SKILL.md) | CLI·엔진·지원 범위 읽기 전용 점검, 처음 사용 안내 | session-start, setup, health-check, tutorial 외 |

원본 53개 스킬과 참고 문서·도구를 하나씩 어떻게 처리했는지는 [원본 전수 대응표](docs/upstream-coverage.md)에 있습니다.

## 설치

Road Music 소스 키트(CLI)가 먼저 있어야 합니다. 엔진이 없어도 작사·프롬프트·검수·준비 점검까지는 됩니다.

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

Road Music이 기본 위치(`/Users/freelife/youtube/music/music-road`)가 아니면:

```bash
export ROAD_MUSIC_HOME=/path/to/music-road
```

Release ZIP 설치, Windows, 업데이트·제거는 [시작하기](docs/getting-started.md)를 보세요.

## 문서

| 문서 | 내용 |
| --- | --- |
| [시작하기](docs/getting-started.md) | 준비물, 설치(Claude·Codex·Release ZIP), 설치 확인, 첫 곡, 업데이트·제거 |
| [작업 흐름](docs/workflow.md) | 전체 흐름도, 요청 모드, 매번 받는 보고, 예시 대화 4가지 |
| [스킬 레퍼런스](docs/skills.md) | 13개 스킬의 용도·핵심 규칙·CLI·원본 대응 |
| [원본 전수 대응표](docs/upstream-coverage.md) | 원본 53개 스킬·참고 문서·도구의 전환·통합·대체·제외 판정 |
| [Suno→YuE2 대응표](skills/yue-music/references/suno-to-yue2.md) | Style 칸, 메타태그, 슬라이더, Cover 등 Suno 개념별 변환 |
| [공통 규칙](skills/yue-music/references/common-rules.md) | 엔진, 입력 계약(공식 사실과 Road Music 규칙 구분), 원문 보존, 승인, 로컬/서비스 명령 |
| [Road Music CLI 연결](skills/yue-music/references/road-music-cli.md) | 명령 순서, 요청 JSON 필드, `song:prepare` 결과와 `officialGuide` 점검 ID |
| [Codex에서 쓰기](docs/codex.md) | 설치·호출·Codex에서 주의할 점 |
| [테스트와 검증](docs/testing.md) | 정적 검사, 예시 검증, Claude·Codex 시나리오 테스트 결과 |
| [문제 해결](docs/troubleshooting.md) | zsh 함정, `ok:false`/`valid:false`, 남은 서비스, 미설치 표시 등 |
| [릴리스 노트](release/README.md) | 버전별 변경과 릴리스 절차 |

## 원본 대비 주요 변경

| Suno 원본 | 이 묶음 |
| --- | --- |
| Style 칸(1,000자), "보컬 먼저" 문장 블록 | 장르·악기·보컬·언어·템포를 짧은 쉼표 태그로(태그당 10단어 이하) |
| Performance Cue `[Verse - cold regal]`, 무드 태그, 괄호 백보컬 | 쓰지 않음. 부를 말 + 구간 태그만, 의도는 곡 전체 style로 |
| 발음용 철자 바꾸기 | 폐기. 가사 주석·철자는 그대로 불릴 수 있고 발음 제어 채널이 없음 |
| Exclude Styles, `no drums` | `negative_prompt` 없음. 긍정형 편성 묘사 권장, 배제 보장 없음 |
| v6 모델·Variety·Weirdness·Style Influence·Max Mode | 대응 없음. 엔진 선택과 YuE2 고유 `cot`·`seed`·`abc` |
| Duration(값에서 자름) | `targetSeconds`는 기록용, 실제 길이는 가사 분량과 자연 종료 |
| Persona·Voices·오디오 업로드 Cover | 참조 가수·음원 필드 없음. 악보 기반 커버(SheetSage2 → `cot:"melody"`) |
| Extend·Replace Section·Stems | 대응 없음. 악보 사본 편집 후 전체 재생성 |
| Python MCP 서버(80+ 도구)·상태 캐시 | Road Music CLI와 앱 상태 |
| 스템별 믹싱 | YuE2는 스템을 내지 않으므로 전체 믹스 마스터링만 |
| "다시 생성해 보기" | 확인된 기술 원인이 있을 때만 재제작(Road Music 효율 기준) |

## 검증

- **정적 검사:** `node --test tests/*.test.cjs`. manifest·frontmatter·Codex 메타데이터·링크·zsh 함정·예시 필드·릴리스 스크립트를 확인합니다. GitHub Actions 릴리스 관문에서도 실행됩니다.
- **예시 검증:** `ROADMUSIC_DATA_DIR="$(mktemp -d)" node scripts/verify-examples.mjs --write verification/RESULTS.md`. 예시 요청 7개를 실제 `song:prepare`에 넣어 `valid:true`, 엔진 유지, 공식 점검 advice가 기대와 같은지 봅니다. 최근 결과는 [verification/RESULTS.md](verification/RESULTS.md)에 있습니다.
- **시나리오 테스트:** Suno 변환, 새 곡 검토 모드, 자동 위임 + 사용자 가사, 마스터링의 4가지 요청을 Claude와 Codex로 돌려 채점했습니다([테스트와 검증](docs/testing.md)).

이 검증은 입력 계약과 절차 확인입니다. 이 작업에서 실제 YuE2 음악 생성은 하지 않았고, 가창·음질은 생성 후 청취로만 확인할 수 있습니다.

## 남은 한계

- `officialGuide`는 문자열 휴리스틱입니다. 실제로 부르는 괄호 메아리도 주석으로 표시하고, 모든 위반을 잡지는 못합니다.
- `score:check`는 YuE 런타임이 있어야 동작합니다. 오프라인에서는 `score:inspect`·`score:compare`를 씁니다.
- `yue` 엔진(Windows NVIDIA)은 Mac에서 `song:prepare`로만 확인했습니다.
- 한국어 YuE2 가창 품질은 공식 자료가 보증하지 않습니다(YuE2 모델 카드 언어 메타데이터는 zh/en).
- Suno 쪽 사실(칸 글자 수, 모델명 등)은 원본 스킬 문서 기준이며 Suno 공식 자료로 다시 확인하지 않았습니다.
- Road Music CLI·문서가 바뀌면 요약이 낡을 수 있습니다. 실행 버전 `cli:schema`와 Road Music 문서가 우선이며, 바뀌면 검증을 다시 돌립니다.

## 출처와 라이선스

- **이 묶음:** MIT, Copyright (c) 2026 하이밸류연구소.
- **원본 스킬:** [bitwize-music-studio/claude-ai-music-skills](https://github.com/bitwize-music-studio/claude-ai-music-skills)(커밋 `597d928`), CC0 1.0 Universal. 원문을 복사하지 않고 구조와 기법을 참고해 새로 썼습니다.
- **YuE2:** 공식 고정판 `yue2-v0.1.6`의 코드·문서·스킬은 CC BY-NC 4.0, 공식 main은 Apache-2.0, 커뮤니티 MLX 포트 코드는 Apache-2.0, 모델 가중치는 별도 모델 라이선스입니다. 이 묶음은 공식 원문을 동봉하지 않고 Road Music 저장소의 보관본을 가리키며 규칙만 요약합니다. 생성물의 권리와 상업 이용 조건은 `yue-release` 스킬과 Road Music `docs/yue-prompt-guide.md#rights`, 최신 공식 조건을 확인하세요.
- **Road Music:** [roadkwonai/music-road](https://github.com/roadkwonai/music-road). 이 묶음은 그 문서와 CLI를 참조만 합니다.
