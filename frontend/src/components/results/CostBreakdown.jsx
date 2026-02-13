/**
 * CostBreakdown — cost decomposition with hover explanations.
 *
 * Compact by default: bar + value per cost component.
 * Hover to expand: plain-English explanation of what each cost means.
 */
import { useState } from 'react'

const COST_ITEMS = [
  { key: 'gap_cost', label: 'Gap Cost', colour: '#ef4444' },
  { key: 'debt_cost', label: 'Debt Cost', colour: '#f59e0b' },
  { key: 'process_cost', label: 'Process Cost', colour: '#3b82f6' },
  { key: 'execution_cost', label: 'Execution Cost', colour: '#8b5cf6' },
]

function gapExplanation(b) {
  if (b.gap_direction === 'Balanced') {
    return 'Capability and operations are well-aligned — there is no significant off-diagonal penalty. ' +
      'The project is delivering proportionally to its process maturity.'
  }
  if (b.gap_direction === 'Cap > Ops') {
    return `Capability exceeds operations by ${(b.gap * 100).toFixed(0)} percentage points — ` +
      'the project has invested in process and governance but is not yet delivering proportionally. ' +
      `This gap is compensated by Time capacity (${(b.gap_compensator_value * 100).toFixed(0)}%). ` +
      'Without enough time tolerance, this investment in capability is wasted overhead.'
  }
  return `Operations exceed capability by ${(b.gap * 100).toFixed(0)} percentage points — ` +
    'the project is delivering beyond its process maturity, which means quality risk. ' +
    `This gap is compensated by ${b.gap_compensator} capacity (${(b.gap_compensator_value * 100).toFixed(0)}%). ` +
    'Without enough recovery or overwork capacity, this pace is unsustainable.'
}

function debtExplanation(b) {
  const avg = ((b.cap || 0) + (b.ops || 0)) / 2
  if (b.debt_cost < 0.01) {
    return 'Average maturity is high enough that compounding debt is negligible. ' +
      'The project has sufficient process foundation to avoid accumulating hidden problems.'
  }
  return `Average maturity is ${(avg * 100).toFixed(0)}%, which is below the debt threshold. ` +
    'Operating at low maturity accumulates compounding problems: undocumented decisions, ' +
    'untested paths, and knowledge gaps. The lower the average, the faster debt compounds.'
}

function processExplanation(b) {
  if (b.process_cost < 0.01) {
    return 'Capability maturity is low enough that governance overhead is minimal — ' +
      'there are few processes to maintain.'
  }
  return 'The cost of maintaining process maturity — standards, documentation, training, ' +
    `governance. At this capability level, Investment capacity (${(b.investment_relief / 0.10 * 100).toFixed(0)}%) ` +
    'offsets some of this overhead. Under-funded teams buckle under process weight; ' +
    'well-funded teams sustain it comfortably.'
}

function executionExplanation(b) {
  if (b.execution_cost < 0.01) {
    return 'Operational output is low enough that delivery overhead is minimal — ' +
      'there is little execution cadence to sustain.'
  }
  return `The cost of sustaining delivery output — release cadence, operational rhythm, ` +
    `and coordination. Best compensated by ${b.exec_compensator} capacity ` +
    `(${(b.exec_compensator_value * 100).toFixed(0)}%). ` +
    'Higher operational maturity demands more capacity to maintain without burning out the team.'
}

const EXPLANATIONS = {
  gap_cost: gapExplanation,
  debt_cost: debtExplanation,
  process_cost: processExplanation,
  execution_cost: executionExplanation,
}

export default function CostBreakdown({ breakdown }) {
  const [hoveredCost, setHoveredCost] = useState(null)

  if (!breakdown) return null

  const maxCost = Math.max(
    ...COST_ITEMS.map(c => breakdown[c.key] || 0),
    0.01
  )

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold text-[var(--text-primary)]">
        Cost Breakdown
        <span className="text-sm font-normal text-[var(--text-muted)] ml-2">
          at Cap {Math.round((breakdown.cap || 0) * 100)}%, Ops {Math.round((breakdown.ops || 0) * 100)}%
          — hover for details
        </span>
      </h3>

      {/* Direction badge */}
      <div className="flex items-center gap-2 text-sm">
        <span className="px-2 py-0.5 rounded bg-[var(--bg-hover)] text-[var(--text-secondary)] font-medium">
          {breakdown.gap_direction}
        </span>
        {breakdown.gap_direction !== 'Balanced' && (
          <span className="text-[var(--text-muted)]">
            Compensated by {breakdown.gap_compensator}
          </span>
        )}
      </div>

      {/* Cost items with hover explanations */}
      <div className="space-y-2">
        {COST_ITEMS.map(item => {
          const val = breakdown[item.key] || 0
          const pct = (val / maxCost) * 100

          return (
            <div
              key={item.key}
              className="cursor-help"
              onMouseEnter={() => setHoveredCost(item.key)}
              onMouseLeave={() => setHoveredCost(null)}
            >
              <div className="flex items-center justify-between text-sm mb-0.5">
                <span className="font-medium text-[var(--text-primary)]">{item.label}</span>
                <span className="text-[var(--text-muted)] tabular-nums">{val.toFixed(3)}</span>
              </div>
              <div className="h-2.5 bg-[var(--bg-primary)] rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-300"
                  style={{ width: `${pct}%`, backgroundColor: item.colour }}
                />
              </div>
              {hoveredCost === item.key && (
                <p className="text-sm text-[var(--text-secondary)] leading-relaxed mt-1">
                  {EXPLANATIONS[item.key]?.(breakdown)}
                </p>
              )}
            </div>
          )
        })}
      </div>

      {/* Summary */}
      <div className="border-t border-[var(--border)] pt-2 space-y-1 text-sm">
        <div className="flex justify-between">
          <span className="text-[var(--text-secondary)]">Total cost</span>
          <span className="tabular-nums">{breakdown.total_cost?.toFixed(3)}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-[var(--text-secondary)]">Investment relief</span>
          <span className="text-green-400 tabular-nums">-{breakdown.investment_relief?.toFixed(3)}</span>
        </div>
        <div className="flex justify-between font-medium">
          <span>Net cost</span>
          <span className={`tabular-nums ${breakdown.sustainable ? 'text-green-400' : 'text-red-400'}`}>
            {breakdown.net_cost?.toFixed(3)} / {breakdown.threshold?.toFixed(2)}
          </span>
        </div>
        <p className="text-sm text-[var(--text-muted)] leading-relaxed pt-1">
          {breakdown.sustainable
            ? `This position is sustainable — net cost is within the threshold with ${breakdown.headroom?.toFixed(3)} headroom. ` +
              'The organisation can maintain this Cap/Ops balance without exhausting its capacity.'
            : `This position is unsustainable — net cost exceeds the threshold by ${Math.abs(breakdown.headroom || 0).toFixed(3)}. ` +
              'The organisation cannot maintain this balance long-term without increasing investment or reducing maturity ambition.'
          }
        </p>
      </div>
    </div>
  )
}
