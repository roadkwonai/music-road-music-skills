#!/usr/bin/env node
// music-road-music-skills 업데이트 확인(읽기 전용). Road Music CLI의 cli:update:check처럼
// 설치본 버전과 GitHub 최신 Release를 비교해 stdout에 JSON 한 줄을 낸다. 아무것도 설치하지 않는다.
// 사용: node check-update.mjs [--force] [--offline]
import { existsSync, mkdirSync, readFileSync, realpathSync, writeFileSync } from 'node:fs'
import { execFileSync } from 'node:child_process'
import { homedir } from 'node:os'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const REPO = 'roadkwonai/music-road-music-skills'
const TTL_MS = 12 * 60 * 60 * 1000
const args = new Set(process.argv.slice(2))
// 심볼릭 링크로 설치돼도 실제 묶음 루트(skills/<이름>/scripts의 두 단계 위)를 찾는다.
const root = join(dirname(realpathSync(fileURLToPath(import.meta.url))), '..', '..', '..')
const cacheDir = join(process.env.XDG_CACHE_HOME || join(homedir(), '.cache'), 'music-road-music-skills')
const cacheFile = join(cacheDir, 'update-check.json')

const valid = v => /^\d+\.\d+\.\d+$/.test(v || '')
const cmp = (a, b) => { const x = a.split('.').map(Number); const y = b.split('.').map(Number); return x[0] - y[0] || x[1] - y[1] || x[2] - y[2] }
const read = f => { try { return readFileSync(f, 'utf8') } catch { return null } }

function local () {
  const version = (read(join(root, 'VERSION')) || '').trim() || null
  const git = existsSync(join(root, '.git'))
  let commit = null
  if (git) { try { commit = execFileSync('git', ['-C', root, 'rev-parse', 'HEAD'], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).trim() } catch {} }
  return { root, version, installMode: git ? 'git' : version ? 'release' : 'unknown', commit }
}

async function remote () {
  const get = async url => {
    const r = await fetch(url, { headers: { Accept: 'application/vnd.github+json', 'User-Agent': 'music-road-music-skills-update-check' }, signal: AbortSignal.timeout(8000) })
    if (!r.ok) throw new Error(`GitHub API ${r.status}`)
    return r.json()
  }
  const rel = await get(`https://api.github.com/repos/${REPO}/releases/latest`)
  const tag = rel.tag_name
  let tagCommit = null
  try { tagCommit = (await get(`https://api.github.com/repos/${REPO}/commits/${encodeURIComponent(tag)}`)).sha } catch {}
  return { latest: tag?.replace(/^v/, '') || null, tag, tagCommit, releaseUrl: rel.html_url, publishedAt: rel.published_at, title: rel.name, notes: (rel.body || '').slice(0, 1200) }
}

const loc = local()
let rem = null; let fromCache = false; let error = null
const cached = (() => { try { return JSON.parse(read(cacheFile)) } catch { return null } })()
if (!args.has('--force') && cached && Date.now() - cached.checkedAt < TTL_MS) { rem = cached.remote; fromCache = true }
else if (args.has('--offline')) { rem = cached?.remote || null; fromCache = Boolean(rem); error = rem ? null : 'offline' }
else {
  try { rem = await remote(); mkdirSync(cacheDir, { recursive: true }); writeFileSync(cacheFile, JSON.stringify({ checkedAt: Date.now(), remote: rem })) }
  catch (e) { error = String(e.message || e); rem = cached?.remote || null; fromCache = Boolean(rem) }
}

let status = 'unknown'
if (!valid(loc.version)) status = 'local-version-unknown'
else if (!rem || !valid(rem.latest)) status = error ? 'check-failed' : 'no-release'
else if (cmp(rem.latest, loc.version) > 0) status = 'update-available'
else if (cmp(rem.latest, loc.version) < 0) status = 'local-newer'
// 같은 번호의 재배포(예: 0.1.0 유지 기간)는 git 설치본에서만 커밋으로 구분할 수 있다.
else if (loc.installMode === 'git' && rem.tagCommit && loc.commit && rem.tagCommit !== loc.commit) {
  // 태그 커밋이 이미 로컬 기록에 포함돼 있으면(개발 중인 체크아웃) 최신으로 본다.
  let contained = false
  try { execFileSync('git', ['-C', root, 'merge-base', '--is-ancestor', rem.tagCommit, 'HEAD'], { stdio: 'ignore' }); contained = true } catch {}
  status = contained ? 'local-ahead' : 'same-version-different-commit'
}
else status = 'up-to-date'

console.log(JSON.stringify({ ok: true, status, available: status === 'update-available' || status === 'same-version-different-commit', current: loc.version, ...loc, latest: rem?.latest ?? null, tag: rem?.tag ?? null, tagCommit: rem?.tagCommit ?? null, releaseUrl: rem?.releaseUrl ?? null, publishedAt: rem?.publishedAt ?? null, title: rem?.title ?? null, notes: rem?.notes ?? null, fromCache, error }))
