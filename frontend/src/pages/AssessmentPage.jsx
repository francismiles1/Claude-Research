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
import { useAssessment, useAssessmentDispatch } from '../context/AssessmentContext'
import ContextForm from '../components/ContextForm'
import QuestionCard from '../components/questions/QuestionCard'
import NoteModal from '../components/NoteModal'

export default function AssessmentPage() {
  const navigate = useNavigate()
  const state = useAssessment()
  const dispatch = useAssessmentDispatch()

  // Phase tracking — need both bridgeResult AND contextAnswers for Phase 2
  // (quick-start sets bridgeResult but not contextAnswers)
  const phase = (state.bridgeResult && state.contextAnswers) ? 2 : 1

  // Phase 2 state — initialise from context to survive navigation
  const [categories, setCategories] = useState([])
  const [currentCatIdx, setCurrentCatIdx] = useState(0)
  const [answers, setAnswers] = useState(state.miraAnswers || {})
  const [scores, setScores] = useState(state.engineScores || null)
  const [loading, setLoading] = useState(false)
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
  const fetchVisible = useCallback(async (currentAnswers, ctx) => {
    const context = ctx || contextRef.current
    if (!context) return
    setLoading(true)
    try {
      const res = await api.post('/assessment/visible', {
        answers: currentAnswers,
        context,
      })
      setCategories(res.data.categories)
    } catch (err) {
      console.error('Visible fetch failed:', err)
    } finally {
      setLoading(false)
    }
  }, [])

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

  // Initial fetch when entering Phase 2 (use context answers to survive remount)
  useEffect(() => {
    if (phase === 2 && categories.length === 0 && state.contextAnswers) {
      const persisted = state.miraAnswers || {}
      fetchVisible(persisted, state.contextAnswers)
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

  // Phase 2: Maturity questions
  const currentCat = categories[currentCatIdx]
  const totalAnswered = Object.keys(answers).length
  const totalVisible = categories.reduce((sum, cat) => sum + cat.questions.length, 0)

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
          <ScoreBox label="Progress" value={null} loading={false}
            custom={`${totalAnswered} / ${totalVisible}`} sub="questions answered" />
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

          <div className="space-y-2">
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
