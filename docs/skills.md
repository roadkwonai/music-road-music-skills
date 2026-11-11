# 스킬 레퍼런스

[README](../README.md) · [작업 흐름](workflow.md) · [원본 대응표](upstream-coverage.md)

14개 스킬 모두 [공통 규칙](../skills/yue-music/references/common-rules.md)을 따른다. "CLI"는 주로 쓰는 Road Music 명령이며, **로컬**은 서비스 없이 실행되고 **서비스**는 Road Music 백그라운드 서비스를 시작한다.

## 진입

### `yue-music` — YuE2 음악 제작

- **언제:** YuE2·YuE MLX 곡 요청이면 항상 여기서 시작한다. Suno 프롬프트를 옮길 때도.
- **하는 일:** 요청 모드 판정, 엔진 유지, 단계별 스킬 연결, 필수 출력 골격(검수·보정 보고·끝맺음 질문) 제공.
- **참고 문서:** [공통 규칙](../skills/yue-music/references/common-rules.md), [CLI 연결](../skills/yue-music/references/road-music-cli.md), [보고 형식](../skills/yue-music/references/report-template.md), [Suno→YuE2 대응표](../skills/yue-music/references/suno-to-yue2.md).
- **원본:** session-start·help·next-step의 길잡이 역할.

## 창작

### `yue-lyric-writer` — 작사

- **언제:** 가사를 새로 쓰거나 허용된 범위를 개사할 때. 사용자가 완성 가사를 줬으면 쓰지 않는다.
- **핵심:** 부를 말 + `[Verse]`·`[Chorus]` 등 구간 태그만. 괄호·발음 표기·화자 표시·무대 지시 금지. 장면으로 보여주기, 절/후렴 대비, 절-후렴 반복 피하기, 2절 전진, 제목은 가사 안에.
- **CLI:** `song:prepare`(로컬, 정리본 확인).
- **원본:** lyric-writer, lyric-refiner.

### `yue-style-engineer` — style·옵션

- **언제:** style·`parts`·`cot`·`seed`·`abc`를 정할 때, `officialGuide` advice를 고칠 때, Suno 스타일 프롬프트를 바꿀 때.
- **핵심:** 장르·악기·보컬·언어·템포를 짧은 쉼표 태그로(기본 배열: 언어, 장르, 보컬, 악기, 선율·프레이징, BPM). 긍정형 묘사 권장, 명령문·실존 가수명 금지, 태그 10단어 이하, 기본값 유지. `parts.strict`·`strong`·`structure`·`instrumental`의 실제 효과를 알고 쓴다.
- **CLI:** `song:prepare`, `yue:capabilities`(로컬).
- **원본:** suno-engineer.

### `yue-album-planner` — 앨범 기획

- **언제:** 여러 곡을 묶어 만들 때.
- **핵심:** 곡마다 장면·감정 하나, 에너지·템포 배치, 곡별 별도 요청 JSON, 한 번에 한 곡씩 제출.
- **원본:** album-conceptualizer.

## 검수·관문

### `yue-lyric-reviewer` — 제목·가사 검수

- **언제:** 생성 전, 가사가 바뀔 때마다.
- **핵심:** 14항목(제목, 문장, 전곡 내용, 장면, 가창 문구, 반복 위치, YuE2 계약, 구조, 절-후렴 반복, 발음 위험, AI 투, 분량, 노골적 표현, 차용). 한국어가 없는 항목은 해당 없음. 원문은 수정안만.
- **원본:** lyric-reviewer, pronunciation-specialist, voice-checker, explicit-checker.

### `yue-pre-generation-check` — 생성 전 관문

- **언제:** 생성·렌더·리플레이 직전, "생성 준비해줘", "이대로 만들어줘".
- **핵심:** G0~G10 관문, `song:prepare` 2회(보정 전후), 기본값·runtime 확인, 서비스 명령은 생성 준비 단계에서만, 모드별 승인, `song:generate`→`job:wait`.
- **CLI:** `song:prepare`·`yue:capabilities`·`cli:schema`(로컬), `engines:list`·`lyrics:clean`·`lyrics:check`·`prompt:compose`(서비스), `song:generate`·`job:wait`(생성).
- **원본:** pre-generation-check.

