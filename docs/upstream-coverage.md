# 원본 스킬·기능 전수 대응표

[README](../README.md) · [스킬 레퍼런스](skills.md) · [Suno→YuE2 대응표](../skills/yue-music/references/suno-to-yue2.md)

원본 [bitwize-music-studio/claude-ai-music-skills](https://github.com/bitwize-music-studio/claude-ai-music-skills)(커밋 `597d928`, 2026-10-13, CC0)의 스킬 53개와 참고 문서·도구를 하나씩 이 묶음에 대응시켰다. 판정은 네 가지다.

| 판정 | 뜻 |
| --- | --- |
| **전환** | Suno 전용 내용을 YuE2 공식 계약·Road Music CLI로 다시 썼다 |
| **통합** | 다른 원본 스킬과 묶어 하나의 YuE2 스킬로 합쳤다 |
| **Road Music 대체** | Road Music 앱·CLI·기존 스킬이 같은 일을 하므로 그것을 가리킨다 |
| **해당 없음** | YuE2·Road Music에 대응 기능이 없거나 원본 내부 인프라라서 옮기지 않았다(이유 표기) |

## 스킬 53개

### 창작 핵심

| 원본 스킬 | 판정 | 이 묶음 | 메모 |
| --- | --- | --- | --- |
| suno-engineer | 전환 | `yue-style-engineer` | Style 칸·Exclude·Variety·모델 선택 → YuE2 `style`·`parts`·`cot`·`seed`·`abc` |
| lyric-writer | 전환 | `yue-lyric-writer` | 13항목 점검 중 언어 무관 기법 유지, Suno 발음 철자·밀도 한도 폐기 |
| lyric-refiner | 통합 | `yue-lyric-writer`(다듬기 패스) | AI 초안에만 적용, 사용자 원문은 제안만 |
| lyric-reviewer | 전환 | `yue-lyric-reviewer` | 14항목 → 한국어 검수 + YuE2 가사 계약 |
| pronunciation-specialist | 통합 | `yue-lyric-reviewer`(#10) | 철자 바꾸기 대신 부를 형태·단어 대체 제안. 발음 보장 없음 |
| voice-checker | 통합 | `yue-lyric-reviewer`(#11) | 가사 AI 투 패턴 1~7류 |
| explicit-checker | 통합 | `yue-lyric-reviewer`(#13), `yue-release` | 배포 등급 판단은 사용자 |
| plagiarism-checker | 통합 | `yue-release`(차용 점검), `yue-lyric-reviewer`(#14) | 웹 검색 가능할 때만, 미실행 표시 |
| pre-generation-check | 전환 | `yue-pre-generation-check` | 6관문 → G0~G10, `song:prepare` `officialGuide` |
| album-conceptualizer | 전환 | `yue-album-planner` | 7단계 → 곡별 요청 JSON 설계 |
| genre-creator | 해당 없음 | — | 원본 장르 문서 생성기. 장르 출발점은 Road Music `docs/genre-prompts.md`·`prompt:knowledge genres` |

### 악보·커버

| 원본 스킬 | 판정 | 이 묶음 | 메모 |
| --- | --- | --- | --- |
| sheet-music-publisher | 전환 | `yue-score-editor`(악보 내보내기) | AnthemScore·MuseScore 대신 YuE2 `score.abc`와 `song:score`·`score:convert`. 생성 계획이지 채보 결과가 아님 |
| (참고) workflows/covers-and-personas.md | 전환 | `yue-score-editor`(커버) | 오디오 업로드 커버 → 공식 SheetSage2 전사 → 코드 제거 → `cot:"melody"`. Persona·Voice는 대응 없음 |
| (참고) workflows/song-editor.md | 전환 | `yue-score-editor` | 구간 교체(인페인팅) 없음 → ABC 사본 편집 + 전체 재생성(`song:render`) |

### 조사

| 원본 스킬 | 판정 | 이 묶음 | 메모 |
| --- | --- | --- | --- |
| researcher | 통합 | `yue-research` | 1차 자료·교차 검증·링크 기록 |
| researchers-legal / financial / gov / historical / journalism / biographical / primary-source / security / tech | 통합 | `yue-research`(분야별 자료 위치 표) | 9개 전문 리서처를 한 표로 |
| researchers-verifier | 통합 | `yue-research`(검증 단계) | |
| document-hunter | 통합 | `yue-research` | 자동 브라우저 수집 대신 사용 가능한 검색·브라우저 도구, 유료벽·CAPTCHA 우회 금지 |
| verify-sources | 통합 | `yue-research`(사람 확인), `yue-pre-generation-check`(G8) | 확인 전 생성 차단 |

### 음원 후처리·공개

| 원본 스킬 | 판정 | 이 묶음 | 메모 |
| --- | --- | --- | --- |
| mastering-engineer | 전환 | `yue-mastering` | 48kHz 전체 믹스, ffmpeg 2패스 loudnorm, 원본 보존. 업샘플링을 품질 향상이라 하지 않음 |
| mix-engineer | 통합(축소) | `yue-mastering` | YuE2는 스템을 내지 않으므로 스템별 정리는 해당 없음 |
| release-director | 전환 | `yue-release` | Suno 약관 → YuE2 코드·모델 라이선스, AI 고지 |
| promo-writer / promo-reviewer | 통합 | `yue-release`(홍보 문구) | 게시는 사용자 |
| album-art-director | 통합 | `yue-release`(아트 브리프) | 이미지 생성은 사용자·이미지 도구 |
| promo-director | Road Music 대체 | `road-music-mv`, 쇼릴 스킬 | 영상 렌더는 Road Music 영상 스킬 |
| cloud-uploader | 해당 없음 | — | 개인 R2/S3 업로드 인프라. 외부 전송은 사용자 몫 |
| import-art | 해당 없음 | — | 원본 폴더 구조 전용 |

### 상태·관리

| 원본 스킬 | 판정 | 이 묶음 | 메모 |
| --- | --- | --- | --- |
| resume | 전환 | `yue-project-status`(이어 하기) | MCP 상태 캐시 → `songs:list`·`song:detail` |
| next-step | 전환 | `yue-project-status`(다음 단계 판단) | 재제작을 기본 추천하지 않음 |
| album-dashboard | 전환 | `yue-project-status`(진행 현황) | |
| album-ideas / promote-idea | 통합 | `yue-project-status`(아이디어) | `IDEAS.md` + `projects:create` |
| new-album | 통합 | `yue-project-status`, `yue-album-planner` | 프로젝트 생성 ≠ 곡 생성 |
| rename | Road Music 대체 | `yue-project-status`(`song:rename`) | |
| validate-album | 통합 | `yue-project-status`(구조 점검) | 정리는 `road-music-storage` |
| import-track / import-audio | Road Music 대체 | `songs:import` | |
| clipboard | 해당 없음 | — | Suno 웹에 붙여넣기용. YuE2는 JSON 파일로 제출 |
| session-start / setup / configure / health-check | 전환 | `yue-setup-check` | Python venv·MCP 점검 → Road Music CLI 읽기 전용 점검 |
| help / tutorial / about | 통합 | `yue-setup-check`, README, [docs](getting-started.md) | |
| test | 전환 | `scripts/verify-examples.mjs`, `tests/*.test.cjs`, `evals/` | [테스트 문서](testing.md) |

## 참고 문서

| 원본 | 판정 | 대응 |
| --- | --- | --- |
| reference/suno/*(14개: best-practices, models, structure-tags, voice-tags, instrumental-tags, pronunciation-guide, creative-sliders, artist-blocklist 등) | 전환 | [Suno→YuE2 대응표](../skills/yue-music/references/suno-to-yue2.md), `yue-style-engineer`, `yue-lyric-writer`. 아티스트 차단 원칙만 유지 |
| reference/workflows/album-planning-phases.md | 전환 | `yue-album-planner` |
| reference/workflows/error-recovery.md | 전환 | `yue-result-review`(재제작 판단), Road Music `music-review.md#retry-value` |
| reference/workflows/status-tracking.md | 전환 | `yue-project-status`(단계 값) |
| reference/workflows/source-verification-handoff.md | 통합 | `yue-research` |
| reference/workflows/importing-audio.md | Road Music 대체 | `songs:import` |
| reference/workflows/release-procedures.md, reference/release/*, reference/distribution.md | 통합 | `yue-release` |
| reference/mastering/*, reference/streaming-mastering-specs.md | 통합 | `yue-mastering` |
| reference/promotion/* | 통합/대체 | `yue-release`(문구), Road Music 영상 스킬(영상) |
| reference/sheet-music/* | 전환 | `yue-score-editor` |
| reference/model-strategy.md | 해당 없음 | Claude 모델 계층 전략. Codex·Claude 공용 묶음이라 스킬별 모델 고정 안 함 |
| reference/state-schema.md, reference/SKILL_INDEX.md, reference/terminology.md | 대체 | Road Music 상태, [스킬 레퍼런스](skills.md) |
| reference/quick-start/* | 통합 | [시작하기](getting-started.md), [작업 흐름](workflow.md) |
| reference/overrides/* | 전환 | 공통 규칙 9절 "사용자 선호 파일" |
| genres/(장르 문서 다수) | Road Music 대체 | `docs/genre-prompts.md`, `prompt:knowledge genres`. Suno 팁이 섞여 있어 옮기지 않음 |
| templates/(album, track, research, sources 등) | 통합 | `yue-research`의 SOURCES/RESEARCH 형식, `yue-project-status`의 IDEAS 형식. 트랙 파일 대신 Road Music 곡 정보 |

## 도구·인프라

| 원본 | 판정 | 이유 |
| --- | --- | --- |
| servers/(MCP 서버 80+ 도구) | Road Music 대체 | Road Music CLI가 상태·가사 정리·준비 점검을 제공 |
| tools/mastering, tools/mixing | 전환(축소) | ffmpeg 명령으로 `yue-mastering`에 정리 |
| tools/sheet-music | 대체 | YuE2 ABC + Road Music `score:*` |
| tools/promotion | 대체 | Road Music 영상 스킬 |
| tools/cloud, tools/database, tools/n8n, tools/userscripts | 해당 없음 | 개인 배포·DB·자동화 인프라 |
| tools/state | 대체 | Road Music 상태 |
| hooks/ | 해당 없음 | 원본 저장소 개발용 훅 |
| tests/(4,412개) | 전환 | 이 묶음의 [테스트](testing.md) |

## Suno 전용 기능 중 대응이 없는 것

Variety, Weirdness, Style Influence, Audio Influence, Max Mode, Persona·Voices, Custom Model, Extend, Replace Section, Stems, Exclude Styles 칸, Duration 자르기. 이 기능들은 비슷한 YuE2 옵션(CFG·temperature 등)으로 흉내 내지 않는다. 자세한 근거는 [대응표](../skills/yue-music/references/suno-to-yue2.md#모델설정).
