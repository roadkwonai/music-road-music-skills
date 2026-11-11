---
name: yue-music
description: Road Music에서 YuE2(yue-mlx Apple Silicon / yue Windows NVIDIA)로 곡·앨범을 기획·작사·프롬프트 작성·생성 준비·검수할 때의 진입 스킬. 요청 모드(기본 검토/초안만/전체 자동 위임)를 판정하고 작사·style·검수·생성 전 관문·결과 검수·악보 편집·조사·마스터링·공개 준비·현황 스킬로 연결한다. Suno용 프롬프트·가사를 YuE2로 바꿀 때도 사용. Use for any YuE2 / YuE MLX song request in Road Music, or converting Suno prompts and Suno skill workflows to YuE2.
---

# YuE2 음악 제작 (Road Music)

Suno용 음악 스킬 묶음을 YuE2 공식 가이드와 Road Music CLI에 맞게 다시 만든 묶음의 진입점이다. 모든 단계에서 [공통 규칙](references/common-rules.md)을 먼저 적용한다.

## 먼저 읽기

1. [공통 규칙](references/common-rules.md) — 엔진 유지, YuE2 입력 계약, 원문 보존, 한국어 검수, 승인, 보장하지 않는 것.
2. 작업에 필요한 Road Music 절만 읽는다(`ROAD_MUSIC_HOME`, 기본 `/Users/freelife/youtube/music/music-road`). CLI `prompt:knowledge {"topic":"yue"}`(로컬, 필요 시 `yue-advanced`, `lyrics`, `review`, `genres`)는 Road Music 가이드 본문을 돌려줄 뿐 고정 공식 원문·`yue-cli-workflow.md`를 대신하지 않는다. 제목·가사 표현만 검토하는 요청에는 엔진 조회·생성 준비 자료를 요구하지 않는다.
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
| ABC 악보 편집·재화성·악보 기반 커버·악보 내보내기 | `yue-score-editor` | Song Editor·Cover·Persona 흐름, sheet-music-publisher |
| 실화·다큐·유행 조사와 출처 확인 관문 | `yue-research` | researcher, researchers-*(10종), document-hunter, researchers-verifier, verify-sources |
| 완성 음원 라우드니스·QC·내보내기 | `yue-mastering` | mastering-engineer, mix-engineer |
| 권리·라이선스·차용·메타데이터·아트·홍보 문구·배포 점검 | `yue-release` | release-director, promo-writer, promo-reviewer, album-art-director, plagiarism-checker, explicit-checker |
| 이어 하기·다음 단계·진행 현황·아이디어·이름 변경 | `yue-project-status` | resume, next-step, album-dashboard, album-ideas, promote-idea, new-album, rename, validate-album, import-* |
| 작업 환경 점검·처음 사용 안내 | `yue-setup-check` | session-start, setup, configure, health-check, help, tutorial, about |

단일 곡의 기본 순서: 가사(`yue-lyric-writer`, 사용자가 가사를 줬으면 건너뜀) → style(`yue-style-engineer`) → 검수(`yue-lyric-reviewer`) → 관문·준비·보고(`yue-pre-generation-check`) → 승인 → `song:generate` → `job:wait` → `yue-result-review`.

스킬을 호출할 수 없는 환경이면 해당 스킬의 `SKILL.md`를 직접 읽고 같은 절차를 수행한다.

## 3. 필수 출력 골격

참고 문서를 다 읽지 못했더라도 YuE 프롬프트·생성 준비 답변은 아래 골격을 지킨다. 제목과 표 머리글은 글자 그대로 쓴다(Road Music `docs/yue-prompt-guide.md#official-report`).

````text
**모드:** 기본 검토 / 초안만 / 전체 자동 위임 / 제공안 승인 / 지정 수정·재생성 / 수정만 — 한 줄 이유

## 제목·가사 검수
- 검수 방식: 독립 검수 / 자체 검수(별도 단계)
- 제목 판정: 검토 완료 / 보완 필요 / 원문 보존·제안만 / 확인 불가 / 해당 없음
- 가사 판정: (같은 값) — 화자·대상·흐름 요약
| 위치 | 원문 | 수정안 | 이유 | 적용 |

