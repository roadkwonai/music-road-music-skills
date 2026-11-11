---
name: yue-pre-generation-check
description: Road Music YuE2(yue-mlx/yue) 생성 직전 관문. 엔진·상태 확인, 한국어 검수 완료, lyrics:clean·prompt:compose·yue:capabilities·song:prepare 점검, officialGuide 기반 공식 가이드 보정과 보정 전후 보고, 요청자 승인 확인 후에만 song:generate → job:wait를 실행한다. Use before any YuE2 generation or when asked "생성 준비", "ready to generate" (replaces pre-generation-check).
---

# YuE2 생성 전 관문

원본 `pre-generation-check`(Suno 6관문)를 Road Music CLI 관문으로 바꿨다. [공통 규칙](../yue-music/references/common-rules.md), [CLI 연결](../yue-music/references/road-music-cli.md), [보고 형식](../yue-music/references/report-template.md)을 적용한다. 근거: Road Music `docs/yue-prompt-guide.md#workflow`, `#official-correction`, `docs/music-review.md#validation`, `#proposal`, `#approval`.

```bash
ROAD_MUSIC_HOME="${ROAD_MUSIC_HOME:-/Users/freelife/youtube/music/music-road}"
RM="node $ROAD_MUSIC_HOME/cli/road-music.js"
```

## 관문

| # | 관문 | 통과 조건 | 실패 시 |
| --- | --- | --- | --- |
| G0 | 요청 모드 | 기본 검토/제공안 승인/전체 자동 위임/초안만 중 하나로 판정 | 판정이 애매하면 기본 검토 |
| G1 | 엔진 | 요청 JSON `engine`이 사용자가 고른 `yue-mlx`/`yue`. `engines:list`에서 준비됨 | 다른 엔진으로 바꾸지 않음. 미설치면 보고하고 생성 단계에서 멈춤(설치는 요청 시에만) |
| G2 | 실행 계약 | `schema`·`yue:capabilities`에 없는 필드·runtime 키를 쓰지 않음 | 필드 제거 |
| G3 | 한국어 검수 | `yue-lyric-reviewer` 판정이 `검토 완료` 또는 `원문 보존·제안만`(연주곡은 가사 `해당 없음`) | 보완 후 재검수 |
| G4 | 가사 정리 | `lyrics:clean` 전후에 의미 손실·잘림 없음 | 바뀐 부분만 보고·재검토 |
| G5 | style 조합 | `song:prepare`의 `changes.style.dropped`가 비었고 핵심 지시가 남음 | 긴 태그를 나눔 |
| G6 | 준비 | `song:prepare` `valid:true` | `errors` 해결 |
| G7 | 공식 점검 | `officialGuide.advice`가 0이거나 남은 advice마다 유지 이유가 있음 | 보정 절차 |
| G8 | 권리 | style에 실존 가수·밴드 이름 없음, 커버면 원곡 권리 확인 | 묘사로 대체 제안 |
| G9 | 원문 보존 | 사용자 원문과 전달본(`nativeRequest`) 차이가 모두 보고·승인됨 | 해결 전 생성 금지 |
| G10 | 승인 | 기본 검토면 사용자의 명시적 승인. 자동 위임·제공안 승인은 그 범위 확인 | 검토안 제시 후 대기 |

연주곡(`instrumental:true`)은 G3의 가사, G7의 언어·보컬·가사 점검이 해당 없음이다.

## 절차

1. **상태 읽기(첫 연결 1회):** `$RM cli:version`, `$RM cli:update:check`(알리기만, 설치 안 함), `$RM app:state`, `$RM engines:list`, `$RM projects:list`, `$RM songs:list`. 다른 프로필의 조회 결과로 설치 상태를 대신하지 않는다.
2. **계약:** `$RM schema`, `$RM yue:capabilities --json '{"engine":"<엔진>"}'`.
3. **요청 파일 작성:** 생성과 **같은** JSON을 파일로 만든다(예: 작업 폴더의 `song.json`). 원문 가사·style은 별도 파일이나 메모로 보존한다.
4. **준비 1차:** `$RM song:prepare --file song.json`. `valid`, `errors`, `notes`, `changes`, `officialGuide`, `effective`, `nativeRequest`를 읽는다.
5. **보정:** `advice`마다 공식 근거를 확인한다.
   - AI가 쓴 style·가사 → 바로 보정.
   - 사용자 원문 → 원문 유지, 보정안·근거·예상 영향을 제안(승인 후 반영). 전체 자동 위임도 AI가 새로 정한 부분만 보정.
6. **준비 2차:** 보정한 파일로 다시 `song:prepare`. 남은 advice와 유지 이유를 기록.
7. **기본값 확인:** `effective.advanced`가 기본값(full/melody CFG 1, off CFG 1.01, ODE 32 등)인지. 바꿨다면 실험·한 요소임을 밝힌다.
8. **보고:** 모드에 따라
   - 기본 검토/부분 위임: [생성 전 검토안](../yue-music/references/report-template.md#생성-전-검토안-기본-검토-모드) + `## YuE2 공식 가이드 보정 보고` + 한국어 검수 결과를 한 번에 보여주고 "이 가사·프롬프트·옵션으로 생성할까요?"라고 묻고 멈춘다.
   - 초안만: 같은 자료를 주고 생성하지 않는다.
   - 전체 자동 위임·제공안 승인: 멈추지 않고 9로.
9. **생성(승인 후):** `$RM song:generate --file song.json` → 받은 `jobId`로 `$RM job:wait --json '{"jobId":"…"}'`. `uncertain:true`면 재제출하지 말고 `service:status`·`queue:list`·`songs:list`로 확인한다. 승인 수량(`count`)만 생성한다.
10. **결과:** `yue-result-review`로 넘긴다. 제작 기록은 Road Music `skills/road-music-production-records`를 함께 적용한다.

`song:prepare`를 실행할 수 없는 환경(Road Music 미설치 등)에서는 정적 점검만 하고 보고서에 `미실행(사유)`을 적는다. 이때 생성으로 넘어가지 않는다.

## 관문 보고 형식

```text
## 생성 전 관문
| 관문 | 결과 | 근거 |
| --- | --- | --- |
| G1 엔진 | 통과 (yue-mlx, engines:list ready) | |
| G7 공식 점검 | 통과 (advice 0) | song:prepare 2차 |
...
- 생성 여부: 승인 대기 / 자동 위임으로 제출 / 초안만이라 미제출
```

이어서 `## YuE2 공식 가이드 보정 보고` 절을 붙인다.
