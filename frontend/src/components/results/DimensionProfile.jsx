/**
 * DimensionProfile — bar chart display of 8 project dimensions.
 *
 * Each dimension shows a filled bar (1–5), colour-coded by impact,
 * with a hover tooltip explaining what the dimension means in context.
 */
import { useState } from 'react'
import { DIMENSIONS, VALUE_LABELS, barColour } from '../comparison/dimensionMeta'

export default function DimensionProfile({ dimensions }) {
  const [hoveredDim, setHoveredDim] = useState(null)

  if (!dimensions || dimensions.length < 8) return null

  return (
    <div>
      <h3 className="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wide mb-3">
        Dimension Profile
        <span className="normal-case font-normal ml-2">— hover for details</span>
      </h3>
      <div className="space-y-2">
        {DIMENSIONS.map((dim, i) => {
          const val = dimensions[i]
          const desc = VALUE_LABELS[dim.label]?.[val] || ''
          const widthPct = (val / 5) * 100

          return (
            <div
              key={dim.key}
              className="cursor-help"
              onMouseEnter={() => setHoveredDim(dim.key)}
              onMouseLeave={() => setHoveredDim(null)}
            >
              {/* Label row */}
              <div className="flex items-center justify-between mb-0.5">
                <span className="text-sm font-medium text-[var(--text-primary)]">
                  {dim.key} {dim.label}
                </span>
                <span className="text-sm text-[var(--text-secondary)]">
                  {desc} ({val}/5)
                </span>
              </div>

              {/* Bar */}
              <div className="flex items-center gap-2">
                <span className="text-xs text-[var(--text-muted)] w-16 text-right flex-shrink-0">{dim.lo}</span>
                <div className="flex-1 h-2.5 rounded-full bg-[var(--bg-primary)] border border-[var(--border)] overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all ${barColour(val, dim.inverted)}`}
                    style={{ width: `${widthPct}%` }}
                  />
                </div>
                <span className="text-xs text-[var(--text-muted)] w-20 flex-shrink-0">{dim.hi}</span>
              </div>

              {/* Tooltip — shown on hover */}
              {hoveredDim === dim.key && (
                <p className="text-sm text-[var(--text-secondary)] leading-relaxed mt-1 pl-[calc(4rem+0.5rem)]">
                  {dim.tooltip}
                </p>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
