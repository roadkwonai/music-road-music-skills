---
version: 0.1.1
date: 2026-11-12
title: Music Road YuE2 Skills v0.1.1 — 실제 생성 감사 보완
---

# 0.1.1 — 실제 생성 감사 보완

스킬을 그대로 따라 실제 YuE2(`yue-mlx`) 곡을 만들며 절차를 감사했고, 그 과정에서 찾은 결함을 고쳤습니다.

## 감사에 쓴 실제 생성

- 요청: "성량 좋고 고음을 날카롭게 뽑아내는 여성 락보컬의 락발라드", 가사·프롬프트 전체 자동 위임.
- 곡: 「끝까지 부를게」, style `Korean, powerful rock ballad, powerful female rock vocal, bright piercing high belting, wide vocal range, …, melodic guitar solo, 76 BPM`, `cot:"full"`, seed 20261112, 기본 CFG·ODE, runtime 8bit.
- 생성 전: `song:prepare` valid · 공식 점검 advice 0, 한국어 자체 검수로 한 줄 수정, `lyrics:check` 추정에 맞춰 기타 솔로 구간 추가.
- 결과: 514초 만에 완료, 268.1초 48kHz stereo FLAC, `truncated.abc`·`truncated.semantic` 모두 false, -12.9 LUFS, 트루피크 +0.2 dBFS.
- 가사 반영: 로컬 Whisper large-v3-turbo(단일 계열) 무유도 전곡 전사에서 대부분 일치. 브리지·마지막 후렴은 30초 문맥 재검사로 확인. "객석"·"정류장"·"쥐면"·"떨리는"은 전사가 엇갈려 확인 필요로 남김. 직접 청취는 하지 않음.

## 고친 점

- **상태 확인이 서비스를 띄우던 문제:** 일반 `cli:status`는 Road Music 서비스를 시작합니다. 상태 확인을 `service:status`·`queue:list --no-start`로 바꿨습니다.
- **새 곡이 다른 프로젝트에 섞이던 문제:** 생성 전에 현재 프로젝트를 확인하고, 새 곡이면 `projects:create`→`projects:select`하는 단계를 관문에 넣었습니다.
- **제작 기록 중복:** `song:generate`의 `requestPrompt`가 요청 원문을 자동 기록하므로 별도 `production:request`를 쓰지 않습니다. 결과 검수는 같은 요청에 `review` 작업으로 연결합니다.
- **생성 실행 블록:** 프로젝트 선택·생성·`job:wait`을 한 블록으로 묶어 일부만 실행하거나 기록하지 않게 했습니다.
- **결과 검수:** 원본 `audio.flac`으로 검사(`audio` 필드는 MP3일 수 있음), 결과 필드(`seconds`·`timing`·`source`·`runtime`) 보고, 트루피크가 0 dBFS를 넘으면 마스터링 권고, 로컬 Whisper 무유도 전사·SRT 시각·30초 문맥 재검사 절차와 흔한 전사 착시("감사합니다", "자막 by …", 간주 구간 반복 루프)를 추가했습니다.
- **style 보컬 묘사 예:** 성량·고음 요청을 실존 가수 비교 없이 옮기는 표현을 추가했습니다.
- **길이 추정:** `lyrics:check`의 추정은 거친 참고값이라는 점을 실측(164초 추정 → 268초)으로 밝혔습니다.

## 검증

- `node --test tests/*.test.cjs` 통과, 예시 `song:prepare` 7/7.
- 같은 요청(생성 금지)으로 보완한 스킬을 재시험: Claude 19/19, Codex 19/19(테스트 하네스 문구 수정 후). 자세한 내용은 [테스트와 검증](https://github.com/roadkwonai/music-road-music-skills/blob/main/docs/testing.md).

## 설치 안내

- 저장소 링크 설치면 `git pull`로 바로 반영됩니다. Release 설치면 `MusicRoad-YuE2-Skills-0.1.1.zip`을 `SHA256SUMS.txt`로 확인한 뒤 교체합니다.

## 제한

- 고음의 날카로움·성량·발음은 청취로만 판단할 수 있으며, 이번 감사에서는 직접 청취를 하지 않았습니다.
- 생성된 음원·프로젝트는 Release 자산에 포함하지 않습니다.
