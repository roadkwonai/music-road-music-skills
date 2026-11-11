---
name: yue-mastering
description: Road Music YuE2로 생성한 완성 음원(48kHz stereo FLAC)을 원본은 보존한 채 스트리밍·영상 납품용으로 라우드니스(-14 LUFS 등)·트루피크 확인·조정, 기술 QC, MP3/WAV 내보내기를 한다. 스템 분리 믹싱은 하지 않는다. Use when mastering, loudness-normalizing, QC-checking or exporting finished YuE2 songs (replaces mastering-engineer and mix-engineer).
---

# YuE2 완성 음원 마스터링·납품

원본 `mastering-engineer`·`mix-engineer`를 YuE2 출력에 맞게 줄였다. YuE2는 **스템을 내지 않고** 48kHz stereo 전체 믹스(`audio.flac`)를 만든다. ABC의 `Vocal`·`Ins`도 오디오 스템이 아니다. 그래서 원본의 스템별 정리(보컬·드럼·베이스…)는 옮기지 않고 전체 믹스 마스터링만 다룬다. [공통 규칙](../yue-music/references/common-rules.md)을 적용한다.

## 원칙

- **원본 보존:** Road Music의 원본 FLAC·악보·artifact는 그대로 두고 새 경로에 결과를 쓴다. 기존 파일을 덮어쓰지 않는다(ffmpeg는 `-n`).
- **완주한 곡만:** `result.json`의 `truncated.abc`·`truncated.semantic`이 참이면 마스터링보다 원인 조사가 먼저다(`yue-result-review`).
- **표시·메타데이터 제거 금지:** 생성물에 붙은 메타데이터·식별 정보를 지우거나 숨기는 처리는 마스터링이 아니며 하지 않는다(원본 스킬의 "watermark 제거 금지" 원칙 유지).
- **업샘플링을 품질 향상이라고 하지 않는다:** 원본이 48kHz이므로 96kHz로 올려도 정보가 늘지 않는다. 플랫폼 배지 요건 때문에 올렸다면 그 사실을 적는다.
- **들은 것과 잰 것 구분:** 수치 측정(LUFS·피크)과 청취 판단을 나눈다. 듣지 않았으면 음색·밸런스 개선을 주장하지 않는다.
- 공식 YuE2 문서: MP3는 별도 납품 변환이다.

## 목표값(출발점)

| 용도 | 통합 라우드니스 | 트루피크 상한 | 형식 |
| --- | --- | --- | --- |
| 스트리밍 일반 | -14 LUFS | -1.0 dBTP | WAV 24-bit 48kHz |
| 유튜브·영상 | -14 LUFS | -1.0 dBTP | WAV 또는 영상 렌더 입력 |
| 조용한 장르(어쿠스틱·앰비언트) | -16 ~ -14 LUFS | -1.0 dBTP | 동일 |
| 강한 장르(EDM·록) | -14 ~ -11 LUFS(사용자가 원할 때) | -1.0 dBTP | 동일 |

플랫폼은 재생 시 음량을 맞추므로 더 크게 만드는 것이 유리하다고 단정하지 않는다. 사용자 목표가 있으면 그것을 따른다.

## 절차

1. **대상 확인:** `songs:list`/`song:detail`에서 곡 `dir`과 실제 오디오 경로를 얻는다. 사용자가 승인한 곡만 다룬다.
2. **측정(원본):** ffmpeg가 있어야 한다(Road Music 필수 도구).

   ```bash
   ffprobe -v error -show_entries stream=sample_rate,channels,codec_name -show_entries format=duration -of json "$IN"
   ffmpeg -hide_banner -nostats -i "$IN" -af ebur128=peak=true -f null - 2>&1 | tail -12
   ffmpeg -hide_banner -nostats -i "$IN" -af astats=metadata=0:measure_overall=Peak_level+RMS_level+DC_offset -f null - 2>&1 | tail -8
   ffmpeg -hide_banner -nostats -i "$IN" -af silencedetect=noise=-50dB:d=2 -f null - 2>&1 | grep silence_ | head
   ```

3. **기술 QC(원본 7항목 대응):** 통합 라우드니스·LRA, 트루피크(클리핑 위험), 앞뒤·중간의 긴 무음, DC 오프셋, 길이·포맷·채널, 좌우 위상(모노 합산 시 크게 줄면 위상 문제 의심), 끝맺음(잘림). 문제를 표로 적는다.
4. **조정(2패스 loudnorm):**

   ```bash
   # 1패스: 측정값 얻기
   ffmpeg -hide_banner -nostats -i "$IN" -af loudnorm=I=-14:TP=-1.0:LRA=11:print_format=json -f null - 2>&1 | tail -12
   # 2패스: 측정값(measured_*)을 넣어 선형 보정, 새 파일로만 쓰기
   ffmpeg -n -hide_banner -i "$IN" -af "loudnorm=I=-14:TP=-1.0:LRA=11:measured_I=<I>:measured_TP=<TP>:measured_LRA=<LRA>:measured_thresh=<thresh>:offset=<offset>:linear=true" -ar 48000 -c:a pcm_s24le "$OUT_DIR/<제목>-master.wav"
   ```

   측정값을 셸 변수로 넣을 때는 `${OFFSET}:linear=true`처럼 중괄호를 쓴다(zsh는 `$OFFSET:l…`을 변수 수식어로 해석해 값이 깨진다). 2026-11-12에 ffmpeg로 -32.6 LUFS 시험 신호를 -14.0 LUFS로 맞춰 이 명령을 확인했다.

   EQ·압축 같은 음색 처리는 사용자가 원하고 청취로 확인할 수 있을 때만, 한 번에 하나씩 한다.
5. **재측정:** 결과 파일로 2단계를 다시 실행하고 목표 대비 차이를 기록한다.
6. **내보내기:** Road Music `song:export`(`{"dir":"…","format":"mp3"|"wav"}`)나 앨범 `album:export`가 있으면 그것을 쓰고, 마스터 WAV를 따로 만든 경우 MP3는 그 WAV에서 변환한다(`-c:a libmp3lame -b:a 320k`, 새 파일).
7. **앨범 일관성(여러 곡):** 곡별 통합 라우드니스 차이가 크면(예: 2 LU 이상) 맞추되, 의도된 조용한 곡은 사용자 확인 후 유지한다.

## 보고

```text
## 마스터링 결과
| 곡 | 원본 경로 | 결과 경로 | 원본 LUFS/TP | 결과 LUFS/TP | 형식 | QC 문제 |
- 원본 보존: 예(덮어쓰기 없음)
- 청취: 미실행 / 실행(범위)
- 메모: 업샘플링 여부, 장르 목표 선택 이유
```
