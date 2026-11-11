# 테스트와 검증

[README](../README.md) · [Codex에서 쓰기](codex.md) · [예시 검증 결과](../verification/RESULTS.md)

## 1. 정적 검사 (Road Music 없이)

```bash
node --test tests/*.test.cjs
```

| 테스트 | 확인하는 것 |
| --- | --- |
| `tests/bundle.test.cjs` | `manifest.json`·`VERSION`·스킬 폴더 일치, frontmatter(`name`=폴더, description 길이·YAML 안전), Codex `agents/openai.yaml`, 마크다운 상대 링크, zsh에서 깨지는 `$RM` 패턴 금지, 예시 요청의 금지 필드·엔진 명시·기대값 짝 |
| `tests/release.test.cjs` | 첫 버전·중복 태그·버전 불일치 판정, 허용 목록 ZIP·SHA256SUMS 생성, 작업 폴더 제외 |

GitHub Actions 릴리스 워크플로가 Release를 만들기 전에 이 검사를 돌린다.

## 2. 예시 요청 검증 (Road Music CLI 필요)

```bash
ROADMUSIC_DATA_DIR="$(mktemp -d)" node scripts/verify-examples.mjs --write verification/RESULTS.md
```

`examples/*.json`을 실제 `song:prepare`(로컬, 모델·서비스 없음)에 넣어 `valid:true`, 엔진 유지, `officialGuide` advice가 [`examples/expectations.json`](../examples/expectations.json)과 같은지 본다. 2026-11-12 결과는 7/7 일치다([결과](../verification/RESULTS.md)).

| 예시 | 보여주는 것 |
| --- | --- |
| `ko-ballad-yue-mlx.json` | 기본 배열 style + `bpm` 필드 |
| `ko-trot-parts-yue-mlx.json` | style 없이 `parts`만 |
| `en-pop-yue-windows.json` | Windows용 `engine:"yue"`, `cot:"melody"` |
| `instrumental-yue-mlx.json` | `instrumental:true`(가사 생략) |
| `ko-melody-abc-yue-mlx.json` | 코드 없는 ABC + `cot:"melody"`, `Q:`와 style BPM 일치 |
| `suno-style-before.json` | Suno식 입력 그대로 → 의도된 advice 5개 |
| `suno-style-after.json` | 대응표대로 변환 → advice 0 |

## 3. 시나리오 테스트 (skill-creator 방식)

실제 사용자가 할 만한 요청 4가지를 에이전트에게 주고, 응답·명령 기록·요청 JSON을 [`evals/grade.py`](../evals/grade.py)로 채점했다. 채점기는 최종 요청 JSON을 `song:prepare`에 다시 넣어 `valid`·엔진·advice를 직접 확인하고, 마스터링 결과는 ffmpeg로 LUFS·트루피크를 다시 잰다. 모든 테스트는 음악 생성·설치를 금지하고 `ROADMUSIC_DATA_DIR`를 분리했다.

| # | 요청 | 주로 보는 것 |
| --- | --- | --- |
| 1 | Suno 프롬프트·가사를 YuE MLX로, 원문은 그대로, 생성하지 말 것 | 원문 보존, Suno 전용 설정 "대응 없음", 긍정형 style, 주석·수식어 태그 보정안, advice 0 |
| 2 | 한국어 여성 락발라드 1곡, 가사는 AI가 | 기본 검토 모드(승인 질문), 한국어 검수 판정, style 언어 우선, 길이 비보장 |
| 3 | Windows `yue`, 사용자 가사 그대로, 전부 자동 생성, 정확히 3분 | 엔진 유지, 사용자 가사 무단 수정 금지, 3분 비보장, 생성 명령 기록 |
| 4 | YuE 곡 파일을 -14 LUFS로 마스터링, 원본 유지 | 원본 해시 불변, 결과 -14±0.5 LUFS·TP ≤ -1, 측정 표, 미청취 명시 |

### Claude Code

| 회차 | 구성 | 통과 | 평균 시간 | 평균 토큰 |
| --- | --- | --- | --- | --- |
| 1차 | 초기 스킬(요청 1~3) | 45/45 (100%) | 62초 | 109k |
| 1차 | 스킬 없이 Road Music 문서만(요청 1~3) | 44/45 (98%) | 105초 | 140k |
| 2차 | 보완한 스킬(요청 1~4) | 53/53 (100%) | 76초 | 117k |

1차에서 스크립트 채점 점수는 스킬 유무로 거의 차이가 없었다. Road Music 저장소의 AGENTS.md·가이드가 이미 강하기 때문이다. 차이는 시간(-40%)·토큰(-22%)과 응답 내용에서 나왔다. 응답을 읽고 찾은 문제와 보완:

