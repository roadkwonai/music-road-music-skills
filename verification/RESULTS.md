# 예시 요청 검증 결과

- 실행 시각: 2026-11-11T18:43:51.061Z
- Road Music CLI: 0.1.0 (app 0.1.0, protocol 2)
- 명령: `song:prepare --file examples/<파일>` (모델·서비스 없이 로컬 검증, 음악 생성 없음), `yue:capabilities`(읽기 전용)
- 데이터 폴더: `ROADMUSIC_DATA_DIR`를 임시 폴더로 분리
- 결과: 7/7 통과

| 예시 | 엔진 | valid | pass | advice | 해당 없음 | 판정 |
| --- | --- | --- | --- | --- | --- | --- |
| en-pop-yue-windows.json | yue | true | 8 | 0 | 2 | 기대와 일치 |
| instrumental-yue-mlx.json | yue-mlx | true | 4 | 0 | 6 | 기대와 일치 |
| ko-ballad-yue-mlx.json | yue-mlx | true | 8 | 0 | 2 | 기대와 일치 |
| ko-melody-abc-yue-mlx.json | yue-mlx | true | 10 | 0 | 0 | 기대와 일치 |
| ko-trot-parts-yue-mlx.json | yue-mlx | true | 8 | 0 | 2 | 기대와 일치 |
| suno-style-after.json | yue-mlx | true | 8 | 0 | 2 | 기대와 일치 |
| suno-style-before.json | yue-mlx | true | 3 | lyrics-no-annotations, style-language, style-no-instruction, style-positive-description, style-tempo | 2 | 기대와 일치 |

## 예시별 메모

### en-pop-yue-windows.json

- Windows NVIDIA용 engine yue, cot melody(외부 ABC 없음).
- 최종 style(nativeRequest): `English, soft piano pop, warm female vocal, acoustic piano, round bass, light drums, singable melody, relaxed phrasing, 92 BPM`
- 가사 정리 변경: false

### instrumental-yue-mlx.json

- instrumental:true라 언어·보컬·가사 점검은 not-applicable.
- 최종 style(nativeRequest): `lo-fi hip hop, dusty and relaxed, Rhodes electric piano, upright bass, brushed drums, gentle swing, 76 BPM, instrumental only, no vocals, no singing, no humming, no choir, no chanting, no spoken word, no narration, no vocal samples, no ad-libs, no vocal chops, no backing vocals, melody carried by lead instrument`
- 가사 정리 변경: true

### ko-ballad-yue-mlx.json

- AI 작성 한국어 발라드. bpm 필드가 style 끝에 72 BPM으로 조합된다.
- 최종 style(nativeRequest): `Korean, emotional piano ballad, solo female vocal, clear Korean phrasing, piano, cello, string ensemble, restrained verse and open chorus, unhurried phrasing, 72 BPM`
- 가사 정리 변경: false

### ko-melody-abc-yue-mlx.json

- 코드 없는 원작 ABC(Q:1/4=80)와 style 80 BPM 일치, cot melody.
- 최종 style(nativeRequest): `Korean, acoustic folk pop, warm solo male vocal, acoustic guitar, piano, light percussion, simple stepwise melody, 80 BPM`
- 가사 정리 변경: false

### ko-trot-parts-yue-mlx.json

- style 없이 parts(genre·vocal·instrumentation·dynamics·bpm)만 사용.
- 최종 style(nativeRequest): `Korean, traditional trot, Chorus accordion lead melody, Chorus accordion bright fills, Chorus brass section responses between vocal lines, drums rhythm, drums two-beat ppongjjak, mature solo male vocal, clear Korean phrasing, lively verse, festive chorus lift, 120 BPM, accordion, brass section and drums`
- 가사 정리 변경: false

### suno-style-after.json

- before를 대응표대로 변환한 결과.
- 최종 style(nativeRequest): `English, heavy rock, gritty emotional male baritone vocal, distorted electric guitar, bass guitar, drums, organic guitar-driven arrangement, melodic guitar solo, stadium anthem chorus, 140 BPM`
- 가사 정리 변경: true

### suno-style-before.json

- Suno식 입력(보컬 먼저 문장 블록, no synths, 명령문, 수식어 태그, 무드 태그, 괄호 메아리, 무대 지시). advice가 나와야 정상.
- 최종 style(nativeRequest): `Male baritone, gritty and emotional, Heavy rock, distorted guitars, no synths, Make a song that feels like a stadium anthem`
- 가사 정리 변경: true
- 남은 advice와 이유(Suno식 입력을 변환 전 그대로 둔 비교용 예시):
  - style-language: style 앞쪽에 실제 가사 언어(예: Korean)를 적는다.
  - style-tempo: bpm 필드나 style에 의도한 BPM을 적는다. 정확한 템포 보장은 아니다.
  - style-positive-description: 부정·제외 문구는 제외를 보장하지 않는다. 원하는 편성·질감을 긍정형으로 바꾸는 안을 제안한다.
  - style-no-instruction: 명령문을 지우고 음악 묘사(장르·악기·보컬·언어·템포)만 남기는 안을 제안한다.
  - lyrics-no-annotations: 실제로 부를 말이 아니면 주석을 빼고 style이나 검수 메모로 옮기는 안을 제안한다: Every echo calls my name (my name)

## 엔진 지원 범위(yue:capabilities)

- yue-mlx: platform=Apple Silicon macOS, platformMatches=true, defaults cfgScale=1, odeSteps=32
- yue: platform=Windows NVIDIA, platformMatches=false, defaults cfgScale=1, odeSteps=32

이 검증은 입력 계약 점검이다. 실제 가창·길이·발음·음질은 생성 후 청취로만 확인할 수 있다.