### `yue-result-review` — 결과 검수·재제작 판단

- **언제:** 생성이 끝난 뒤, "검수해줘", "다시 만들까?".
- **핵심:** `truncated.abc`·`truncated.semantic`, 실제 길이·포맷, 전곡 무유도 전사와 문맥 구간 재검사, 직접 청취 여부 구분, 효율 기준·미세 발음 기준, 악보 선택.
- **원본:** Regeneration Workflow, error-recovery.

## 악보·조사·후처리

### `yue-score-editor` — 악보 편집·커버

- **언제:** 화성·멜로디·형식 수정, 선율 보존 편집, 악보 기반 커버, 악보 내보내기.
- **핵심:** 보존 계약 4종, 원본 보존·사본 편집, `score:inspect`·`score:compare`, 악보만 바꾸면 `song:render`, 가사·style도 바꾸면 새 prepare→generate, 커버는 SheetSage2 → 코드 제거 → `cot:"melody"`.
- **원본:** sheet-music-publisher, Suno Song Editor·Cover·Persona 흐름.

### `yue-research` — 자료 조사·출처 확인

- **언제:** 실화·다큐·역사·인물·사건·유행을 다루는 곡.
- **핵심:** 1차 자료 우선, 핵심 사실 2곳 이상 교차 확인, 링크·날짜 기록(`SOURCES.md`·`RESEARCH.md`), 사람 확인 전 생성 차단.
- **원본:** researcher, researchers-*(10종), document-hunter, verify-sources.

### `yue-mastering` — 마스터링·납품

- **언제:** 완성 곡을 스트리밍·영상용으로 낼 때.
- **핵심:** 원본 보존, 완주한 곡만, ffmpeg 측정(ebur128·astats·silencedetect)과 2패스 loudnorm, 기본 -14 LUFS / -1 dBTP / 48kHz 24-bit WAV, 업샘플링을 품질 향상이라 하지 않음, 메타데이터 제거 금지.
- **원본:** mastering-engineer, mix-engineer(스템 처리는 제외).

### `yue-release` — 공개 준비

- **언제:** 유튜브·음원 배포·SNS 공개 전.
- **핵심:** YuE2 코드·모델 라이선스와 생성물 권리 구분, AI 생성 고지, 차용·노골적 표현 점검, 메타데이터·가사 파일·자막, 아트 브리프, 홍보 문구 초안. 게시는 사용자가 한다.
- **원본:** release-director, promo-writer, promo-reviewer, album-art-director, plagiarism-checker.

## 관리

### `yue-project-status` — 현황·이어 하기

- **언제:** "이어서", "어디까지 했지", "다음 뭐 해", 곡 이름을 말할 때.
- **핵심:** `songs:list`·`song:detail`·`production:*`로 읽고 다음 단계 하나를 추천, 진행 현황 표, 아이디어·프로젝트, 이름 변경.
- **원본:** resume, next-step, album-dashboard, album-ideas, promote-idea, new-album, rename, validate-album, import-*.

### `yue-skills-update` — 스킬 업데이트 확인

- **언제:** yue-* 스킬을 처음 쓸 때 자동(세션당 한 번, 12시간 캐시), "스킬 업데이트", "최신 버전이야?".
- **핵심:** `scripts/check-update.mjs`가 설치 `VERSION`·git 커밋과 GitHub 최신 Release·태그 커밋을 비교해 `status`(up-to-date / update-available / same-version-different-commit 등)를 낸다. 알림만 하고, 업데이트는 요청 시 git `pull --ff-only` 또는 Release ZIP 체크섬 확인 후 새 폴더 교체.
- **원본:** 없음(Road Music `cli:update:check` 대응).

### `yue-setup-check` — 환경 점검·안내

- **언제:** 세션 시작, "설정 확인", "도움말", "처음 써봐".
- **핵심:** Road Music 위치, Node, CLI 버전·업데이트 알림, 필수 도구, 엔진, YuE 지원 범위, 묶음 버전을 읽기 전용으로 점검.
- **원본:** session-start, setup, configure, health-check, help, tutorial, about.
