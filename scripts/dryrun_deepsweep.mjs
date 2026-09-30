#!/usr/bin/env node
// Dry-run the critical-deep-sweep workflow on an args file: build every subagent prompt
// WITHOUT dispatching, and assert the contract actually reached each one. Costs 0 tokens.
//
//   node scripts/dryrun_deepsweep.mjs <STG>/deepsweep_args.json [--out <STG>/prompts_dryrun.txt]
//
// Why: R2 (2026-09-15) shipped 8 agents that never saw the batch brief (extra_brief_path was
// skipped). A lean pass also depends on the LEAN PASS and FAMILY GROUP sections landing. Exit 1
// if any prompt is missing a required marker, the brief's first/last line, or a group PID.
// Prints per-agent prompt size — multiply by agents to see what the brief costs before paying it.
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const argv = process.argv.slice(2)
if (!argv.length) { console.error('usage: dryrun_deepsweep.mjs <args.json> [--out file]'); process.exit(2) }
const outIdx = argv.indexOf('--out')
const outFile = outIdx >= 0 ? argv[outIdx + 1] : null
const A = JSON.parse(fs.readFileSync(argv[0], 'utf8'))
const repo = path.dirname(path.dirname(fileURLToPath(import.meta.url)))
const src = fs.readFileSync(path.join(repo, '.claude/workflows/critical-deep-sweep.js'), 'utf8')
  .replace('export const meta', 'const meta')

const prompts = []
const run = new Function('args', 'phase', 'log', 'agent', 'parallel', `return (async()=>{${src}})()`)
await run(A, () => {}, () => {},
  async (p, o) => { prompts.push({ label: o.label, prompt: p, model: o.model }); return 'dry-run' },
  async fns => Promise.all(fns.map(f => f())))

const brief = (A.extra_brief || '').trim().split('\n').filter(l => l.trim())
const markers = ['`shard_upsert.py --remaining`']
if (A.extra_brief) markers.push('## Scope-specific guidance', brief[0], brief[brief.length - 1])
if (A.lean) markers.push('## LEAN PASS')
if (A.status_review) markers.push('## STATUS REVIEW')

let bad = 0
const seen = new Set()
for (const { label, prompt, model } of prompts) {
  const pids = label.replace(/^audit:/, '').split('+')
  pids.forEach(p => seen.add(p))
  const need = [...markers, ...pids, ...(pids.length > 1 ? ['## FAMILY GROUP'] : [])]
  const missing = need.filter(m => !prompt.includes(m))
  if (missing.length) bad++
  console.log(`${missing.length ? 'FAIL' : 'ok  '} ${label.padEnd(40)} ${String(prompt.length).padStart(7)} chars  model=${model}` +
    (missing.length ? `  MISSING: ${missing.map(m => JSON.stringify(m.slice(0, 50))).join(', ')}` : ''))
}
const unseen = (A.pids || []).filter(p => !seen.has(p))
if (unseen.length) { bad++; console.log(`FAIL pids with no agent: ${unseen.join(', ')}`) }
const total = prompts.reduce((n, x) => n + x.prompt.length, 0)
console.log(`\n${prompts.length} agents for ${(A.pids || []).length} pids; ` +
  `prompt chars total ${total.toLocaleString()} (brief ${(A.extra_brief || '').length.toLocaleString()} each)`)
if (outFile) fs.writeFileSync(outFile, prompts.map(x => `=== ${x.label}\n${x.prompt}`).join('\n\n'))
process.exit(bad ? 1 : 0)
