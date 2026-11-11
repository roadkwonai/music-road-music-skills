'use strict'
// Road Music CLI 없이 돌아가는 묶음 정적 검사(CI·릴리스 관문).
const assert = require('node:assert/strict')
const fs = require('node:fs')
const path = require('node:path')
const { test } = require('node:test')

const root = path.resolve(__dirname, '..')
const read = file => fs.readFileSync(path.join(root, file), 'utf8')
const manifest = JSON.parse(read('manifest.json'))
const skillDirs = fs.readdirSync(path.join(root, 'skills')).filter(name => fs.statSync(path.join(root, 'skills', name)).isDirectory()).sort()

function frontmatter (text) {
  const match = /^---\n([\s\S]*?)\n---\n/.exec(text)
  assert.ok(match, 'frontmatter 없음')
  return Object.fromEntries(match[1].split('\n').map(line => /^([a-z_-]+):\s*(.*)$/.exec(line)).filter(Boolean).map(m => [m[1], m[2]]))
}

test('manifest·VERSION·스킬 폴더가 일치한다', () => {
  assert.equal(manifest.version, read('VERSION').trim())
  assert.deepEqual(manifest.skills.map(s => s.id).sort(), skillDirs)
  for (const skill of manifest.skills) assert.equal(skill.path, `skills/${skill.id}`)
  assert.ok(fs.existsSync(path.join(root, manifest.releaseNotes)), 'releaseNotes 파일 없음')
})

test('각 스킬의 frontmatter와 Codex 메타데이터가 유효하다', () => {
  for (const name of skillDirs) {
    const fm = frontmatter(read(`skills/${name}/SKILL.md`))
    assert.equal(fm.name, name, `${name}: name 불일치`)
    assert.ok(/^[a-z0-9-]{1,64}$/.test(fm.name), `${name}: name 형식`)
    assert.ok(fm.description && fm.description.length >= 50 && fm.description.length <= 1024, `${name}: description 길이 ${fm.description && fm.description.length}`)
    assert.ok(!/:\s/.test(fm.description), `${name}: description에 ': '가 있으면 YAML 평문 스칼라가 깨진다`)
    const yaml = read(`skills/${name}/agents/openai.yaml`)
    for (const key of ['display_name', 'short_description', 'default_prompt']) assert.match(yaml, new RegExp(`${key}: ".+"`), `${name}: openai.yaml ${key}`)
    assert.match(yaml, new RegExp(`\\$${name}\\b`), `${name}: default_prompt는 $${name}으로 시작`)
  }
})

test('마크다운 상대 링크가 모두 열린다', () => {
  const files = []
  const walk = dir => { for (const entry of fs.readdirSync(dir, { withFileTypes: true })) { const full = path.join(dir, entry.name); if (entry.isDirectory()) { if (!['node_modules', '.git', 'yue-music-workspace', 'dist'].includes(entry.name)) walk(full) } else if (entry.name.endsWith('.md')) files.push(full) } }
  walk(root)
  const broken = []
  for (const file of files) {
    for (const [, target] of fs.readFileSync(file, 'utf8').replace(/```[\s\S]*?```/g, '').replace(/`[^`\n]*`/g, '').matchAll(/\]\(([^)#\s]+)(?:#[^)]*)?\)/g)) {
      if (/^[a-z]+:/i.test(target)) continue
      if (!fs.existsSync(path.resolve(path.dirname(file), target))) broken.push(`${path.relative(root, file)} → ${target}`)
    }
  }
  assert.deepEqual(broken, [])
})

test('zsh에서 깨지는 $RM 호출 패턴을 쓰지 않는다', () => {
  for (const name of skillDirs) {
    for (const file of fs.readdirSync(path.join(root, 'skills', name), { recursive: true }).filter(f => String(f).endsWith('.md'))) {
      const text = read(`skills/${name}/${file}`)
      assert.ok(!/\$RM\s|RM="node/.test(text), `${name}/${file}: roadmusic() 함수를 쓴다`)
    }
  }
})

test('예시 요청에 YuE2에 없는 필드가 없고 기대값이 짝을 이룬다', () => {
  const expectations = JSON.parse(read('examples/expectations.json'))
  const files = fs.readdirSync(path.join(root, 'examples')).filter(f => f.endsWith('.json') && f !== 'expectations.json').sort()
  assert.deepEqual(Object.keys(expectations).sort(), files)
  const forbidden = /"(negative_prompt|negativePrompt|phonemes|reference_audio|referenceAudio|variety|weirdness|maxMode|excludeStyles)"/
  for (const file of files) {
    const text = read(`examples/${file}`)
    assert.ok(!forbidden.test(text), `${file}: 금지 필드`)
    const body = JSON.parse(text)
    assert.ok(['yue', 'yue-mlx'].includes(body.engine), `${file}: engine 명시`)
  }
})
