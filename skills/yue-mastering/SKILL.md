---
name: yue-mastering
description: Road Music YuE2로 생성한 완성 음원을 원본은 보존한 채 스트리밍·영상 납품용으로 라우드니스(-14 LUFS 등)·트루피크 확인·조정, 기술 QC, WAV/MP3 내보내기를 한다. loudnorm의 Dynamic 전환을 감지해 다이내믹을 보존한다. 스템 분리 믹싱은 하지 않는다. Use when mastering, loudness-normalizing, QC-checking or exporting finished YuE2 songs (replaces mastering-engineer and mix-engineer).
---

# YuE2 완성 음원 마스터링·납품

원본 `mastering-engineer`·`mix-engineer`를 YuE2 출력에 맞게 줄였다. YuE2는 **스템을 내지 않고** 전체 믹스 하나를 만든다. ABC의 `Vocal`·`Ins`도 오디오 스템이 아니다. 그래서 스템별 정리는 옮기지 않고 전체 믹스 마스터링만 다룬다. [공통 규칙](../yue-music/references/common-rules.md)을 적용한다.

## 원칙

- **원본 보존:** 곡 폴더의 오디오·악보·artifact는 그대로 두고 결과는 새 파일로 쓴다. ffmpeg는 `-n`(덮어쓰기 거부).
- **작업 폴더 위치:** 결과는 **Road Music 곡 보관 폴더 밖**에 쓴다. `songs:list`는 프로젝트 폴더 안에서 오디오가 없는 하위 폴더를 정리(삭제)하고, 곡 폴더 안의 추가 `.wav`/`.mp3`는 곡 오디오로 잘못 집힐 수 있다. 사용자가 정한 폴더가 없으면 `app:state.songsDir`의 상위(프로젝트들이 있는 Songs 폴더)와 나란한 별도 폴더를 쓴다(예: `~/Documents/YueStudio/Masters/<곡 제목>/`).
- **완주한 곡만:** `song:detail`의 `truncated`(`abc`·`semantic`)가 참이면 마스터링보다 원인 조사가 먼저다(`yue-result-review`).
- **메타데이터 보존:** 생성물에 붙은 메타데이터·식별 정보를 지우거나 숨기는 처리는 하지 않는다.
- **업샘플링은 품질 향상이 아니다:** 48kHz 원본을 96kHz로 올려도 정보가 늘지 않는다. 배지 요건 때문에 올렸다면 그 사실을 적는다.
- **들은 것과 잰 것 구분:** 수치 측정과 청취 판단을 나눈다. 듣지 않았으면 음색·밸런스 개선을 주장하지 않는다. MP3는 별도 납품 변환이다(공식 YuE2 문서).

## 목표값(출발점)

| 용도 | 통합 라우드니스 | 트루피크 상한 | 형식 |
| --- | --- | --- | --- |
| 스트리밍·유튜브 일반 | -14 LUFS | -1.0 dBTP | WAV 24-bit 48kHz, 필요하면 MP3 320k |
| 조용한 장르(어쿠스틱·앰비언트) | -16 ~ -14 LUFS | -1.0 dBTP | 동일 |
| 강한 장르(EDM·록) | 사용자가 원하면 -14 ~ -11 LUFS | -1.0 dBTP | 동일 |

이 값은 업계에서 흔히 쓰는 출발점이며 플랫폼 공식 요구값을 이번에 확인한 것이 아니다. 플랫폼 기준이 중요하면 실행일에 해당 플랫폼 안내를 확인한다. 사용자 목표가 있으면 그것을 따른다.

## 절차

1. **입력 확인:** 입력이 곡처럼 보이지 않으면(수 초 길이, 단일 톤, 무음 등) 그 사실을 먼저 알리고 사용자가 의도한 파일인지 확인한다. 곡이 YuE2 생성물인지 기록(`song:detail`·제작 기록)으로 확인되지 않으면 그렇게 적는다. `songs:list`/`song:detail`의 곡 `dir`·`audio`를 얻는다(서비스 명령). `ffprobe`로 실제 코덱을 확인한다. `yue-mlx`는 무손실 `audio.flac`을 남기지만, Windows `yue`는 `audio.wav`만 쓰고, 설정에 따라 MP3만 남은 곡도 있다. 손실(MP3) 원본이면 WAV 마스터도 무손실 품질이 아님을 보고한다.
2. **측정(원본):**

   ```bash
   ffprobe -v error -show_entries stream=sample_rate,channels,codec_name -show_entries format=duration -of compact "$IN"
   ffmpeg -hide_banner -nostats -i "$IN" -af ebur128=peak=true -f null - 2>&1 | grep -E '^\s+(I|LRA|Peak):'
   ffmpeg -hide_banner -nostats -i "$IN" -af astats=metadata=0:measure_overall=Peak_level+RMS_level+DC_offset -f null - 2>&1 | grep -E 'Peak level|RMS level|DC offset' | tail -3
   ffmpeg -hide_banner -nostats -i "$IN" -af silencedetect=noise=-50dB:d=2 -f null - 2>&1 | grep -c silence_start
   ffmpeg -hide_banner -nostats -i "$IN" -af "pan=mono|c0=0.5*c0+0.5*c1,ebur128" -f null - 2>&1 | grep -E '^\s+I:' | tail -1
   ```

