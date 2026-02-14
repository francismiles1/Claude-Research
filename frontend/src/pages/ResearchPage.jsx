/**
 * ResearchPage — academic research background, framework relationships,
 * and the theoretical foundations of the Cap/Ops Balance Model.
 *
 * Separated from WelcomePage to give depth without overwhelming the
 * landing experience. This is the page to link in publications or
 * share with collaborators who want the full rationale.
 */
import { useNavigate } from 'react-router-dom'
import {
  Microscope, ArrowRight, Layers, Search, Telescope,
  Users, AlertTriangle, BookOpen,
} from 'lucide-react'

export default function ResearchPage() {
  const navigate = useNavigate()

  return (
    <div className="max-w-[1400px] mx-auto px-6 py-10 space-y-10">

      {/* ── Header ───────────────────────────────────────────────── */}
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <Microscope className="w-7 h-7 text-[var(--accent)]" />
          <h1 className="text-2xl font-bold">Research Background</h1>
        </div>
        <p className="text-base text-[var(--text-secondary)]">
          Theoretical foundations, prior work, and the research questions this
          platform is designed to answer.
        </p>
      </div>

      {/* ── The Core Proposition ──────────────────────────────────── */}
      <Section id="proposition" title="The Core Proposition" icon={Layers}>
        <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
          Traditional maturity models treat maturity as a single ladder — higher
          is always better. This model separates maturity into two independent
          axes: <strong className="text-[var(--text-primary)]">Capability</strong> (what
          you can do — process, governance, standards) and <strong
          className="text-[var(--text-primary)]">Operational</strong> (what you are
          doing — delivery performance, execution quality, measurable outcomes).
        </p>
        <p className="text-sm text-[var(--text-secondary)] leading-relaxed mt-3">
          The hypothesis is that success is not maximum maturity but <em>right-sized</em> maturity.
          Every position on the grid can succeed, but each carries costs that must be
          absorbable by the organisation. The question becomes: for a given project type,
          what is the viable range — and what determines its boundaries?
        </p>
      </Section>

      {/* ── Building on Existing Work ────────────────────────────── */}
      <Section id="prior-work" title="Building on Existing Work" icon={BookOpen}>
        <p className="text-sm text-[var(--text-secondary)] leading-relaxed mb-5">
          This model does not exist in isolation. It draws on — and attempts to
          connect — ideas from several established frameworks, each of which
          addresses part of the problem.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FrameworkCard
            tag="Philosophical foundation"
            title="Context-Driven Testing"
            body={<>
              James Bach and the context-driven school have argued since 1994 that
              appropriate maturity depends on project type — &ldquo;practices
              appropriate to one project would be criminally negligent in
              another.&rdquo; This model formalises that philosophy into a
              computable function.
            </>}
          />
          <FrameworkCard
            tag="Axis validation"
            title="Design vs Operational Effectiveness"
            body={<>
              Koenders and Osborne independently identified the same axis split —
              separating &ldquo;having capabilities&rdquo; from &ldquo;actually
              using them&rdquo; — in data governance. Their work validates that
              this decomposition is fundamental, not domain-specific. This model
              applies it to software project maturity and adds context-dependent
              targets.
            </>}
          />
          <FrameworkCard
            tag="Structural precedent"
            title="Digital Maturity Matrix"
            body={<>
              Westerman et al. (MIT, 2014) demonstrated that a two-axis maturity
              grid produces richer insight than a single ladder. Their model treats
              the top-right quadrant as universally desirable. This model adopts the
              two-axis structure but rejects the universal target — the right
              position depends on your project type.
            </>}
          />
          <FrameworkCard
            tag="Measurement instruments"
            title="CMMI, TMMi, DORA"
            body={<>
              Existing frameworks already measure the individual axes well. CMMI
              and TMMi assess process capability; DORA measures delivery
              performance. This model does not replace them — it sits above
              them as a contextualisation layer, connecting their measurements
              to the question: <em>&ldquo;given your project type, what should
              those scores be?&rdquo;</em>
            </>}
          />
        </div>

        <div className="bg-[var(--bg-primary)] border border-[var(--border)] rounded-md p-5 mt-5">
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
      </Section>

      {/* ── The Classification Gap ────────────────────────────────── */}
      <Section id="classification" title="The Classification Gap" icon={Search}>
        <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
          Surprisingly, the software industry has never settled on a structural
          taxonomy of project types. Shenhar &amp; Dvir (2007) studied 600+ projects
          across four dimensions but deliberately avoided naming discrete types.
          Kruchten (2013) identified 13 contextual dimensions for agile projects but
          derived no categories. Cockburn, Boehm, and others proposed 2–5 dimension
          models with at most a handful of broad categories. <strong
          className="text-[var(--text-primary)]">No published framework defines named
          structural archetypes of software projects with outcome predictions.</strong>
        </p>
        <p className="text-sm text-[var(--text-secondary)] leading-relaxed mt-3">
          This model proposes 15 named archetypes across 8 dimensions — more granular
          than anything in the literature. Whether 15 is the right number, whether the
          dimensions are the right ones, and whether the taxonomy captures real-world
          project diversity are open questions. That is precisely what we are testing.
        </p>
      </Section>

      {/* ── The Bigger Picture ────────────────────────────────────── */}
      <Section id="bigger-picture" title="The Bigger Picture" icon={Telescope}>
        <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
          This research is the foundation for a <strong
          className="text-[var(--text-primary)]">continuous maturity and risk
          assessment tool</strong>. The goal is not a one-time classification — it
          is an instrument that can derive a close approximation to how a software
          project works and where it is vulnerable, then track its position on the
          Cap/Ops grid over time.
        </p>
        <p className="text-sm text-[var(--text-secondary)] leading-relaxed mt-3">
          Imagine a tool that can detect when a project is drifting out of its viable
          zone, derive risk-based measures from the gap between where you are and
          where your project type needs to be, and calculate maturity on an ongoing
          basis — not as a static audit, but as a living assessment that evolves
          with the project.
        </p>
        <p className="text-sm text-[var(--text-secondary)] leading-relaxed mt-3">
          This platform tests the first half of that vision: <strong
          className="text-[var(--text-primary)]">does the archetype taxonomy and its
          parameterisation match practitioner reality?</strong> If the structural
          model is valid, it provides the strategic layer — which maturity balance is
          viable for your project type. A companion instrument (MIRA) provides the
          tactical layer — which specific KPIs to track and improve. Together they
          form two sides of the same coin: strategy and instrumentation.
        </p>
      </Section>

      {/* ── Capacity & Respondent Bias ───────────────────────────── */}
      <Section id="respondent-bias" title="Capacity & Respondent Bias" icon={Users}>
        <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
          Every self-assessment measures the organisation <em>as seen through one
          person's lens</em>. The same organisation assessed by five people in
          different roles produces five different Cap/Ops positions — not because
          anyone is wrong, but because each has different blind spots and emotional
          framing.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 mt-4">
          <BiasCard
            role="PM / Delivery Lead"
            frame="We're on track"
            bias="Over-rates process existence and investment; under-rates testing depth and QA authority"
          />
          <BiasCard
            role="Test Manager / QA Lead"
            frame="Nobody listens"
            bias="Over-rates defect severity and process gaps; under-rates team capability"
          />
          <BiasCard
            role="Developer / Architect"
            frame="Just let us build"
            bias="Over-rates tooling and automation; under-rates governance and process value"
          />
          <BiasCard
            role="Senior Manager / Sponsor"
            frame="We've funded this"
            bias="Over-rates strategic investment; under-rates execution reality and team overwork"
          />
          <BiasCard
            role="Recently Burnt Practitioner"
            frame="It's all broken"
            bias="Over-rates everything negative; driven by recent frustration rather than steady-state reality"
          />
        </div>

        <p className="text-sm text-[var(--text-secondary)] leading-relaxed mt-5">
          This isn't noise — it's signal about the organisation's internal coherence.
          But only if you can separate role-bias from reality.
        </p>

        <h3 className="text-base font-semibold text-[var(--text-primary)] mt-6 mb-2">
          How the Self-Assessment Normalises
        </h3>
        <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
          Before the detailed assessment questions, we ask four plain-English capacity
          questions — each mapped to one of the model's capacity sliders:
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-3">
          <div className="bg-[var(--bg-primary)] border border-[var(--border)] rounded-md p-3">
            <p className="text-sm font-semibold text-[var(--text-primary)]">Investment Capacity</p>
            <p className="text-xs text-[var(--text-muted)]">&ldquo;How much capacity does your organisation have to invest in quality improvement right now?&rdquo;</p>
          </div>
          <div className="bg-[var(--bg-primary)] border border-[var(--border)] rounded-md p-3">
            <p className="text-sm font-semibold text-[var(--text-primary)]">Recovery Capacity</p>
            <p className="text-xs text-[var(--text-muted)]">&ldquo;If something goes seriously wrong, how well can your team absorb and recover from it?&rdquo;</p>
          </div>
          <div className="bg-[var(--bg-primary)] border border-[var(--border)] rounded-md p-3">
            <p className="text-sm font-semibold text-[var(--text-primary)]">Team Overwork</p>
            <p className="text-xs text-[var(--text-muted)]">&ldquo;How much is your team currently compensating through extra effort or overtime?&rdquo;</p>
          </div>
          <div className="bg-[var(--bg-primary)] border border-[var(--border)] rounded-md p-3">
            <p className="text-sm font-semibold text-[var(--text-primary)]">Schedule Pressure</p>
            <p className="text-xs text-[var(--text-muted)]">&ldquo;How much schedule pressure is your project under?&rdquo;</p>
          </div>
        </div>
        <p className="text-sm text-[var(--text-secondary)] leading-relaxed mt-4">
          This achieves three things:
        </p>
        <div className="space-y-3 mt-3">
          <MechanismCard
            title="Common conceptual frame"
            desc="Forces every respondent — PM, tester, architect — to think about the same four capacity dimensions before answering questions. Role-agnostic language, no jargon. Everyone starts from the same mental model."
          />
          <MechanismCard
            title="Cognitive consistency pressure"
            desc={<>Once someone commits to &ldquo;our recovery capacity is low,&rdquo; they face
              internal pressure to answer subsequent process questions consistently. The PM
              hesitates before answering &ldquo;yes, comprehensive regression testing&rdquo;
              when they've just admitted they can't recover from failures.</>}
          />
          <MechanismCard
            title="Measurable bias"
            desc="Captures gut feeling separately from question-derived scores. The gap between self-assessed and model-derived slider values IS the bias signal — visible, measurable, and correctable across many respondents."
          />
        </div>

        <h3 className="text-base font-semibold text-[var(--text-primary)] mt-6 mb-2">
          Three-Point Triangulation
        </h3>
        <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
          The platform captures three independent reference points for each capacity
          slider, enabling triangulation:
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-3">
          <div className="bg-[var(--bg-primary)] border border-[var(--border)] rounded-md p-4">
            <p className="text-sm font-semibold text-[var(--text-primary)] mb-1">Model-Derived</p>
            <p className="text-xs text-[var(--text-muted)]">
              What the structural archetype predicts based on project dimensions.
            </p>
          </div>
          <div className="bg-[var(--bg-primary)] border border-[var(--border)] rounded-md p-4">
            <p className="text-sm font-semibold text-[var(--text-primary)] mb-1">Self-Assessed</p>
            <p className="text-xs text-[var(--text-muted)]">
              What the practitioner believes, captured before detailed questions.
            </p>
          </div>
          <div className="bg-[var(--bg-primary)] border border-[var(--border)] rounded-md p-4">
            <p className="text-sm font-semibold text-[var(--text-primary)] mb-1">Calibrated</p>
            <p className="text-xs text-[var(--text-muted)]">
              The practitioner's considered opinion after exploring the model.
            </p>
          </div>
        </div>

        <h3 className="text-base font-semibold text-[var(--text-primary)] mt-6 mb-2">
          What This Unlocks
        </h3>
        <ul className="text-sm text-[var(--text-secondary)] leading-relaxed space-y-2 list-disc list-inside">
          <li>Do PMs and testers from the same archetype systematically disagree on
            Investment? If so, the model needs role-adjusted defaults.</li>
          <li>Does self-assessed overwork predict question-derived operational scores?
            If so, a single intuitive question captures what dozens of process questions
            try to measure.</li>
          <li>When self-assessment and model defaults agree, are calibration adjustments
            smaller? If so, the model is well-calibrated for those cases.</li>
        </ul>
      </Section>

      {/* ── Model Transparency ───────────────────────────────────── */}
      <Section id="transparency" title="Model Transparency" icon={AlertTriangle}>
        <p className="text-sm text-[var(--text-secondary)] leading-relaxed mb-4">
          Honest science requires honest limitations. This model has several, and
          they are stated here rather than buried in footnotes.
        </p>
        <div className="space-y-3">
          <LimitationCard
            title="Static equilibrium, not dynamic simulation"
            desc="All four capacity sliders take effect instantaneously. The model cannot represent transition dynamics — the lag between hiring and productivity, the negative initial effect of organisational change, or the time required for process adoption. It answers 'what configuration is viable?' but not 'how long does it take to get there?'"
          />
          <LimitationCard
            title="Uncalibrated constants"
            desc="The success function parameters (sigmoid steepness, cost weights, pass thresholds) are domain-derived from practitioner experience, not empirically fitted to outcome data. They produce reasonable predictions for the 12 validation personas, but may need adjustment as real-world data accumulates."
          />
          <LimitationCard
            title="Taxonomy is a hypothesis"
            desc="The 15 archetypes and 8 dimensions are a working proposal, not an established classification. Whether 15 is the right number, whether the dimensions are the right ones, and whether the taxonomy captures real-world diversity are open questions — precisely what this platform tests."
          />
          <LimitationCard
            title="Selection bias"
            desc="People who care about quality complete the assessment. The dataset will over-represent quality-conscious practitioners. This is acknowledged and acceptable — they are the target population for the instrument being validated."
          />
        </div>
      </Section>

      {/* ── CTA ──────────────────────────────────────────────────── */}
      <div className="pt-4">
        <button
          onClick={() => navigate('/assess')}
          className="w-full flex items-center justify-center gap-2 px-6 py-4 bg-[var(--accent)] text-white text-base font-semibold rounded-lg hover:bg-[var(--accent-hover)] transition-colors"
        >
          Begin Assessment <ArrowRight className="w-5 h-5" />
        </button>
      </div>
    </div>
  )
}


