---
name: yue-result-review
description: Road Music YuE2(yue-mlx/yue) 생성 완료 후 결과를 검수하고 재제작 여부를 판단한다. result.json truncation·실제 길이·포맷 확인, 가사 반영의 무유도 전사와 직접 청취 구분, 악보 선택(score-choice), 효율 기준(retry-value)에 따른 재시도 추천을 적용한다. Reviews finished YuE2 songs and decides whether a retry is worthwhile.
---

# YuE2 결과 검수·재제작 판단

원본의 Regeneration Workflow·error-recovery를 대체한다(Suno의 "비결정적이니 다시 돌려보기"를 기본으로 삼지 않는다). [공통 규칙](../yue-music/references/common-rules.md)을 적용한다. 근거: Road Music `docs/yue-prompt-guide.md#verification`, `#lyrics-verification`, `#score-choice`, `docs/music-review.md#retry-value`, `#micro-pronunciation`, `#delivery`.

## 1. 기술 검사

1. `job:wait` 결과와 `songs:list`/`song:detail`의 절대 경로로 실제 파일을 찾는다.
2. 실제 worker의 엔진·모델/VAE·runtime, 요청/정리/전달 가사, style·cot·seed·실효 설정을 승인안과 대조한다.
3. `result.json`의 `status`와 **`truncated.abc`·`truncated.semantic`을 각각** 확인한다. 둘 중 하나라도 참이면 재생 가능해도 완주로 채택하지 않는다.
4. 실제 길이·포맷(48kHz stereo)·전체 디코딩·끝맺음. `targetSeconds`와 실제 길이를 나란히 적는다(차이는 정상일 수 있음).
5. 원본 FLAC·악보·artifact를 보존한다. MP3는 별도 납품 변환.

## 2. 가사 반영 (가사가 있는 곡)

- 승인된 가사와 실제 native 요청을 먼저 비교한다. 불일치면 전달·정리·잘림부터 조사한다.
- 로컬 ASR이 있을 때만 **전곡 무유도** 전사(참고 가사를 prompt·grammar로 주지 않음). 가능하면 다른 계열 모델 두 개, 하나면 단일 모델이라고 적는다. 같은 계열 두 개는 독립 증거가 아니다. 도구가 없으면 `확인 불가`. 음성 모델을 임의 설치하거나 음원을 외부로 보내지 않는다.
- 비교에서 정규화한 항목(태그·공백 등)을 기록하고 원문·원시 전사를 보관한다. 조사·어미·부정어를 지우거나 환각성 말미를 잘라 일치율을 높이지 않는다. 문자 일치율·CER은 전사 문자열 비교이지 가창 오류율·음질 점수가 아니다.
- 가사가 있는 구간이 전사에서 빠지면 현재 악보의 해당 구간도 본다(예: Intro/Outro의 Vocal이 모두 쉼표이거나 구간 자체가 없음). ASR만으로 누락을 확정하거나 가사를 지워 맞추지 않는다.
- 새 악보 실행 여부는 native 요청의 외부 ABC 부재, `plan.request.abc`, planner 로그를 함께 본다. **악보 해시가 다르다는 것만으로 새 계획 실행을 증명하지 않고**, 같다는 것만으로 재사용이라 단정하지 않는다.
- 바뀐 구절은 새 음원에서 위치를 찾고, 앞뒤 문맥(약 30초를 출발점)으로 재전사한다. 짧은 클립의 엉뚱한 결과는 가창 실패로 단정하지 않는다. 유리한 결과만 골라 통과시키지 않는다.
- 판정을 나눈다: 입력·보존 / 악보 생성·재사용 / 파일 기술 검사 / 자동 전사상 확인 / 엇갈림·확인 필요 / 확인 불가·해당 없음 / 직접 청취(미실행이면 그렇게).
- 한국어 내용의 자연스러움과 음원 전달 충실도는 별개 판정이다.

연주곡은 Vocal 쉼표·`instrumental:true`가 무보컬을 보장하지 않으므로 보컬 누출을 청취로 확인해야 한다(못 했으면 미청취).

## 3. 재제작 판단

추가 생성을 권하기 전에 Road Music `docs/music-review.md#retry-value`를 적용한다.

| 상황 | 추천 |
| --- | --- |
| 입력 누락·잘림(truncated)·잘못된 악보·실행 실패 등 **확인된 기술 원인** | 그 원인을 고친 재제작(승인·위임 범위 안, 원인 하나씩) |
| ASR만의 불일치, 직접 청취 미실행 | 판별 검사 우선. 전사 100%를 맞추려는 개사·전곡 재생성을 기본 추천하지 않음 |
| 한 음절·받침·어미만의 발음 | 미세 교정을 위한 전곡 재생성을 기본 추천하지 않음(`#micro-pronunciation`) |
| 반복 회귀, 새 원인 없음 | 추가 재제작은 비효율이라고 설명하고 가장 안정적인 후보 유지를 추천 |
| 사용자가 한계를 알고 특정 실험을 명시 | 그 범위에서만 실행. 결과를 다음 실험의 자동 승인으로 쓰지 않음 |

가사 수정 재제작의 악보 선택(`#score-choice`):

- 가사 전달 우선 + 선율 고정 요구 없음 → 외부 `abc` 없이 `cot:"full"`로 새 계획(새 `song:prepare`→`song:generate`).
- 원곡 선율·제공 ABC 보존을 명시 → 원 ABC 사본과 새 가사의 호흡을 대조해 재사용.
- `song:render`는 기존 원문(가사·style)을 재사용하므로 **수정 가사 전달에 쓰지 않는다.** 악보만 바꿀 때 쓴다.
- 새 seed·CFG·ABC로 바꾸는 것 자체를 새 해결책처럼 이어 붙이지 않는다.

권장 방법 하나와 이유·남은 불확실성을 먼저 제시한다. 실행은 승인 범위에서 `yue-pre-generation-check`를 다시 거친다. "안정 후보 유지·추가 재제작 비추천·남은 발음 미확인"도 정상 종료 결론이다.

## 4. 결과 보고

[보고 형식](../yue-music/references/report-template.md#생성-후-결과-보고)의 표에 따라 실제 경로, 전달 가사, 최종 style, 요청 JSON, seed, 실효 옵션, 길이·truncation, 전사·청취 구분, 한국어 검수 결과, `## YuE2 공식 가이드 보정 보고`를 포함한다. 청취하지 않은 음색·발음·편곡 품질을 평가하지 않는다.
