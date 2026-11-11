'use strict'
const assert = require('node:assert/strict')
const fs = require('node:fs/promises')
const path = require('node:path')
const os = require('node:os')
const { test } = require('node:test')
const { spawnSync } = require('node:child_process')
const { verifyReleaseVersion } = require('../scripts/release-version.cjs')

const NOTE = 'release/2026-11-12-first-release.md'
async function fixture () {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'yue2-skills-release-test-'))
  await fs.mkdir(path.join(root, 'release'))
  await fs.writeFile(path.join(root, 'VERSION'), '0.1.0\n')
  await fs.writeFile(path.join(root, 'manifest.json'), JSON.stringify({ schemaVersion: 1, name: 'music-road-music-skills', version: '0.1.0', releaseNotes: NOTE, skills: [{ id: 'yue-music', path: 'skills/yue-music' }] }))
  await fs.writeFile(path.join(root, NOTE), '---\nversion: 0.1.0\ndate: 2026-11-12\ntitle: First release\n---\n\nnotes\n')
  return root
}

test('첫 버전을 받아들이고 중복 태그·건너뛴 버전을 거부한다', async () => {
  const root = await fixture()
  try {
    const result = await verifyReleaseVersion(root, { tag: 'v0.1.0', releases: [] })
    assert.equal(result.title, 'First release')
    await assert.rejects(verifyReleaseVersion(root, { tag: 'v0.1.0', releases: [{ tag_name: 'v0.1.0' }] }), /이미 존재/)
    await assert.rejects(verifyReleaseVersion(root, { tag: 'v0.2.0', releases: [] }), /일치하지 않습니다/)
  } finally { await fs.rm(root, { recursive: true, force: true }) }
})

test('허용 목록 파일만 ZIP에 담고 체크섬을 쓴다', async () => {
  const root = await fixture()
  try {
    await fs.mkdir(path.join(root, 'skills', 'yue-music'), { recursive: true })
    await fs.writeFile(path.join(root, 'skills', 'yue-music', 'SKILL.md'), '---\nname: yue-music\ndescription: test\n---\n')
    for (const name of ['README.md', 'LICENSE', 'AGENTS.md']) await fs.writeFile(path.join(root, name), name)
    await fs.mkdir(path.join(root, 'yue-music-workspace'), { recursive: true }); await fs.writeFile(path.join(root, 'yue-music-workspace', 'private.txt'), 'x')
    const output = path.join(root, 'out')
    const built = spawnSync('python3', [path.resolve(__dirname, '..', 'scripts', 'build-release.py'), '--root', root, '--out', output], { encoding: 'utf8' })
    assert.equal(built.status, 0, built.stderr)
    const archive = path.join(output, 'MusicRoad-YuE2-Skills-0.1.0.zip')
    const names = spawnSync('unzip', ['-Z1', archive], { encoding: 'utf8' }).stdout
    assert.match(names, /MusicRoad-YuE2-Skills-0.1.0\/skills\/yue-music\/SKILL.md/)
    assert.doesNotMatch(names, /yue-music-workspace/)
    assert.match(await fs.readFile(path.join(output, 'SHA256SUMS.txt'), 'utf8'), /MusicRoad-YuE2-Skills-0.1.0.zip/)
  } finally { await fs.rm(root, { recursive: true, force: true }) }
})
