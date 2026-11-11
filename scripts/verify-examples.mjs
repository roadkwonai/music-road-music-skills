#!/usr/bin/env node
// examples/*.json을 Road Music `song:prepare`(모델·서비스 없이 로컬 실행)에 넣어
// valid·엔진 유지·officialGuide advice를 examples/expectations.json과 대조한다.
// 음악을 생성하지 않는다. 사용법: node scripts/verify-examples.mjs [--write verification/RESULTS.md]
import { execFileSync } from 'node:child_process'
import { mkdtempSync, readFileSync, readdirSync, writeFileSync, mkdirSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = join(dirname(fileURLToPath(import.meta.url)), '..')
const home = process.env.ROAD_MUSIC_HOME || '/Users/freelife/youtube/music/music-road'
const cli = process.env.ROAD_MUSIC_CLI || join(home, 'cli', 'road-music.js')
// 사용자 데이터 폴더를 건드리지 않도록 항상 분리한다.
const dataDir = process.env.ROADMUSIC_DATA_DIR || mkdtempSync(join(tmpdir(), 'rm-skill-verify-'))
const env = { ...process.env, ROADMUSIC_DATA_DIR: dataDir, ROADMUSIC_STUDIO_AUTO_OPEN: '0' }

const run = (args) => {
  let out
  try { out = execFileSync('node', [cli, ...args], { env, encoding: 'utf8', maxBuffer: 64 << 20 }) } catch (e) { out = e.stdout || '' }
  try { return JSON.parse(out.trim().split('\n').pop()) } catch { return { ok: false, error: { message: `JSON 아님: ${out.slice(0, 200)}` } } }
}

const exDir = join(root, 'examples')
const expectations = JSON.parse(readFileSync(join(exDir, 'expectations.json'), 'utf8'))
const files = readdirSync(exDir).filter(f => f.endsWith('.json') && f !== 'expectations.json').sort()
const version = run(['cli:version'])
const rows = []
let failed = 0

for (const file of files) {
  const exp = expectations[file]
  const input = JSON.parse(readFileSync(join(exDir, file), 'utf8'))
  const res = run(['song:prepare', '--file', join(exDir, file)])
  const r = res.result || {}
  const guide = r.officialGuide || { checks: [] }
  const adviceIds = guide.checks.filter(c => c.status === 'advice').map(c => c.id).sort()
  const count = s => guide.checks.filter(c => c.status === s).length
  const problems = []
  if (!exp) problems.push('expectations.json에 기대값 없음')
  if (!res.ok) problems.push(`CLI 오류: ${res.error && res.error.message}`)
  if (res.ok && r.valid !== true) problems.push(`valid=${r.valid} ${JSON.stringify(r.errors)}`)
  if (res.ok && r.engine !== input.engine) problems.push(`엔진 변경: ${input.engine} → ${r.engine}`)
  if (res.ok && !r.officialGuide) problems.push('officialGuide 없음')
  if (exp && JSON.stringify(adviceIds) !== JSON.stringify([...exp.advice].sort())) problems.push(`advice 불일치: 기대 [${exp.advice}] 실제 [${adviceIds}]`)
  if (problems.length) failed++
  rows.push({ file, engine: input.engine, valid: r.valid, pass: count('pass'), advice: adviceIds, na: count('not-applicable'),
    style: r.nativeRequest && r.nativeRequest.style, lyricsChanged: r.changes && r.changes.lyrics.changed, adviceText: guide.checks.filter(c => c.advice).map(c => `${c.id}: ${c.advice}`),
    note: exp && exp.note, problems })
}

const caps = ['yue-mlx', 'yue'].map(engine => {
  const c = run(['yue:capabilities', '--json', JSON.stringify({ engine })])
  const e = c.ok && c.result.engines && c.result.engines[0]
  return `- ${engine}: ${e ? `platform=${e.platform}, platformMatches=${e.platformMatches}, defaults cfgScale=${e.defaults.cfgScale}, odeSteps=${e.defaults.odeSteps}` : `조회 실패 ${JSON.stringify(c.error)}`}`
})

const lines = [
  '# 예시 요청 검증 결과', '',
  `- 실행 시각: ${new Date().toISOString()}`,
  `- Road Music CLI: ${version.ok ? `${version.result.cliVersion} (app ${version.result.appVersion}, protocol ${version.result.protocolVersion})` : '버전 조회 실패'}`,
  '- 명령: `song:prepare --file examples/<파일>` (모델·서비스 없이 로컬 검증, 음악 생성 없음), `yue:capabilities`(읽기 전용)',
  '- 데이터 폴더: `ROADMUSIC_DATA_DIR`를 임시 폴더로 분리',
  `- 결과: ${files.length - failed}/${files.length} 통과`, '',
  '| 예시 | 엔진 | valid | pass | advice | 해당 없음 | 판정 |', '| --- | --- | --- | --- | --- | --- | --- |',
  ...rows.map(x => `| ${x.file} | ${x.engine} | ${x.valid} | ${x.pass} | ${x.advice.length ? x.advice.join(', ') : 0} | ${x.na} | ${x.problems.length ? '실패: ' + x.problems.join('; ') : '기대와 일치'} |`),
  '', '## 예시별 메모', '',
  ...rows.flatMap(x => [`### ${x.file}`, '', `- ${x.note || ''}`, `- 최종 style(nativeRequest): \`${x.style}\``, `- 가사 정리 변경: ${x.lyricsChanged}`,
    ...(x.adviceText.length ? ['- 남은 advice와 이유(Suno식 입력을 변환 전 그대로 둔 비교용 예시):', ...x.adviceText.map(t => `  - ${t}`)] : []), '']),
  '## 엔진 지원 범위(yue:capabilities)', '', ...caps, '',
  '이 검증은 입력 계약 점검이다. 실제 가창·길이·발음·음질은 생성 후 청취로만 확인할 수 있다.', ''
]
const report = lines.join('\n')
const writeAt = process.argv.indexOf('--write')
if (writeAt > 0) { const out = join(root, process.argv[writeAt + 1] || 'verification/RESULTS.md'); mkdirSync(dirname(out), { recursive: true }); writeFileSync(out, report) }
process.stdout.write(report)
process.exit(failed ? 1 : 0)
