---
name: yue-score-editor
description: Road Music YuE2(yue-mlx/yue)의 ABC 악보를 읽고·검사하고·수정본을 만들어 다시 생성하거나, 악보 기반 커버(SheetSage2 전사 또는 MIDI 가져오기→코드 제거→cot melody)와 재화성·선율 보존 편집을 준비한다. song:score, score:inspect, score:compare, score:strip-chords, score:transcribe, score:open/convert, song:render를 쓴다. Use for YuE2 score editing, reharmonization, melody-preserving edits or score-based covers (replaces Suno Song Editor, covers/personas and sheet-music-publisher).
---

# YuE2 악보 편집·커버

원본의 Suno Song Editor·Cover·Persona 흐름과 `sheet-music-publisher`를 YuE2 공식 편집 계약으로 바꿨다. YuE2는 파형 인페인팅이 없고 **수정한 악보·style·가사로 곡 전체를 새로 생성**한다. [공통 규칙](../yue-music/references/common-rules.md)을 적용한다.

근거: 공식 `official/skills/yue2-music/SKILL.md`(Cover·Edit 절), `references/editing-workflows.md`, `references/abc-editing.md`, main `docs/generation.md`("What the score controls"), Road Music `docs/yue-prompt-guide.md#planning`, `#editing`, `#score-choice`, `docs/yue-cli-workflow.md`.

```bash
roadmusic() { node "${ROAD_MUSIC_HOME:-/Users/freelife/youtube/music/music-road}/cli/road-music.js" "$@"; }  # bash·zsh 공통. 셸 호출마다 다시 정의
```

## 먼저 정할 것: 보존 계약

공식 editing-workflows의 네 가지 계약 중 하나를 정해 기록한다.

| 계약 | 고정되는 것 |
| --- | --- |
| 정확한 선율·리듬 | 지정 성부·구간의 음높이·시작 시점·길이 |
| 같은 음높이, 리듬 수정 | 음높이 순서. 허용한 리듬·아티큘레이션 변경을 기록 |
| 알아볼 수 있는 주제 | 프레이즈 순서·반복. 허용한 꾸밈을 나열 |
| 범위 안 자유 편곡 | 합의한 프레이즈·음역·윤곽·종지·모티프. 실제 바뀐 음을 보고 |

템포·박자·가사·연주 구간을 바꿔도 되는지도 정한다. 템포를 바꾸면 박 기준 리듬은 같아도 초 단위 시간이 바뀐다.

## 작업 흐름

1. **기준 확보:** 곡 `dir`(`songs:list`/`song:detail`의 절대 경로)에서 `roadmusic song:score --json '{"dir":"…"}'`로 악보를 읽는다. 기준 음원이 있으면 함께 기록한다. 원본 디렉터리·`score.abc`·요청·음원은 **제자리에서 고치지 않는다**.
2. **작업 폴더:** 사본과 수정본은 **Road Music 곡 보관 폴더(Songs와 그 아래 프로젝트·곡 폴더) 밖**의 작업 폴더에 둔다(예: `~/Documents/YueStudio/Work/<곡 제목>/`). `songs:list`가 프로젝트 안의 오디오 없는 하위 폴더를 정리(삭제)하기 때문이다.
3. **원본 검사:** `roadmusic score:inspect --json '{"file":"/abs/source.abc"}'`(로컬). 모델이 만든 계획·전사에도 실수가 있을 수 있다. `cot:"melody"`로 만든 곡의 악보에는 코드가 없으므로 재화성의 기준으로는 `cot:"full"` 악보가 필요하다.
4. **수정(지원 방언 안에서만):**
   - `Vocal`·`Ins` 두 단선율, `L:1/<2의 거듭제곱>`, 박자 `M:`, 템포 `Q:1/4=N`, 코드는 따옴표 기호(`"Am7"`)로 `Vocal`에 둔다. 공식 helper가 아는 기본 코드 어휘를 쓰고 확장 보이싱(`C13`, `A7alt` 등)은 style 묘사로 보낸다.
   - 지원하지 않는 것: 셋잇단음표, 꾸밈음·장식, 화음 쌓기, 반복 기호·endings, 이음줄(slur), 붙점 단축 리듬(broken rhythm), `w:` 가사 줄, 사용자 성부. 세 번째 성부는 독립 제어되지 않는다.
   - 4/4 한 마디는 `L:1/32` 기준 32단위. 지속음 중간의 코드 변경은 붙임줄로 나눈다(`"C"E16-"Am7"E16`). 압축 쉼표 `Z`를 화성·조 변경 위에 쓰지 않는다(쉼표 마디에 코드를 넣을 때 일반 쉼표로 풀어 쓴다). 임시표는 그 마디 안에서 같은 글자 전 옥타브에 적용된다(원생 규칙).
