/**
 * WelcomePage — research overview, Cap/Ops grid explanation, interactive flow,
 * and entry points.
 *
 * Academic tone. Explains the novel concept (two-axis maturity grid), why it
 * matters, what participation involves, model limitations, and how data is used.
 * Two entry points: full assessment (primary) and quick-start archetype
 * explorer (secondary).
 */
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  FlaskConical, ArrowRight, BookOpen,
  AlertTriangle, Linkedin,
} from 'lucide-react'
import api from '../api/client'
import { useAssessment, useAssessmentDispatch } from '../context/AssessmentContext'

/** Quadrant data for the Cap/Ops grid visual */
const QUADRANTS = [
  {
    key: 'heroics',
    label: 'Heroics',
    row: 0, col: 0,
    colour: 'text-orange-400',
    bg: 'bg-orange-900/15',
    border: 'border-orange-700/30',
    desc: 'Results through individual effort, not system. Fast but fragile — when key people leave, performance collapses.',
    example: 'Startup shipping fast with no documentation',
  },
  {
    key: 'mature',
    label: 'Mature',
    row: 0, col: 1,
    colour: 'text-green-400',
    bg: 'bg-green-900/15',
    border: 'border-green-700/30',
    desc: 'Process and execution aligned. Reliable, scalable, and sustainable — but requires significant investment to reach.',
    example: 'Enterprise with strong governance and delivery',
  },
  {
    key: 'adhoc',
    label: 'Ad Hoc',
    row: 1, col: 0,
    colour: 'text-red-400',
    bg: 'bg-red-900/15',
    border: 'border-red-700/30',
    desc: 'Minimal process, minimal results. Acceptable for very early-stage projects with low stakes — unsustainable otherwise.',
    example: 'Weekend prototype, internal tool hack',
  },
  {
    key: 'theatre',
    label: 'Theatre',
    row: 1, col: 1,
    colour: 'text-blue-400',
    bg: 'bg-blue-900/15',
    border: 'border-blue-700/30',
    desc: 'Strong governance, weak execution. Processes exist on paper but don\'t translate to delivery. Common in compliance-heavy environments.',
    example: 'Regulated org with perfect docs but late delivery',
  },
]

