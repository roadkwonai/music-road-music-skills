---
version: 0.1.0
date: 2026-11-12
title: Music Road YuE2 Skills v0.1.0 — YuE2 음악 스킬 묶음 첫 릴리스
---

# 0.1.0 — YuE2 음악 스킬 묶음 첫 릴리스

Suno용 [claude-ai-music-skills](https://github.com/bitwize-music-studio/claude-ai-music-skills)(스킬 53개, CC0)를 YuE2 공식 가이드와 Road Music CLI 기준으로 다시 만든 첫 정식 릴리스입니다. Claude Code와 Codex에서 같은 스킬을 씁니다.

## 포함

- **스킬 13개:** `yue-music`(진입), `yue-album-planner`, `yue-research`, `yue-lyric-writer`, `yue-style-engineer`, `yue-lyric-reviewer`, `yue-pre-generation-check`, `yue-result-review`, `yue-score-editor`, `yue-mastering`, `yue-release`, `yue-project-status`, `yue-setup-check`.
- **원본 53개 스킬 전수 대응:** 전환·통합·Road Music 대체·해당 없음으로 판정하고 근거를 [원본 전수 대응표](https://github.com/roadkwonai/music-road-music-skills/blob/main/docs/upstream-coverage.md)에 기록했습니다.
- **공통 규칙:** 사용자 원문 보존(보정안만 제안), 한국어 제목·가사 검수, 요청 모드별 승인(전체 자동 위임만 검토 생략), 매번 `## YuE2 공식 가이드 보정 보고`와 보정 전후 표, 길이·가창·발음·무보컬 비보장. 공식 원문 사실과 Road Music 운영 규칙을 구분해 표기합니다.
- **Suno→YuE2 대응표:** Style 칸, 메타태그, Exclude Styles, 슬라이더, Persona, Cover, Extend, Stems의 변환과 "대응 없음" 판정.
- **Codex 지원:** 스킬마다 `agents/openai.yaml`, 루트 `AGENTS.md`, zsh에서도 동작하는 `roadmusic()` 셸 함수, 필수 출력 골격과 보내기 전 자체 점검.
- **릴리스 체계:** `VERSION`·`manifest.json`·`release/` 노트, 허용 목록 ZIP + SHA256SUMS, 태그 push 시 GitHub Release를 만드는 워크플로.

## 설치 안내

- Release의 `MusicRoad-YuE2-Skills-0.1.0.zip`을 받아 `SHA256SUMS.txt`로 확인한 뒤 `skills/*`를 `~/.claude/skills` 또는 `${CODEX_HOME:-~/.codex}/skills`에 연결합니다. 저장소를 clone해 링크해도 됩니다.
- Road Music 소스 키트(CLI 0.1.0 기준)가 필요합니다. 위치가 기본값과 다르면 `ROAD_MUSIC_HOME`을 지정합니다.
- 이 묶음은 엔진·모델을 설치하지 않습니다. 엔진 없이도 작사·프롬프트·검수·`song:prepare` 점검은 할 수 있습니다.

## 검증 범위

- `node --test tests/*.test.cjs`: manifest·frontmatter·Codex 메타데이터·상대 링크·zsh 함정·예시 필드·릴리스 스크립트.
- `scripts/verify-examples.mjs`: 예시 요청 7개를 실제 `song:prepare`에 넣어 7/7 기대와 일치(변환 예시 advice 0, Suno식 비교 예시는 의도된 advice 5).
- 시나리오 테스트(Suno 변환·새 곡 검토 모드·자동 위임+사용자 가사·마스터링)를 Claude와 Codex로 실행하고 채점했습니다. 결과는 [테스트와 검증](https://github.com/roadkwonai/music-road-music-skills/blob/main/docs/testing.md).
- 독립 검토 에이전트가 공식 원문·Road Music 문서·CLI 코드와 한 줄씩 대조해 찾은 23건을 반영했습니다.

## 제한

- 실제 YuE2 음악 생성·청취는 이 릴리스 검증에 포함하지 않았습니다.
- `score:check`는 YuE 런타임이 있어야 동작합니다. `yue`(Windows NVIDIA) 경로는 Mac에서 준비 점검만 했습니다.
- `officialGuide`는 문자열 휴리스틱이며 사람 판단의 검수를 대신하지 않습니다.
- 개인 음원·프로젝트·토큰·모델은 묶음과 Release 자산에 포함하지 않습니다.
