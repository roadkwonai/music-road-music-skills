# 문제 해결

[README](../README.md) · [시작하기](getting-started.md) · [Codex에서 쓰기](codex.md)

| 증상 | 원인 | 해결 |
| --- | --- | --- |
| `no such file or directory: node /…/road-music.js` | zsh는 `RM="node …"; $RM cmd`처럼 변수에 넣은 명령을 단어로 나누지 않는다 | 셸 함수를 쓴다: `roadmusic() { node "${ROAD_MUSIC_HOME:-…}/cli/road-music.js" "$@"; }` |
| `song:prepare`가 `ok:false`, `INVALID_ARGUMENT` | 입력 자체가 거부됨 | 메시지대로 고친다: YuE `targetSeconds` 20~360, `cot:"off"`에 `abc`·`mode:"plan"` 불가, `instruments`와 `instrumentation` 동시 사용 불가, 가사도 `instrumental`도 없음 |
| `ok:true`인데 `valid:false` | 10단어 넘는 style 태그가 삭제됨 | 태그를 짧게 나누고 `changes.style.dropped` 확인 |
| `engine`을 안 썼더니 ACE로 준비됨 | CLI 기본 엔진은 `ace` | 요청 JSON에 `"engine":"yue-mlx"` 또는 `"yue"`를 항상 쓴다 |
| style에 `Korean`·`120 BPM`·`no vocals…`가 자동으로 붙음 | Road Music 조합기 동작(한글 가사면 Korean, `bpm` 필드면 BPM, 연주곡이면 무보컬 문구) | 정상. 보고만 하고 원문 변경으로 보지 않는다 |
| `parts.strict`를 켰더니 style에 부정문이 길게 붙음 | strict는 "나열한 악기만" 목록을 붙인다 | 사용자가 편성 고정을 원할 때만 쓰고 보고서에 밝힌다. `strong`까지 켜면 CFG 1.5(실험) |
| 연주곡인데 준 가사가 사라짐 | `instrumental:true`는 가사를 골격으로 바꾼다 | 연주곡은 `lyrics`를 생략하고 필요하면 `parts.structure` |
| `score:check`가 "실행 환경이 없어" 실패 | YuE 런타임이 필요한 서비스 명령 | 오프라인 `score:inspect`·`score:compare`를 쓰고 `미실행(사유)` 보고 |
| `engines:list`에서 미설치로 나옴 | 임시 `ROADMUSIC_DATA_DIR`나 다른 프로필로 조회함 | 사용자 실제 프로필로 다시 읽는다. 설치는 요청이 있을 때만 |
| 검사 뒤 Electron 프로세스가 남음 | `lyrics:clean`·`engines:list` 같은 서비스 명령이 서비스를 시작함 | 같은 `ROADMUSIC_DATA_DIR`로 `roadmusic cli:stop`. 초안 단계에서는 로컬 명령(`song:prepare`)만 쓴다 |
| `job:wait`이 시간 초과 | 생성이 오래 걸림 | 같은 `jobId`로 다시 기다린다. 새로 제출하지 않는다 |
| 응답에 `uncertain:true` | 연결이 끊겨 제출 여부가 불확실 | `service:status`·`queue:list --no-start`·`songs:list`로 확인 후 판단. 자동 재제출 금지 |
| 상태만 보려 했는데 서비스가 뜸 | 일반 `cli:status`는 서비스를 시작한다 | `service:status` 또는 `--no-start`를 붙인다 |
| 새 곡이 다른 프로젝트 폴더에 저장됨 | 앱에서 마지막으로 선택한 프로젝트에 저장된다 | 생성 전 `projects:create`→`projects:select`로 새 프로젝트를 선택한다 |
| 곡이 생각보다 짧음 | 길이는 가사 분량과 자연 종료가 정함 | `truncated` 확인. 길이를 원하면 가사 분량을 조정(사용자 가사는 제안만) |
| 괄호 안 말이 그대로 불림 | 가사 주석은 제어 채널이 아님 | 가사에서 주석을 빼고 의도는 style로 |
| ffmpeg `Unable to parse "offset" option value "0.03inear=true"` | zsh가 `$OFF:l…`을 변수 수식어로 해석 | `${OFF}:linear=true`처럼 중괄호 |
| Codex가 스킬을 못 찾음 | 링크 위치가 다름 | `${CODEX_HOME:-~/.codex}/skills/yue-*` 링크 확인. `codex exec`에서 "yue- 스킬 목록" 질문으로 확인 |