export default function WelcomePage() {
  const navigate = useNavigate()
  const state = useAssessment()
  const dispatch = useAssessmentDispatch()
  const [archetypes, setArchetypes] = useState(null)
  const [selected, setSelected] = useState('')
  const [loading, setLoading] = useState(false)
  const [showQuickStart, setShowQuickStart] = useState(false)
  const [hoveredQuadrant, setHoveredQuadrant] = useState(null)

  useEffect(() => {
    api.get('/meta/archetypes').then(r => setArchetypes(r.data))
  }, [])

  async function handleQuickStart() {
    if (!selected || !archetypes) return
    setLoading(true)
    const arch = archetypes.archetypes[selected]
    dispatch({
      type: 'SET_CONTEXT_RESULT',
      contextAnswers: null,
      bridgeResult: {
        archetype: selected,
        dimensions: arch.dimensions,
        confidence: 'direct',
      },
      defaultSliders: arch.default_sliders,
      defaultPosition: arch.default_position,
    })
    setLoading(false)
    navigate('/results')
  }

  return (
    <div className="max-w-[1400px] mx-auto px-6 py-12 space-y-12">

      {/* ── Hero ──────────────────────────────────────────────────── */}
      <div className="text-center space-y-5">
        <div className="flex items-center justify-center gap-3">
          <FlaskConical className="w-10 h-10 text-[var(--accent)]" />
          <h1 className="text-4xl font-bold">Cap/Ops Balance Model</h1>
        </div>
        <p className="text-xl text-[var(--text-secondary)] leading-relaxed max-w-3xl mx-auto">
          A research instrument exploring whether there is a derivable equilibrium
          on the Capability vs Operational maturity grid that maximises software
          project success, parameterised by project type.
        </p>
      </div>

      {/* ── The Problem ──────────────────────────────────────────── */}
      <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-lg p-8 space-y-4">
        <h2 className="text-xl font-semibold">The Problem</h2>
        <p className="text-base text-[var(--text-secondary)] leading-relaxed">
          Every major maturity framework — CMMI, TMMi, SPICE, TPI Next — treats
          maturity as a <strong className="text-[var(--text-primary)]">single
          ladder</strong>: higher is better, and everyone should climb. But
          practitioners know intuitively that this is wrong. A three-person startup
          does not need (and cannot afford) enterprise governance. A medical device
          company cannot operate on startup heroics. An agile team shipping daily
          should not be penalised for lacking a waterfall gate review.
        </p>
        <p className="text-base text-[var(--text-secondary)] leading-relaxed">
          The industry measures maturity on <em>one axis</em> and prescribes the
          same direction for everyone. This model proposes something different: <strong
          className="text-[var(--text-primary)]">two independent axes</strong>, where
          the right position depends on your project type.
        </p>
      </div>

      {/* ── The Cap/Ops Grid — conceptual visual ─────────────────── */}
      <div className="space-y-5">
        <div className="space-y-2">
          <h2 className="text-xl font-semibold">The Two-Axis Grid</h2>
          <p className="text-base text-[var(--text-secondary)] leading-relaxed">
            Traditional models conflate two fundamentally different things: <strong
            className="text-[var(--text-primary)]">what you can do</strong> (process
            maturity, governance, standards) and <strong
            className="text-[var(--text-primary)]">what you are doing</strong> (delivery
            performance, execution quality, measurable outcomes). This model separates
            them into two independent, continuously scored axes.
          </p>
        </div>

        {/* Grid visual */}
        <div className="flex gap-0 items-stretch">
          {/* Y-axis label */}
          <div className="flex flex-col items-center justify-center pr-3 flex-shrink-0">
            <div className="writing-mode-vertical text-sm font-semibold text-[var(--text-primary)] tracking-wider"
                 style={{ writingMode: 'vertical-rl', transform: 'rotate(180deg)' }}>
              OPERATIONAL MATURITY
            </div>
          </div>

          <div className="flex-1 space-y-1">
            {/* Y-axis high/low labels */}
            <div className="grid grid-cols-2 gap-3">
              {/* Top row: High Ops */}
              {QUADRANTS.filter(q => q.row === 0).map(q => (
                <button
                  key={q.key}
                  onMouseEnter={() => setHoveredQuadrant(q.key)}
                  onMouseLeave={() => setHoveredQuadrant(null)}
                  className={`${q.bg} border ${q.border} rounded-lg p-5 text-left transition-all cursor-default ${
                    hoveredQuadrant === q.key ? 'ring-1 ring-[var(--text-muted)] scale-[1.01]' : ''
                  }`}
                >
                  <div className="flex items-baseline justify-between mb-2">
                    <span className={`text-lg font-bold ${q.colour}`}>{q.label}</span>
                    {q.row === 0 && q.col === 0 && (
                      <span className="text-xs text-[var(--text-muted)] opacity-70">Low Cap / High Ops</span>
                    )}
                    {q.row === 0 && q.col === 1 && (
                      <span className="text-xs text-[var(--text-muted)] opacity-70">High Cap / High Ops</span>
                    )}
                  </div>
                  <p className="text-sm text-[var(--text-secondary)] leading-relaxed">{q.desc}</p>
                  <p className="text-xs text-[var(--text-muted)] mt-2 italic">e.g. {q.example}</p>
                </button>
              ))}
            </div>

            <div className="grid grid-cols-2 gap-3">
              {/* Bottom row: Low Ops */}
              {QUADRANTS.filter(q => q.row === 1).map(q => (
                <button
                  key={q.key}
                  onMouseEnter={() => setHoveredQuadrant(q.key)}
                  onMouseLeave={() => setHoveredQuadrant(null)}
                  className={`${q.bg} border ${q.border} rounded-lg p-5 text-left transition-all cursor-default ${
                    hoveredQuadrant === q.key ? 'ring-1 ring-[var(--text-muted)] scale-[1.01]' : ''
                  }`}
                >
                  <div className="flex items-baseline justify-between mb-2">
                    <span className={`text-lg font-bold ${q.colour}`}>{q.label}</span>
                    {q.row === 1 && q.col === 0 && (
                      <span className="text-xs text-[var(--text-muted)] opacity-70">Low Cap / Low Ops</span>
                    )}
                    {q.row === 1 && q.col === 1 && (
                      <span className="text-xs text-[var(--text-muted)] opacity-70">High Cap / Low Ops</span>
                    )}
                  </div>
                  <p className="text-sm text-[var(--text-secondary)] leading-relaxed">{q.desc}</p>
                  <p className="text-xs text-[var(--text-muted)] mt-2 italic">e.g. {q.example}</p>
                </button>
              ))}
            </div>

            {/* X-axis label */}
            <div className="text-center pt-2">
              <span className="text-sm font-semibold text-[var(--text-primary)] tracking-wider">
                CAPABILITY MATURITY &rarr;
              </span>
            </div>
          </div>
        </div>

        {/* Axis definitions */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-lg p-5 space-y-2">
            <h3 className="text-base font-semibold text-[var(--text-primary)]">
              Capability Maturity <span className="text-sm font-normal text-[var(--text-muted)]">
              &mdash; &ldquo;What you can do&rdquo;</span>
            </h3>
            <ul className="text-sm text-[var(--text-secondary)] space-y-1 leading-relaxed">
              <li>Processes are defined, documented, institutionalised</li>
              <li>Tools, infrastructure, and standards exist</li>
              <li>Governance structures are in place</li>
              <li>The organisation has the <em>capacity</em> to perform consistently</li>
            </ul>
          </div>
          <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-lg p-5 space-y-2">
            <h3 className="text-base font-semibold text-[var(--text-primary)]">
              Operational Maturity <span className="text-sm font-normal text-[var(--text-muted)]">
              &mdash; &ldquo;What you are doing&rdquo;</span>
            </h3>
            <ul className="text-sm text-[var(--text-secondary)] space-y-1 leading-relaxed">
              <li>Evidence of execution: metrics, outcomes, delivered results</li>
              <li>Delivery performance: defect rates, build success, deployment frequency</li>
              <li>Consistency and trends demonstrating systematic performance</li>
              <li>The organisation has the <em>track record</em> to back up claims</li>
            </ul>
          </div>
        </div>
      </div>

      {/* ── The Hypothesis ───────────────────────────────────────── */}
      <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-lg p-8 space-y-4">
        <h2 className="text-xl font-semibold">The Hypothesis</h2>
        <p className="text-base text-[var(--text-secondary)] leading-relaxed">
          Success is not maximum maturity — it is <em>right-sized</em> maturity.
          Every position on the grid can succeed, but each carries costs that must
          be absorbable by the organisation. The question is: <strong
          className="text-[var(--text-primary)]">for a given project type, what is
          the viable range — and what determines its boundaries?</strong>
        </p>
        <p className="text-base text-[var(--text-secondary)] leading-relaxed">
          This model proposes 15 structural archetypes — project types characterised
          not by industry domain but by eight structural dimensions (consequence,
          market pressure, complexity, regulation, team stability, outsourcing,
          lifecycle, coherence). Each archetype has a predicted <strong
          className="text-[var(--text-primary)]">viable zone</strong> on the grid,
          shaped by four capacity sliders: Investment, Recovery, Overwork, and Time.
        </p>
      </div>

      {/* ── Building on existing work ────────────────────────────── */}
      <div className="space-y-5">
        <div className="space-y-2">
          <h2 className="text-xl font-semibold">Building on Existing Work</h2>
          <p className="text-base text-[var(--text-secondary)] leading-relaxed">
            This model does not exist in isolation. It draws on — and attempts to
            connect — ideas from several established frameworks, each of which
            addresses part of the problem.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Bach / Context-Driven */}
          <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-lg p-5 space-y-2">
            <div className="flex items-baseline gap-2">
              <span className="text-sm font-bold text-[var(--accent)]">Philosophical foundation</span>
            </div>
            <h3 className="text-base font-semibold text-[var(--text-primary)]">
              Context-Driven Testing
            </h3>
            <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
              James Bach and the context-driven school have argued since 1994 that
              appropriate maturity depends on project type — &ldquo;practices
              appropriate to one project would be criminally negligent in
              another.&rdquo; This model formalises that philosophy into a
              computable function.
            </p>
          </div>

          {/* Koenders / Osborne */}
          <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-lg p-5 space-y-2">
            <div className="flex items-baseline gap-2">
              <span className="text-sm font-bold text-[var(--accent)]">Axis validation</span>
            </div>
            <h3 className="text-base font-semibold text-[var(--text-primary)]">
              Design vs Operational Effectiveness
            </h3>
            <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
              Koenders and Osborne independently identified the same axis split —
              separating &ldquo;having capabilities&rdquo; from &ldquo;actually
              using them&rdquo; — in data governance. Their work validates that
              this decomposition is fundamental, not domain-specific. This model
              applies it to software project maturity and adds context-dependent
              targets.
            </p>
          </div>

          {/* Westerman */}
          <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-lg p-5 space-y-2">
            <div className="flex items-baseline gap-2">
              <span className="text-sm font-bold text-[var(--accent)]">Structural precedent</span>
            </div>
            <h3 className="text-base font-semibold text-[var(--text-primary)]">
              Digital Maturity Matrix
            </h3>
            <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
              Westerman et al. (MIT, 2014) demonstrated that a two-axis maturity
              grid produces richer insight than a single ladder. Their model treats
              the top-right quadrant as universally desirable. This model adopts the
              two-axis structure but rejects the universal target — the right
              position depends on your project type.
            </p>
          </div>

          {/* CMMI + DORA as measurement */}
          <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-lg p-5 space-y-2">
            <div className="flex items-baseline gap-2">
              <span className="text-sm font-bold text-[var(--accent)]">Measurement instruments</span>
            </div>
            <h3 className="text-base font-semibold text-[var(--text-primary)]">
              CMMI, TMMi, DORA
            </h3>
            <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
              Existing frameworks already measure the individual axes well. CMMI
              and TMMi assess process capability; DORA measures delivery
              performance. This model does not replace them — it sits above
              them as a contextualisation layer, connecting their measurements
              to the question: <em>&ldquo;given your project type, what should
              those scores be?&rdquo;</em>
            </p>
          </div>
        </div>

        <div className="bg-[var(--bg-primary)] border border-[var(--border)] rounded-md p-5">
          <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
            <strong className="text-[var(--text-primary)]">The connective layer.</strong> Each
            of these frameworks addresses part of the problem: Bach provides the philosophical
            licence, Koenders validates the axis decomposition, Westerman proves the 2D structure,
            and CMMI/DORA provide measurement instruments. What appears to be missing — and what
            this research explores — is the layer that connects measurement to context: a model
            that takes project characteristics as input and outputs a viable maturity range on
            both axes simultaneously. This has not, to our knowledge, been formally proposed in
            software engineering literature.
          </p>
        </div>
      </div>

      {/* ── The classification gap ────────────────────────────────── */}
      <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-lg p-8 space-y-4">
        <h2 className="text-xl font-semibold">The Classification Gap</h2>
        <p className="text-base text-[var(--text-secondary)] leading-relaxed">
          Surprisingly, the software industry has never settled on a structural
          taxonomy of project types. Shenhar &amp; Dvir (2007) studied 600+ projects
          across four dimensions but deliberately avoided naming discrete types.
          Kruchten (2013) identified 13 contextual dimensions for agile projects but
          derived no categories. Cockburn, Boehm, and others proposed 2–5 dimension
          models with at most a handful of broad categories. <strong
          className="text-[var(--text-primary)]">No published framework defines named
          structural archetypes of software projects with outcome predictions.</strong>
        </p>
        <p className="text-base text-[var(--text-secondary)] leading-relaxed">
          This model proposes 15 named archetypes across 8 dimensions — more granular
          than anything in the literature. Whether 15 is the right number, whether the
          dimensions are the right ones, and whether the taxonomy captures real-world
          project diversity are open questions. That is precisely what we are testing.
        </p>
      </div>

      {/* ── Why we need your help ─────────────────────────────────── */}
      <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-lg p-8 space-y-4">
        <h2 className="text-xl font-semibold">Why We Need Your Help</h2>
        <p className="text-base text-[var(--text-secondary)] leading-relaxed">
          The model's constants are theoretically derived, not empirically calibrated.
          The 15 archetypes were designed to cover the software project landscape, but
          we do not know whether the taxonomy is comprehensive or the parameterisation
          accurate. <strong className="text-[var(--text-primary)]">We need real-world
          practitioners to test the model against their experience.</strong>
        </p>
        <p className="text-base text-[var(--text-secondary)] leading-relaxed">
          Specifically, we are investigating:
        </p>
        <ul className="text-base text-[var(--text-secondary)] leading-relaxed space-y-2 list-disc list-inside">
          <li>Do real projects map cleanly to the 15 archetypes?</li>
          <li>Where is the dimensional divergence when the match is imperfect?</li>
          <li>Are there project types the taxonomy does not capture?</li>
          <li>Does the assessment produce maturity scores that practitioners recognise?</li>
        </ul>
      </div>

      {/* ── The bigger picture ───────────────────────────────────── */}
      <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-lg p-8 space-y-4">
        <h2 className="text-xl font-semibold">The Bigger Picture</h2>
        <p className="text-base text-[var(--text-secondary)] leading-relaxed">
          This research is the foundation for a <strong
          className="text-[var(--text-primary)]">continuous maturity and risk
          assessment tool</strong>. The goal is not a one-time classification — it
          is an instrument that can derive a close approximation to how a software
          project works and where it is vulnerable, then track its position on the
          Cap/Ops grid over time.
        </p>
        <p className="text-base text-[var(--text-secondary)] leading-relaxed">
          Imagine a tool that can detect when a project is drifting out of its viable
          zone, derive risk-based measures from the gap between where you are and
          where your project type needs to be, and calculate maturity on an ongoing
          basis — not as a static audit, but as a living assessment that evolves
          with the project.
        </p>
        <p className="text-base text-[var(--text-secondary)] leading-relaxed">
          Before that tool can be built, the archetype taxonomy and its
          parameterisation must be validated against real-world experience. <strong
          className="text-[var(--text-primary)]">That is what this assessment
          does.</strong> Every response helps us determine whether the model's
          predictions match practitioner reality — and where they do not, what
          needs to change.
        </p>
      </div>

      {/* ── How it works — guide link ──────────────────────────────── */}
      <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-lg p-6 flex items-center justify-between">
        <div className="space-y-1">
          <h2 className="text-lg font-semibold">How It Works</h2>
          <p className="text-sm text-[var(--text-secondary)]">
            A four-step process taking approximately 10–20 minutes. The Guide covers
            each screen in detail and explains how to get the most from the results.
          </p>
        </div>
        <button
          onClick={() => navigate('/guide')}
          className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-[var(--accent)] border border-[var(--accent)] rounded-md hover:bg-[var(--accent)]/10 transition-colors flex-shrink-0 ml-4"
        >
          <BookOpen className="w-4 h-4" /> View Guide
        </button>
      </div>

      {/* ── Model transparency ────────────────────────────────────── */}
      <div className="bg-amber-900/15 border border-amber-700/30 rounded-lg p-6 space-y-3">
        <div className="flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-amber-400 flex-shrink-0" />
          <h3 className="text-base font-semibold text-amber-400">Model Limitations</h3>
        </div>
        <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
          This is a static equilibrium model, not a dynamic simulation. All capacity
          sliders take effect instantaneously — the model cannot represent transition
          dynamics (e.g. the lag between hiring and productivity). The success function
          constants are domain-derived, not empirically fitted. The 15-archetype taxonomy
          is a working hypothesis, not an established classification. Your participation
          helps determine whether these simplifications produce useful predictions.
        </p>
      </div>

      {/* ── Data use ──────────────────────────────────────────────── */}
      <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-lg p-6 space-y-3">
        <h3 className="text-base font-semibold text-[var(--text-primary)]">Data &amp; Privacy</h3>
        <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
          If you consent (via the banner below), your anonymised responses are stored
          for research analysis. No personally identifiable information is collected.
          The assessment works fully without consent — you simply will not contribute
          to the aggregated dataset. All data is used solely to validate and improve
          the model.
        </p>
      </div>

      {/* ── Call to action ────────────────────────────────────────── */}
      <div className="space-y-5">
        <button
          onClick={() => navigate('/assess')}
          className="w-full flex items-center justify-center gap-2 px-6 py-4 bg-[var(--accent)] text-white text-base font-semibold rounded-lg hover:bg-[var(--accent-hover)] transition-colors"
        >
          Begin Assessment <ArrowRight className="w-5 h-5" />
        </button>

        {/* Quick start toggle */}
        <div className="text-center">
          <button
            onClick={() => setShowQuickStart(!showQuickStart)}
            className="text-sm text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors"
          >
            {showQuickStart ? 'Hide quick start' : 'Already familiar? Quick-start with an archetype'}
          </button>
        </div>

        {showQuickStart && archetypes && (
          <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-lg p-5 space-y-3">
            <p className="text-sm text-[var(--text-muted)]">
              If you already know which archetype to explore, select one below to skip
              directly to the interactive explorer. This bypasses the assessment and
              comparison steps.
            </p>
            <select
              value={selected}
              onChange={e => setSelected(e.target.value)}
              className="w-full bg-[var(--bg-primary)] border border-[var(--border)] rounded-md px-3 py-2 text-sm text-[var(--text-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent)]"
            >
              <option value="">Choose an archetype...</option>
              {archetypes.archetype_order.map(name => (
                <option key={name} value={name}>{name}</option>
              ))}
            </select>
            <button
              onClick={handleQuickStart}
              disabled={!selected || loading}
              className="flex items-center gap-2 px-4 py-2 bg-[var(--accent)] text-white text-sm font-medium rounded-md hover:bg-[var(--accent-hover)] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Explore Archetype <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>

      {/* ── Contact ───────────────────────────────────────────────── */}
      <div className="border-t border-[var(--border)] pt-8 text-center space-y-3">
        <p className="text-base text-[var(--text-secondary)]">
          This research is conducted by <strong className="text-[var(--text-primary)]">Francis Miles</strong>.
        </p>
        <a
          href="https://www.linkedin.com/in/francismiles/"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 text-base text-[var(--accent)] hover:underline"
        >
          <Linkedin className="w-5 h-5" /> Connect on LinkedIn
        </a>
        <p className="text-sm text-[var(--text-muted)] mt-2">
          Questions, feedback, or collaboration enquiries are welcome.
        </p>
      </div>
    </div>
  )
}