## YuE2 공식 가이드 보정 보고
- 참고 원문: 공식 yue2-v0.1.6 generation·generation-and-covers, main(1116bea, 2026-11-01) generation, (yue-mlx면) MLX usage, 엔진 <엔진>
- 공식 점검(song:prepare officialGuide): pass N · advice N · 해당 없음 N  (미실행이면 미실행(사유))

| 항목 | 원래 입력 | 보정 후 | 공식 근거 | 적용 |
| --- | --- | --- | --- | --- |
| (보정 없으면) 보정 없음 | … | … | 통과한 점검 ID | 보정 없음 |

- 최종 style 구성: 언어 / 장르 / 보컬 / 악기 / 분위기·프레이징 / BPM
- 가사 구성: 구간 태그 순서, 주석·지시문 처리, 정리 전후 차이
- 모드·옵션: cot, seed, abc 유무, 기본값(CFG·ODE·runtime) 유지 또는 변경 이유
- 보장하지 않는 것: 특정 가수·발음·정확한 템포와 길이·무보컬은 청취로 확인
````

- **"원래 입력" 열에는 사용자 원문을 글자 그대로** 옮긴다(요약·번역하지 않음). AI가 새로 정한 값은 `(미지정)`.
- **적용 열 값:** AI 작성분 `적용`, 사용자 원문 `제안(승인 대기)`·승인 후 `적용(승인)`, 의도적으로 남긴 권고 `유지(이유)`, 해당 없음 `—`.
- **요청 JSON:** 사용자 원문이 있고 보정안이 있으면 두 개를 낸다. ① 원문 그대로의 JSON(`song.original.json`) ② 보정안을 반영한 JSON(`song.proposed.json`, 승인 시 실행). "원문은 건드리지 말라"는 원문 값·파일을 덮어쓰지 말라는 뜻이며 보정안 JSON을 만들지 말라는 뜻이 아니다. 두 JSON 모두 `song:prepare`를 돌려 결과를 적는다.
- **끝맺음:** 기본 검토·부분 위임은 마지막 줄에 정확히 "이 가사·프롬프트·옵션으로 생성할까요? 수정할 부분이 있으면 알려주세요."라고 묻는다. 초안만·수정만은 "승인하시면 실행할 명령"만 소개하고 생성하지 않는다. 전체 자동 위임·제공안 승인은 묻지 않고 생성 결과를 보고한다.

### 보내기 전 자체 점검

답변을 보내기 직전에 다음을 확인하고, 빠진 것이 있으면 고친 뒤 보낸다.

1. 첫 줄에 `**모드:**`가 있는가.
2. `## YuE2 공식 가이드 보정 보고` 제목과 `| 항목 | 원래 입력 | 보정 후 | 공식 근거 | 적용 |` 머리글이 **글자 그대로** 있는가(`근거`로 줄이지 않는다).
3. "원래 입력" 열이 사용자 원문 그대로인가.
4. 한국어 제목·가사가 있으면 `제목 판정:`·`가사 판정:` 줄이 있는가.
5. 기본 검토·부분 위임이면 **마지막 줄**이 "이 가사·프롬프트·옵션으로 생성할까요? 수정할 부분이 있으면 알려주세요."인가.
6. 길이·가수·발음·무보컬을 보장한다는 표현이 없는가. 듣지 않았으면 "미청취"라고 썼는가.

## 4. 출력 원칙

- 기본 검토 모드의 검토안은 [보고 형식](references/report-template.md)의 항목을 **한 번에** 보여주고, `## YuE2 공식 가이드 보정 보고` 절을 보정이 없어도 포함한다.
- 초안만 요청한 경우도 보정 보고 절을 포함하고, 실행하지 않은 CLI 점검은 `미실행`으로 적는다(`song:prepare`는 로컬 무추론이므로 가능하면 실행).
- 전체 자동 위임이면 질문으로 멈추지 않고 검수·검증 후 생성하며, 결과 보고에 같은 절을 넣는다.
- 길이·템포·가수·발음·무보컬을 보장한다고 쓰지 않는다.

## 이 묶음에 없는 것

스템 단위 믹싱(YuE2가 스템을 내지 않음), 홍보 영상 렌더(Road Music 영상 스킬 사용), 클라우드 업로드·DB·n8n 자동화, 원본 MCP 서버·상태 캐시는 옮기지 않았다. 전체 대응은 묶음 루트의 `docs/upstream-coverage.md`를 본다.
