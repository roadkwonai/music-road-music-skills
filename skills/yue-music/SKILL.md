---
name: yue-music
description: Road Music에서 YuE2(yue-mlx Apple Silicon / yue Windows NVIDIA)로 곡·앨범을 기획·작사·프롬프트 작성·생성 준비·검수할 때의 진입 스킬. 요청 모드(기본 검토/초안만/전체 자동 위임)를 판정하고 yue-style-engineer, yue-lyric-writer, yue-lyric-reviewer, yue-pre-generation-check, yue-album-planner, yue-result-review로 연결한다. Suno용 프롬프트·가사를 YuE2로 바꿀 때도 사용. Use for YuE2 / YuE MLX song requests in Road Music, or converting Suno prompts to YuE2.
---

# YuE2 음악 제작 (Road Music)

Suno용 음악 스킬 묶음을 YuE2 공식 가이드와 Road Music CLI에 맞게 다시 만든 묶음의 진입점이다. 모든 단계에서 [공통 규칙](references/common-rules.md)을 먼저 적용한다.

## 먼저 읽기

1. [공통 규칙](references/common-rules.md) — 엔진 유지, YuE2 입력 계약, 원문 보존, 한국어 검수, 승인, 보장하지 않는 것.
2. 작업에 필요한 Road Music 절만 읽는다(`ROAD_MUSIC_HOME`, 기본 `/Users/freelife/youtube/music/music-road`). CLI로는 `prompt:knowledge {"topic":"yue"}`(필요 시 `yue-advanced`, `lyrics`, `review`, `genres`)로 같은 내용을 읽을 수 있다.
3. Suno 자료·프롬프트를 받았으면 [Suno→YuE2 대응표](references/suno-to-yue2.md).
4. CLI 명령·필드·`officialGuide` 읽는 법은 [Road Music CLI 연결](references/road-music-cli.md), 보고 형식은 [보고 형식](references/report-template.md).

## 1. 요청 해석

- 엔진·곡 수·언어·장르·보컬·길이·수정 범위를 정한다. 엔진은 사용자가 고른 값(`yue-mlx`/`yue`)을 유지하고, 미지정이면 환경에 맞는 값을 가정값으로 표시한다.
- 요청 모드를 [공통 규칙 5절](references/common-rules.md#5-요청-모드와-승인)로 판정하고 첫 응답에 한 줄로 밝힌다. 예: "기본 검토 모드로 진행하고 생성 전에 확인받습니다."
- 받은 원문(가사·프롬프트·옵션)과 AI가 새로 정할 부분을 구분해 기록한다.
- 문서 조사·스킬 수정·초안 요청에 음악 생성을 추가하지 않는다.

## 2. 단계별 스킬

| 단계 | 스킬 | 원본(Suno) 대응 |
| --- | --- | --- |
| 여러 곡·앨범 기획 | `yue-album-planner` | album-conceptualizer |
| 가사 작성·개사·다듬기 | `yue-lyric-writer` | lyric-writer, lyric-refiner |
| style·parts·cot·seed·abc 작성 | `yue-style-engineer` | suno-engineer |
| 제목·가사 검수(한국어·YuE2 계약·발음 위험·AI 투) | `yue-lyric-reviewer` | lyric-reviewer, pronunciation-specialist, voice-checker, explicit-checker |
| 생성 전 관문·`song:prepare`·보정 보고·승인·생성 | `yue-pre-generation-check` | pre-generation-check |
| 완성본 검수·재제작 판단 | `yue-result-review` | 원본 Regeneration Workflow, error-recovery |

단일 곡의 기본 순서: 가사(`yue-lyric-writer`, 사용자가 가사를 줬으면 건너뜀) → style(`yue-style-engineer`) → 검수(`yue-lyric-reviewer`) → 관문·준비·보고(`yue-pre-generation-check`) → 승인 → `song:generate` → `job:wait` → `yue-result-review`.

스킬을 호출할 수 없는 환경이면 해당 스킬의 `SKILL.md`를 직접 읽고 같은 절차를 수행한다.

## 3. 출력 원칙

- 기본 검토 모드의 검토안은 [보고 형식](references/report-template.md)의 항목을 **한 번에** 보여주고, `## YuE2 공식 가이드 보정 보고` 절을 보정이 없어도 포함한다.
- 초안만 요청한 경우도 보정 보고 절을 포함하고, 실행하지 않은 CLI 점검은 `미실행`으로 적는다(`song:prepare`는 로컬 무추론이므로 가능하면 실행).
- 전체 자동 위임이면 질문으로 멈추지 않고 검수·검증 후 생성하며, 결과 보고에 같은 절을 넣는다.
- 길이·템포·가수·발음·무보컬을 보장한다고 쓰지 않는다.

## 이 묶음에 없는 것

마스터링·믹스(스템), 홍보 문구·영상, 배포·릴리스, 클라우드 업로드, 다큐멘터리 리서치 에이전트, MCP 서버는 옮기지 않았다(README의 "원본 대비 변경점" 참고). 영상은 Road Music의 별도 영상 스킬을 사용한다.
