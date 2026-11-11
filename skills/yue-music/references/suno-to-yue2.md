# Suno → YuE2(Road Music) 변환 대응표

원본 [claude-ai-music-skills](https://github.com/bitwize-music-studio/claude-ai-music-skills)(커밋 `597d928`, 2026-10-13)의 Suno 전용 개념을 YuE2 공식 계약과 Road Music CLI로 옮길 때의 기준이다. **"대응 없음"은 YuE2에 같은 기능이 없다는 뜻이며, 비슷한 옵션으로 흉내 내지 않는다.** Road Music `docs/genre-prompts.md#external-adaptation`도 Suno의 Variety·Exclude Styles를 YuE의 CFG·temperature로 대응시키지 말라고 정한다.

> Suno 쪽 사실(칸 글자 수, v6 모델군, Variety·Max Mode 등)은 원본 스킬 문서 기준이며 이번에 Suno 공식 자료로 다시 검증하지 않았다. YuE2·Road Music 쪽은 고정 공식 원문과 CLI 실측으로 확인했다.

## 입력 칸

| Suno | YuE2 / Road Music | 변환 방법 |
| --- | --- | --- |
| Style of Music 칸(1,000자), "보컬 먼저" 구조 `[Vocal]. [Genre]. [Production]` | `style` (schema ≤2000자) | 공식 순서 **언어, 장르, 보컬, 악기, 선율·프레이징, BPM**의 쉼표 태그로 다시 쓴다. 태그당 10단어 이하. 마침표 문장 블록을 쓰지 않는다 |
| 언어 자동 감지 | `style` 맨 앞의 언어 | `Korean,` / `English,`를 명시한다(`style-language`) |
| Lyrics 칸(5,000자) | `lyrics` (schema ≤20000자, 실제 한계는 토큰 예산) | 부를 말 + 구간 태그만. 문자 수로 자르지 않는다 |
| Exclude Styles 칸, `no drums` | **대응 없음**(`negative_prompt` 필드 없음, 공식) | 원하는 편성의 긍정형 묘사: `sparse piano and cello arrangement`(Road Music 권장, `style-positive-description`). 공식 예시에도 `no guitar`가 있듯 부정 문구가 금지는 아니지만 완전 배제는 보장하지 않는다 |
| Vocal Gender 설정 | `style` 보컬 묘사 / `parts.vocal` | `solo female vocal`. 특정 음색 보장 아님 |
| BPM을 style에 적기 | `bpm`(40~220) 또는 `parts.bpm` → style의 `NN BPM`(끝 또는 악기 요약 앞) | 원생 bpm 필드는 없다. 정확한 템포 보장 아님. ABC를 쓰면 `Q:`와 같은 값 |
| Duration(Custom 10초~6:00, 그 값에서 자름) | `targetSeconds` | YuE는 **기록용**. 자연 EOS로 끝나며 길이를 맞추려고 가사를 줄이거나 오디오를 자르지 않는다 |
| Instrumental 토글 | `instrumental:true` | 무보컬 의도 요청. Vocal 쉼표도 무보컬을 보장하지 않으므로 청취 확인 |
| 생성당 2곡 | `count` | 같은 설정의 후보에만. 1곡 요청은 `count:1` |
| (없음) | `seed` | 재현 추적용. 엔진·런타임이 다르면 같은 곡 아님 |
| (없음) | `cot` = `full`/`melody`/`off` | 새 곡은 `full`. Suno에 대응 기능 없음 |
| (없음) | `abc` | 외부 악보(`Vocal`·`Ins` 두 선율). `score:check`로 확인 |

## 가사 태그·표기

| Suno 표기 | Road Music 정리 결과(실측) | YuE2 처리 |
| --- | --- | --- |
| `[Verse 1]`, `[Verse 2]` | `[Verse]` | 번호 없이 반복 |
| Performance Cue `[Verse 1 - cold regal]`, `[Chorus - anthemic]` | `[Verse]`, `[Chorus]` (수식어 삭제) | 구간별 창법 채널이 없다. 곡 전체 성향만 `style`/`parts.vocal`/`parts.dynamics`로 요청 |
| 단독 무드 태그 `[Whispered]`, `[Aggressive]` | 삭제 | `intimate soft vocal` 같은 style 태그로 옮김 |
| `[Post-Chorus]` | `[Chorus]` | 의도한 구간이면 `[Chorus]`로 적고 차이를 보고 |
| `[Break]`, `[Guitar Solo]` | `[Interlude]` + `[instrumental]` | 악기 정보는 style(`melodic guitar solo`) |
| `[Fade Out]`, `[End]` | `[Outro]` + `[instrumental]` | 페이드·종료 시각 보장 없음 |
| `[Build]` | 삭제 | `gradual build`를 `parts.dynamics`/style로 |
| `(guitar solo)` 같은 무대 지시 줄 | 줄 삭제 | 가사에 쓰지 않는다 |
| 백보컬 괄호 `(ooh)`, 줄 안 `(…)` | **남음** → `lyrics-no-annotations` advice | 실제로 부를 말이면 괄호 없이 쓰고, 아니면 빼고 style `layered vocal harmonies`로 |
| 발음용 철자 바꾸기(phonetic respelling) | 그대로 불림 | 쓰지 않는다. 발음 위험은 검수 메모로 남기고, 표기 변경은 원문 승인 시에만. 발음 보장 없음 |
| `/발음/` 표기, 화자 표시(`남:`/`여:`) | advice 또는 그대로 불림 | 쓰지 않는다. 구간별 가수 필드 없음 |

## 모델·설정

| Suno | YuE2 / Road Music | 비고 |
| --- | --- | --- |
| 모델 v6 / v6-wild / v6-mini / Custom Model | `engine`: `yue-mlx`(Apple Silicon) / `yue`(Windows NVIDIA), 모델은 YuE2-3B 고정 | 사용자가 고른 엔진 유지 |
| Variety(Off/Normal) | **대응 없음** | temperature 등과 짝짓지 않는다 |
| Weirdness / Style Influence / Audio Influence 슬라이더 | **대응 없음** | `advanced`의 샘플링은 다른 개념. 기본값 유지, 바꾸면 실험·한 요소만 |
| Max Mode | **대응 없음** | |
| Advanced/Simple Mode | 해당 없음 | 항상 JSON 입력 |

## 기능

| Suno | YuE2 / Road Music | 비고 |
| --- | --- | --- |
| Personas / Voices / 참조 가수 | **대응 없음**(참조 가수·화자 필드 없음) | 실존 가수 이름을 style에 쓰지 않는다 |
| Cover(오디오 업로드) | 공식: SheetSage2 전사 → 사람이 검토한 멜로디 ABC → 코드 제거 → `cot:"melody"`(화성까지 유지하면 full 전사 + `cot:"full"`) | Road Music: 별도 SheetSage2 환경이 있을 때 `score:transcribe`(`audio`·`output`·`python`·`modelDir` 절대 경로 필수, `task` 기본 `melody-full`은 이미 코드 없는 선율) → 필요 시 `score:strip-chords`(`voice`로 한 성부 선택) → `abc`. 절차는 `yue-score-editor`. `coverAudio`·`recording`은 ACE 전용. 원곡 가수 음색·파형 보존 아님. 원곡 권리 확인 |
| Extend / Replace Section / Song Editor(구간 재생성) | **대응 없음**(로컬 인페인팅 없음) | 수정은 새 전체 생성. 원문 유지 악보 수정은 `song:render`, 가사·style 변경은 새 `song:prepare`→`song:generate` |
| Stems 다운로드 | **대응 없음** | ABC `Vocal`/`Ins`는 스템이 아니다 |
| (원본 sheet-music-publisher) 악보 PDF·출판 | **CLI 대응 없음** | `song:score`로 `score.abc`만 읽을 수 있다. 생성 계획이지 음원 채보가 아니다(`yue-score-editor`) |
| Suno 웹에 붙여넣기(clipboard) | `song:generate --file song.json` | 승인 후에만 |
| Generation Log(트랙 md) | `songs:list`, `song:detail`, 제작 기록 스킬 | |
| 재생성(비결정성에 기대어 다시 돌리기) | `docs/music-review.md#retry-value` 판단 후 | 순이득 근거 없는 반복을 권하지 않는다 |

## 원본에서 유지한 비-Suno 요소

작사 기법(장면으로 보여주기, 절/후렴 대비, 절-후렴 반복 표현 회피, 훅·제목 배치, 시점·시제 일관성, 2절의 전진), 앨범 순서·에너지 설계, 생성 전 관문 점검, 실존 아티스트명 차단. 단, 영어 운율·강세 수치와 Suno 밀도 한도는 한국어·YuE2 규칙으로 옮기지 않고 호흡·음절 밀도 점검으로 바꿨다.