- 스킬 사용 쪽이 `prompt:compose`·`lyrics:check`를 빠뜨림 → 생성 준비 단계 절차에 추가(단, 서비스 명령임을 표시).
- 근거 없는 수치(설치 "약 10GB", "8~20분 소요", 모델 라이선스 혼동)를 씀 → "확인한 사실만 쓰기" 규칙.
- 자체 한국어 검수가 후함(모호한 장면 「컵이 식어 가는 밤」 통과) → 장면 점검 항목과 "약한 줄 두 개 근거 대기" 절차.
- 가사가 여러 언어인데 style 언어를 하나만 씀 → 부르는 언어를 모두 쓰도록.

### Codex (codex-cli 0.167.0, 기본 모델)

| 회차 | 구성 | 통과 | 평균 시간 |
| --- | --- | --- | --- |
| 1차 | 보완 중간본(요청 1~3) | 34/45 (76%) | 102초 |
| 2차 | 필수 출력 골격 추가(요청 1~4) | 48/53 (91%) | 125초 |
| 3차 | 보내기 전 자체 점검 추가(요청 1~2 재실행) | 28/30 (93%) | 106초 |
| 4차 | 하네스 문구만 바로잡아 요청 2 재실행 | 15/15 (100%) | 95초 |

Codex는 참고 문서를 덜 열고 SKILL.md 본문 위주로 따른다. 1차에서 보고서 표 머리글, 승인 질문, 검수 판정어가 빠졌고, "원문은 건드리지 말라"를 "보정안 JSON도 만들지 말라"로 읽었다. 필수 출력 골격(원문판·보정판 JSON 두 개 포함)을 `yue-music` 본문에 넣자 대부분 해결됐다. 2차에 남은 `근거`/`공식 근거` 열 이름 축약은 "보내기 전 자체 점검"으로 해결됐다(3차). 3차 요청 1에 남은 1건은 원문에 BPM이 없어 임의로 정하지 않고 `유지(미지정)`로 보고한 `style-tempo` 권고로, 규칙상 정상 처리다. 요청 2의 마지막 승인 질문 누락은 스킬이 아니라 테스트 하네스의 "질문으로 되묻지 말 것" 문구를 Codex가 최종 승인 질문 금지로 읽은 탓이었고, 문구를 "작업 도중 멈추지 말 것"으로 고치자 정확한 질문으로 끝났다(4차).

채점 기준은 회차를 거치며 엄격하게 고쳤다(예: 승인 질문은 `생성할까요?` 문구 필수). 표의 모든 회차는 최종 채점기로 다시 채점한 값이다.

## 4. 독립 검토

제 결론을 모르는 별도 에이전트에게 스킬 파일과 기준 문서(공식 원문·Road Music 문서·CLI 코드)만 주고 한 줄씩 대조하게 했다. 23건(높음 2·중간 10·낮음 11)을 찾았고 모두 반영했다. 주요 항목:

- `lyrics:clean`·`prompt:compose`·`engines:list` 등이 서비스를 시작하는 명령인데 "로컬"이라고 쓴 오류 → 로컬/서비스 명령 표, 초안 단계는 `song:prepare`만.
- `parts.strict`가 style에 부정문 목록을 붙이고 `strict`+`strong`이면 CFG가 1.5가 되는 점 누락 → 명시.
- 비한국어 가사의 검수 처리, 지정 수정·재생성·수정만 모드, 승인 후 의미 변경 재검토 누락 → 추가.
- 공식 사실과 Road Music 규칙 혼동(공식 예시에도 `no guitar`가 있음) → 구분 표기.
- `ok:false`(입력 거부)와 `valid:false`(태그 삭제) 두 실패 경로, `targetSeconds` 20~360, `cot:"off"`+`plan` 불가 → 명시.

## 5. 테스트 중 발견한 실제 결함

- **zsh에서 `$RM` 호출이 깨짐:** `RM="node …"; $RM cmd`는 zsh가 단어로 나누지 않아 실행되지 않았다. macOS 기본 셸이자 Claude Code·Codex 셸이다. 모든 스킬을 `roadmusic()` 함수로 바꾸고 정적 테스트로 막았다.
- **시험 서비스가 남음:** 서비스 명령이 임시 데이터 폴더로 Road Music 서비스를 띄운 뒤 남았다. 모두 정리했고, 규칙에 "같은 `ROADMUSIC_DATA_DIR`로 `cli:stop`"을 넣었다.
- **ffmpeg 2패스 명령의 zsh 함정:** `$OFF:linear`가 변수 수식어로 해석됐다. `${OFF}`로 안내.

## 결과 파일

시나리오 테스트 산출물(`yue-music-workspace/`)은 개인 작업 기록이라 저장소와 Release에 넣지 않는다(`.gitignore`). 채점기·요청 목록은 [`evals/`](../evals/)에 있다.