5. **수정본 검사(로컬):** `score:inspect`로 구조를, `score:compare`로 계약을 확인한다. 문자열이 아니라 해석된 음 사건을 비교한다.

   ```bash
   roadmusic score:compare --json '{"source":{"file":"/abs/source.abc"},"candidate":{"file":"/abs/edit.abc"},"invariants":{"melody":true,"harmony":false,"form":true,"allowTempoChange":false}}'
   ```

   - 기본 `invariants`는 선율·형식만 보고 화성은 보지 않는다. 재화성이면 `harmony:false`로 두고 선율 보존을 확인한 뒤, `harmony:true`로 한 번 더 돌려 화성이 실제로 바뀌었는지(불일치)도 확인한다.
   - 템포를 바꾸면 `allowTempoChange:true`가 없을 때 불일치로 나온다. 의도한 리듬 변경도 정확 비교에서 실패하는 것이 맞으며, 실패를 "선율 보존"으로 바꿔 적지 않는다.
   - 경로는 절대 경로로 준다.
6. **독립 검토(가능하면):** 다른 에이전트에게 수정 전후 ABC, 요청, 사용자 제약, 들을 수 있으면 기준 음원을 주고, 편집자의 진단을 알려주기 **전에** 위반·음악적 문제를 찾게 한다. 불가능하면 직접 별도 단계로 검토하고 그렇게 밝힌다.
7. **다시 생성(승인 범위에서, `yue-pre-generation-check` 관문):**

   | 바꾼 것 | 경로 |
   | --- | --- |
   | 악보만(코드·음표), 가사·style·템포 그대로 | `song:render`(`{"dir":"…","abc":"<수정 ABC>","title":"…","requestPrompt":"<사용자 요청 원문>"}`) |
   | 템포(`Q:`) | style의 BPM도 바뀌어야 하므로 render가 아니라 새 `song:prepare`→`song:generate`(`abc`에 수정본) |
   | 가사나 style | 새 `song:prepare`→`song:generate`(`abc`에 수정본, 화성까지 쓰면 `cot:"full"`, 선율만이면 `cot:"melody"`) |

   - `song:render`는 원래 곡의 가사·style을 그대로 재사용하고 `song:prepare`를 거치지 않는다. 또 `cot`을 사용자 값이 아니라 **ABC에 코드 기호가 있으면 full, 없으면 melody**로 정한다. 그래서 render 전에도 원래 요청에 `abc`만 넣은 임시 요청으로 `song:prepare`를 돌려 `abc-tempo-consistency`·`melody-abc-chord-free`를 확인한다.
   - 가사가 비어 있는 곡(연주곡)은 `song:render`가 거부한다. 새 `instrumental:true` 생성을 쓴다.
   - `requestPrompt`에 사용자 요청 원문을 넣어 제작 기록을 남긴다.
8. **비교·보고:** 전곡과 수정 구간 주변을 비교하고 기호 검사·자동 전사·청취를 구분한다. ABC 검사만으로 "음이 정확히 재현됐다", "악기가 빠졌다"고 쓰지 않는다. 각 시도와 실제 요청을 보존한다.

## 재화성 요령 (공식 editing-workflows 요약)

