/**
 * Layout — top nav bar with step indicator.
 */
import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { FlaskConical, RotateCcw, AlertTriangle } from 'lucide-react'
import { useAssessment, useAssessmentDispatch } from '../context/AssessmentContext'

const STEPS = [
  { path: '/', label: 'Welcome', key: 'welcome' },
  { path: '/guide', label: 'Guide', key: 'guide' },
  { path: '/assess', label: 'Assessment', key: 'assess' },
  { path: '/comparison', label: 'Results', key: 'comparison' },
  { path: '/results', label: 'Explorer', key: 'results' },
  { path: '/identify', label: 'Feedback', key: 'identify' },
]

export default function Layout({ children }) {
  const location = useLocation()
  const navigate = useNavigate()
  const state = useAssessment()
  const dispatch = useAssessmentDispatch()
  const [showResetModal, setShowResetModal] = useState(false)

  const hasProgress = !!(state.contextAnswers || state.bridgeResult || Object.keys(state.miraAnswers || {}).length > 0)

  const currentIdx = STEPS.findIndex(s => s.path === location.pathname)

  function canNavigate(step, idx) {
    if (idx === 0) return true                      // Welcome — always
    if (idx === 1) return true                      // Guide — always
    if (idx === 2) return true                      // Assessment — always
    if (idx === 3) return !!state.contextAnswers    // Results — needs full assessment
    if (idx === 4) return !!state.bridgeResult      // Explorer — just needs archetype
    if (idx === 5) return !!state.contextAnswers    // Feedback — needs full assessment
    return false
  }

  return (
    <div className="min-h-screen flex flex-col">
      {/* Top nav */}
      <nav className="border-b border-[var(--border)] bg-[var(--bg-secondary)]">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          {/* Brand */}
          <div className="flex items-center gap-2 cursor-pointer" onClick={() => navigate('/')}>
            <FlaskConical className="w-5 h-5 text-[var(--accent)]" />
            <span className="font-semibold text-sm">Cap/Ops Balance</span>
            <span className="text-xs text-[var(--text-muted)] ml-1">Research</span>
          </div>

          {/* Steps */}
          <div className="flex items-center gap-1">
            {STEPS.map((step, idx) => {
              const isCurrent = idx === currentIdx
              const isEnabled = canNavigate(step, idx)
              const isComplete = idx < currentIdx && isEnabled

              return (
                <button
                  key={step.key}
                  onClick={() => isEnabled && navigate(step.path)}
                  disabled={!isEnabled}
                  className={`
                    px-3 py-1.5 text-xs font-medium rounded-md transition-colors
                    ${isCurrent
                      ? 'bg-[var(--accent)] text-white'
                      : isComplete
                        ? 'bg-[var(--bg-hover)] text-[var(--text-primary)] hover:bg-[var(--accent)]/20'
                        : isEnabled
                          ? 'text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-hover)]'
                          : 'text-[var(--text-muted)] cursor-not-allowed opacity-50'
                    }
                  `}
                >
                  {step.label}
                </button>
              )
            })}
          </div>

          {/* Start Over */}
          {hasProgress && (
            <button
              onClick={() => setShowResetModal(true)}
              className="flex items-center gap-1.5 px-2.5 py-1.5 text-xs text-[var(--text-muted)] hover:text-red-400 hover:bg-red-400/10 rounded-md transition-colors"
              title="Start over"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Start Over</span>
            </button>
          )}
        </div>
      </nav>

      {/* Content */}
      <main className="flex-1">
        {children}
      </main>

      {/* Reset confirmation modal */}
      {showResetModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-lg shadow-xl max-w-sm w-full mx-4 p-6 space-y-4">
            <div className="flex items-start gap-3">
              <AlertTriangle className="w-6 h-6 text-amber-400 shrink-0 mt-0.5" />
              <div className="space-y-2">
                <h3 className="text-base font-semibold text-[var(--text-primary)]">Start over?</h3>
                <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
                  This will clear all your progress — context answers, assessment
                  responses, and any Explorer adjustments. This cannot be undone.
                </p>
              </div>
            </div>
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setShowResetModal(false)}
                className="px-4 py-2 text-sm border border-[var(--border)] rounded-md hover:bg-[var(--bg-hover)] transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  dispatch({ type: 'RESET' })
                  setShowResetModal(false)
                  navigate('/')
                }}
                className="px-4 py-2 text-sm bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
              >
                Yes, start over
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
