/**
 * ArchetypeList — ranked list of all 15 archetypes for self-mapping.
 *
 * Sorted by Euclidean distance from user's profile (closest first).
 * Distance numbers are hidden to avoid anchoring bias.
 * Each archetype expandable to show full DimensionComparison.
 */
import { useState, useMemo } from 'react'
import { ChevronDown, ChevronRight, Check, X } from 'lucide-react'
import DimensionComparison from './DimensionComparison'

function euclideanDistance(a, b) {
  if (!a || !b || a.length !== b.length) return Infinity
  return Math.sqrt(a.reduce((sum, v, i) => sum + (v - b[i]) ** 2, 0))
}

export default function ArchetypeList({
  userDimensions,
  archetypeData,
  archetypeOrder,
  onSelect,
  onNoneMatch,
}) {
  const [expandedArch, setExpandedArch] = useState(null)
  const [noneMatchMode, setNoneMatchMode] = useState(false)
  const [noneMatchDesc, setNoneMatchDesc] = useState('')

  // Sort archetypes by distance from user profile
  const ranked = useMemo(() => {
    if (!archetypeData || !userDimensions) return []
    return archetypeOrder
      .map(name => ({
        name,
        ...archetypeData[name],
        distance: euclideanDistance(userDimensions, archetypeData[name]?.dimensions),
      }))
      .sort((a, b) => a.distance - b.distance)
  }, [archetypeData, archetypeOrder, userDimensions])

  function toggleExpand(name) {
    setExpandedArch(expandedArch === name ? null : name)
  }

  return (
    <div className="space-y-3">
      <div>
        <h3 className="text-sm font-semibold text-[var(--text-primary)] mb-1">
          Which archetype best describes your project?
        </h3>
        <p className="text-sm text-[var(--text-muted)]">
          These are ordered by structural similarity to your profile. Expand any to see a
          detailed dimension comparison. Select the one that best matches your real-world
          experience — or tell us if none fit.
        </p>
      </div>

      {/* Archetype cards */}
      <div className="space-y-1.5">
        {ranked.map(arch => {
          const isExpanded = expandedArch === arch.name

          return (
            <div
              key={arch.name}
              className="bg-[var(--bg-card)] border border-[var(--border)] rounded-lg overflow-hidden"
            >
              {/* Header row */}
              <div className="flex items-center gap-3 px-4 py-3">
                {/* Expand toggle */}
                <button
                  onClick={() => toggleExpand(arch.name)}
                  className="text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors flex-shrink-0"
                >
                  {isExpanded
                    ? <ChevronDown className="w-4 h-4" />
                    : <ChevronRight className="w-4 h-4" />
                  }
                </button>

                {/* Name + description */}
                <div
                  className="flex-1 min-w-0 cursor-pointer"
                  onClick={() => toggleExpand(arch.name)}
                >
                  <p className="text-sm font-medium text-[var(--text-primary)]">{arch.name}</p>
                  {!isExpanded && arch.description && (
                    <p className="text-sm text-[var(--text-muted)] truncate">{arch.description}</p>
                  )}
                </div>

                {/* Select button */}
                <button
                  onClick={() => onSelect(arch.name)}
                  className="flex items-center gap-1 px-3 py-1 text-sm text-[var(--accent)] border border-[var(--accent)] rounded-md hover:bg-[var(--accent)] hover:text-white transition-colors flex-shrink-0"
                >
                  <Check className="w-3.5 h-3.5" /> This one
                </button>
              </div>

              {/* Expanded detail */}
              {isExpanded && (
                <div className="px-4 pb-4 space-y-3 border-t border-[var(--border)]">
                  {arch.description && (
                    <p className="text-sm text-[var(--text-secondary)] leading-relaxed pt-3">
                      {arch.description}
                    </p>
                  )}
                  <DimensionComparison
                    userDimensions={userDimensions}
                    archetypeDimensions={arch.dimensions}
                    archetypeName={arch.name}
                  />
                </div>
              )}
            </div>
          )
        })}
      </div>

      {/* None match option */}
      <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-lg p-4 space-y-3">
        {!noneMatchMode ? (
          <button
            onClick={() => setNoneMatchMode(true)}
            className="flex items-center gap-2 text-sm text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors"
          >
            <X className="w-4 h-4" />
            None of these match my project
          </button>
        ) : (
          <div className="space-y-3">
            <p className="text-sm font-medium text-[var(--text-primary)]">
              None of these match — this is valuable!
            </p>
            <p className="text-sm text-[var(--text-secondary)]">
              Your project may represent a structural pattern the model hasn't captured yet.
              Please describe what makes your project different from the archetypes above.
            </p>
            <textarea
              value={noneMatchDesc}
              onChange={e => setNoneMatchDesc(e.target.value)}
              maxLength={1000}
              rows={3}
              placeholder="e.g. We're a mid-size team doing embedded systems with no market pressure but extreme safety requirements..."
              className="w-full bg-[var(--bg-primary)] border border-[var(--border)] rounded-md px-3 py-2 text-sm text-[var(--text-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent)] resize-y"
            />
            <div className="flex gap-2">
              <button
                onClick={() => onNoneMatch(noneMatchDesc)}
                className="px-4 py-1.5 text-sm bg-[var(--accent)] text-white rounded-md hover:bg-[var(--accent-hover)] transition-colors"
              >
                Submit
              </button>
              <button
                onClick={() => { setNoneMatchMode(false); setNoneMatchDesc('') }}
                className="px-4 py-1.5 text-sm text-[var(--text-muted)] border border-[var(--border)] rounded-md hover:bg-[var(--bg-hover)] transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
