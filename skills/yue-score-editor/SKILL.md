---
name: yue-score-editor
description: Road Music YuE2(yue-mlx/yue)의 ABC 악보를 읽고·검사하고·수정본을 만들어 다시 생성하거나, 악보 기반 커버(SheetSage2 전사→코드 제거→cot melody)와 재화성·선율 보존 편집을 준비한다. song:score, score:inspect, score:compare, score:strip-chords, score:transcribe, song:render를 쓴다. Use for YuE2 score editing, reharmonization, melody-preserving edits, score-based covers, or sheet-music export (replaces Suno Song Editor, covers/personas and sheet-music-publisher).
---

# YuE2 악보 편집·커버

원본의 Suno Song Editor·Cover·Persona 흐름과 `sheet-music-publisher`를 YuE2 공식 편집 계약으로 바꿨다. YuE2는 파형 인페인팅이 없고 **수정한 악보·style·가사로 곡 전체를 새로 생성**한다. [공통 규칙](../yue-music/references/common-rules.md)을 적용한다.

근거: 공식 `official/skills/yue2-music/SKILL.md`(Cover·Edit 절), `references/editing-workflows.md`, `references/abc-editing.md`, main `docs/generation.md`("What the score controls"), Road Music `docs/yue-prompt-guide.md#planning`, `#editing`, `#score-choice`, `docs/yue-cli-workflow.md`.

## 먼저 정할 것: 보존 계약

편집을 시작하기 전에 사용자에게서(또는 요청에서) 무엇을 고정할지 정해 기록한다. 공식 editing-workflows의 네 가지 계약을 쓴다.

| 계약 | 고정되는 것 |
| --- | --- |
| 정확한 선율·리듬 | 지정 성부·구간의 음높이·시작 시점·길이 |
| 같은 음높이, 리듬 수정 | 음높이 순서. 허용한 리듬·아티큘레이션 변경을 기록 |
| 알아볼 수 있는 주제 | 프레이즈 순서·반복. 허용한 꾸밈을 나열 |
| 범위 안 자유 편곡 | 합의한 프레이즈·음역·윤곽·종지·모티프. 실제 바뀐 음을 보고 |

템포·박자·가사·연주 구간을 바꿔도 되는지도 정한다. 템포를 바꾸면 박 기준 리듬은 같아도 초 단위 시간이 바뀐다.

## 작업 흐름

```bash
roadmusic() { node "${ROAD_MUSIC_HOME:-/Users/freelife/youtube/music/music-road}/cli/road-music.js" "$@"; }  # bash·zsh 공통. 셸 호출마다 다시 정의
```

1. **기준 확보:** 편집할 곡의 `dir`(`songs:list`/`song:detail`의 절대 경로)에서 `roadmusic song:score --json '{"dir":"…"}'`로 악보를 읽는다. 원본 디렉터리·`score.abc`·요청·음원은 **제자리에서 고치지 않는다**(저장된 plan은 해시로 검증된다). 수정은 새 파일 사본에서 한다.
2. **원본 검사:** `roadmusic score:inspect --json '{"file":"/abs/source.abc"}'`. 모델이 만든 계획·전사에도 실수가 있을 수 있으니 기준으로 쓰기 전에 확인한다.
3. **수정:** 지원 방언 안에서만 고친다.
   - `Vocal`·`Ins` 두 단선율, `L:1/<2의 거듭제곱>`, 박자 `M:`, 템포 `Q:1/4=N`, 코드는 따옴표 기호(`"Am7"`)로 `Vocal`에 둔다.
   - 지원하지 않는 것: 셋잇단음표, 꾸밈음, 화음 쌓기, 반복 기호, 이음줄(slur), `w:` 가사 줄, 사용자 성부. 세 번째 성부는 독립 제어되지 않는다.
   - 4/4 한 마디는 `L:1/32` 기준 32단위. 지속음 중간의 코드 변경은 붙임줄로 나눈다(`"C"E16-"Am7"E16`). 임시표는 그 마디 안에서 같은 글자 전 옥타브에 적용된다(원생 규칙).
   - 템포를 바꾸면 `Q:`와 style의 BPM을 같이 바꾼다.
