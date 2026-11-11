# 작업 흐름

[README](../README.md) · [스킬 레퍼런스](skills.md) · [시작하기](getting-started.md)

## 전체 흐름

```text
(필요하면) 조사 yue-research ─┐
                              ▼
아이디어 → 기획 yue-album-planner → 작사 yue-lyric-writer → style yue-style-engineer
        → 검수 yue-lyric-reviewer → 생성 전 관문 yue-pre-generation-check
        → [승인] → song:generate → job:wait → 결과 검수 yue-result-review
        → (필요하면) 악보 편집 yue-score-editor → 재생성
        → 마스터링 yue-mastering → 공개 준비 yue-release
현황·이어 하기: yue-project-status   환경 점검·도움말: yue-setup-check
```

모든 단계에 [공통 규칙](../skills/yue-music/references/common-rules.md)이 적용된다.

## 요청 모드

| 이렇게 말하면 | 모드 | AI가 하는 일 |
| --- | --- | --- |
| "1곡 만들어줘", "가사는 네가 써줘" | 기본 검토 | 전부 준비해 보여주고 승인을 기다림 |
| "가사·프롬프트만 먼저 보여줘" | 초안만 | 생성하지 않음. 로컬 점검(`song:prepare`)만 |
| "가사와 프롬프트까지 전부 자동으로 정하고 생성해줘" | 전체 자동 위임 | 검수·검증 후 바로 생성, 결과 보고 |
| "이 가사와 프롬프트 그대로 생성해줘" | 제공안 승인 | 재승인 없이 생성. 원문은 고치지 않고 권고만 보고 |
| "어색한 가사 고쳐서 다시 만들어줘" | 지정 수정·재생성 | 허용 범위만 고치고 재생성 |
| "후렴만 바꿔줘" | 수정만 | 수정안만 보여줌 |

"빨리 만들어줘"나 한쪽만 맡긴 요청은 전체 자동 위임이 아니다.

## 매번 받는 보고

생성 전 검토안·초안·자동 위임 결과에는 항상 다음이 들어간다.

```text
## YuE2 공식 가이드 보정 보고
- 참고 원문: 공식 yue2-v0.1.6 generation·generation-and-covers, main(1116bea, 2026-11-01) generation, (yue-mlx면) MLX usage, 엔진 yue-mlx
- 공식 점검(song:prepare officialGuide): pass 8 · advice 0 · 해당 없음 2

| 항목 | 원래 입력 | 보정 후 | 공식 근거 | 적용 |
| --- | --- | --- | --- | --- |
| 보정 없음 | … | … | 통과 점검 ID | 보정 없음 |

- 최종 style 구성 / 가사 구성 / 모드·옵션 / 보장하지 않는 것
```

보정할 것이 없어도 이 절은 빠지지 않는다. 사용자 원문을 고칠 제안은 `제안(승인 대기)`로, 의도적으로 남긴 권고는 `유지(이유)`로 표시된다.

## 예시 1 — Suno 프롬프트 옮기기

```text
예전에 Suno에서 쓰던 프롬프트와 가사인데 YuE MLX로 옮기고 싶어. 원문은 건드리지 말고 보정안과 실행할 JSON만 보여줘.
Style: Female vocals, breathy and intimate. Dream pop, shimmering guitars, reverb-heavy, no drums. Variety Off, Weirdness 35, Max Mode on
Lyrics: [Verse 1 - whispered] …
```

결과 요지: 원문은 그대로 보여주고, style은 언어를 앞에 둔 쉼표 태그로, `no drums`는 긍정형 편성 묘사로, `[Verse 1 - whispered]`는 `[Verse]`와 style의 보컬 묘사로 나눈다. Variety·Weirdness·Max Mode는 "대응 없음"으로 보고하고 JSON에 넣지 않는다. 모든 변경은 승인 대기다.

## 예시 2 — 자동 위임 + 사용자 가사

```text
윈도우 PC에서 yue 엔진으로. 가사는 아래 그대로, 프롬프트는 알아서 정하고 생성까지 해줘. 정확히 3분으로.
```

결과 요지: 엔진은 `yue` 그대로. 가사는 그대로 제출하되 `(남자 파트)` 같은 괄호 주석이 불릴 수 있다는 권고를 `유지(사용자 원문)`로 보고한다. "정확히 3분"은 보장할 수 없다고 밝힌다(`targetSeconds`는 기록용, 실제 길이는 가사 분량과 자연 종료).

## 예시 3 — 결과 검수와 재제작

```text
방금 만든 곡 검수해줘. 2절 첫 줄이 잘 안 들려.
```

`yue-result-review`가 truncation·길이·파일을 확인하고, 로컬 ASR이 있으면 무유도 전사로 해당 구절을 본다. 한 음절 발음 문제라면 전곡 재생성을 기본 추천하지 않고, 확인된 기술 원인이 있을 때만 재제작을 권한다.

## 예시 4 — 악보 편집

```text
이 곡 후렴 화성만 재즈풍으로 바꾸고 선율은 그대로 둬.
```

`yue-score-editor`가 보존 계약(정확한 선율·리듬)을 정하고, `score.abc` 사본을 고쳐 `score:inspect`·`score:compare`로 확인한 뒤, 승인 범위에서 `song:render`로 다시 만든다.
