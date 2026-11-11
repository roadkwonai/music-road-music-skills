---
name: yue-pre-generation-check
description: Road Music YuE2(yue-mlx/yue) 생성 직전 관문. 엔진 확인, 제목·가사 언어 검수 완료, song:prepare의 officialGuide 기반 공식 가이드 보정과 보정 전후 보고, 요청 모드에 따른 승인 확인을 거친 뒤에만 song:generate → job:wait를 실행한다(전체 자동 위임·제공안 승인은 재승인 없이 진행). Use before any YuE2 generation, re-render or replay, or when asked "생성 준비", "ready to generate", "이대로 만들어줘" (replaces pre-generation-check).
---

# YuE2 생성 전 관문

원본 `pre-generation-check`(Suno 6관문)를 Road Music CLI 관문으로 바꿨다. [공통 규칙](../yue-music/references/common-rules.md), [CLI 연결](../yue-music/references/road-music-cli.md), [보고 형식](../yue-music/references/report-template.md)을 적용한다. 근거: Road Music `docs/yue-prompt-guide.md#workflow`, `#official-correction`, `docs/music-review.md#mode`, `#validation`, `#proposal`, `#approval`.

```bash
ROAD_MUSIC_HOME="${ROAD_MUSIC_HOME:-/Users/freelife/youtube/music/music-road}"
roadmusic() { node "${ROAD_MUSIC_HOME:-/Users/freelife/youtube/music/music-road}/cli/road-music.js" "$@"; }  # bash·zsh 공통. 셸 호출마다 다시 정의
```

## 관문

