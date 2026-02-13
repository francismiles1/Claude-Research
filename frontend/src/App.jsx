import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AssessmentProvider } from './context/AssessmentContext'
import Layout from './components/Layout'
import WelcomePage from './pages/WelcomePage'
import GuidePage from './pages/GuidePage'
import AssessmentPage from './pages/AssessmentPage'
import ComparisonPage from './pages/ComparisonPage'
import ResultsPage from './pages/ResultsPage'
import IdentifyPage from './pages/IdentifyPage'

export default function App() {
  return (
    <BrowserRouter>
      <AssessmentProvider>
        <Layout>
          <Routes>
            <Route path="/" element={<WelcomePage />} />
            <Route path="/guide" element={<GuidePage />} />
            <Route path="/assess" element={<AssessmentPage />} />
            <Route path="/comparison" element={<ComparisonPage />} />
            <Route path="/results" element={<ResultsPage />} />
            <Route path="/identify" element={<IdentifyPage />} />
          </Routes>
        </Layout>
      </AssessmentProvider>
    </BrowserRouter>
  )
}
