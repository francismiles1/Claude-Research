/**
 * ConsentBanner — persistent banner at top of page requesting data consent.
 * App works fully without consent; logging is simply skipped.
 * Consent state persisted in localStorage + AssessmentContext.
 */
import { useState, useEffect } from 'react'
import { Shield, X } from 'lucide-react'
import { useAssessment, useAssessmentDispatch } from '../context/AssessmentContext'

const STORAGE_KEY = 'capops_consent'

export default function ConsentBanner() {
  const state = useAssessment()
  const dispatch = useAssessmentDispatch()
  const [dismissed, setDismissed] = useState(false)

  // Restore consent from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored === 'true' && !state.consentGiven) {
      dispatch({ type: 'SET_CONSENT' })
    }
    if (stored === 'dismissed') {
      setDismissed(true)
    }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  function handleConsent() {
    localStorage.setItem(STORAGE_KEY, 'true')
    dispatch({ type: 'SET_CONSENT' })
  }

  function handleDismiss() {
    localStorage.setItem(STORAGE_KEY, 'dismissed')
    setDismissed(true)
  }

  // Already consented or dismissed
  if (state.consentGiven || dismissed) return null

  return (
    <div className="bg-blue-900/30 border-b border-blue-700/50">
      <div className="max-w-7xl mx-auto px-4 py-3 flex items-center gap-3">
        <Shield className="w-5 h-5 text-blue-400 flex-shrink-0" />
        <p className="text-xs text-blue-200 flex-1">
          <strong>Research data.</strong> This tool is part of an academic research project.
          If you consent, your anonymised responses will be stored for analysis.
          No personal information is collected. You can use the tool fully without consenting.
        </p>
        <button
          onClick={handleConsent}
          className="flex-shrink-0 px-3 py-1 text-xs font-medium bg-blue-600 text-white rounded-md hover:bg-blue-500 transition-colors"
        >
          I consent
        </button>
        <button
          onClick={handleDismiss}
          className="flex-shrink-0 p-1 text-blue-400 hover:text-white transition-colors"
          title="Dismiss"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}
