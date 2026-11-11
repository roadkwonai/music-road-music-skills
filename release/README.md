# 릴리스 노트

각 GitHub Release는 `release/YYYY-MM-DD-title.md` 노트와 같은 버전을 사용합니다. 최신 묶음 버전은 루트의 `VERSION`과 `manifest.json`, 그리고 [GitHub Releases](https://github.com/roadkwonai/music-road-music-skills/releases)에서 확인합니다.

| 버전 | 날짜 | 노트 |
| --- | --- | --- |
| 0.1.0 | 2026-11-12 | [YuE2 음악 스킬 묶음 첫 릴리스](2026-11-12-yue2-music-skills-0-1-0.md) |

## 새 릴리스 만드는 법

1. `VERSION`과 `manifest.json`의 `version`을 한 단계 올린다(0.1.0 → 0.1.1 / 0.2.0 / 1.0.0).
2. `release/YYYY-MM-DD-title.md`를 하나 쓰고 frontmatter에 `version`·`date`·`title`을 넣는다. `manifest.json`의 `releaseNotes`가 이 파일을 가리키게 한다.
3. `node --test tests/*.test.cjs`, Road Music이 있으면 `node scripts/verify-examples.mjs --write verification/RESULTS.md`.
4. 커밋 후 태그 `vX.Y.Z`를 push하면 `.github/workflows/release.yml`이 검사·ZIP·SHA256SUMS를 만들고 Latest Release로 게시한다.
5. 이미 있는 태그·Release는 덮어쓰지 않는다.
