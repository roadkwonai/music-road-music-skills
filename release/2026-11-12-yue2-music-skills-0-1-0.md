---
version: 0.1.0
date: 2026-11-12
title: Music Road YuE2 Skills v0.1.0 — YuE2 음악 스킬 묶음(재게시)
---

# 0.1.0 — YuE2 음악 스킬 묶음 (재게시)

Suno용 [claude-ai-music-skills](https://github.com/bitwize-music-studio/claude-ai-music-skills)(스킬 53개, CC0)를 YuE2 공식 가이드와 Road Music CLI 기준으로 다시 만든 스킬 묶음입니다. Claude Code와 Codex에서 같은 스킬을 씁니다.

> **재게시 안내:** 실제 배포 전까지 버전을 `0.1.0`으로 유지하기로 해(2026-11-12 사용자 결정), 같은 날 게시했던 v0.1.1·v0.1.2를 철회하고 그 변경을 모두 담아 `0.1.0`을 다시 게시했습니다. 이전 `0.1.0` 파일과 같다고 가정하지 말고 `SHA256SUMS.txt`로 확인하세요. 철회한 노트는 [보관 기록](https://github.com/roadkwonai/music-road-music-skills/tree/main/docs/release-history)에 있습니다.

## 포함

- **스킬 14개:** `yue-music`(진입), `yue-album-planner`, `yue-research`, `yue-lyric-writer`, `yue-style-engineer`, `yue-lyric-reviewer`, `yue-pre-generation-check`, `yue-result-review`, `yue-score-editor`, `yue-mastering`, `yue-release`, `yue-project-status`, `yue-setup-check`, `yue-skills-update`.
- **원본 53개 스킬 전수 대응:** 전환·통합·Road Music 대체·해당 없음 판정과 근거([원본 전수 대응표](https://github.com/roadkwonai/music-road-music-skills/blob/main/docs/upstream-coverage.md)).
- **공통 규칙:**
  - 사용자 원문 보존(보정안만 제안), 한국어 제목·가사 검수, 요청 모드별 승인(전체 자동 위임만 검토 생략).
  - 매번 `## YuE2 공식 가이드 보정 보고`와 보정 전후 표.
  - 길이·가창·발음·무보컬 비보장.
  - 공식 원문 사실과 Road Music 운영 규칙을 구분해 표기.
- **스킬 업데이트 확인(`yue-skills-update`):** Road Music `cli:update:check`처럼 스킬을 처음 쓸 때 GitHub 최신 Release를 확인(12시간 캐시)하고 새 버전이 있으면 알립니다. git 설치본은 같은 번호의 재게시도 태그 커밋으로 구분합니다. 업데이트는 요청할 때만 합니다.
- **Codex 지원:** 스킬마다 `agents/openai.yaml`, 루트 `AGENTS.md`, zsh에서도 동작하는 `roadmusic()` 셸 함수, 필수 출력 골격과 보내기 전 자체 점검.
- **릴리스 체계:** `VERSION`·`manifest.json`·`release/` 노트, 허용 목록 ZIP + SHA256SUMS, 태그 push 시 Release를 만드는 워크플로.

## 실제 사용으로 검증하고 고친 점

- **실제 생성 감사:** 스킬대로 「끝까지 부를게」(여성 락보컬 락발라드, `yue-mlx`)를 생성·검수·마스터링하며 다음을 고쳤습니다.
  - 상태 확인은 `service:status`·`--no-start`로 합니다(일반 `cli:status`는 서비스를 시작합니다).
  - 새 곡은 새 프로젝트에서 생성합니다(`projects:create`는 바로 선택됩니다).
  - `requestPrompt`로 요청 원문을 자동 기록합니다.
  - 생성 실행 블록을 넣었습니다.
  - 결과 검수 보강: 실제 원본 오디오로 검사, truncation은 `meta.json` 기준, 트루피크가 0을 넘으면 마스터링 권고, 로컬 Whisper 무유도 전사와 흔한 전사 착시를 안내합니다.
- **마스터링:** loudnorm 2패스가 조용히 `dynamic`으로 바뀌는 경우를 감지하고, 선형 이득과 오버샘플링 리미터로 다이내믹을 보존합니다. 측정 명령 출력 추출도 고쳤습니다.
- **작업 파일 위치:** `songs:list`는 프로젝트 폴더 안의 오디오 없는 하위 폴더를 정리(삭제)합니다. 그래서 조사·수정 악보·마스터·납품물은 곡 보관 폴더 밖에 쓰도록 했습니다.
- **악보 편집:**
  - `song:render`는 원래 style을 재사용하고 ABC의 코드 유무로 `cot`을 정합니다.
  - 템포를 바꾸면 새 생성이 필요하고, `score:compare`에서 `invariants`의 `allowTempoChange`를 켜야 합니다.
  - Road Music CLI에는 악보 PDF로 내보내는 명령이 없습니다.
  - MIDI는 가져오기 경로로 다룹니다.
- **공개 준비:**
  - 고정 가중치의 LICENSE는 CC BY-NC 4.0이고, 개인 창작자 추가 조항은 공식 main의 MODEL_LICENSE에만 있다는 점을 구분합니다.
  - YuE에는 LRC 자막이 없고, SRT는 추정입니다.
  - 가사를 웹 검색에 보내기 전에 동의를 받습니다.
- **현황:** 제작 기록 원장을 먼저 읽고, 검수·마스터링 작업 기록으로 다음 단계를 판단합니다. `song:rename`은 오디오 파일명도 바꿉니다.
- **환경 점검:** 로컬 점검과 서비스 점검을 나누고, 서비스 연결이 막히면 "바로 생성 가능"이라고 단정하지 않습니다.

## 검증

- `node --test tests/*.test.cjs`: manifest·frontmatter·Codex 메타데이터·상대 링크·zsh 함정·예시 필드·릴리스 스크립트.
- `scripts/verify-examples.mjs`: 예시 요청 7개를 실제 `song:prepare`로 확인, 7/7.
- 시나리오 테스트 11종(변환·검토·자동 위임·마스터링·자동 생성·악보 편집·조사·공개 준비·현황·앨범 기획·환경 점검)을 Claude와 Codex로 실행·채점했습니다([테스트와 검증](https://github.com/roadkwonai/music-road-music-skills/blob/main/docs/testing.md)).
- 독립 검토 2회(앞선 7개 스킬 23건, 나중 6개 스킬 19건)를 반영했습니다.

## 제한

- 실제 생성은 1곡만 감사했고 직접 청취는 하지 않았습니다.
- `yue`(Windows NVIDIA) 경로는 Mac에서 준비 점검만 했습니다. `score:check`는 YuE 런타임이 필요합니다.
- `officialGuide`는 문자열 휴리스틱이며 사람 판단의 검수를 대신하지 않습니다.
- 개인 음원·프로젝트·토큰·모델은 묶음과 Release 자산에 포함하지 않습니다.
