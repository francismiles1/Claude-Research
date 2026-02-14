/**
 * SliderControls — interactive capacity sliders with hover explanations.
 *
 * Compact by default: label, band, slider, value.
 * Hover to expand: question, detail, key drivers.
 */
import { useState } from 'react'
import { RotateCcw } from 'lucide-react'

const SLIDERS = [
  {
    key: 'investment',
    label: 'Investment',
    question: 'How much capacity does the project have to invest in quality improvement?',
    lowLabel: 'No capacity — frozen budgets, no headcount or tooling available',
    highLabel: 'Full capacity — can add people, tools, consultants, training as needed',
    detail: 'Covers any resource addition: hiring, contractors, tooling, training, consultancy. ' +
      'Without investment capacity the viable zone shrinks — this slider sets the upper bound ' +
      'on what the project can sustain. High regulation and outsourcing demand more; stable teams need less.',
    drivers: ['D4 Regulation', 'D6 Outsourcing', 'D5 Stability'],
  },
  {
    key: 'recovery',
    label: 'Recovery',
    question: 'How well can the project absorb serious setbacks without derailing?',
    lowLabel: 'Fragile — single points of failure, any serious setback could derail the project',
    highLabel: 'Resilient — redundancy, documented processes, institutional knowledge absorbs shocks',
    detail: 'Covers resilience to shocks: key person leaving, major defect found late, environment failure, ' +
      'supplier problems. Not about preventing failures but surviving them. Projects delivering beyond ' +
      'their process maturity need recovery capacity to stay viable.',
    drivers: ['D1 Consequence', 'D3 Complexity', 'D8 Coherence'],
  },
  {
    key: 'overwork',
    label: 'Overwork',
    question: 'How much extra effort can the team absorb beyond normal capacity?',
    lowLabel: 'None — team at capacity, burnt out, or constrained (e.g. retention risk)',
    highLabel: 'Significant — fresh team with spare capacity and willingness to push harder',
    detail: 'Short-term elasticity: overtime, weekend work, heroics. The model treats this as a ' +
      'temporary compensator, not a sustainable strategy. Keeps delivery going when processes are ' +
      'immature — uniquely dominant for micro startups where effort compensates for missing process.',
    drivers: ['D2 Market Pressure', 'D5 Stability', 'D7 Lifecycle'],
  },
  {
    key: 'time',
    label: 'Time',
    question: 'How much schedule flexibility does the project have?',
    lowLabel: 'None — hard deadlines, contractual penalties, market windows closing',
    highLabel: 'Fully flexible — can take as long as needed, no external time pressure',
    detail: 'Tolerance for delivery delays: market patience, contractual flexibility, ' +
      'stakeholder expectations. Projects investing in capability ahead of delivery need time ' +
      'to let that investment mature. High market pressure and early lifecycle reduce time capacity.',
    drivers: ['D2 Market Pressure', 'D7 Lifecycle', 'D4 Regulation'],
  },
]

const BANDS = [
  [0.00, 0.15, 'Very Low'],
  [0.15, 0.30, 'Low'],
  [0.30, 0.40, 'Low-Med'],
  [0.40, 0.55, 'Medium'],
  [0.55, 0.70, 'Med-High'],
  [0.70, 0.85, 'High'],
  [0.85, 1.01, 'Very High'],
]

function toBand(value) {
  for (const [lo, hi, label] of BANDS) {
    if (value >= lo && value < hi) return label
  }
  return 'Very High'
}

function bandColour(value) {
  if (value < 0.30) return 'text-red-400'
  if (value < 0.55) return 'text-yellow-400'
  return 'text-green-400'
}

export default function SliderControls({ sliders, defaults, onChange }) {
  const [hoveredSlider, setHoveredSlider] = useState(null)

  if (!sliders || !defaults) return null

  function handleChange(idx, value) {
    const next = [...sliders]
    next[idx] = parseFloat(value)
    onChange(next)
  }

  function handleReset() {
    onChange([...defaults])
  }

  const hasChanges = sliders.some((v, i) => Math.abs(v - defaults[i]) > 0.001)

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wide">
          Capacity Sliders
          <span className="normal-case font-normal ml-2">— hover for details</span>
        </h3>
        {hasChanges && (
          <button
            onClick={handleReset}
            className="flex items-center gap-1 text-xs text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors"
          >
            <RotateCcw className="w-3 h-3" /> Reset
          </button>
        )}
      </div>

      {SLIDERS.map((s, idx) => {
        const val = sliders[idx]
        const def = defaults[idx]
        const delta = val - def
        const band = toBand(val)

        return (
          <div
            key={s.key}
            onMouseEnter={() => setHoveredSlider(s.key)}
            onMouseLeave={() => setHoveredSlider(null)}
          >
            {/* Header: name + band + value */}
            <div className="flex items-center justify-between mb-0.5">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-[var(--text-primary)]">{s.label}</span>
                <span className={`text-sm font-medium ${bandColour(val)}`}>{band}</span>
              </div>
              <span className="text-sm text-[var(--text-secondary)] tabular-nums">
                {(val * 100).toFixed(0)}%
                {Math.abs(delta) > 0.001 && (
                  <span className={delta > 0 ? 'text-green-400 ml-1' : 'text-red-400 ml-1'}>
                    ({delta > 0 ? '+' : ''}{(delta * 100).toFixed(0)})
                  </span>
                )}
              </span>
            </div>

            {/* Slider */}
            <input
              type="range"
              min="0" max="1" step="0.05"
              value={val}
              onChange={e => handleChange(idx, e.target.value)}
              className="w-full h-1.5 rounded-full appearance-none bg-[var(--border)] cursor-pointer accent-[var(--accent)]"
            />

            {/* Hover detail */}
            {hoveredSlider === s.key && (
              <div className="mt-1 space-y-1">
                <p className="text-sm text-[var(--text-secondary)] italic">{s.question}</p>
                <div className="flex justify-between text-xs text-[var(--text-muted)] gap-4">
                  <span>0% — {s.lowLabel}</span>
                  <span className="text-right">100% — {s.highLabel}</span>
                </div>
                <p className="text-sm text-[var(--text-secondary)] leading-relaxed">{s.detail}</p>
                <p className="text-sm text-[var(--text-muted)]">
                  Key drivers: <span className="text-[var(--text-secondary)]">{s.drivers.join(', ')}</span>
                </p>
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
