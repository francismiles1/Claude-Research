/**
 * GuidePage — how the platform works + detailed screen instructions.
 *
 * Always accessible from the nav. Covers the assessment flow, results
 * interpretation, explorer interaction, and key concepts.
 */
import { useNavigate } from 'react-router-dom'
import {
  ClipboardList, GitCompare, Map, MessageSquare,
  ArrowRight, MousePointerClick, SlidersHorizontal, Layers,
  Target, TrendingUp, AlertTriangle, BookOpen,
} from 'lucide-react'

const FLOW = [
  { icon: ClipboardList, label: 'Assessment', time: '5–10 min', colour: 'text-blue-400' },
  { icon: GitCompare, label: 'Results', time: '2–5 min', colour: 'text-emerald-400' },
  { icon: Map, label: 'Explorer', time: 'Open-ended', colour: 'text-amber-400' },
  { icon: MessageSquare, label: 'Feedback', time: '1–2 min', colour: 'text-purple-400' },
]

export default function GuidePage() {
  const navigate = useNavigate()

  return (
    <div className="max-w-[1400px] mx-auto px-6 py-10 space-y-10">

      {/* ── Header ───────────────────────────────────────────────── */}
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <BookOpen className="w-7 h-7 text-[var(--accent)]" />
          <h1 className="text-2xl font-bold">Guide</h1>
        </div>
        <p className="text-base text-[var(--text-secondary)]">
          How the platform works, what each screen does, and how to get the most
          value from the interactive tools.
        </p>
      </div>

      {/* ── Overview — the 4-step flow ───────────────────────────── */}
      <Section id="overview" title="The Flow" icon={ArrowRight}>
        <p className="text-sm text-[var(--text-secondary)] mb-4">
          The full process takes approximately 10–20 minutes. Each step builds on the
          previous, but you can navigate freely once a step is unlocked.
        </p>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {FLOW.map((step, idx) => {
            const Icon = step.icon
            return (
              <div
                key={step.label}
                className="bg-[var(--bg-card)] border border-[var(--border)] rounded-lg p-4 text-center space-y-2"
              >
                <div className="flex items-center justify-center gap-2">
                  <span className="text-xs font-bold text-[var(--text-muted)]">{idx + 1}</span>
                  <Icon className={`w-5 h-5 ${step.colour}`} />
                </div>
                <p className="text-sm font-semibold">{step.label}</p>
                <p className="text-xs text-[var(--text-muted)]">{step.time}</p>
              </div>
            )
          })}
        </div>
      </Section>

      {/* ── Assessment Guide ─────────────────────────────────────── */}
      <Section id="assessment" title="Assessment" icon={ClipboardList}>
        <div className="space-y-4">
          <div className="space-y-2">
            <h3 className="text-base font-semibold">Phase 1: Project Context</h3>
            <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
              Nine questions capture your project's structural profile. These map to
              eight dimensions — Consequence, Market Pressure, Complexity, Regulation,
              Team Stability, Outsourcing, Lifecycle, and Coherence — each scored 1–5.
              The model uses Euclidean distance in this 8D space to find the closest
              structural archetype.
            </p>
            <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
              Answer honestly about your current project, not an aspirational state.
              The model works best with accurate input — there are no "right" answers.
            </p>
          </div>

          <div className="space-y-2">
            <h3 className="text-base font-semibold">Phase 2: Maturity Questions</h3>
            <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
              An adaptive questionnaire assesses your current capability and operational
              maturity. Questions are organised by category (Governance, Test Strategy,
              Test Assets, etc.) and filtered based on your context — you only see
              what's relevant to your project type.
            </p>
            <Tip>
              Questions appear and disappear as you answer. For example, selecting "No
              automation" skips all automation health questions. This is intentional —
              the assessment adapts to your situation.
            </Tip>
          </div>

          <div className="space-y-2">
            <h3 className="text-base font-semibold">Score Preview</h3>
            <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
              The top bar shows live Capability and Operational scores as you answer.
              These update with every answer. You don't need to answer every question —
              skip to results at any point for a partial assessment.
            </p>
          </div>

          <div className="space-y-2">
            <h3 className="text-base font-semibold">Category Notes</h3>
            <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
              Each category has an "Add Note" button. Use this to flag questions you
              disagree with, suggest missing questions, or explain why your situation
              is unusual. Reference question IDs (e.g. GOV-C1) for specificity. Notes
              are reviewed before final submission.
            </p>
          </div>
        </div>
      </Section>

      {/* ── Results Guide (ComparisonPage) ────────────────────────── */}
      <Section id="results" title="Results" icon={GitCompare}>
        <div className="space-y-4">
          <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
            The Results screen presents your assessment output and asks you to
            validate the model's archetype classification. It runs in three phases.
          </p>

          <div className="space-y-2">
            <h3 className="text-base font-semibold">Phase 1: Your Profile</h3>
            <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
              Your dimension profile is displayed as eight horizontal bars (1–5 scale).
              Hover over any dimension to see what it measures and what your score
              means. If you completed the maturity questions, your Capability and
              Operational scores are also shown.
            </p>
          </div>

          <div className="space-y-2">
            <h3 className="text-base font-semibold">Phase 2: Self-Mapping</h3>
            <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
              You're shown all 15 structural archetypes. Expand any archetype to see a
              side-by-side dimension comparison against your profile. Select the one
              that best matches your real-world project — or select "None of these
              match" if none fits.
            </p>
            <Tip>
              Distances are deliberately hidden until after you choose. This prevents
              anchoring bias — we want your genuine assessment, not the model's
              suggestion influencing your decision. This self-mapping data is the most
              valuable research output.
            </Tip>
          </div>

          <div className="space-y-2">
            <h3 className="text-base font-semibold">Phase 3: Reveal</h3>
            <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
              After selection, the system reveals its own match alongside yours.
              You'll see the Euclidean distance (lower = closer), confidence band
              (strong/reasonable/ambiguous), and a dimension-by-dimension comparison.
              Disagreements between your choice and the system's are expected and
              especially valuable.
            </p>
          </div>
        </div>
      </Section>

      {/* ── Explorer Guide (ResultsPage) ──────────────────────────── */}
      <Section id="explorer" title="Explorer" icon={Map}>
        <div className="space-y-6">
          <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
            The Explorer is the core interactive tool — a visual answer to
            "what maturity balance does my project type need?" It shows which
            combinations of Capability and Operational maturity are viable for
            your archetype, and what makes each position sustainable or
            unsustainable.
          </p>

          {/* Heatmap */}
          <div className="space-y-2">
            <h3 className="text-base font-semibold flex items-center gap-2">
              <Layers className="w-4 h-4 text-[var(--accent)]" />
              The Heatmap
            </h3>
            <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
              A 101×101 grid where each cell represents a Capability/Operational
              maturity combination (0–100% on each axis). Colour indicates the
              combined viability margin:
            </p>
            <ul className="text-sm text-[var(--text-secondary)] leading-relaxed space-y-1 ml-4 list-disc">
              <li><strong className="text-green-400">Green</strong> — viable, sustainable position</li>
              <li><strong className="text-yellow-400">Yellow</strong> — marginal, near the boundary</li>
              <li><strong className="text-red-400">Red</strong> — unsustainable, costs exceed capacity</li>
            </ul>
            <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
              The <strong className="text-[var(--text-primary)]">white dashed
              contour</strong> marks the viable zone boundary — positions inside
              pass all three viability tests. The <strong
              className="text-[var(--text-primary)]">star marker (★)</strong> shows
              the archetype's predicted default position. The <strong
              className="text-[var(--text-primary)]">diamond marker (◆)</strong> shows
              whichever position you've clicked to inspect.
            </p>
          </div>

          {/* Click interaction */}
          <div className="space-y-2">
            <h3 className="text-base font-semibold flex items-center gap-2">
              <MousePointerClick className="w-4 h-4 text-[var(--accent)]" />
              Click to Inspect
            </h3>
            <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
              Click any position on the heatmap to inspect it. The score panel
              and cost breakdown below update to show exactly why that position is
              viable or not. Three scores are shown:
            </p>
            <ul className="text-sm text-[var(--text-secondary)] leading-relaxed space-y-1 ml-4 list-disc">
              <li><strong className="text-[var(--text-primary)]">Viable</strong> — is capability maturity above the floor? (Buffered by Recovery capacity)</li>
              <li><strong className="text-[var(--text-primary)]">Sufficient</strong> — is operational maturity above the floor? (Buffered by Overwork capacity)</li>
              <li><strong className="text-[var(--text-primary)]">Sustainable</strong> — are the four cost components within tolerance? (Investment sets the upper bound)</li>
            </ul>
            <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
              All three must pass for a position to be inside the viable zone.
            </p>
          </div>

          {/* View modes */}
          <div className="space-y-2">
            <h3 className="text-base font-semibold flex items-center gap-2">
              <Layers className="w-4 h-4 text-[var(--accent)]" />
              View Modes
            </h3>
            <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
              Four buttons switch the heatmap between different visualisations:
            </p>
            <ul className="text-sm text-[var(--text-secondary)] leading-relaxed space-y-1 ml-4 list-disc">
              <li><strong className="text-[var(--text-primary)]">Gradient</strong> (default) — combined viability margin. Green = comfortable, red = failing.</li>
              <li><strong className="text-[var(--text-primary)]">Viable</strong> — the first sigmoid test only. Shows the capability floor and Recovery buffer.</li>
              <li><strong className="text-[var(--text-primary)]">Sufficient</strong> — the second sigmoid test only. Shows the operational floor and Overwork buffer.</li>
              <li><strong className="text-[var(--text-primary)]">Sustainable</strong> — the third test only. Shows the cost sustainability boundary shaped by all four sliders.</li>
            </ul>
            <Tip>
              Use the individual views to understand which test is the binding
              constraint for your archetype. If the viable zone is narrow, switching
              views reveals whether it's a capability floor problem, a sufficiency
              problem, or a sustainability problem.
            </Tip>
          </div>

          {/* Sliders */}
          <div className="space-y-2">
            <h3 className="text-base font-semibold flex items-center gap-2">
              <SlidersHorizontal className="w-4 h-4 text-[var(--accent)]" />
              The Four Capacity Sliders
            </h3>
            <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
              Four sliders control the resourcing assumptions that shape the viable
              zone. Each represents a real-world capacity that your project either
              has or lacks:
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-2">
              <SliderCard
                name="Investment"
                desc="Can you afford to move on the grid?"
                detail="Budget, hiring, tooling, training. Dominates the sustainability upper bound for 14 of 15 archetypes. Increasing Investment expands the viable zone from the top-right."
              />
              <SliderCard
                name="Recovery"
                desc="Can you survive failures?"
                detail="Redundancy, resilience, rollback capability. Buffers the capability viability floor and sustains Ops > Cap positions. Essential for projects where operational performance outpaces governance."
              />
              <SliderCard
                name="Overwork"
                desc="Can the team compensate through effort?"
                detail="Team effort above sustainable baseline. Buffers the operational sufficiency floor. Effective short-term but unsustainable — the model treats it as a temporary capacity, not a strategy."
              />
              <SliderCard
                name="Time"
                desc="Can you afford to be slow?"
                detail="Market patience, deadline flexibility. Sustains Cap > Ops positions where governance exceeds delivery. Low Time capacity compresses the viable zone for high-governance archetypes."
              />
            </div>

            <Tip>
              Start with the defaults, then try extreme values. Drag Investment to
              minimum and watch the zone collapse. Push Overwork to maximum and see
              the short-term expansion. This reveals which sliders are binding for
              your archetype and which have diminishing returns.
            </Tip>
          </div>

          {/* Cost breakdown */}
          <div className="space-y-2">
            <h3 className="text-base font-semibold flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-[var(--accent)]" />
              Cost Breakdown
            </h3>
            <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
              Below the heatmap, the cost breakdown shows exactly why a position
              is sustainable or not. Four cost components combine to determine
              sustainability:
            </p>

            <div className="space-y-3 mt-2">
              <CostCard
                name="Gap Cost"
                desc="The cost of being off-diagonal — when capability and operational maturity diverge. Cap > Ops means 'theatre' (process without delivery); Ops > Cap means 'heroics' (delivery without process). The further off-diagonal, the higher the cost."
                compensator="Time compensates Cap > Ops gaps; Recovery compensates Ops > Cap gaps."
              />
              <CostCard
                name="Debt Cost"
                desc="Technical and process debt that compounds at low maturity levels. Very low maturity in either axis generates accelerating costs — the 'debt trap' where you can't afford to improve because you're spending everything on firefighting."
                compensator="Investment is the primary lever. Higher investment absorbs debt costs."
              />
              <CostCard
                name="Process Cost"
                desc="The overhead of governance, standards, and formal processes. High capability maturity requires investment to sustain — processes don't maintain themselves. This is the cost of rigour."
                compensator="Investment offsets process costs directly."
              />
              <CostCard
                name="Execution Cost"
                desc="The cost of maintaining delivery rhythm and operational performance. High operational maturity requires ongoing effort. This is the cost of execution quality."
                compensator="Overwork and Recovery buffer execution costs."
              />
            </div>

            <p className="text-sm text-[var(--text-secondary)] leading-relaxed mt-2">
              The <strong className="text-[var(--text-primary)]">direction
              badge</strong> (Cap &gt; Ops / Ops &gt; Cap / Balanced) shows which side
              of the diagonal you're on. This determines which compensation
              mechanisms are relevant.
            </p>
          </div>

          {/* How to explore */}
          <div className="space-y-2">
            <h3 className="text-base font-semibold flex items-center gap-2">
              <Target className="w-4 h-4 text-[var(--accent)]" />
              Getting the Most Value
            </h3>
            <div className="text-sm text-[var(--text-secondary)] leading-relaxed space-y-2">
              <p>Suggested exploration pattern:</p>
              <ol className="list-decimal ml-5 space-y-1">
                <li>Start at the <strong className="text-[var(--text-primary)]">default position</strong> (star marker). Read the cost breakdown — this is the model's prediction for where your archetype naturally sits.</li>
                <li>Click positions <strong className="text-[var(--text-primary)]">inside the viable zone</strong> (green area) to see what makes them sustainable. Compare costs at different points.</li>
                <li>Click positions <strong className="text-[var(--text-primary)]">outside the viable zone</strong> (red area) to see exactly which test fails and why.</li>
                <li>Drag <strong className="text-[var(--text-primary)]">Investment to minimum</strong>. Watch the zone collapse. This shows how dependent your archetype is on resource investment.</li>
                <li>Drag <strong className="text-[var(--text-primary)]">Overwork to maximum</strong>. See the temporary expansion. Then consider whether that's sustainable for your team.</li>
                <li>Switch between <strong className="text-[var(--text-primary)]">view modes</strong> to find which test is the binding constraint for your archetype.</li>
                <li>Try the <strong className="text-[var(--text-primary)]">archetype selector</strong> (top of the page) to compare different project types. Notice how the zone shape changes — enterprise archetypes have different viable zones from startups.</li>
              </ol>
            </div>
          </div>
        </div>
      </Section>

      {/* ── Key Concepts ──────────────────────────────────────────── */}
      <Section id="concepts" title="Key Concepts" icon={BookOpen}>
        <div className="space-y-4">
          <Concept
            term="Capability Maturity"
            definition="Process maturity, governance, standards — 'what you can do'. Measures whether the organisation has defined, documented, and institutionalised its quality practices. High capability doesn't guarantee good outcomes — it means the mechanisms exist."
          />
          <Concept
            term="Operational Maturity"
            definition="Delivery performance, execution quality, measurable outcomes — 'what you are doing'. Measures actual results: defect rates, build success, deployment frequency, test effectiveness. High operational maturity means consistent, demonstrable delivery."
          />
          <Concept
            term="Viable Zone"
            definition="The region on the Cap/Ops grid where a position passes all three viability tests (viable, sufficient, sustainable). Positions inside the zone are achievable and maintainable given the project's capacity sliders. The zone's size and shape depend on the archetype and slider settings."
          />
          <Concept
            term="Structural Archetype"
            definition="One of 15 named project types defined by their dimension profile, not by industry domain. A fintech startup and a gaming startup may share the same archetype if their structural dimensions (consequence, complexity, regulation, etc.) are similar. The taxonomy is a working hypothesis under validation."
          />
          <Concept
            term="The 8 Dimensions"
            definition="Consequence (failure impact), Market Pressure (competitive urgency), Complexity (system scope), Regulation (compliance burden), Team Stability (workforce continuity), Outsourcing (external dependency), Lifecycle (product maturity), Coherence (organisational alignment). Each scored 1–5, together they define the project's structural shape."
          />
          <Concept
            term="The 4 Capacity Sliders"
            definition="Investment (budget/resources), Recovery (resilience/redundancy), Overwork (team effort above baseline), Time (deadline flexibility). These are the resourcing levers that reshape the viable zone. They represent what the organisation chooses to allocate, not what it inherently is."
          />
        </div>
      </Section>

      {/* ── CTA ──────────────────────────────────────────────────── */}
      <div className="flex justify-center pt-4">
        <button
          onClick={() => navigate('/assess')}
          className="flex items-center gap-2 px-6 py-3 bg-[var(--accent)] text-white text-sm font-semibold rounded-lg hover:bg-[var(--accent-hover)] transition-colors"
        >
          Begin Assessment <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}

/* ── Shared sub-components ─────────────────────────────────────────── */

function Section({ id, title, icon: Icon, children }) {
  return (
    <section id={id} className="space-y-4">
      <div className="flex items-center gap-2">
        <Icon className="w-5 h-5 text-[var(--accent)]" />
        <h2 className="text-xl font-semibold">{title}</h2>
      </div>
      <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-lg p-6">
        {children}
      </div>
    </section>
  )
}

function Tip({ children }) {
  return (
    <div className="flex gap-2 bg-amber-900/15 border border-amber-700/30 rounded-md p-3 mt-2">
      <AlertTriangle className="w-4 h-4 text-amber-400 mt-0.5 flex-shrink-0" />
      <p className="text-sm text-[var(--text-secondary)] leading-relaxed">{children}</p>
    </div>
  )
}

function SliderCard({ name, desc, detail }) {
  return (
    <div className="bg-[var(--bg-primary)] border border-[var(--border)] rounded-md p-4 space-y-1">
      <p className="text-sm font-semibold text-[var(--text-primary)]">{name}</p>
      <p className="text-xs font-medium text-[var(--accent)]">{desc}</p>
      <p className="text-sm text-[var(--text-secondary)] leading-relaxed">{detail}</p>
    </div>
  )
}

function CostCard({ name, desc, compensator }) {
  return (
    <div className="bg-[var(--bg-primary)] border border-[var(--border)] rounded-md p-4 space-y-2">
      <p className="text-sm font-semibold text-[var(--text-primary)]">{name}</p>
      <p className="text-sm text-[var(--text-secondary)] leading-relaxed">{desc}</p>
      <p className="text-xs text-[var(--text-muted)] italic">{compensator}</p>
    </div>
  )
}

function Concept({ term, definition }) {
  return (
    <div className="border-l-2 border-[var(--accent)] pl-4 space-y-1">
      <p className="text-sm font-semibold text-[var(--text-primary)]">{term}</p>
      <p className="text-sm text-[var(--text-secondary)] leading-relaxed">{definition}</p>
    </div>
  )
}
