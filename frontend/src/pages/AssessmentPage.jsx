/**
 * AssessmentPage — two-phase assessment flow.
 *
 * Phase 1: Context form → archetype match
 * Phase 2: Category-by-category maturity questions with adaptive filtering
 */
import { useState, useEffect, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { CheckCircle, ChevronRight, Loader2, ArrowRight, SkipForward, MessageSquarePlus, MessageSquareText } from 'lucide-react'
import api from '../api/client'
import { MINIMUM_ANSWER_PCT, getAnswerPct, answerPctColour } from '../constants'
import { useAssessment, useAssessmentDispatch } from '../context/AssessmentContext'
import ContextForm from '../components/ContextForm'
import QuestionCard from '../components/questions/QuestionCard'
import NoteModal from '../components/NoteModal'

export default function AssessmentPage() {
  const navigate = useNavigate()
  const state = useAssessment()
  const dispatch = useAssessmentDispatch()

  // Phase tracking — 3-phase for full flow:
  //   1: context form (no bridgeResult or no contextAnswers)
  //   2: capacity self-assessment (bridgeResult + contextAnswers but no selfAssessedSliders)
  //   3: maturity questions (all three present)
  // Quick-start skips phases 1+2 (sets bridgeResult but not contextAnswers)
  const phase = (!state.bridgeResult || !state.contextAnswers) ? 1
    : !state.selfAssessedSliders ? 2
    : 3

  // Phase 2 state — initialise from context to survive navigation
  const [categories, setCategories] = useState([])
  const [currentCatIdx, setCurrentCatIdx] = useState(0)
  const [answers, setAnswers] = useState(state.miraAnswers || {})
  const [scores, setScores] = useState(state.engineScores || null)
  const [loading, setLoading] = useState(false)
  const [refreshing, setRefreshing] = useState(false)
  const [scoresLoading, setScoresLoading] = useState(false)
  const [noteModalOpen, setNoteModalOpen] = useState(false)

  // Refs to avoid stale closure issues
  const debounceRef = useRef(null)
  const contextRef = useRef(state.contextAnswers)
  contextRef.current = state.contextAnswers

  // ── Phase 1 completion ──────────────────────────────────────────────
  function handleContextComplete(contextAnswers, apiResult) {
    dispatch({
      type: 'SET_CONTEXT_RESULT',
      contextAnswers,
      bridgeResult: {
        archetype: apiResult.archetype,
        dimensions: apiResult.dimensions,
        confidence: apiResult.confidence,
        match_distance: apiResult.match_distance,
        alternatives: apiResult.alternatives,
      },
      defaultSliders: apiResult.default_sliders,
      defaultPosition: apiResult.default_position,
    })
  }

  // ── Phase 2: fetch visible questions ───────────────────────────────
  const fetchVisible = useCallback(async (currentAnswers, ctx, isInitial) => {
    const context = ctx || contextRef.current
    if (!context) return
    if (isInitial) setLoading(true)
    else setRefreshing(true)
    try {
      const res = await api.post('/assessment/visible', {
        answers: currentAnswers,
        context,
      })
      setCategories(res.data.categories)

      // Prune answers to questions no longer visible (e.g. trigger changed)
      const visibleIds = new Set()
      for (const cat of res.data.categories) {
        for (const q of cat.questions) visibleIds.add(q.id)
      }
      const pruned = {}
      let didPrune = false
      for (const [qid, val] of Object.entries(currentAnswers)) {
        if (visibleIds.has(qid)) {
          pruned[qid] = val
        } else {
          didPrune = true
        }
      }
      if (didPrune) {
        setAnswers(pruned)
        dispatch({ type: 'REPLACE_ANSWERS', answers: pruned })
      }
    } catch (err) {
      console.error('Visible fetch failed:', err)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }, [dispatch])

  // Fetch scores
  const fetchScores = useCallback(async (currentAnswers, ctx) => {
    const context = ctx || contextRef.current
    if (!context) return
    setScoresLoading(true)
    try {
      const res = await api.post('/assessment/scores', {
        answers: currentAnswers,
        context,
        phase: context.project_phase || 'mid_dev',
      })
      setScores(res.data)
      dispatch({ type: 'SET_ENGINE_SCORES', scores: res.data })
    } catch (err) {
      console.error('Scores fetch failed:', err)
    } finally {
      setScoresLoading(false)
    }
  }, [dispatch])

  // Initial fetch when entering Phase 3 (use context answers to survive remount)
  useEffect(() => {
    if (phase === 3 && categories.length === 0 && state.contextAnswers) {
      const persisted = state.miraAnswers || {}
      fetchVisible(persisted, state.contextAnswers, true)
      fetchScores(persisted, state.contextAnswers)
    }
  }, [phase, state.contextAnswers]) // eslint-disable-line react-hooks/exhaustive-deps

  // ── Answer handling ─────────────────────────────────────────────────
  function handleAnswer(questionId, value) {
    const next = { ...answers, [questionId]: value }
    setAnswers(next)
    dispatch({ type: 'SET_ANSWER', questionId, value })

    // Debounced visibility + scores refresh
    clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(() => {
      fetchVisible(next)
      fetchScores(next)
    }, 300)
  }

  // ── Navigation ──────────────────────────────────────────────────────
  function handleSkipToResults() {
    navigate('/comparison')
  }

  function handleNextCategory() {
    if (currentCatIdx < categories.length - 1) {
      setCurrentCatIdx(currentCatIdx + 1)
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
  }

  function handlePrevCategory() {
    if (currentCatIdx > 0) {
      setCurrentCatIdx(currentCatIdx - 1)
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
  }

  function handleFinish() {
    navigate('/comparison')
  }

  // ── Render ──────────────────────────────────────────────────────────

  // Phase 1: Context form
  if (phase === 1) {
    return (
      <div className="max-w-[1400px] mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-2">Project Context</h1>
        <p className="text-sm text-[var(--text-secondary)] mb-6">
          Tell us about your project. These questions determine which structural archetype
          best matches your situation and set the baseline for the maturity assessment.
        </p>
        <ContextForm onComplete={handleContextComplete} />
      </div>
    )
  }

  // Phase 2: Capacity self-assessment
  if (phase === 2) {
    return (
      <SelfAssessmentPhase
        archetype={state.bridgeResult?.archetype}
        confidence={state.bridgeResult?.confidence}
        matchDistance={state.bridgeResult?.match_distance}
        onComplete={(sliders, role) => {
          dispatch({ type: 'SET_SELF_ASSESSMENT', sliders, role })
        }}
      />
    )
  }

  // Phase 3: Maturity questions
  const currentCat = categories[currentCatIdx]
  const totalAnswered = Object.keys(answers).length
  const totalVisible = categories.reduce((sum, cat) => sum + cat.questions.length, 0)
  const answerPct = getAnswerPct(totalAnswered, totalVisible)
  const pctColour = answerPctColour(answerPct)
  const isSufficient = answerPct >= MINIMUM_ANSWER_PCT

  return (
    <div className="max-w-[1400px] mx-auto px-4 py-6 space-y-4">
      {/* Archetype result banner */}
      <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-lg p-4 space-y-1">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-bold text-[var(--text-primary)]">{state.bridgeResult.archetype}</p>
            <p className="text-sm text-[var(--text-muted)]">
              {state.bridgeResult.confidence} match
              {state.bridgeResult.match_distance != null &&
                ` — distance: ${state.bridgeResult.match_distance.toFixed(2)}`
              }
            </p>
          </div>
          <button
            onClick={handleSkipToResults}
            className="flex items-center gap-1.5 px-3 py-1.5 text-sm text-[var(--text-muted)] border border-[var(--border)] rounded-md hover:bg-[var(--bg-hover)] hover:text-[var(--text-primary)] transition-colors"
          >
            <SkipForward className="w-3.5 h-3.5" /> Skip to Results
          </button>
        </div>
      </div>

      {/* Score preview */}
      {scores && (
        <div className="grid grid-cols-3 gap-3">
          <ScoreBox label="Capability" value={scores.capability_pct} loading={scoresLoading} />
          <ScoreBox label="Operational" value={scores.operational_pct} loading={scoresLoading} />
          <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-md p-3 text-center">
            <p className="text-sm text-[var(--text-muted)] mb-1">Progress</p>
            <p className="text-lg font-bold">{totalAnswered} / {totalVisible}</p>
            <div className="w-full h-1.5 bg-[var(--bg-primary)] rounded-full mt-2 mb-1.5 overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-300"
                style={{
                  width: `${Math.min(answerPct * 100, 100)}%`,
                  backgroundColor: pctColour,
                }}
              />
            </div>
            <p className="text-xs" style={{ color: pctColour }}>
              {isSufficient ? 'Sufficient for submission' : 'Insufficient for submission'}
            </p>
          </div>
        </div>
      )}

      {/* Category tabs */}
      <div className="overflow-x-auto -mx-4 px-4">
        <div className="flex gap-1 min-w-max">
          {categories.map((cat, idx) => {
            const answered = cat.questions.filter(q => answers[q.id] !== undefined).length
            const total = cat.questions.length
            const complete = answered === total && total > 0
            const isCurrent = idx === currentCatIdx
            const hasNote = !!state.categoryNotes[cat.id]

            return (
              <button
                key={cat.id}
                onClick={() => setCurrentCatIdx(idx)}
                className={`relative flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm whitespace-nowrap transition-colors ${
                  isCurrent
                    ? 'bg-[var(--accent)] text-white'
                    : complete
                      ? 'bg-green-900/30 text-green-400'
                      : 'bg-[var(--bg-card)] text-[var(--text-muted)] hover:bg-[var(--bg-hover)]'
                }`}
              >
                {complete && <CheckCircle className="w-3 h-3" />}
                {cat.name}
                <span className="opacity-60">{answered}/{total}</span>
                {hasNote && (
                  <span className="absolute -top-1 -right-1 w-2 h-2 bg-[var(--accent)] rounded-full" />
                )}
              </button>
            )
          })}
        </div>
      </div>

      {/* Loading overlay */}
      {loading && categories.length === 0 && (
        <div className="flex items-center justify-center gap-2 py-12 text-[var(--text-muted)]">
          <Loader2 className="w-5 h-5 animate-spin" /> Loading questions...
        </div>
      )}

      {/* Current category questions */}
      {currentCat && (
        <div className="space-y-3">
          <div>
            <h2 className="text-lg font-semibold">{currentCat.name}</h2>
            <p className="text-sm text-[var(--text-muted)]">{currentCat.description}</p>
          </div>

          <div className={`space-y-2 relative transition-opacity duration-200 ${refreshing ? 'opacity-60 pointer-events-none' : ''}`}>
            {refreshing && (
              <div className="absolute inset-0 flex items-start justify-center pt-4 z-10">
                <span className="flex items-center gap-1.5 text-xs text-[var(--text-muted)] bg-[var(--bg-card)] border border-[var(--border)] rounded-full px-3 py-1 shadow-lg">
                  <Loader2 className="w-3 h-3 animate-spin" /> Updating questions...
                </span>
              </div>
            )}
            {currentCat.questions.map(q => (
              <QuestionCard
                key={q.id}
                question={q}
                value={answers[q.id]}
                onChange={val => handleAnswer(q.id, val)}
              />
            ))}
          </div>

          {/* Category navigation */}
          <div className="flex items-center justify-between pt-4 border-t border-[var(--border)]">
            <button
              onClick={handlePrevCategory}
              disabled={currentCatIdx === 0}
              className="px-4 py-2 text-sm text-[var(--text-muted)] border border-[var(--border)] rounded-md hover:bg-[var(--bg-hover)] disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              Previous
            </button>

            {/* Note button */}
            <button
              onClick={() => setNoteModalOpen(true)}
              className={`flex items-center gap-1.5 px-3 py-2 text-sm rounded-md border transition-colors ${
                state.categoryNotes[currentCat.id]
                  ? 'border-[var(--accent)] text-[var(--accent)] bg-[var(--accent)]/10 hover:bg-[var(--accent)]/20'
                  : 'border-[var(--border)] text-[var(--text-muted)] hover:bg-[var(--bg-hover)]'
              }`}
              title="Add a comment or suggestion for this category"
            >
              {state.categoryNotes[currentCat.id]
                ? <><MessageSquareText className="w-4 h-4" /> Edit Note</>
                : <><MessageSquarePlus className="w-4 h-4" /> Add Note</>
              }
            </button>

            {currentCatIdx < categories.length - 1 ? (
              <button
                onClick={handleNextCategory}
                className="flex items-center gap-1.5 px-4 py-2 text-sm bg-[var(--accent)] text-white rounded-md hover:bg-[var(--accent-hover)] transition-colors"
              >
                Next: {categories[currentCatIdx + 1]?.name} <ChevronRight className="w-4 h-4" />
              </button>
            ) : (
              <button
                onClick={handleFinish}
                className="flex items-center gap-1.5 px-4 py-2 text-sm bg-[var(--accent)] text-white rounded-md hover:bg-[var(--accent-hover)] transition-colors"
              >
                View Results <ArrowRight className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>
      )}

      {/* Note modal */}
      {currentCat && (
        <NoteModal
          isOpen={noteModalOpen}
          onClose={() => setNoteModalOpen(false)}
          onSave={note => dispatch({ type: 'SET_CATEGORY_NOTE', categoryId: currentCat.id, note })}
          categoryName={currentCat.name}
          initialValue={state.categoryNotes[currentCat.id] || ''}
        />
      )}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Phase 2: Capacity Self-Assessment
// ---------------------------------------------------------------------------

const CAPACITY_QUESTIONS = [
  {
    key: 'inv',
    label: 'Investment in Quality',
    prompt: 'How much can your project invest in improving quality right now?',
    scope: 'Think broadly: hiring or contracting additional resource, purchasing tools or licences, funding training, or dedicating existing staff time to quality initiatives.',
    options: [
      'Nothing — no budget, no headcount, no time allocated',
      'Very little — token effort only (e.g. one person part-time)',
      'Some — modest but real investment (e.g. dedicated budget or resource)',
      'Good — well-supported programme (e.g. funded team, tools, training)',
      'Significant — quality improvement is a funded strategic priority',
    ],
  },
  {
    key: 'rec',
    label: 'Recovery from Setbacks',
    prompt: 'When the project hits a serious setback, how well can it absorb the impact and recover?',
    scope: 'Examples: a critical defect found late, a failed release, a key team member leaving, a major requirement change, or a security incident. Consider the whole project, not just your team.',
    options: [
      "We can't recover — a serious setback would threaten the project",
      'Poorly — recovery takes weeks and derails other work',
      'With difficulty — we get through it but it sets us back significantly',
      'Reasonably well — we have contingency plans and can absorb most setbacks',
      'Very well — setbacks are routine and we have the resilience to handle them',
    ],
  },
  {
    key: 'owk',
    label: 'Team Overwork',
    prompt: 'How much is the team currently relying on extra effort to meet commitments?',
    scope: 'Consider: regular overtime, weekend work, skipping breaks, people covering multiple roles, or consistently working beyond contracted hours. Sustained overwork, not occasional crunch.',
    options: [
      'Not at all — the team works at a sustainable pace',
      'A little — occasional late evenings around deadlines',
      'Moderately — regular overtime is expected to meet commitments',
      'Heavily — the team is stretched thin and people are burning out',
      'Constantly — delivery depends on people working well beyond capacity',
    ],
  },
  {
    key: 'time',
    label: 'Schedule Pressure',
    prompt: 'How much time pressure is the project under?',
    scope: 'Consider whether there is slack in the schedule for quality activities: code reviews, proper testing, refactoring, documentation. Not just deadline pressure, but whether quality can be given time.',
    options: [
      'Extreme — no slack, quality activities are regularly cut to meet dates',
      'High — tight deadlines, quality gets squeezed',
      'Moderate — some breathing room for quality work',
      'Low — comfortable timeline, quality activities are rarely compromised',
      'Very relaxed — time to do things properly without schedule pressure',
    ],
  },
]

const ROLE_OPTIONS = [
  'Project / Delivery Manager',
  'Test Manager / QA Lead',
  'Developer / Architect',
  'Senior Manager / Sponsor',
  'Other',
]

function SelfAssessmentPhase({ archetype, confidence, matchDistance, onComplete }) {
  const [selections, setSelections] = useState({})
  const [role, setRole] = useState('')
  const [customRole, setCustomRole] = useState('')

  const allAnswered = CAPACITY_QUESTIONS.every(q => selections[q.key] !== undefined)

  function handleSelect(key, idx) {
    setSelections(prev => ({ ...prev, [key]: idx }))
  }

  function handleContinue() {
    if (!allAnswered) return
    // Map 0-4 indices to [0, 0.25, 0.5, 0.75, 1.0]
    const sliders = CAPACITY_QUESTIONS.map(q => selections[q.key] * 0.25)
    const finalRole = role === 'Other' ? (customRole.trim() || 'Other') : (role || null)
    onComplete(sliders, finalRole)
  }

  return (
    <div className="max-w-[1400px] mx-auto px-4 py-6 space-y-5">
      {/* Archetype banner */}
      <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-lg p-4">
        <p className="text-sm font-bold text-[var(--text-primary)]">{archetype}</p>
        <p className="text-sm text-[var(--text-muted)]">
          {confidence} match
          {matchDistance != null && ` — distance: ${matchDistance.toFixed(2)}`}
        </p>
      </div>

      {/* Research context */}
      <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-lg p-5 space-y-3">
        <h2 className="text-lg font-semibold">Capacity Self-Assessment</h2>
        <div className="text-sm text-[var(--text-secondary)] space-y-2">
          <p>
            Before the detailed assessment, we'd like your instinctive view of four capacity
            dimensions that shape your project's viability. There are no right answers — this
            captures <em>your perspective</em> as a practitioner, which may differ from what the
            model predicts or what the detailed questions reveal.
          </p>
          <p>
            That difference is itself valuable research data. Every self-assessment measures the
            organisation as seen through one person's lens — a project manager, test lead, and
            developer assessing the same project will each emphasise different things. By capturing
            your gut feeling separately, we can measure how respondent perspective shapes the
            assessment and where the model needs calibration.
          </p>
        </div>
      </div>

      {/* Four capacity questions */}
      {CAPACITY_QUESTIONS.map(q => (
        <div key={q.key} className="bg-[var(--bg-card)] border border-[var(--border)] rounded-lg p-4 space-y-3">
          <div>
            <h3 className="text-sm font-semibold text-[var(--text-primary)]">{q.label}</h3>
            <p className="text-sm text-[var(--text-muted)] mt-0.5">{q.prompt}</p>
            {q.scope && (
              <p className="text-xs text-[var(--text-muted)] mt-1.5 leading-relaxed italic">{q.scope}</p>
            )}
          </div>
          <div className="grid gap-1.5">
            {q.options.map((opt, idx) => {
              const selected = selections[q.key] === idx
              return (
                <button
                  key={idx}
                  onClick={() => handleSelect(q.key, idx)}
                  className={`text-left text-sm px-3 py-2 rounded-md border transition-colors ${
                    selected
                      ? 'border-[var(--accent)] bg-[var(--accent)]/15 text-[var(--text-primary)]'
                      : 'border-[var(--border)] text-[var(--text-secondary)] hover:bg-[var(--bg-hover)] hover:text-[var(--text-primary)]'
                  }`}
                >
                  {opt}
                </button>
              )
            })}
          </div>
        </div>
      ))}

      {/* Respondent role (optional) */}
      <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-lg p-4 space-y-3">
        <div>
          <h3 className="text-sm font-semibold text-[var(--text-primary)]">
            Your Role <span className="font-normal text-[var(--text-muted)]">(optional)</span>
          </h3>
          <p className="text-sm text-[var(--text-muted)] mt-0.5">
            Knowing your role helps us understand how perspective shapes assessment.
            This is entirely optional and anonymous.
          </p>
        </div>
        <div className="grid gap-1.5">
          {ROLE_OPTIONS.map(opt => {
            const selected = role === opt
            return (
              <button
                key={opt}
                onClick={() => setRole(prev => prev === opt ? '' : opt)}
                className={`text-left text-sm px-3 py-2 rounded-md border transition-colors ${
                  selected
                    ? 'border-[var(--accent)] bg-[var(--accent)]/15 text-[var(--text-primary)]'
                    : 'border-[var(--border)] text-[var(--text-secondary)] hover:bg-[var(--bg-hover)] hover:text-[var(--text-primary)]'
                }`}
              >
                {opt}
              </button>
            )
          })}
          {role === 'Other' && (
            <input
              type="text"
              value={customRole}
              onChange={e => setCustomRole(e.target.value)}
              placeholder="Describe your role..."
              className="text-sm px-3 py-2 rounded-md border border-[var(--border)] bg-[var(--bg-primary)] text-[var(--text-primary)] placeholder:text-[var(--text-muted)] focus:outline-none focus:border-[var(--accent)]"
            />
          )}
        </div>
      </div>

      {/* Continue button */}
      <div className="flex justify-end pt-2">
        <button
          onClick={handleContinue}
          disabled={!allAnswered}
          className="flex items-center gap-1.5 px-5 py-2.5 text-sm font-medium bg-[var(--accent)] text-white rounded-md hover:bg-[var(--accent-hover)] disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
          Continue to Assessment <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}


/** Small score box for the preview bar */
function ScoreBox({ label, value, loading, custom, sub }) {
  return (
    <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-md p-3 text-center">
      <p className="text-sm text-[var(--text-muted)] mb-1">{label}</p>
      {loading ? (
        <Loader2 className="w-4 h-4 animate-spin mx-auto text-[var(--text-muted)]" />
      ) : custom ? (
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
