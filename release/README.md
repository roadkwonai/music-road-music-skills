# 릴리스 노트

각 GitHub Release는 `release/YYYY-MM-DD-title.md` 노트와 같은 버전을 사용합니다. 최신 묶음 버전은 루트의 `VERSION`과 `manifest.json`, 그리고 [GitHub Releases](https://github.com/roadkwonai/music-road-music-skills/releases)에서 확인합니다. 스킬을 쓸 때 `yue-skills-update`가 최신 Release를 확인해 알려 줍니다.

| 버전 | 날짜 | 노트 |
| --- | --- | --- |
| 0.1.0 | 2026-11-12 | [YuE2 음악 스킬 묶음 0.1.0](2026-11-12-yue2-music-skills-0-1-0.md) |

**버전 정책:** 실제 배포·정식 릴리스 전까지 버전은 `0.1.0`으로 유지하며, 그 사이의 수정은 같은 `0.1.0`을 다시 게시합니다(2026-11-12 사용자 결정). 이때 git 설치본은 `yue-skills-update`가 태그 커밋으로 새 게시를 구분하고, ZIP 설치본은 Release 날짜와 `SHA256SUMS.txt`로 확인합니다. 정식 릴리스부터는 새 버전·새 태그·새 노트만 사용합니다.

철회한 이전 노트(v0.1.1, v0.1.2)는 [보관 기록](../docs/release-history/)에서 볼 수 있습니다.

## 새 릴리스 만드는 법

1. 정식 릴리스 전에는 `0.1.0`을 유지한다. 재게시할 때는 기존 `v0.1.0` Release와 태그를 지운 뒤 같은 태그로 다시 push한다. 정식 릴리스부터는 `VERSION`과 `manifest.json`의 `version`을 한 단계 올린다.
2. `release/YYYY-MM-DD-title.md` 노트 하나의 frontmatter(`version`·`date`·`title`)를 현재 버전에 맞추고 `manifest.json`의 `releaseNotes`가 가리키게 한다.
3. `node --test tests/*.test.cjs`, Road Music이 있으면 `node scripts/verify-examples.mjs --write verification/RESULTS.md`.
4. 커밋 후 태그 `vX.Y.Z`를 push하면 `.github/workflows/release.yml`이 검사·ZIP·SHA256SUMS를 만들고 Latest Release로 게시한다.
