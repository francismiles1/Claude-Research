import { lazy, Suspense } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AssessmentProvider } from './context/AssessmentContext'
import Layout from './components/Layout'
import { Loader2 } from 'lucide-react'

// Eager — lightweight pages loaded immediately
import WelcomePage from './pages/WelcomePage'
import GuidePage from './pages/GuidePage'
import ResearchPage from './pages/ResearchPage'

// Lazy — heavy pages (Plotly, question engine) loaded on demand
const AssessmentPage = lazy(() => import('./pages/AssessmentPage'))
const ComparisonPage = lazy(() => import('./pages/ComparisonPage'))
const ResultsPage = lazy(() => import('./pages/ResultsPage'))
const IdentifyPage = lazy(() => import('./pages/IdentifyPage'))

function PageLoader() {
  return (
    <div className="flex items-center justify-center py-24 text-[var(--text-muted)]">
      <Loader2 className="w-6 h-6 animate-spin" />
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
