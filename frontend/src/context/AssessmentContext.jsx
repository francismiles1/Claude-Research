/**
 * Assessment context — cross-page session state.
 * Persisted to sessionStorage so page refreshes don't lose progress.
 * Clears automatically when the browser tab closes.
 */
import { createContext, useContext, useReducer, useEffect } from 'react'
import { v4 as uuidv4 } from 'uuid'

const STORAGE_KEY = 'capops_assessment'

const AssessmentContext = createContext(null)
const DispatchContext = createContext(null)

const initialState = {
  // Consent
  consentGiven: false,
  sessionId: null,

  // Phase 1: context
  contextAnswers: null,
  bridgeResult: null,
  defaultSliders: null,
  defaultPosition: null,

  // Phase 2: maturity
  miraAnswers: {},
  engineScores: null,

  // Results page
  currentSliders: null,
  inspectCap: null,
  inspectOps: null,

  // Capacity self-assessment (front-loaded before questions)
  selfAssessedSliders: null,  // [inv, rec, owk, time] — 0-1 each
  respondentRole: null,       // string or null

  // Per-category notes (categoryId → string)
  categoryNotes: {},

  // Flow type: 'full' (assessment) | 'quick_start' (archetype only)
  flowType: null,

  // Logging
  assessmentId: null,
  maturityLogId: null,
  selfMapChoice: null,
  selfMapNoneMatch: false,
  selfMapNoneMatchDesc: '',
}

function reducer(state, action) {
  switch (action.type) {
    case 'SET_CONSENT':
      return {
        ...state,
        consentGiven: true,
        sessionId: state.sessionId || uuidv4(),
      }
    case 'SET_CONTEXT_RESULT':
      return {
        ...state,
        contextAnswers: action.contextAnswers,
        bridgeResult: action.bridgeResult,
        defaultSliders: action.defaultSliders,
        defaultPosition: action.defaultPosition,
        currentSliders: action.defaultSliders,
        inspectCap: action.defaultPosition[0],
        inspectOps: action.defaultPosition[1],
        flowType: action.contextAnswers ? 'full' : 'quick_start',
      }
    case 'SET_ANSWER':
      return {
        ...state,
        miraAnswers: { ...state.miraAnswers, [action.questionId]: action.value },
      }
    case 'SET_ANSWERS_BATCH':
      return {
        ...state,
        miraAnswers: { ...state.miraAnswers, ...action.answers },
      }
    case 'REPLACE_ANSWERS':
      return {
        ...state,
        miraAnswers: action.answers,
      }
    case 'SET_ENGINE_SCORES':
      return { ...state, engineScores: action.scores }
    case 'SET_SLIDERS':
      return { ...state, currentSliders: action.sliders }
    case 'SET_INSPECT':
      return { ...state, inspectCap: action.cap, inspectOps: action.ops }
    case 'SET_ASSESSMENT_ID':
      return { ...state, assessmentId: action.id }
    case 'SET_MATURITY_LOG_ID':
      return { ...state, maturityLogId: action.id }
    case 'SET_SELF_ASSESSMENT':
      return {
        ...state,
        selfAssessedSliders: action.sliders,
        respondentRole: action.role || null,
      }
    case 'SET_SELF_MAP':
      return {
        ...state,
        selfMapChoice: action.choice,
        selfMapNoneMatch: action.noneMatch || false,
        selfMapNoneMatchDesc: action.noneMatchDesc || '',
      }
    case 'SET_CATEGORY_NOTE': {
      const notes = { ...state.categoryNotes }
      if (action.note && action.note.trim()) {
        notes[action.categoryId] = action.note.trim()
      } else {
        delete notes[action.categoryId]
      }
      return { ...state, categoryNotes: notes }
    }
    case 'RESET':
      sessionStorage.removeItem(STORAGE_KEY)
      return { ...initialState }
    default:
      return state
  }
}

function loadPersistedState() {
  let state = initialState
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY)
    if (raw) {
      const parsed = JSON.parse(raw)
      state = { ...initialState, ...parsed }
    }
  } catch {
    // Corrupt data — start fresh
    sessionStorage.removeItem(STORAGE_KEY)
  }
  // Restore consent from localStorage (persists across tabs/sessions)
  if (!state.consentGiven && localStorage.getItem('capops_consent') === 'true') {
    state = { ...state, consentGiven: true, sessionId: state.sessionId || uuidv4() }
  }
  return state
}

export function AssessmentProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, null, loadPersistedState)

  // Persist to sessionStorage on every state change
  useEffect(() => {
    try {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(state))
    } catch {
      // Storage full or unavailable — non-critical
    }
  }, [state])

  return (
    <AssessmentContext.Provider value={state}>
      <DispatchContext.Provider value={dispatch}>
        {children}
      </DispatchContext.Provider>
    </AssessmentContext.Provider>
  )
}

export function useAssessment() {
  return useContext(AssessmentContext)
}

export function useAssessmentDispatch() {
  return useContext(DispatchContext)
}
