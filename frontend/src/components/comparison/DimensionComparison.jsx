/**
 * DimensionComparison — side-by-side 8D comparison between user profile and an archetype.
 *
 * Shows dual bars per dimension with delta indicators.
 * Hover-to-expand for contextual explanations.
 */
import { useState } from 'react'
import { DIMENSIONS, VALUE_LABELS } from './dimensionMeta'

function deltaColour(delta) {
  if (delta === 0) return 'text-green-400'
  if (Math.abs(delta) === 1) return 'text-yellow-400'
  return 'text-red-400'
}

function deltaLabel(delta) {
  if (delta === 0) return '='
  return delta > 0 ? `+${delta}` : `${delta}`
}

function deltaExplanation(dim, userVal, archVal) {
  const delta = userVal - archVal
  if (delta === 0) return `Your project matches the archetype on ${dim.label}.`
  const direction = delta > 0 ? 'higher' : 'lower'
  const userDesc = VALUE_LABELS[dim.label]?.[userVal] || userVal
  const archDesc = VALUE_LABELS[dim.label]?.[archVal] || archVal
  return `Your project scores ${Math.abs(delta)} point${Math.abs(delta) > 1 ? 's' : ''} ${direction} ` +
    `on ${dim.label} (${userDesc} vs ${archDesc}).`
}

export default function DimensionComparison({ userDimensions, archetypeDimensions, archetypeName }) {
  const [hoveredDim, setHoveredDim] = useState(null)

  if (!userDimensions || !archetypeDimensions) return null

  const totalDelta = userDimensions.reduce((sum, v, i) => sum + Math.abs(v - archetypeDimensions[i]), 0)

  return (
    <div className="space-y-2">
      {/* Legend */}
      <div className="flex items-center gap-4 text-sm text-[var(--text-muted)]">
        <span className="flex items-center gap-1.5">
          <span className="w-3 h-2 rounded-sm bg-[var(--accent)] inline-block" /> Your profile
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-3 h-2 rounded-sm bg-[var(--text-muted)] opacity-40 inline-block" /> {archetypeName}
        </span>
        <span className="ml-auto">Total delta: <span className={totalDelta === 0 ? 'text-green-400' : totalDelta <= 4 ? 'text-yellow-400' : 'text-red-400'}>{totalDelta}</span></span>
      </div>

      {/* Dimension rows */}
      {DIMENSIONS.map((dim, i) => {
        const userVal = userDimensions[i]
        const archVal = archetypeDimensions[i]
        const delta = userVal - archVal
        const userPct = (userVal / 5) * 100
        const archPct = (archVal / 5) * 100

        return (
          <div
            key={dim.key}
            className="cursor-help"
            onMouseEnter={() => setHoveredDim(dim.key)}
            onMouseLeave={() => setHoveredDim(null)}
          >
            {/* Label + delta */}
            <div className="flex items-center justify-between mb-0.5">
              <span className="text-sm font-medium text-[var(--text-primary)]">
                {dim.key} {dim.label}
              </span>
              <div className="flex items-center gap-2 text-sm">
                <span className="text-[var(--text-muted)] tabular-nums">{userVal}</span>
                <span className={`font-medium tabular-nums ${deltaColour(delta)}`}>
                  {deltaLabel(delta)}
                </span>
                <span className="text-[var(--text-muted)] tabular-nums opacity-50">{archVal}</span>
              </div>
            </div>

            {/* Dual bars */}
            <div className="space-y-0.5">
              <div className="h-2 rounded-full bg-[var(--bg-primary)] border border-[var(--border)] overflow-hidden">
                <div
                  className="h-full rounded-full bg-[var(--accent)] transition-all"
                  style={{ width: `${userPct}%` }}
                />
              </div>
              <div className="h-1.5 rounded-full bg-[var(--bg-primary)] border border-[var(--border)] overflow-hidden opacity-40">
                <div
                  className="h-full rounded-full bg-[var(--text-muted)] transition-all"
                  style={{ width: `${archPct}%` }}
                />
              </div>
            </div>

            {/* Hover tooltip */}
            {hoveredDim === dim.key && (
              <div className="mt-1 space-y-0.5">
                <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
                  {deltaExplanation(dim, userVal, archVal)}
                </p>
                <p className="text-sm text-[var(--text-muted)] leading-relaxed">
                  {dim.tooltip}
                </p>
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