// ---------------------------------------------------------------------------
// Helper components
// ---------------------------------------------------------------------------

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

function FrameworkCard({ tag, title, body }) {
  return (
    <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-lg p-5 space-y-2">
      <span className="text-sm font-bold text-[var(--accent)]">{tag}</span>
      <h3 className="text-base font-semibold text-[var(--text-primary)]">{title}</h3>
      <p className="text-sm text-[var(--text-secondary)] leading-relaxed">{body}</p>
    </div>
  )
}

function BiasCard({ role, frame, bias }) {
  return (
    <div className="bg-[var(--bg-primary)] border border-[var(--border)] rounded-md p-4 space-y-1.5">
      <p className="text-sm font-semibold text-[var(--text-primary)]">{role}</p>
      <p className="text-xs text-[var(--accent)] italic">&ldquo;{frame}&rdquo;</p>
      <p className="text-xs text-[var(--text-muted)] leading-relaxed">{bias}</p>
    </div>
  )
}

function MechanismCard({ title, desc }) {
  return (
    <div className="border-l-2 border-[var(--accent)] pl-4 py-1">
      <p className="text-sm font-semibold text-[var(--text-primary)] mb-1">{title}</p>
      <p className="text-xs text-[var(--text-secondary)] leading-relaxed">{desc}</p>
    </div>
  )
}

function LimitationCard({ title, desc }) {
  return (
    <div className="bg-amber-900/10 border border-amber-700/20 rounded-md p-4 space-y-1">
      <p className="text-sm font-semibold text-amber-400">{title}</p>
      <p className="text-xs text-[var(--text-secondary)] leading-relaxed">{desc}</p>
    </div>
  )
}