| # | 관문 | 통과 조건 | 실패 시 |
| --- | --- | --- | --- |
| G0 | 요청 모드 | [모드 표](../yue-music/references/common-rules.md#5-요청-모드와-승인)로 판정. 애매하면 기본 검토 | — |
| G1 | 엔진 | 요청 JSON `engine`이 사용자가 고른 `yue-mlx`/`yue`. 생성 단계에서는 사용자 프로필의 `engines:list`에서 준비됨 | 다른 엔진으로 바꾸지 않음. 미설치면 보고하고 생성 단계에서 멈춤(설치는 요청 시에만) |
| G2 | 실행 계약 | `cli:schema`·`yue:capabilities`에 없는 필드·runtime 키를 쓰지 않음 | 필드 제거 |
| G3 | 언어 검수 | 한국어 제목·가사가 있으면 `yue-lyric-reviewer` 판정이 `검토 완료` 또는 `원문 보존·제안만`. 한국어가 없는 항목·연주곡의 가사는 `해당 없음`으로 통과 | 보완 후 재검수 |
| G4 | 가사 정리 | 정리본(`changes.lyrics.prepared`)에서 부르는 문장이 삭제·잘림·치환되지 않음. 연주곡은 골격 교체가 정상이므로 예외 | 바뀐 부분만 보고·재검토 |
| G5 | style 조합 | `changes.style.dropped`가 비었고 핵심 지시가 남음 | 긴 태그를 나눔 |
| G6 | 준비 | `song:prepare`가 `ok:true`이고 `valid:true`. `ok:false`(INVALID_ARGUMENT: 길이 20~360 밖, off+abc/plan, instruments+instrumentation 등)와 `valid:false`(태그 삭제 등)를 구분해 보고 | 원인 수정 |
| G7 | 공식 점검 | `officialGuide.advice`가 0이거나 남은 advice마다 `유지(이유)`가 있음 | 보정 절차 |
| G8 | 권리·사실 | style에 실존 가수·밴드 이름 없음, 커버면 원곡 권리 확인, 사실 기반 곡이면 `yue-research`의 사람 확인 완료 | 묘사로 대체 제안 / 확인 대기 |
| G9 | 원문 보존 | 사용자 원문과 전달본의 **의미가 달라지는 차이**(부르는 문장의 삭제·잘림·치환, 지정한 장르·보컬·악기의 뜻 변경)가 없거나 승인됨. BPM·악기 요약·Korean 추가, 태그 이름 정리는 보고만 | 해결 전 생성 금지 |
| G10 | 승인 | 기본 검토·부분 위임: 사용자의 명시적 승인. 제공안 승인·전체 자동 위임·지정 수정·재생성: 그 범위 확인 후 재승인 없이 진행. 승인 후 AI가 의미를 바꿨다면 재검토 | 검토안 제시 후 대기 |

## 절차

1. **요청 기록:** 요청 JSON의 `requestPrompt`에 사용자 요청 원문을 넣는다. `song:generate`가 실제 곡 폴더를 정한 뒤 제작 기록에 자동 연결하므로 `production:request`를 따로 쓰지 않는다(생성 없는 기획·가사 요청만 따로 기록).
2. **계약(로컬):** `roadmusic cli:version`, `roadmusic cli:update:check`(첫 연결 1회, 알리기만), `roadmusic cli:schema`, `roadmusic yue:capabilities --json '{"engine":"<엔진>"}'`.
3. **요청 파일 작성:** 생성과 **같은** JSON을 파일로 만든다(예: 작업 폴더의 `song.json`). 원문 가사·style은 별도 파일이나 메모로 보존한다.
4. **준비 1차(로컬):** `roadmusic song:prepare --file song.json`. `ok`·`valid`·`errors`·`notes`·`changes`·`officialGuide`·`effective`(advanced와 runtime)·`nativeRequest`를 읽는다. 초안만 모드의 정리 확인은 여기까지로 충분하다.
5. **보정:** `advice`마다 근거를 확인한다.
   - AI가 쓴 style·가사 → 바로 보정.
   - 사용자 원문 → 기본 검토에서는 원문 유지 + 보정안·근거·예상 영향을 검토안에 넣는다. 제공안 승인·자동 위임에서는 원문 그대로 진행하고 `유지(사용자 원문)`와 보정안을 보고한다.
6. **준비 2차:** 보정한 파일로 다시 `song:prepare`. 남은 advice와 유지 이유를 기록한다.
7. **기본값 확인:** `effective.advanced`가 기본값(full/melody CFG 1, off CFG 1.01, ODE 32 등)인지, `parts.strict`+`strong`으로 CFG 1.5가 되지 않았는지, `effective.runtime`(yue-mlx 8bit·16GiB 기본, 공식 BF16과 다름)을 확인해 보고에 적는다.
8. **생성 준비 단계의 서비스 명령**(검토안을 보여주기 직전이나 승인 후, 초안만 모드 제외):
   - 상태: `roadmusic app:state`, `roadmusic engines:list`, `roadmusic projects:list`, `roadmusic queue:list --no-start`. 다른 프로필·임시 데이터 폴더의 결과로 설치 상태를 대신하지 않는다. 서비스가 떠 있는지만 볼 때는 `service:status`(일반 `cli:status`는 서비스를 시작한다).
   - 프로젝트: `app:state.songsDir`·`projects:list.current`가 이 곡과 관계없는 다른 작업이면 새 프로젝트를 `projects:create`로 만든다(만들면 바로 선택된다. 새 곡이 남의 프로젝트에 섞이지 않게). 같은 곡의 수정·재제작은 원래 프로젝트를 쓴다.
   - 가사: `roadmusic lyrics:clean --json '{"text":"<가사>"}'`로 정리 전후 비교, `roadmusic lyrics:check --json '{"text":"<가사>","targetSeconds":N}'`로 분량 참고. 결과의 `estimate`(초)는 부르는 줄 기준의 거친 참고값이다(실측 예: 추정 164초 → 실제 268초. 실제 길이는 모델이 계획한 악보를 따른다). 목표보다 많이 짧으면 AI 가사는 구간을 더하거나 `[Interlude]` 같은 연주 구간을 넣어 조정할 수 있고, 사용자 가사는 줄이거나 늘리지 않고 차이만 보고한다.
   - style: `roadmusic prompt:compose`에 생성과 같은 값(`genre`=`parts.genre` 또는 `style`, `instruments`/`instrumentation`, `vocal`, `dynamics`, `mix`, `bpm`, 정리 가사, `instrumental`)을 넣어 최종 style·notes를 확인한다.
9. **보고:** 모드에 따라
   - 기본 검토/부분 위임: [생성 전 검토안](../yue-music/references/report-template.md#생성-전-검토안-기본-검토-모드) + 언어 검수 결과 + `## YuE2 공식 가이드 보정 보고`를 한 번에 보여주고 "이 가사·프롬프트·옵션으로 생성할까요? 수정할 부분이 있으면 알려주세요."라고 묻고 멈춘다.
   - 초안만·수정만: 같은 자료를 주고 생성하지 않는다. 생성 명령은 "승인 후 실행할 명령"으로만 소개한다.
   - 전체 자동 위임·제공안 승인·지정 수정·재생성: 질문으로 멈추지 않고 10으로 간다. 다만 G4·G9의 의미 변경이 있으면 그 부분만 묻는다.
10. **생성:** 아래 블록을 순서대로 실행한다(실행할 수 없는 환경이면 이 블록 전체를 "승인 후/사용자 PC에서 실행할 명령"으로 그대로 적는다. 일부만 적지 않는다).

    ```bash
    roadmusic projects:list                                   # current가 이 곡과 무관하면 다음 줄
    roadmusic projects:create --json '{"name":"<곡 이름 YYYY-MM-DD>"}'   # 만든 프로젝트가 바로 선택된다
    roadmusic song:generate --file song.json                  # song.json에 requestPrompt 포함
    roadmusic job:wait --json '{"jobId":"<받은 jobId>","timeoutMs":3600000}'
    ```

    세부: `roadmusic song:generate --file song.json` → 받은 `jobId`로 `roadmusic job:wait --json '{"jobId":"…"}'`. 시간 초과면 같은 `jobId`로 다시 기다린다. `uncertain:true`면 재제출하지 말고 `service:status`·`queue:list`·`songs:list`로 확인한다. 승인 수량(`count`)만 생성한다.
11. **결과:** `yue-result-review`로 넘기고, 생성 시간·결과 파일을 1의 요청 기록에 연결한다. 임시 데이터 폴더로 서비스를 띄웠다면 같은 `ROADMUSIC_DATA_DIR`로 `roadmusic cli:stop`.

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
