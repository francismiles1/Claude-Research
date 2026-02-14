/**
 * ResultsPage — two-tab dashboard: Profile (static) + Explorer (interactive).
 *
 * Profile: archetype description, dimension profile, default slider explanations.
 * Explorer: heatmap, interactive sliders, score bar, rich cost breakdown.
 */
import { useState, useEffect, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { Loader2, ArrowRight, CheckCircle, Save } from 'lucide-react'
import api from '../api/client'
import { useAssessment, useAssessmentDispatch } from '../context/AssessmentContext'
import HeatmapPlot from '../components/results/HeatmapPlot'
import SliderControls from '../components/results/SliderControls'
import SliderSummary from '../components/results/SliderSummary'
import ScorePanel from '../components/results/ScorePanel'
import CostBreakdown from '../components/results/CostBreakdown'
import DimensionProfile from '../components/results/DimensionProfile'

const VIEW_MODES = [
  { key: 'gradient', label: 'Gradient' },
  { key: 'viable', label: 'Viable', layer: 0 },
  { key: 'sufficient', label: 'Sufficient', layer: 1 },
  { key: 'sustainable', label: 'Sustainable', layer: 2 },
]

const TABS = [
  { key: 'profile', label: 'Project Profile' },
  { key: 'explorer', label: 'Explorer' },
]

export default function ResultsPage() {
  const navigate = useNavigate()
  const state = useAssessment()
  const dispatch = useAssessmentDispatch()

  const {
    bridgeResult, defaultSliders, defaultPosition, currentSliders,
    engineScores, sessionId, assessmentId, contextAnswers, miraAnswers, consentGiven,
  } = state

  // Assessed position from maturity questions (null for quick-start users)
  const assessedCap = engineScores?.capability_pct != null ? engineScores.capability_pct / 100 : null
  const assessedOps = engineScores?.operational_pct != null ? engineScores.operational_pct / 100 : null

  const [archetypes, setArchetypes] = useState(null)
  const [gridData, setGridData] = useState(null)
  const [gradientData, setGradientData] = useState(null)
  const [zoneMetrics, setZoneMetrics] = useState(null)
  const [gridLoading, setGridLoading] = useState(false)
  const [inspectScores, setInspectScores] = useState(null)
  const [inspectBreakdown, setInspectBreakdown] = useState(null)
  const [inspectLoading, setInspectLoading] = useState(false)
  const [viewMode, setViewMode] = useState('gradient')
  const [activeTab, setActiveTab] = useState('profile')

  const debounceRef = useRef(null)
  const lastFetchedArchetype = useRef(null)

  // Practitioner calibration state
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [adjustReason, setAdjustReason] = useState('')

  const hasSliderChanges = currentSliders && defaultSliders &&
    currentSliders.some((v, i) => Math.abs(v - defaultSliders[i]) > 0.001)
  const hasPositionChange = state.inspectCap != null && defaultPosition &&
    (Math.abs(state.inspectCap - defaultPosition[0]) > 0.001 ||
     Math.abs(state.inspectOps - defaultPosition[1]) > 0.001)
  const hasDeviation = hasSliderChanges || hasPositionChange

  // Reset saved state when configuration changes
  useEffect(() => { setSaved(false) }, [currentSliders, state.inspectCap, state.inspectOps])

  useEffect(() => { if (!bridgeResult) navigate('/') }, [bridgeResult, navigate])
  useEffect(() => { api.get('/meta/archetypes').then(r => setArchetypes(r.data)) }, [])

  const fetchGrid = useCallback(async (dims, sliders) => {
    setGridLoading(true)
    try {
      const res = await api.post('/grid', { dimensions: dims, sliders })
      setGridData(res.data.grid)
      setGradientData(res.data.gradient_grid)
      setZoneMetrics({
        zoneArea: res.data.zone_area,
        capRange: res.data.cap_range,
        opsRange: res.data.ops_range,
        capFloor: res.data.cap_floor,
        opsFloor: res.data.ops_floor,
      })
    } catch (err) { console.error('Grid fetch failed:', err) }
    finally { setGridLoading(false) }
  }, [])

  const fetchInspect = useCallback(async (cap, ops, dims, sliders) => {
    setInspectLoading(true)
    try {
      const res = await api.post('/grid/inspect', { cap, ops, dimensions: dims, sliders })
      setInspectScores(res.data.scores)
      setInspectBreakdown(res.data.cost_breakdown)
    } catch (err) { console.error('Inspect fetch failed:', err) }
    finally { setInspectLoading(false) }
  }, [])

  // Save practitioner calibration (shared by manual save and auto-save on archetype change)
  // Returns true on success, false on failure.
  const saveCalibration = useCallback(async (trigger, reason) => {
    if (!bridgeResult || !defaultSliders || !currentSliders) return false
    if (!sessionId) return false
    try {
      await api.post('/log/calibration', {
        session_id: sessionId,
        assessment_id: assessmentId || null,
        archetype: bridgeResult.archetype,
        trigger,
        flow_type: state.flowType || 'quick_start',
        default_sliders: defaultSliders,
        current_sliders: currentSliders,
        default_cap: defaultPosition[0],
        default_ops: defaultPosition[1],
        assessed_cap: assessedCap,
        assessed_ops: assessedOps,
        inspect_cap: state.inspectCap,
        inspect_ops: state.inspectOps,
        context_answers: contextAnswers || null,
        maturity_answers: miraAnswers && Object.keys(miraAnswers).length > 0 ? miraAnswers : null,
        capability_pct: engineScores?.capability_pct ?? null,
        operational_pct: engineScores?.operational_pct ?? null,
        reason: reason || null,
      })
      return true
    } catch (err) {
      console.error('Calibration log failed:', err)
      return false
    }
  }, [bridgeResult, defaultSliders, currentSliders, defaultPosition,
      assessedCap, assessedOps, state.inspectCap, state.inspectOps,
      sessionId, assessmentId, contextAnswers, miraAnswers, engineScores])

  async function handleSaveCalibration() {
    setSaving(true)
    const ok = await saveCalibration('manual', adjustReason.trim() || null)
    setSaved(ok)
    setSaving(false)
  }

  useEffect(() => {
    if (!bridgeResult || !currentSliders) return
    if (lastFetchedArchetype.current === bridgeResult.archetype) return
    lastFetchedArchetype.current = bridgeResult.archetype
    fetchGrid(bridgeResult.dimensions, currentSliders)
    fetchInspect(state.inspectCap, state.inspectOps, bridgeResult.dimensions, currentSliders)
  }, [bridgeResult, currentSliders]) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (!bridgeResult || !currentSliders) return
    if (lastFetchedArchetype.current !== bridgeResult.archetype) return
    clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(() => {
      fetchGrid(bridgeResult.dimensions, currentSliders)
      fetchInspect(state.inspectCap, state.inspectOps, bridgeResult.dimensions, currentSliders)
    }, 500)
    return () => clearTimeout(debounceRef.current)
  }, [currentSliders]) // eslint-disable-line react-hooks/exhaustive-deps

  function handleArchetypeChange(name) {
    if (!archetypes || !name || name === bridgeResult?.archetype) return
    const arch = archetypes.archetypes[name]
    if (!arch) return

    // Auto-save current calibration before switching (fire-and-forget)
    if (hasDeviation) {
      saveCalibration('archetype_change', null)
    }

    lastFetchedArchetype.current = null
    setInspectScores(null)
    setInspectBreakdown(null)
    setSaved(false)
    setAdjustReason('')
    setActiveTab('profile')
    dispatch({
      type: 'SET_CONTEXT_RESULT',
      contextAnswers: null,
      bridgeResult: { archetype: name, dimensions: arch.dimensions, confidence: 'direct' },
      defaultSliders: arch.default_sliders,
      defaultPosition: arch.default_position,
    })
  }

  function handleSlidersChange(newSliders) {
    dispatch({ type: 'SET_SLIDERS', sliders: newSliders })
  }

  function handleClickPosition(cap, ops) {
    dispatch({ type: 'SET_INSPECT', cap, ops })
    if (bridgeResult && currentSliders) {
      fetchInspect(cap, ops, bridgeResult.dimensions, currentSliders)
    }
  }

  if (!bridgeResult) return null

  const activeMode = VIEW_MODES.find(m => m.key === viewMode)
  const layerIndex = activeMode?.layer ?? 3
  const archMeta = archetypes?.archetypes?.[bridgeResult.archetype]
  const description = archMeta?.description || ''

  return (
    <div className="max-w-[1400px] mx-auto px-4 py-4 space-y-3">

      {/* ── Header: archetype selector + description + zone ────── */}
      <div className="space-y-1">
        <div className="flex items-center gap-3 flex-wrap">
          {archetypes && (
            <select
              value={bridgeResult.archetype}
              onChange={e => handleArchetypeChange(e.target.value)}
              className="bg-[var(--bg-card)] border border-[var(--border)] rounded-md px-2 py-1 text-sm font-bold text-[var(--text-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent)] cursor-pointer"
            >
              {archetypes.archetype_order.map(name => (
                <option key={name} value={name}>{name}</option>
              ))}
            </select>
          )}
          {bridgeResult.confidence && bridgeResult.confidence !== 'direct' && (
            <span className="text-xs text-[var(--text-muted)]">{bridgeResult.confidence} match</span>
          )}
          {gridLoading && <Loader2 className="w-4 h-4 animate-spin text-[var(--text-muted)] ml-auto" />}
        </div>
        {description && (
          <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
            {description}
          </p>
        )}
        {zoneMetrics && (
          <p className="text-sm text-[var(--text-muted)] leading-relaxed">
            The viable zone covers <strong className="text-[var(--text-secondary)]">{zoneMetrics.zoneArea}%</strong> of
            the grid. Projects need at least <strong className="text-[var(--text-secondary)]">{pct(zoneMetrics.capFloor)}%</strong> capability
            and <strong className="text-[var(--text-secondary)]">{pct(zoneMetrics.opsFloor)}%</strong> operational
            maturity to survive. Within the zone, capability ranges
            from {pct(zoneMetrics.capRange[0])}–{pct(zoneMetrics.capRange[1])}%
            and operations from {pct(zoneMetrics.opsRange[0])}–{pct(zoneMetrics.opsRange[1])}%.
            {state.inspectCap != null && (
              <span className="ml-1">
                Currently inspecting <strong className="text-[var(--text-secondary)]">Cap {Math.round(state.inspectCap * 100)}%, Ops {Math.round(state.inspectOps * 100)}%</strong>.
              </span>
            )}
          </p>
        )}
      </div>

      {/* ── Tab bar ───────────────────────────────────────────── */}
      <div className="flex gap-1 bg-[var(--bg-card)] border border-[var(--border)] rounded-md p-0.5 w-fit">
        {TABS.map(tab => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`px-3 py-1 text-xs font-medium rounded transition-colors ${
              activeTab === tab.key
                ? 'bg-[var(--accent)] text-white'
                : 'text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-hover)]'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* ── Profile tab ───────────────────────────────────────── */}
      {activeTab === 'profile' && (
        <div className="space-y-4">
          <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-lg p-5">
            <DimensionProfile dimensions={bridgeResult.dimensions} />
          </div>
          <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-lg p-5">
            <SliderSummary defaults={defaultSliders} />
          </div>
        </div>
      )}

      {/* ── Explorer tab ──────────────────────────────────────── */}
      {activeTab === 'explorer' && (
        <div className="space-y-3">
          {/* Hint */}
          <p className="text-sm text-[var(--text-muted)] italic">
            The <span className="text-yellow-400 not-italic">&#9733;</span> star marks where this archetype naturally sits.
            {assessedCap != null && (
              <> The <span className="text-cyan-400 not-italic">&#9679;</span> circle is your assessed position from the maturity questions.</>
            )}
            {' '}Click anywhere on the heatmap to inspect a different position (<span className="text-red-400 not-italic">&#9670;</span> diamond) — the scores and cost breakdown will update.
            Adjust the capacity sliders to see how resourcing decisions reshape the viable zone.
          </p>

          {/* Score bar (full width) */}
          {inspectLoading ? (
            <div className="flex items-center gap-2 text-sm text-[var(--text-muted)] justify-center py-2">
              <Loader2 className="w-4 h-4 animate-spin" /> Calculating scores...
            </div>
          ) : (
            <ScorePanel scores={inspectScores} />
          )}

          {/* Heatmap + Sliders */}
          <div className="grid grid-cols-1 lg:grid-cols-[550px_1fr] gap-4">
            <div className="space-y-2">
              <div className="flex gap-1 bg-[var(--bg-card)] border border-[var(--border)] rounded-md p-0.5 w-fit">
                {VIEW_MODES.map(mode => (
                  <button
                    key={mode.key}
                    onClick={() => setViewMode(mode.key)}
                    className={`px-2.5 py-0.5 text-[11px] rounded transition-colors ${
                      viewMode === mode.key
                        ? 'bg-[var(--accent)] text-white'
                        : 'text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-hover)]'
                    }`}
                  >
                    {mode.label}
                  </button>
                ))}
              </div>
              <HeatmapPlot
                gridData={gridData}
                gradientData={gradientData}
                viewMode={viewMode === 'gradient' ? 'gradient' : 'sigmoid'}
                layerIndex={layerIndex}
                inspectCap={state.inspectCap}
                inspectOps={state.inspectOps}
                defaultCap={defaultPosition?.[0]}
                defaultOps={defaultPosition?.[1]}
                assessedCap={assessedCap}
                assessedOps={assessedOps}
                capFloor={zoneMetrics?.capFloor}
                opsFloor={zoneMetrics?.opsFloor}
                onClickPosition={handleClickPosition}
              />
            </div>
            <div>
              <SliderControls
                sliders={currentSliders}
                defaults={defaultSliders}
                onChange={handleSlidersChange}
              />
            </div>
          </div>

          {/* Cost breakdown (full width) */}
          <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-lg p-5">
            <CostBreakdown breakdown={inspectBreakdown} />
          </div>

          {/* Practitioner calibration */}
          <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-lg p-4">
            {saved ? (
              <div className="flex items-center gap-2 text-sm text-green-400">
                <CheckCircle className="w-4 h-4" /> Practitioner calibration saved
              </div>
            ) : !consentGiven ? (
              <p className="text-sm text-[var(--text-muted)]">
                <strong className="text-[var(--text-secondary)]">Practitioner Calibration</strong> — your
                slider adjustments and confirmation will be saved when you consent and submit on the Feedback page.
              </p>
            ) : hasDeviation ? (
              <div className="space-y-3">
                <p className="text-sm text-[var(--text-secondary)]">
                  <strong className="text-[var(--text-primary)]">Save Practitioner Calibration</strong> — your
                  slider adjustments help calibrate the model against real-world experience.
                </p>
                <div className="flex items-center gap-3">
                  <input
                    type="text"
                    value={adjustReason}
                    onChange={e => setAdjustReason(e.target.value)}
                    maxLength={200}
                    placeholder="Why did you adjust? (optional)"
                    className="flex-1 bg-[var(--bg-primary)] border border-[var(--border)] rounded-md px-3 py-1.5 text-sm text-[var(--text-primary)] placeholder:text-[var(--text-muted)] focus:outline-none focus:ring-1 focus:ring-[var(--accent)]"
                  />
                  <button
                    onClick={handleSaveCalibration}
                    disabled={saving}
                    className="flex items-center gap-1.5 px-3 py-1.5 text-xs bg-[var(--accent)] text-white rounded-md hover:bg-[var(--accent-hover)] disabled:opacity-50 transition-colors whitespace-nowrap"
                  >
                    {saving ? (
                      <><Loader2 className="w-3.5 h-3.5 animate-spin" /> Saving...</>
                    ) : (
                      <><Save className="w-3.5 h-3.5" /> Save Calibration</>
                    )}
                  </button>
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                <p className="text-sm text-[var(--text-secondary)]">
                  <strong className="text-[var(--text-primary)]">Practitioner Calibration</strong> — do
                  the default capacity settings match your real-world project? Confirming
                  that the model got it right is just as valuable as correcting it.
                </p>
                <button
                  onClick={async () => {
                    setSaving(true)
                    const ok = await saveCalibration('defaults_confirmed', null)
                    setSaved(ok)
                    setSaving(false)
                  }}
                  disabled={saving}
                  className="flex items-center gap-1.5 px-3 py-1.5 text-xs bg-emerald-600 text-white rounded-md hover:bg-emerald-500 disabled:opacity-50 transition-colors whitespace-nowrap"
                >
                  {saving ? (
                    <><Loader2 className="w-3.5 h-3.5 animate-spin" /> Saving...</>
                  ) : (
                    <><CheckCircle className="w-3.5 h-3.5" /> Defaults Match My Project</>
                  )}
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ── Footer ─────────────────────────────────────────────── */}
      <div className="flex justify-end pt-2 border-t border-[var(--border)]">
        <button
          onClick={() => navigate('/identify')}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs bg-[var(--accent)] text-white rounded-md hover:bg-[var(--accent-hover)] transition-colors"
        >
          Help Validate the Model <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  )
}

function pct(v) {
  return Math.round(v * 100)
}
