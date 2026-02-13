/**
 * ScorePanel — compact single-row score bar for Viable / Sufficient / Sustainable / Combined.
 *
 * Designed to span the full page width above the heatmap row.
 */
import { CheckCircle, XCircle, AlertTriangle } from 'lucide-react'

const METRICS = [
  { label: 'Viable',      key: 'viable',      desc: 'Can the project cover its stakes?' },
  { label: 'Sufficient',  key: 'sufficient',   desc: 'Is operational output enough?' },
  { label: 'Sustainable', key: 'sustainable',  desc: 'Can costs be maintained long-term?' },
  { label: 'Combined',    key: 'combined',     desc: 'Do all three tests pass together?' },
]

const STYLES = {
  pass:       { box: 'border-green-700/50 bg-green-900/20',   icon: 'text-green-400', val: 'text-green-400' },
  borderline: { box: 'border-yellow-700/50 bg-yellow-900/20', icon: 'text-yellow-400', val: 'text-yellow-400' },
  fail:       { box: 'border-red-700/50 bg-red-900/20',       icon: 'text-red-400', val: 'text-red-400' },
}

export default function ScorePanel({ scores }) {
  if (!scores) return null

  return (
    <div className="grid grid-cols-4 gap-2">
      {METRICS.map(m => {
        const val = scores[m.key]
        const passing = val >= 0.5
        const borderline = val >= 0.4 && val < 0.5
        const s = passing ? STYLES.pass : borderline ? STYLES.borderline : STYLES.fail
        const Icon = passing ? CheckCircle : borderline ? AlertTriangle : XCircle

        return (
          <div
            key={m.key}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-md border ${s.box}`}
            title={m.desc}
          >
            <Icon className={`w-4 h-4 flex-shrink-0 ${s.icon}`} />
            <span className="text-sm font-medium text-[var(--text-primary)]">{m.label}</span>
            <span className={`text-base font-bold ml-auto tabular-nums ${s.val}`}>
              {(val * 100).toFixed(0)}%
            </span>
          </div>
        )
      })}
    </div>
  )
}
