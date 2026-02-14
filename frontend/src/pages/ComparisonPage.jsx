/**
 * ComparisonPage — three-phase research instrument.
 *
 * Phase 1: Your Profile — assessment results (dimensions, Cap/Ops scores)
 * Phase 2: Self-Mapping — browse archetypes, select closest match (or none)
 * Phase 3: Reveal — system match vs user choice, log everything
 *
 * Designed to eliminate anchoring bias: distances hidden until after selection.
 */
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowRight, ChevronDown, HelpCircle } from 'lucide-react'
import api from '../api/client'
import { useAssessment, useAssessmentDispatch } from '../context/AssessmentContext'
import { DIMENSIONS, VALUE_LABELS, barColour } from '../components/comparison/dimensionMeta'
import ArchetypeList from '../components/comparison/ArchetypeList'
import RevealPanel from '../components/comparison/RevealPanel'

export default function ComparisonPage() {
  const navigate = useNavigate()
  const state = useAssessment()
  const dispatch = useAssessmentDispatch()

  const { bridgeResult, engineScores } = state

  const [archetypes, setArchetypes] = useState(null)
  const [phase, setPhase] = useState(1)
  const [userChoice, setUserChoice] = useState(null)       // archetype name or null
  const [noneMatch, setNoneMatch] = useState(false)
  const [noneMatchDesc, setNoneMatchDesc] = useState('')

  // Redirect if no assessment
  useEffect(() => { if (!bridgeResult) navigate('/') }, [bridgeResult, navigate])

  // Fetch archetype metadata
  useEffect(() => {
    api.get('/meta/archetypes').then(r => setArchetypes(r.data))
  }, [])

  // ── Phase 2: Self-mapping handlers ────────────────────────────────
  function handleSelectArchetype(name) {
    setUserChoice(name)
    setNoneMatch(false)
    dispatch({ type: 'SET_SELF_MAP', choice: name, noneMatch: false, noneMatchDesc: '' })
    setPhase(3)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  function handleNoneMatch(description) {
    setUserChoice(null)
    setNoneMatch(true)
    setNoneMatchDesc(description)
    dispatch({ type: 'SET_SELF_MAP', choice: null, noneMatch: true, noneMatchDesc: description })
    setPhase(3)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  if (!bridgeResult) return null

  const hasScores = engineScores && engineScores.questions_answered > 0

  // ── Render ────────────────────────────────────────────────────────
  return (
    <div className="max-w-[1400px] mx-auto px-4 py-6 space-y-6">

      {/* ── Phase 3: Reveal (shown at top when active) ────────────── */}
      {phase === 3 && (
        <div className="space-y-4">
          <RevealPanel
            userChoice={userChoice}
            systemMatch={bridgeResult.archetype}
            systemDistance={bridgeResult.match_distance || 0}
            confidence={bridgeResult.confidence || 'ambiguous'}
            userDimensions={bridgeResult.dimensions}
            archetypeData={archetypes?.archetypes}
            noneMatchDesc={noneMatchDesc}
          />

          {/* Navigation */}
          <div className="flex items-center justify-between pt-4 border-t border-[var(--border)]">
            <button
              onClick={() => { setPhase(2); setUserChoice(null); setNoneMatch(false) }}
              className="px-4 py-2 text-sm text-[var(--text-muted)] border border-[var(--border)] rounded-md hover:bg-[var(--bg-hover)] transition-colors"
            >
              Change selection
            </button>
            <div className="flex gap-2">
              <button
                onClick={() => {
                  // If user selected an archetype, switch Explorer to it
                  if (userChoice && archetypes?.archetypes) {
                    const arch = archetypes.archetypes[userChoice]
                    if (arch && userChoice !== bridgeResult.archetype) {
                      dispatch({
                        type: 'SET_CONTEXT_RESULT',
                        contextAnswers: state.contextAnswers,
                        bridgeResult: { archetype: userChoice, dimensions: arch.dimensions, confidence: 'self_mapped' },
                        defaultSliders: arch.default_sliders,
                        defaultPosition: arch.default_position,
                      })
                    }
                  }
                  navigate('/results')
                }}
                className="flex items-center gap-1.5 px-4 py-2 text-sm bg-[var(--accent)] text-white rounded-md hover:bg-[var(--accent-hover)] transition-colors"
              >
                Explore the Model <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── Phase 1: Your Profile ─────────────────────────────────── */}
      {phase >= 1 && phase < 3 && (
        <div className="space-y-4">
          <div>
            <h2 className="text-lg font-bold text-[var(--text-primary)]">Your Assessment Profile</h2>
            <p className="text-sm text-[var(--text-muted)]">
              These results are derived from your project context and maturity assessment answers.
            </p>
          </div>

          {/* Cap/Ops scores */}
          {hasScores && (
            <div className="grid grid-cols-3 gap-3">
              <ScoreCard label="Capability" value={engineScores.capability_pct} />
              <ScoreCard label="Operational" value={engineScores.operational_pct} />
              <ScoreCard
                label="Questions"
                custom={`${engineScores.questions_answered} / ${engineScores.questions_visible}`}
                sub="answered"
              />
            </div>
          )}

          {!hasScores && (
            <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-lg p-4">
              <p className="text-sm text-[var(--text-muted)]">
                No maturity questions answered — the comparison below is based on your
                project context (dimensions) only.
              </p>
            </div>
          )}

          {/* Dimension profile */}
          <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-lg p-5">
            <DimensionProfileCompact dimensions={bridgeResult.dimensions} />
          </div>

          {/* Advance to Phase 2 */}
          {phase === 1 && (
            <div className="flex justify-center">
              <button
                onClick={() => setPhase(2)}
                className="flex items-center gap-1.5 px-4 py-2 text-sm bg-[var(--accent)] text-white rounded-md hover:bg-[var(--accent-hover)] transition-colors"
              >
                Compare with Archetypes <ChevronDown className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>
      )}

      {/* ── Phase 2: Self-Mapping ─────────────────────────────────── */}
      {phase === 2 && archetypes && (
        <div className="space-y-4">
          <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-lg p-4">
            <div className="flex items-start gap-2">
              <HelpCircle className="w-4 h-4 text-[var(--accent)] mt-0.5 flex-shrink-0" />
              <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
                The model defines 15 structural archetypes — project types characterised by
                their dimension profile, not their industry domain. We need your help to
                validate whether these archetypes are comprehensive and accurate.
                <strong className="text-[var(--text-primary)]"> Which one (if any) best
                matches your real-world project?</strong>
              </p>
            </div>
          </div>

          <ArchetypeList
            userDimensions={bridgeResult.dimensions}
            archetypeData={archetypes.archetypes}
            archetypeOrder={archetypes.archetype_order}
            onSelect={handleSelectArchetype}
            onNoneMatch={handleNoneMatch}
          />
        </div>
      )}
    </div>
  )
}

/** Compact score card for Phase 1 */
function ScoreCard({ label, value, custom, sub }) {
  return (
    <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-md p-3 text-center">
      <p className="text-sm text-[var(--text-muted)] mb-1">{label}</p>
      {custom ? (
        <>
          <p className="text-lg font-bold">{custom}</p>
          {sub && <p className="text-sm text-[var(--text-muted)]">{sub}</p>}
        </>
      ) : (
        <p className="text-lg font-bold">{value != null ? `${value.toFixed(1)}%` : '—'}</p>
      )}
    </div>
  )
}

/** Inline dimension profile for Phase 1 (compact, with hover) */
function DimensionProfileCompact({ dimensions }) {
  const [hoveredDim, setHoveredDim] = useState(null)

  if (!dimensions || dimensions.length < 8) return null

  return (
    <div>
      <h3 className="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wide mb-3">
        Your Dimension Profile
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
              <div className="flex items-center justify-between mb-0.5">
                <span className="text-sm font-medium text-[var(--text-primary)]">
                  {dim.key} {dim.label}
                </span>
                <span className="text-sm text-[var(--text-secondary)]">
                  {desc} ({val}/5)
                </span>
              </div>
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
