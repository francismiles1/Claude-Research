/**
 * SliderSummary — read-only display of default slider values with hover explanations.
 *
 * Compact by default — hover any slider to expand its full explanation.
 * Matches the DimensionProfile interaction pattern.
 */
import { useState } from 'react'

const SLIDERS = [
  {
    key: 'investment',
    label: 'Investment',
    question: 'Can you afford to move on the grid?',
    detail: 'Resource availability for process improvement — hiring, tooling, training. ' +
      'Dominates the sustainability upper bound for almost all archetypes. ' +
      'High regulation and outsourcing demand more investment; stable teams need less.',
    drivers: ['D4 Regulation', 'D6 Outsourcing', 'D5 Stability'],
  },
  {
    key: 'recovery',
    label: 'Recovery',
    question: 'Can you survive failures?',
    detail: 'Ability to absorb setbacks without collapse — redundancy, fallback processes, ' +
      'institutional knowledge. Buffers the viability floor and sustains Ops > Cap positions. ' +
      'High consequence and complexity demand more recovery capacity.',
    drivers: ['D1 Consequence', 'D3 Complexity', 'D8 Coherence'],
  },
  {
    key: 'overwork',
    label: 'Overwork',
    question: 'Can the team compensate through effort?',
    detail: 'Short-term team elasticity — overtime, heroics, crunch. Buffers the sufficiency ' +
      'floor. Uniquely dominant for micro startups. Unsustainable long-term; the model treats ' +
      'it as a temporary compensator, not a strategy.',
    drivers: ['D2 Market Pressure', 'D5 Stability', 'D7 Lifecycle'],
  },
  {
    key: 'time',
    label: 'Time',
    question: 'Can you afford to be slow?',
    detail: 'Tolerance for delivery delays — market patience, contractual flexibility. ' +
      'Sustains Cap > Ops positions (investing in capability ahead of delivery). ' +
      'High market pressure and early lifecycle stages reduce time capacity.',
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

function barBg(value) {
  if (value < 0.30) return 'bg-red-500'
  if (value < 0.55) return 'bg-yellow-500'
  return 'bg-green-500'
}

export default function SliderSummary({ defaults }) {
  const [hoveredSlider, setHoveredSlider] = useState(null)

  if (!defaults) return null

  return (
    <div className="space-y-3">
      <h3 className="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wide">
        Default Capacity Sliders
        <span className="normal-case font-normal ml-2">— hover for details</span>
      </h3>

      {SLIDERS.map((s, idx) => {
        const val = defaults[idx]
        const band = toBand(val)
        const widthPct = val * 100

        return (
          <div
            key={s.key}
            className="cursor-help"
            onMouseEnter={() => setHoveredSlider(s.key)}
            onMouseLeave={() => setHoveredSlider(null)}
          >
            {/* Label row */}
            <div className="flex items-center justify-between mb-0.5">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-[var(--text-primary)]">{s.label}</span>
                <span className={`text-sm font-medium ${bandColour(val)}`}>{band}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm text-[var(--text-secondary)] italic">{s.question}</span>
                <span className="text-sm text-[var(--text-secondary)] tabular-nums">
                  {(val * 100).toFixed(0)}%
                </span>
              </div>
            </div>

            {/* Bar */}
            <div className="h-2.5 rounded-full bg-[var(--bg-primary)] border border-[var(--border)] overflow-hidden">
              <div
                className={`h-full rounded-full ${barBg(val)}`}
                style={{ width: `${widthPct}%` }}
              />
            </div>

            {/* Hover detail */}
            {hoveredSlider === s.key && (
              <div className="mt-1.5 space-y-1">
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
