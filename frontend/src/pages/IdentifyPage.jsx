/**
 * IdentifyPage — self-identification + feedback.
 *
 * Three options:
 * 1. "I match an existing persona" → dropdown of 12 personas
 * 2. "I'm a new persona" → structured form
 * 3. "Skip" → no identification
 *
 * Plus optional feedback form (free text + 1-5 rating).
 * Logs to Supabase if consent was given.
 */
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { User, UserPlus, SkipForward, Send, Star, Loader2, CheckCircle, Pencil, Trash2, MessageSquare, Shield } from 'lucide-react'
import api from '../api/client'
import { useAssessment, useAssessmentDispatch } from '../context/AssessmentContext'
import { MINIMUM_ANSWER_PCT, getAnswerPct } from '../constants'
import NoteModal from '../components/NoteModal'


export default function IdentifyPage() {
  const navigate = useNavigate()
  const state = useAssessment()
  const dispatch = useAssessmentDispatch()

  const [personas, setPersonas] = useState({})
  const [idType, setIdType] = useState(null) // existing_persona | new_persona | skip
  const [selectedPersona, setSelectedPersona] = useState('')
  const [newPersona, setNewPersona] = useState({})
  const [feedbackText, setFeedbackText] = useState('')
  const [rating, setRating] = useState(null)
  const [displayName, setDisplayName] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [submitted, setSubmitted] = useState(false)
  const [editingNoteCategory, setEditingNoteCategory] = useState(null)

  const isQuickStart = state.flowType === 'quick_start'

  // Answer sufficiency check — only applies to full assessment flow
  const answerPct = getAnswerPct(
    state.engineScores?.questions_answered ?? 0,
    state.engineScores?.questions_visible ?? 0
  )
  const hasSufficientAnswers = isQuickStart || answerPct >= MINIMUM_ANSWER_PCT

  // Redirect if no assessment done
  useEffect(() => {
    if (!state.bridgeResult) navigate('/')
  }, [state.bridgeResult, navigate])

  // Fetch persona list
  useEffect(() => {
    api.get('/meta/archetypes').then(r => setPersonas(r.data.personas || {}))
  }, [])

  // Compute whether calibration changes exist
  const hasCalibrationChanges = !!(
    state.currentSliders && state.defaultSliders &&
    (state.currentSliders.some((v, i) => Math.abs(v - state.defaultSliders[i]) > 0.001) ||
     (state.inspectCap != null && state.defaultPosition &&
      (Math.abs(state.inspectCap - state.defaultPosition[0]) > 0.001 ||
       Math.abs(state.inspectOps - state.defaultPosition[1]) > 0.001)))
  )

  async function handleSubmit() {
    setSubmitting(true)

    try {
      // Log assessment first if not already logged
      let assessmentId = state.assessmentId
      if (!assessmentId && state.bridgeResult) {
        const logRes = await api.post('/log/assessment', {
          session_id: state.sessionId,
          bridge_result: state.bridgeResult,
          context: state.contextAnswers || {},
          sliders: state.currentSliders || state.defaultSliders || [],
          cap: state.defaultPosition?.[0] || 0.5,
          ops: state.defaultPosition?.[1] || 0.5,
          assessed_cap: state.engineScores?.capability_pct != null
            ? state.engineScores.capability_pct / 100 : null,
          assessed_ops: state.engineScores?.operational_pct != null
            ? state.engineScores.operational_pct / 100 : null,
          flow_type: state.flowType || 'quick_start',
          has_calibration_changes: hasCalibrationChanges,
          self_inv: state.selfAssessedSliders?.[0] ?? null,
          self_rec: state.selfAssessedSliders?.[1] ?? null,
          self_owk: state.selfAssessedSliders?.[2] ?? null,
          self_time: state.selfAssessedSliders?.[3] ?? null,
          respondent_role: state.respondentRole || null,
        })
        assessmentId = logRes.data.id
        if (assessmentId) {
          dispatch({ type: 'SET_ASSESSMENT_ID', id: assessmentId })
        }
      }

      // Log identification
      if (idType && idType !== 'skip') {
        await api.post('/log/identify', {
          session_id: state.sessionId,
          assessment_id: assessmentId,
          id_type: idType,
          persona_name: idType === 'existing_persona' ? selectedPersona : null,
          new_persona: idType === 'new_persona' ? newPersona : null,
        })
      }

      // Log maturity answers (if any)
      if (Object.keys(state.miraAnswers).length > 0) {
        await api.post('/log/maturity', {
          session_id: state.sessionId,
          assessment_id: assessmentId,
          answers: state.miraAnswers,
          capability_pct: state.engineScores?.capability_pct || 0,
          operational_pct: state.engineScores?.operational_pct || 0,
          unified_pct: state.engineScores?.unified_pct || 0,
          category_scores: state.engineScores?.category_scores || {},
          questions_answered: state.engineScores?.questions_answered || 0,
          questions_visible: state.engineScores?.questions_visible || 0,
        })
      }

      // Log self-mapping choice (if user went through comparison)
      if (state.selfMapChoice || state.selfMapNoneMatch) {
        await api.post('/log/self_map', {
          session_id: state.sessionId,
          assessment_id: assessmentId,
          user_choice: state.selfMapChoice,
          user_says_none_match: state.selfMapNoneMatch,
          none_match_description: state.selfMapNoneMatchDesc,
          system_match: state.bridgeResult?.archetype || '',
          system_distance: state.bridgeResult?.match_distance || 0,
          system_confidence: state.bridgeResult?.confidence || '',
        })
      }

      // Log feedback (including category notes)
      const hasNotes = Object.keys(state.categoryNotes).length > 0
      if (feedbackText.trim() || rating || hasNotes) {
        await api.post('/log/feedback', {
          session_id: state.sessionId,
          assessment_id: assessmentId,
          feedback_text: feedbackText.trim(),
          rating,
          display_name: displayName.trim() || null,
          category_notes: state.categoryNotes,
        })
      }
    } catch (err) {
      console.error('Logging failed:', err)
      // Graceful — don't block the user
    }

    setSubmitting(false)
    setSubmitted(true)
  }

  if (!state.bridgeResult) return null

  if (submitted) {
    return (
      <div className="max-w-[1400px] mx-auto px-4 py-16 text-center">
        <CheckCircle className="w-12 h-12 text-green-400 mx-auto mb-4" />
        <h1 className="text-2xl font-bold mb-2">Thank you!</h1>
        <p className="text-[var(--text-secondary)] mb-6">
          {state.consentGiven
            ? 'Your response has been recorded. It will help us validate the model.'
            : 'Your session is complete. No data was recorded (consent not given).'}
        </p>
        <div className="flex gap-3 justify-center">
          <button
            onClick={() => { dispatch({ type: 'RESET' }); navigate('/') }}
            className="px-4 py-2 text-sm border border-[var(--border)] rounded-md hover:bg-[var(--bg-hover)] transition-colors"
          >
            Start Over
          </button>
          <button
            onClick={() => navigate('/results')}
            className="px-4 py-2 text-sm bg-[var(--accent)] text-white rounded-md hover:bg-[var(--accent-hover)] transition-colors"
          >
            Back to Results
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-[1400px] mx-auto px-4 py-8 space-y-8">
      <div className="space-y-3">
        <h1 className="text-2xl font-bold">
          {isQuickStart ? 'Submit Feedback' : 'Identify Your Profile'}
        </h1>
        {isQuickStart ? (
          <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
            You explored the <strong className="text-[var(--text-primary)]">
            {state.bridgeResult?.archetype || 'unknown'}</strong> archetype via quick-start.
            Any slider adjustments you made on the Explorer are saved as calibration data
            — this helps us tune the model against real-world experience. You can also
            leave general feedback below.
          </p>
        ) : (
          <>
            <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
              The model was developed using <strong className="text-[var(--text-primary)]">12 reference
              profiles</strong> — synthetic project descriptions designed to test whether the archetype
              matching and maturity scoring work correctly. These are not exhaustive — they are validation
              cases covering a range of project shapes (startup to enterprise, agile to waterfall,
              regulated to unregulated).
            </p>
            <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
              The system matched your project to the archetype <strong className="text-[var(--text-primary)]">
              {state.bridgeResult?.archetype || 'unknown'}</strong>. Below, you can tell us whether any
              of the reference profiles resemble your real project — or describe something new.
              <strong className="text-[var(--text-primary)]"> If none match, that is valuable data</strong> — it
              tells us the model's coverage has gaps.
            </p>
          </>
        )}
      </div>

      {/* Identification type selection */}
      <div className="space-y-3">
        <h2 className="text-sm font-semibold text-[var(--text-secondary)]">
          Does your project resemble any of these reference profiles?
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <IdButton
            icon={User}
            label="Existing Profile"
            desc="I recognise my project"
            active={idType === 'existing_persona'}
            onClick={() => setIdType('existing_persona')}
          />
          <IdButton
            icon={UserPlus}
            label="New Profile"
            desc="My project is different"
            active={idType === 'new_persona'}
            onClick={() => setIdType('new_persona')}
          />
          <IdButton
            icon={SkipForward}
            label="Skip"
            desc="Prefer not to say"
            active={idType === 'skip'}
            onClick={() => setIdType('skip')}
          />
        </div>
      </div>

      {/* Existing persona selector */}
      {idType === 'existing_persona' && (
        <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-lg p-4 space-y-3">
          <label className="text-sm font-medium text-[var(--text-secondary)]">
            Which reference profile best describes your project?
          </label>
          <div className="space-y-2 max-h-[400px] overflow-y-auto pr-1">
            {Object.entries(personas).map(([key, persona]) => {
              const isSelected = selectedPersona === key
              return (
                <button
                  key={key}
                  onClick={() => setSelectedPersona(isSelected ? '' : key)}
                  className={`w-full text-left p-3 rounded-md border transition-colors ${
                    isSelected
                      ? 'border-[var(--accent)] bg-[var(--accent)]/10'
                      : 'border-[var(--border)] hover:border-[var(--text-muted)]'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0">
                      <p className="text-sm font-medium text-[var(--text-primary)]">{key}</p>
                      {persona.description && (
                        <p className="text-xs text-[var(--text-muted)] mt-0.5">{persona.description}</p>
                      )}
                    </div>
                    {isSelected && (
                      <CheckCircle className="w-4 h-4 text-[var(--accent)] shrink-0 mt-0.5" />
                    )}
                  </div>
                </button>
              )
            })}
          </div>
        </div>
      )}

      {/* New profile form */}
      {idType === 'new_persona' && (
        <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-lg p-4 space-y-4">
          <p className="text-xs text-[var(--text-muted)]">
            Your project's structural characteristics were already captured in the context
            form. Here, tell us what makes your project different from the 12 reference profiles
            — this helps us identify gaps in the model's coverage.
          </p>
          <div className="space-y-1">
            <label className="text-xs font-medium text-[var(--text-secondary)]">
              Short label for your project type
            </label>
            <input
              type="text"
              maxLength={80}
              value={newPersona.label || ''}
              onChange={e => setNewPersona(prev => ({ ...prev, label: e.target.value }))}
              placeholder="e.g. 'EdTech SaaS with mixed offshore team'"
              className="w-full bg-[var(--bg-primary)] border border-[var(--border)] rounded-md px-3 py-1.5 text-sm text-[var(--text-primary)] placeholder:text-[var(--text-muted)] focus:outline-none focus:ring-1 focus:ring-[var(--accent)]"
            />
          </div>
          <div className="space-y-1">
            <label className="text-xs font-medium text-[var(--text-secondary)]">
              What makes your project different?
            </label>
            <textarea
              value={newPersona.description || ''}
              onChange={e => setNewPersona(prev => ({ ...prev, description: e.target.value }))}
              maxLength={1000}
              rows={4}
              placeholder="What's distinctive about your project that the reference profiles don't capture? e.g. unusual team structure, domain-specific constraints, hybrid delivery challenges..."
              className="w-full bg-[var(--bg-primary)] border border-[var(--border)] rounded-md px-3 py-2 text-sm text-[var(--text-primary)] placeholder:text-[var(--text-muted)] focus:outline-none focus:ring-1 focus:ring-[var(--accent)] resize-y"
            />
          </div>
        </div>
      )}

      {/* Assessment notes review — full assessment only */}
      {!isQuickStart && (
        <>
          <div className="space-y-3">
            <h2 className="text-sm font-semibold text-[var(--text-secondary)]">
              Your Assessment Notes
            </h2>
            {Object.keys(state.categoryNotes).length > 0 ? (
              <div className="space-y-2">
                {Object.entries(state.categoryNotes).map(([catId, note]) => (
                  <div
                    key={catId}
                    className="flex items-start gap-3 bg-[var(--bg-card)] border border-[var(--border)] rounded-lg px-4 py-3"
                  >
                    <MessageSquare className="w-4 h-4 text-[var(--accent)] mt-0.5 shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-medium text-[var(--text-secondary)] mb-1">
                        {catId.split('_').map(w => w[0].toUpperCase() + w.slice(1)).join(' ')}
                      </p>
                      <p className="text-sm text-[var(--text-primary)] whitespace-pre-wrap">{note}</p>
                    </div>
                    <div className="flex gap-1 shrink-0">
                      <button
                        onClick={() => setEditingNoteCategory(catId)}
                        className="p-1 rounded text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-hover)] transition-colors"
                        title="Edit note"
                      >
                        <Pencil className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => dispatch({ type: 'SET_CATEGORY_NOTE', categoryId: catId, note: '' })}
                        className="p-1 rounded text-[var(--text-muted)] hover:text-red-400 hover:bg-[var(--bg-hover)] transition-colors"
                        title="Delete note"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-[var(--text-muted)] italic">
                No category notes added during the assessment.
              </p>
            )}
          </div>

          {/* Note edit modal */}
          <NoteModal
            isOpen={!!editingNoteCategory}
            onClose={() => setEditingNoteCategory(null)}
            onSave={note => {
              dispatch({ type: 'SET_CATEGORY_NOTE', categoryId: editingNoteCategory, note })
              setEditingNoteCategory(null)
            }}
            categoryName={editingNoteCategory || ''}
            initialValue={editingNoteCategory ? (state.categoryNotes[editingNoteCategory] || '') : ''}
          />
        </>
      )}

      {/* Feedback section */}
      <div className="space-y-4">
        <h2 className="text-sm font-semibold text-[var(--text-secondary)]">
          Feedback (optional)
        </h2>

        {/* Star rating */}
        <div className="space-y-1">
          <label className="text-xs text-[var(--text-muted)]">
            {isQuickStart ? 'How useful was this tool?' : 'How useful was this assessment?'}
          </label>
          <div className="flex gap-1">
            {[1, 2, 3, 4, 5].map(n => (
              <button
                key={n}
                onClick={() => setRating(rating === n ? null : n)}
                className="p-1 transition-colors"
              >
                <Star
                  className={`w-6 h-6 ${
                    rating != null && n <= rating
                      ? 'text-yellow-400 fill-yellow-400'
                      : 'text-[var(--text-muted)]'
                  }`}
                />
              </button>
            ))}
          </div>
        </div>

        {/* Free text feedback */}
        <div className="space-y-1">
          <label className="text-xs text-[var(--text-muted)]">
            Comments, suggestions, or corrections
          </label>
          <textarea
            value={feedbackText}
            onChange={e => setFeedbackText(e.target.value)}
            maxLength={2000}
            rows={3}
            className="w-full bg-[var(--bg-primary)] border border-[var(--border)] rounded-md px-3 py-2 text-sm text-[var(--text-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent)] resize-y"
            placeholder="Any thoughts on the model's accuracy for your project?"
          />
        </div>

        {/* Display name */}
        <div className="space-y-1">
          <label className="text-xs text-[var(--text-muted)]">
            Display name (optional — leave blank for anonymous)
          </label>
          <input
            type="text"
            value={displayName}
            onChange={e => setDisplayName(e.target.value)}
            maxLength={100}
            className="w-full bg-[var(--bg-primary)] border border-[var(--border)] rounded-md px-3 py-1.5 text-sm text-[var(--text-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent)]"
            placeholder="Anonymous"
          />
        </div>
      </div>

      {/* Data consent */}
      <div className="bg-blue-900/20 border border-blue-700/40 rounded-lg p-4 space-y-3">
        <div className="flex items-start gap-3">
          <Shield className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
          <div className="space-y-2">
            <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
              <strong className="text-[var(--text-primary)]">Research data consent.</strong> If
              you consent, your anonymised responses will be stored for analysis. No personal
              information is collected. The tool works fully without consenting — your session
              simply won't contribute to the research dataset.
            </p>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={state.consentGiven}
                onChange={e => {
                  if (e.target.checked) {
                    localStorage.setItem('capops_consent', 'true')
                    dispatch({ type: 'SET_CONSENT' })
                  }
                }}
                disabled={state.consentGiven}
                className="w-4 h-4 rounded border-[var(--border)] accent-[var(--accent)]"
              />
              <span className={`text-sm ${state.consentGiven ? 'text-green-400' : 'text-[var(--text-primary)]'}`}>
                {state.consentGiven
                  ? 'Consent given — your responses will be recorded'
                  : 'I consent to my anonymised responses being stored for research'
                }
              </span>
            </label>
          </div>
        </div>
      </div>

      {/* Submit */}
      {state.consentGiven && hasSufficientAnswers ? (
        <button
          onClick={handleSubmit}
          disabled={submitting}
          className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-[var(--accent)] text-white text-sm font-medium rounded-md hover:bg-[var(--accent-hover)] disabled:opacity-50 transition-colors"
        >
          {submitting ? (
            <><Loader2 className="w-4 h-4 animate-spin" /> Submitting...</>
          ) : (
            <><Send className="w-4 h-4" /> Submit &amp; Finish</>
          )}
        </button>
      ) : (
        <div className="space-y-2">
          <button
            disabled
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-[var(--accent)] text-white text-sm font-medium rounded-md opacity-40 cursor-not-allowed"
          >
            <Send className="w-4 h-4" /> Submit &amp; Finish
          </button>
          <p className="text-xs text-center text-[var(--text-muted)]">
            {!state.consentGiven && !hasSufficientAnswers
              ? 'Tick the consent checkbox and answer at least 50% of assessment questions to submit.'
              : !state.consentGiven
                ? 'Tick the consent checkbox above to submit your responses.'
                : `Answer at least 50% of assessment questions to submit (currently ${(answerPct * 100).toFixed(0)}%).`
            }
          </p>
          <button
            onClick={() => setSubmitted(true)}
            className="w-full flex items-center justify-center gap-2 px-4 py-2 text-xs text-[var(--text-muted)] hover:text-[var(--text-secondary)] transition-colors"
          >
            <SkipForward className="w-3.5 h-3.5" /> Finish without submitting
          </button>
        </div>
      )}
    </div>
  )
}

function IdButton({ icon: Icon, label, desc, active, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`flex flex-col items-center gap-2 p-4 rounded-lg border text-center transition-colors ${
        active
          ? 'border-[var(--accent)] bg-[var(--accent)]/10'
          : 'border-[var(--border)] bg-[var(--bg-card)] hover:border-[var(--text-muted)]'
      }`}
    >
      <Icon className={`w-6 h-6 ${active ? 'text-[var(--accent)]' : 'text-[var(--text-muted)]'}`} />
      <span className="text-sm font-medium">{label}</span>
      <span className="text-xs text-[var(--text-muted)]">{desc}</span>
    </button>
  )
}
