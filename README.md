# music-road-music-skills — YuE2용 Road Music 음악 스킬 묶음

Suno용 Claude 음악 스킬 [bitwize-music-studio/claude-ai-music-skills](https://github.com/bitwize-music-studio/claude-ai-music-skills)(커밋 `597d928`, 2026-10-13)를 분석해 **YuE2 공식 가이드와 Road Music CLI**에 맞게 다시 만든 스킬 묶음이다. Road Music(`/Users/freelife/youtube/music/music-road`)과 함께 쓰며, 그 저장소는 수정하지 않는다.

- 대상 엔진: `yue-mlx`(Apple Silicon, 커뮤니티 MLX 포트) / `yue`(Windows NVIDIA, 공식 YuE2 워커). 사용자가 고른 엔진을 유지한다.
- 근거: Road Music `docs/yue-prompt-guide.md`(공식 보정·보고 형식), `docs/music-review.md`(원문 보존·한국어 검수·승인), `docs/lyrics-tags.md`, `docs/yue-cli-workflow.md`, 고정 공식 원문 `docs/vendor/yue2/`(yue2-v0.1.6, main 2026-11-01, MLX usage).
- 기준 CLI: Road Music CLI 0.1.0(protocol 2). 실행 버전의 `schema`가 최종 기준이다.

## 스킬 목록

| 스킬 | 하는 일 | 원본 대응 |
| --- | --- | --- |
| [`yue-music`](skills/yue-music/SKILL.md) | 진입점. 요청 모드 판정, 엔진 유지, 단계별 스킬 연결. [공통 규칙](skills/yue-music/references/common-rules.md)·[CLI 연결](skills/yue-music/references/road-music-cli.md)·[보고 형식](skills/yue-music/references/report-template.md)·[Suno→YuE2 대응표](skills/yue-music/references/suno-to-yue2.md) | session-start, help, next-step |
| [`yue-style-engineer`](skills/yue-style-engineer/SKILL.md) | style(언어, 장르, 보컬, 악기, 선율·프레이징, BPM)·parts·cot·seed·abc 작성과 officialGuide 보정 | suno-engineer |
| [`yue-lyric-writer`](skills/yue-lyric-writer/SKILL.md) | YuE2 가사 계약(부를 말 + 구간 태그만)에 맞춘 작사·허용 범위 개사·다듬기 | lyric-writer, lyric-refiner |
| [`yue-lyric-reviewer`](skills/yue-lyric-reviewer/SKILL.md) | 제목·가사 한국어 검수, 계약·발음 위험·AI 투·노골적 표현 점검, 원문은 제안만 | lyric-reviewer, pronunciation-specialist, voice-checker, explicit-checker |
| [`yue-pre-generation-check`](skills/yue-pre-generation-check/SKILL.md) | 생성 전 관문 G0~G10, `song:prepare` 2회 보정, 보정 보고, 승인 후에만 `song:generate`→`job:wait` | pre-generation-check |
| [`yue-album-planner`](skills/yue-album-planner/SKILL.md) | 여러 곡 순서·에너지·곡별 요청 설계 | album-conceptualizer |
| [`yue-result-review`](skills/yue-result-review/SKILL.md) | truncation·길이·무유도 전사·청취 구분, 악보 선택, 재제작 효율 판단 | Regeneration Workflow, error-recovery |

모든 스킬이 공유하는 규칙: 사용자 원문 가사·프롬프트 보존(보정안만 제안, 승인 후 반영), 한국어 제목·가사 검수, 생성 전 검토·승인(전체 자동 위임일 때만 요청자 검토 생략), 매번 `## YuE2 공식 가이드 보정 보고` 절과 보정 전후 표(보정 없음도 명시), 길이·가창·발음·무보컬을 보장한다고 쓰지 않음.

## 설치

스킬 폴더를 Claude Code(또는 Codex) 스킬 경로에 심볼릭 링크로 연결한다. 기존 같은 이름이 있으면 덮어쓰지 않는다(`ln -s`는 실패한다).

```bash
for d in /Users/freelife/youtube/music/music-road-music-skills/skills/*/; do ln -s "${d%/}" ~/.claude/skills/; done
```

Codex를 쓴다면 대상 경로만 바꾼다(예: `~/.codex/skills/` 또는 프로젝트의 `.agents/skills/`). 스킬 사이의 상대 링크(`../yue-music/references/…`)는 링크의 실제 위치 기준으로 풀리므로 폴더 구조를 유지한 채 링크한다.

Road Music 위치가 다르면(예: Windows) 환경 변수로 알려 준다.

```bash
export ROAD_MUSIC_HOME=/path/to/music-road
```

필요한 것: Node.js(Road Music CLI 실행용)와 `npm ci --include=dev`를 마친 Road Music 소스 키트. 엔진·모델 설치는 이 묶음의 범위가 아니다(Road Music `docs/cli-install.md`).

## 사용

Claude Code에서 평소처럼 요청하면 `yue-music`이 진입점이 된다.

```text
YuE MLX로 한국어 여성 발라드 1곡 준비해줘. 생성 전에 보여줘.
```

```text
이 Suno 프롬프트와 가사를 YuE2용으로 바꿔줘. 원문은 그대로 두고 보정안만 보여줘.
```

```text
가사와 프롬프트까지 전부 자동으로 정해서 yue-mlx로 트로트 1곡 생성해줘.
```

흐름: 가사(`yue-lyric-writer`) → style(`yue-style-engineer`) → 검수(`yue-lyric-reviewer`) → 관문·`song:prepare`·보정 보고(`yue-pre-generation-check`) → 승인 → `song:generate` → `job:wait` → 결과 검수(`yue-result-review`).

### 검증 스크립트

`examples/*.json`을 실제 `song:prepare`(모델·서비스 없이 로컬, 음악 생성 없음)에 넣어 `valid:true`, 엔진 유지, `officialGuide` advice가 [기대값](examples/expectations.json)과 같은지 확인한다. 데이터 폴더는 `ROADMUSIC_DATA_DIR`로 분리한다(지정하지 않으면 OS 임시 폴더에 새로 만든다).

```bash
ROADMUSIC_DATA_DIR="$(mktemp -d)" node scripts/verify-examples.mjs --write verification/RESULTS.md
```

최근 실행 결과: [verification/RESULTS.md](verification/RESULTS.md) — 7/7 통과. 변환 결과 예시 6개는 advice 0, Suno식 입력을 그대로 둔 비교용 예시(`suno-style-before.json`)는 의도대로 advice 5개(`style-language`, `style-tempo`, `style-positive-description`, `style-no-instruction`, `lyrics-no-annotations`)가 나오고, 대응표로 바꾼 `suno-style-after.json`은 0이다.

| 예시 | 보여주는 것 |
| --- | --- |
| `ko-ballad-yue-mlx.json` | 공식 순서 style + `bpm` 필드 |
| `ko-trot-parts-yue-mlx.json` | style 없이 `parts`(genre·vocal·instrumentation·dynamics·bpm) |
| `en-pop-yue-windows.json` | Windows용 `engine:"yue"`, `cot:"melody"` |
| `instrumental-yue-mlx.json` | `instrumental:true` |
| `ko-melody-abc-yue-mlx.json` | 코드 없는 ABC + `cot:"melody"`, ABC `Q:`와 style BPM 일치 |
| `suno-style-before.json` / `suno-style-after.json` | Suno식 입력과 변환 결과 |

## 원본 대비 변경점

### Suno 전용이라 바꾼 것

자세한 표는 [Suno→YuE2 대응표](skills/yue-music/references/suno-to-yue2.md).

- Style 칸 1,000자·"보컬 먼저" 문장 블록 → YuE2 `style`의 공식 순서(언어, 장르, 보컬, 악기, 선율·프레이징, BPM) 쉼표 태그, 태그당 10단어 이하(Road Music 조합기 규칙).
- Lyrics 칸 5,000자 → `lyrics`(부를 말 + 구간 태그만). 문자 수로 자르지 않음.
- Performance Cue(`[Verse - cold regal]`)·무드 태그(`[Whispered]`)·괄호 백보컬·무대 지시 → 쓰지 않음. 전체 성향만 style/`parts`로.
- 발음용 철자 바꾸기(phonetic respelling)·발음표 강제 적용 → 폐기. 가사 주석은 YuE2에서 그대로 불릴 수 있고 발음 제어 채널이 없다. 발음 위험은 검수 메모와 제안으로만.
- Exclude Styles·`no X` 부정 프롬프트 → 긍정형 편성 묘사(`negative_prompt` 없음).
- `[Instrumental]` 지시·Instrumental 토글 → `instrumental:true` + 청취 확인(무보컬 보장 없음).
- Suno 모델(v6/wild/mini/Custom)·Variety·Weirdness·Style Influence·Audio Influence·Max Mode → 대응 없음. `engine`(`yue-mlx`/`yue`)과 YuE2 고유 `cot`·`seed`·`abc`로 대체. 샘플링 옵션과 짝짓지 않음.
- Duration(값에서 자름) → `targetSeconds`는 기록용, 자연 EOS.
- Persona·Voices·참조 가수 → 대응 없음. 실존 가수명 금지 원칙은 유지.
- 오디오 업로드 Cover → 공식 악보 기반 커버(SheetSage2 → 코드 없는 멜로디 ABC → `cot:"melody"`)로 안내, Road Music `coverAudio`는 ACE 전용.
- Extend·Replace Section·Song Editor·Stems → 대응 없음(로컬 인페인팅·스템 없음). 수정은 새 전체 생성 또는 `song:render`(원문 유지 악보 수정).
- 클립보드로 Suno 웹에 붙여넣기 → `song:prepare` → 승인 → `song:generate --file` → `job:wait`.
- "Suno는 비결정적이니 다시 생성" → Road Music 재제작 효율 기준(`music-review.md#retry-value`).
- 영어 운율·강세 수치, Suno 밀도 한도(BPM 100 미만 8줄 금지 등), 단어 수 하드 실패 → 한국어 호흡·음절 밀도 점검으로 바꾸고 수치 규칙은 쓰지 않음.

### 뺀 것 (이 묶음 범위 밖)

| 원본 스킬 | 이유 |
| --- | --- |
| mix-engineer, mastering-engineer | Suno 스템·마스터링 파이프라인 전제. YuE2는 스템을 내지 않음 |
| promo-director, promo-writer, promo-reviewer, cloud-uploader, release-director, sheet-music-publisher, album-art-director, import-art | 홍보·배포·아트. 영상은 Road Music 영상 스킬 사용 |
| researcher, researchers-*(10종), document-hunter, verify-sources | 다큐멘터리 리서치 체계. 필요하면 원본(CC0)을 별도로 사용 |
| new-album, import-track, import-audio, rename, validate-album, album-dashboard, album-ideas, promote-idea, resume, session-start, setup, configure, health-check, test, tutorial, clipboard, about, help, next-step | 원본 MCP 서버·`~/.bitwize-music` 폴더 구조 전제. Road Music은 `projects:*`·`songs:*`·제작 기록 스킬로 관리 |
| plagiarism-checker | 모델과 무관한 웹 검색 점검. 이 묶음에서는 검수 항목 14(차용 의심 알림)로만 남김 |
| genre-creator, genres/(72개 장르 문서) | Suno 팁이 섞인 장르 문서. Road Music `docs/genre-prompts.md`·`prompt:knowledge genres`를 사용 |
| MCP 서버(80+ 도구), hooks, tools/, templates/ | Road Music CLI로 대체 |

### 유지한 것

작사 기법(장면으로 보여주기, 절/후렴 대비, 절-후렴 반복 회피, 2절 전진, 훅·제목 배치, 시점·시제 일관성), 다듬기 패스, AI 투 표현 점검(voice-checker의 가사 패턴), 노골적 표현 확인, 앨범 순서·에너지 설계, 생성 전 관문 구조, 실존 아티스트명 차단, "동조자가 아니라 협업자" 태도.

## 남은 한계

- `officialGuide`는 문자열 휴리스틱이다. 실제로 부르는 괄호 메아리도 주석으로 표시하고, 반대로 모든 계약 위반을 잡지는 않는다. 그래서 스킬은 사람 판단의 검수 항목을 따로 둔다.
- 검증 스크립트는 입력 계약만 확인한다. 실제 가창·길이·발음·음질·무보컬은 생성 후 청취로만 확인할 수 있고, 이 작업에서는 음악을 생성하지 않았다.
- `score:check`는 실행 환경(런타임)이 있어야 동작해 이 환경에서는 쓸 수 없었다. ABC 예시는 오프라인 `score:inspect`로 구조만 확인했다(Vocal 22음, 8마디, 80 BPM).
- `yue` 엔진 예시는 Mac에서 `song:prepare`로만 확인했다(`platformMatches:false`). Windows NVIDIA 실제 환경 검증은 하지 않았다.
- `parts` 조합 순서는 Road Music 조합기가 정한다. 공식 예시 순서를 정확히 지키려면 `style` 한 줄로 쓴다.
- Road Music CLI·문서가 바뀌면 이 묶음의 요약(공통 규칙·CLI 표)이 낡을 수 있다. 실행 버전 `schema`와 Road Music 문서가 우선이며, 바뀌면 `scripts/verify-examples.mjs`를 다시 돌린다.
- 한국어 YuE2 가창 품질은 공식 자료가 보증하지 않는다(YuE2 모델 카드 언어 메타데이터는 zh/en).

## 출처와 라이선스

- 원본 스킬: [bitwize-music-studio/claude-ai-music-skills](https://github.com/bitwize-music-studio/claude-ai-music-skills), **CC0 1.0 Universal**(퍼블릭 도메인 헌정, 복사·수정·재배포 허용). 원문을 복사하지 않고 구조와 기법을 참고해 새로 썼다. 원본 README의 고지대로, 장르 문서의 실존 아티스트 언급은 교육·참고용이었다.
- YuE2 공식 자료: 고정판 `yue2-v0.1.6`의 코드·문서·스킬은 **CC BY-NC 4.0**, 공식 main(2026-11-01)은 **Apache-2.0**, 커뮤니티 MLX 포트 코드는 **Apache-2.0**, 모델 가중치는 별도 모델 라이선스. 이 묶음은 공식 원문을 동봉하지 않고 Road Music 저장소의 보관본 경로를 가리키며, 규칙은 요약해 적었다. 생성물의 권리·상업 이용 조건은 Road Music `docs/yue-prompt-guide.md#rights`와 최신 공식 조건을 확인한다.
- Road Music 문서: 같은 사용자의 저장소이며 이 묶음은 그 문서를 참조만 한다.
- 이 묶음 자체의 라이선스는 정하지 않았다. 공개 배포 전에 사용자가 정한다.