4. **수정본 검사:** `roadmusic score:inspect --json '{"file":"/abs/edit.abc"}'`, 그리고 `roadmusic score:compare --json '{"source":{"file":"/abs/source.abc"},"candidate":{"file":"/abs/edit.abc"}}'`로 계약 위반을 찾는다. 문자열이 아니라 해석된 음 사건(붙임줄 병합 후 소리 나는 음)을 비교한다. 의도한 리듬 변경은 정확 비교에서 실패하는 것이 맞으며, 실패를 "선율 보존"으로 바꿔 적지 않는다.
5. **독립 검토(가능하면):** 다른 에이전트에게 수정 전후 ABC, 요청, 사용자 제약, 들을 수 있으면 기준 음원을 주고, 편집자의 진단을 알려주기 **전에** 위반·음악적 문제를 찾게 한다(공식 editing-workflows). 불가능하면 직접 별도 단계로 검토하고 그렇게 밝힌다.
6. **다시 생성(승인 범위에서):**
   - **원래 가사·style을 그대로 두고 악보만 바꾼 경우:** `song:render`(`{"dir":"…","abc":"<수정 ABC>","title":"…"}`). render는 원래 가사·style을 재사용한다.
   - **가사나 style도 바꾼 경우:** render가 아니라 바뀐 전체 입력으로 새 `song:prepare` → `song:generate`, `abc`에 수정본, `cot`은 화성까지 쓰면 `full`, 선율만이면 `melody`.
   - 둘 다 실제 생성이므로 `yue-pre-generation-check`의 관문·승인을 거친다.
7. **비교·보고:** 전곡과 수정 구간 주변을 비교하고, 기호 검사·자동 전사·청취를 구분해 보고한다. ABC 검사만으로 "음이 정확히 재현됐다", "악기가 빠졌다"고 쓰지 않는다. 각 시도와 실제 요청을 보존한다.

## 재화성 요령 (공식 editing-workflows 요약)

- 두 성부 모두에서 지속음·강박 음·종지·프레이즈 경계를 먼저 표시한다.
- 바꿀 코드마다 음 전체 길이 동안의 코드, 베이스 진행, 인접 선율음, 긴장 해결을 본다. 두 박 충돌과 짧은 반음 접근은 판단이 다르다.
- 색채는 방향을 갖고 넣는다(부속 도미넌트, 짧은 ii–V, 차용 화음, 트라이톤 접근, 공통음 연결). 마디당 치환 수가 많다고 좋은 편곡이 아니다.
- 스타일 변경이면 악보와 함께 편곡 style도 바꾼다. 악기를 뺀다고 적어도 실제 음원에서 빠졌다는 증거는 아니다.

## 커버 (악보 기반)

| 출발점 | 경로 |
| --- | --- |
| 녹음 | `score:transcribe`(별도 설치된 SheetSage2 환경 필요, 자동 설치 없음) → 경고·누락 검토 → 코드 제거 → `cot:"melody"` |
| ABC 선율 | `score:inspect` → 필요하면 방언 변환 → `score:strip-chords` → `cot:"melody"` |

- `score:transcribe`에는 `audio`·`output`·`python`·`modelDir` 절대 경로가 모두 필요하다. `task`: `full`(화성 포함) / `melody-full`(기본, 코드 없는 전체 선율) / `melody-vocal`(보컬 선율만).
- `score:strip-chords`는 기본적으로 두 선율을 모두 남긴다. 한 성부만 남기려면 `voice:"Vocal"` 또는 `"Ins"`를 명시한다. 커버라는 이유만으로 `Ins`를 버리지 않는다.
- 원곡 화성도 유지하려면 full 전사와 `cot:"full"`을 쓰고 "선율·화성 조건 재생성"이라고 부른다.
- 이것은 기호 선율 조건이다. **원곡 가수의 음색·파형을 보존하지 않는다.** 원곡·가사·녹음의 권리를 먼저 확인한다. Road Music의 `coverAudio`·`recording` 필드는 ACE 전용이므로 YuE 요청에 붙이지 않는다.
- 가사를 번역·개사해 커버할 때는 음절·강세·모음·숨 자리를 맞추고, 음절↔음표 대응은 별도 메모(sidecar)로 남긴다. `phonemes` 필드를 만들지 않으며 메모를 강제 정렬로 착각하지 않는다.

## 악보 내보내기 (원본 sheet-music-publisher 대체)

- YuE2 `full`/`melody` 생성은 `score.abc`를 남긴다. `song:score`로 읽고, Road Music `score:convert`·`score:open`(악보 창)이 지원하는 변환을 실행 버전 `schema`로 확인해 쓴다.
- 이 악보는 **생성 조건으로 쓴 계획**이지 실제 음원을 채보한 결과가 아니다. 출판용 악보로 낼 때 "음원과 같은 악보"라고 쓰지 않는다. 실제 음원의 선율이 필요하면 `score:transcribe`(SheetSage2) 결과를 별도로 검토한다.
- `cot:"off"`로 만든 곡에는 악보가 없다.

## 연주곡 악보

공식 main의 연주곡 절차는 빈 가사로 선율을 `Ins`로 옮기는 별도 스킬이다. Road Music의 `instrumental:true`는 이 절차와 같지 않다. Vocal 쉼표도 무보컬을 보장하지 않으므로 납품 전에 듣는다.
