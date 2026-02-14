import { lazy, Suspense } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AssessmentProvider } from './context/AssessmentContext'
import Layout from './components/Layout'
import { Loader2 } from 'lucide-react'

// Eager — lightweight pages loaded immediately
import WelcomePage from './pages/WelcomePage'
import GuidePage from './pages/GuidePage'
import ResearchPage from './pages/ResearchPage'

// Retry wrapper for lazy imports — handles stale chunks after deployment.
// If the dynamic import fails (old chunk hash no longer on server),
// retry once after a cache-busting reload prompt.
function lazyWithRetry(importFn) {
  return lazy(() =>
    importFn().catch(() => {
      // Stale chunk — force a full page reload to pick up new assets.
      // Guard against infinite reload loops with a sessionStorage flag.
      const key = 'capops_chunk_retry'
      if (!sessionStorage.getItem(key)) {
        sessionStorage.setItem(key, '1')
        window.location.reload()
        // Return a never-resolving promise to prevent rendering during reload
        return new Promise(() => {})
      }
      sessionStorage.removeItem(key)
      // If retry also failed, show a user-friendly error
      return { default: () => <ChunkError /> }
    })
  )
}

// Lazy — heavy pages (Plotly, question engine) loaded on demand
const AssessmentPage = lazyWithRetry(() => import('./pages/AssessmentPage'))
const ComparisonPage = lazyWithRetry(() => import('./pages/ComparisonPage'))
const ResultsPage = lazyWithRetry(() => import('./pages/ResultsPage'))
const IdentifyPage = lazyWithRetry(() => import('./pages/IdentifyPage'))

function PageLoader() {
  return (
    <div className="flex items-center justify-center py-24 text-[var(--text-muted)]">
      <Loader2 className="w-6 h-6 animate-spin" />
    </div>
  )
}

function ChunkError() {
  return (
    <div className="flex flex-col items-center justify-center py-24 text-center space-y-4">
      <p className="text-[var(--text-secondary)]">
        A new version was deployed while you were working.
        Your progress is saved — please reload to continue.
      </p>
      <button
        onClick={() => window.location.reload()}
        className="px-4 py-2 text-sm bg-[var(--accent)] text-white rounded-md hover:bg-[var(--accent-hover)] transition-colors"
      >
        Reload Page
      </button>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AssessmentProvider>
        <Layout>
          <Suspense fallback={<PageLoader />}>
            <Routes>
              <Route path="/" element={<WelcomePage />} />
              <Route path="/guide" element={<GuidePage />} />
              <Route path="/research" element={<ResearchPage />} />
              <Route path="/assess" element={<AssessmentPage />} />
              <Route path="/comparison" element={<ComparisonPage />} />
              <Route path="/results" element={<ResultsPage />} />
              <Route path="/identify" element={<IdentifyPage />} />
            </Routes>
          </Suspense>
        </Layout>
      </AssessmentProvider>
    </BrowserRouter>
  )
}