3. **기술 QC:** 통합 라우드니스·LRA, 트루피크(0 dBFS 이상이면 클리핑 위험), 긴 무음, DC 오프셋, 길이·포맷·채널, 모노 합산 차이(스테레오 대비 크게 줄면 위상·폭 확인), 끝맺음을 표로 적는다.
4. **조정 — 2패스 loudnorm:**

   ```bash
   # 1패스: JSON에서 input_i·input_tp·input_lra·input_thresh·target_offset을 얻는다
   ffmpeg -hide_banner -nostats -i "$IN" -af loudnorm=I=-14:TP=-1.0:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p'
   # 2패스: measured_I=input_i, measured_TP=input_tp, measured_LRA=input_lra, measured_thresh=input_thresh, offset=target_offset
   ffmpeg -n -hide_banner -i "$IN" -af "loudnorm=I=-14:TP=-1.0:LRA=11:measured_I=${MI}:measured_TP=${MTP}:measured_LRA=${MLRA}:measured_thresh=${MT}:offset=${OFF}:linear=true:print_format=json" -ar 48000 -c:a pcm_s24le "$OUT_DIR/<제목> - master -14LUFS.wav" 2>&1 | sed -n '/^{/,/^}/p'
   ```

   셸 변수는 `${OFF}:linear=true`처럼 중괄호로 쓴다(zsh는 `$OFF:l…`을 변수 수식어로 해석한다).

   **2패스 JSON의 `normalization_type`을 반드시 본다.** 선형 이득만으로 트루피크 목표를 못 맞추면(원본 TP가 높을 때) loudnorm은 조용히 `dynamic`으로 바뀌어 다이내믹을 압축한다(2026-11-12 실측: LRA 9.9→7.8). 이때는 그 파일을 쓰지 않고 다이내믹을 보존하는 방식으로 다시 만든다.

   ```bash
   # 선형 이득(목표 LUFS - 측정 LUFS) + 4배 오버샘플링 피크 리미터
   ffmpeg -n -i "$IN" -af "volume=<이득>dB,aresample=192000,alimiter=limit=0.85:attack=1:release=60:level=false,aresample=48000" -ar 48000 -c:a pcm_s24le "$OUT_DIR/<제목> - master -14LUFS.wav"
   ```

   실측 예: -12.9 LUFS·TP +0.2 원본에 `volume=-1.05dB` + 리미터 → -14.0 LUFS, TP -1.4 dBTP, LRA 원본과 같음. 두 결과의 LRA를 비교해 원본에 가까운 쪽을 고르고 이유를 보고한다. EQ·압축 같은 음색 처리는 사용자가 원하고 청취로 확인할 수 있을 때만 한 번에 하나씩 한다.
5. **재측정:** 결과 파일로 2단계를 다시 실행하고 목표 대비 차이를 기록한다.
6. **내보내기:** 마스터 MP3는 마스터 WAV에서 만든다(`ffmpeg -n -i "<제목> - master -14LUFS.wav" -c:a libmp3lame -b:a 320k "<제목> - master -14LUFS.mp3"`). MP3로 바꾸면 피크가 조금 오를 수 있으니 MP3도 다시 잰다. 아티스트·앨범 태그가 필요하면 ffmpeg `-metadata`로 넣는다. Road Music `song:export`(`--output FILE.mp3|.wav`)·`album:export`(`--output DIR`)는 **곡 폴더의 원본 오디오**를 복사·변환하므로 마스터 내보내기가 아니다. 원본 내보내기로만 쓰고 기존 파일은 `--overwrite`를 요청받았을 때만 덮어쓴다.
7. **앨범 일관성(여러 곡):** 곡별 통합 라우드니스 차이가 크면(예: 2 LU 이상) 맞추되, 의도된 조용한 곡은 사용자 확인 후 유지한다.
8. **제작 기록:** 같은 곡의 `requestId`·`groupId`(곡 `song:detail`의 기록 또는 생성 응답)에 `production:task-start`(`taskType:"mastering"`, `engine:"ffmpeg"`) → `production:task-finish`(`files`에 마스터 경로 `role:"final"`, 원본 `role:"input"`)로 남긴다. 그래야 `yue-project-status`가 마스터 존재를 안다. 기록하지 못했으면 보고에 적는다.

## 보고

```text
## 마스터링 결과
| 곡 | 원본 경로 | 결과 경로 | 원본 LUFS/TP/LRA | 결과 LUFS/TP/LRA | 형식 | QC 문제 |
- 원본 보존: 예(해시 비교)
- 방식: loudnorm Linear / Dynamic(미채택) / 이득+리미터 — 이유
- 모노 합산 차이: 원본 대비
- 청취: 미실행 / 실행(범위)
- 제작 기록: mastering 작업으로 기록함 / 미기록(사유)
```