- 두 성부 모두에서 지속음·강박 음·종지·프레이즈 경계를 먼저 표시한다.
- 바꿀 코드마다 음 전체 길이 동안의 코드, 베이스 진행, 인접 선율음, 긴장 해결을 본다. 두 박 충돌과 짧은 반음 접근은 판단이 다르다.
- 색채는 방향을 갖고 넣는다(부속 도미넌트, 짧은 ii–V, 차용 화음, 트라이톤 접근, 공통음 연결). 마디당 치환 수가 많다고 좋은 편곡이 아니다.
- 스타일 변경이면 악보와 함께 편곡 style도 바꾼다(이 경우 render가 아니라 새 생성). 악기를 뺀다고 적어도 실제 음원에서 빠졌다는 증거는 아니다.

## 커버 (악보 기반)

| 출발점 | 경로 |
| --- | --- |
| 녹음 | `yue:capabilities`에 `transcription:{python,modelDir}`로 SheetSage2 가용성 확인 → `score:transcribe` → 경고·누락 검토 → (필요 시) 코드 제거 → `cot:"melody"` |
| ABC 선율 | `score:inspect` → 필요하면 방언 변환 → `score:strip-chords` → `cot:"melody"` |
| MIDI | `roadmusic score:open --input /abs/file.mid`(서비스) → `score:convert --json '{"choice":{"vocal":"<트랙>","ins":"<트랙>","chords":false}}'` → `score:inspect` → `cot:"melody"` |

- `score:transcribe`(로컬, 자동 설치 없음)에는 `audio`·`output`·`python`·`modelDir` 절대 경로가 모두 필요하다. `task`: `full`(화성 포함) / `melody-full`(기본, 이미 코드 없는 전체 선율) / `melody-vocal`(보컬 선율만).
- `score:strip-chords`는 기본적으로 두 선율을 모두 남긴다. 한 성부만 남기려면 `voice:"Vocal"` 또는 `"Ins"`를 명시한다. 이때 다른 성부는 쉼표가 되므로 `score:compare`에서 그 성부는 불일치로 나온다(Road Music 래퍼에는 성부 지정 비교가 없다). 커버라는 이유만으로 `Ins`를 버리지 않는다.
- 원곡 화성도 유지하려면 full 전사와 `cot:"full"`을 쓰고 "선율·화성 조건 재생성"이라고 부른다.
- 이것은 기호 선율 조건이다. **원곡 가수의 음색·파형을 보존하지 않는다.** 원곡·가사·녹음의 권리와 SheetSage2 가중치 라이선스(CC BY-NC 4.0, 공식 models-and-setup)를 확인한다. Road Music의 `coverAudio`·`recording`은 ACE 전용이다.
- 가사를 번역·개사해 커버할 때는 음절·강세·모음·숨 자리를 맞추고 음절↔음표 대응은 별도 메모(sidecar)로 남긴다. `phonemes` 필드를 만들지 않는다.

## 악보 출력 (원본 sheet-music-publisher 대응)

- YuE2 `full`/`melody` 생성은 `score.abc`를 남기고 `song:score`로 읽을 수 있다. **Road Music CLI에는 PDF·MusicXML·MIDI로 내보내는 명령이 없다**(`score:open`·`score:convert`는 외부 악보를 가져오는 입구다). 출판용 악보가 필요하면 ABC를 사용자가 쓰는 악보 도구로 옮기거나, 별도 설치된 SheetSage2 렌더 도구를 쓰는 방법을 안내한다(자동 설치 없음).
- 이 악보는 **생성 조건으로 쓴 계획**이지 실제 음원을 채보한 결과가 아니다. 실제 음원의 선율이 필요하면 `score:transcribe` 결과를 별도로 검토한다. `cot:"off"`로 만든 곡에는 악보가 없다.

## 연주곡 악보

공식 main의 연주곡 절차는 빈 가사로 선율을 `Ins`로 옮기는 별도 스킬이다. Road Music의 `instrumental:true`는 이 절차와 같지 않다. Vocal 쉼표도 무보컬을 보장하지 않으므로 납품 전에 듣는다.
