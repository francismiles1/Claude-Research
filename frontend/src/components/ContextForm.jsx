/**
 * ContextForm — 9-question project context wizard.
 * Maps to POST /api/context → archetype match.
 */
import { useState } from 'react'
import { Loader2 } from 'lucide-react'
import api from '../api/client'

const SCALE_OPTIONS = [
  { value: 'small', label: 'Small (1-10 people)' },
  { value: 'medium', label: 'Medium (10-50 people)' },
  { value: 'large', label: 'Large (50-200 people)' },
  { value: 'enterprise', label: 'Enterprise (200+ people)' },
]

const DELIVERY_OPTIONS = [
  { value: 'agile', label: 'Agile (Scrum/Kanban)' },
  { value: 'devops', label: 'DevOps / Continuous' },
  { value: 'hybrid_agile', label: 'Hybrid (Agile-leaning)' },
  { value: 'hybrid_traditional', label: 'Hybrid (Traditional-leaning)' },
  { value: 'waterfall', label: 'Waterfall' },
  { value: 'v_model', label: 'V-Model' },
]

const STAGE_OPTIONS = [
  { value: 'startup', label: 'Startup / New product' },
  { value: 'growth', label: 'Growth / Scaling' },
  { value: 'mature', label: 'Mature / Established' },
  { value: 'legacy', label: 'Legacy / End-of-life' },
]

const PHASE_OPTIONS = [
  { value: 'planning', label: 'Planning' },
  { value: 'early_dev', label: 'Early Development' },
  { value: 'mid_dev', label: 'Mid Development' },
  { value: 'testing_phase', label: 'Testing Phase' },
  { value: 'transition', label: 'Transition / Release' },
  { value: 'closure', label: 'Project Closure' },
  { value: 'maintenance', label: 'Maintenance' },
]

const REGULATORY_OPTIONS = [
  { value: 'iso_27001', label: 'ISO 27001 (InfoSec)' },
  { value: 'sox', label: 'SOX (Financial)' },
  { value: 'hipaa', label: 'HIPAA (Healthcare)' },
  { value: 'gdpr', label: 'GDPR (Data Protection)' },
  { value: 'pci_dss', label: 'PCI DSS (Payments)' },
  { value: 'fda', label: 'FDA (Medical Device)' },
  { value: 'iso_26262', label: 'ISO 26262 (Automotive)' },
  { value: 'do_178c', label: 'DO-178C (Aviation)' },
]

const AUDIT_OPTIONS = [
  { value: 'none', label: 'None' },
  { value: 'annual', label: 'Annual' },
  { value: 'bi_annual', label: 'Bi-annual' },
  { value: 'quarterly', label: 'Quarterly' },
  { value: 'continuous', label: 'Continuous' },
]

const INITIAL = {
  scale: '',
  delivery_model: '',
  product_stage: '',
  project_phase: '',
  regulatory_standards: [],
  audit_frequency: 'none',
  complexity: 3,
  team_stability: 3,
  has_third_party: false,
}

export default function ContextForm({ onComplete }) {
  const [form, setForm] = useState(INITIAL)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  function set(key, value) {
    setForm(prev => ({ ...prev, [key]: value }))
  }

  function toggleRegulatory(value) {
    setForm(prev => ({
      ...prev,
      regulatory_standards: prev.regulatory_standards.includes(value)
        ? prev.regulatory_standards.filter(v => v !== value)
        : [...prev.regulatory_standards, value],
    }))
  }

  const canSubmit = form.scale && form.delivery_model && form.product_stage && form.project_phase

  async function handleSubmit() {
    if (!canSubmit) return
    setLoading(true)
    setError(null)
    try {
      const res = await api.post('/context', form)
      onComplete(form, res.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to match archetype')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Scale */}
      <Field label="Organisation / team scale">
        <ButtonGroup options={SCALE_OPTIONS} value={form.scale} onChange={v => set('scale', v)} />
      </Field>

      {/* Delivery model */}
      <Field label="Delivery model">
        <ButtonGroup options={DELIVERY_OPTIONS} value={form.delivery_model} onChange={v => set('delivery_model', v)} />
      </Field>

      {/* Product stage */}
      <Field label="Product / system maturity stage">
        <ButtonGroup options={STAGE_OPTIONS} value={form.product_stage} onChange={v => set('product_stage', v)} />
      </Field>

      {/* Project phase */}
      <Field label="Current project phase">
        <ButtonGroup options={PHASE_OPTIONS} value={form.project_phase} onChange={v => set('project_phase', v)} />
      </Field>

      {/* Regulatory */}
      <Field label="Applicable regulatory standards (select all that apply)">
        <div className="flex flex-wrap gap-2">
          {REGULATORY_OPTIONS.map(opt => (
            <button
              key={opt.value}
              onClick={() => toggleRegulatory(opt.value)}
              className={`px-3 py-1.5 rounded-md text-sm border transition-colors ${
                form.regulatory_standards.includes(opt.value)
                  ? 'bg-blue-600 text-white border-blue-600'
                  : 'bg-[var(--bg-primary)] text-[var(--text-muted)] border-[var(--border)] hover:bg-[var(--bg-hover)]'
              }`}
            >
              {opt.label}
            </button>
          ))}
          {form.regulatory_standards.length === 0 && (
            <span className="text-sm text-[var(--text-muted)] self-center ml-1">None selected</span>
          )}
        </div>
      </Field>

      {/* Audit frequency */}
      <Field label="External audit frequency">
        <ButtonGroup options={AUDIT_OPTIONS} value={form.audit_frequency} onChange={v => set('audit_frequency', v)} />
      </Field>

      {/* Complexity slider */}
      <Field label={`System complexity: ${form.complexity}/5`}>
        <input
          type="range"
          min={1} max={5} step={1}
          value={form.complexity}
          onChange={e => set('complexity', parseInt(e.target.value))}
          className="w-full h-1.5 rounded-full appearance-none bg-[var(--border)] cursor-pointer accent-[var(--accent)]"
        />
        <div className="flex justify-between text-xs text-[var(--text-muted)] mt-1">
          <span>Simple</span><span>Complex</span>
        </div>
      </Field>

      {/* Team stability slider */}
      <Field label={`Team stability: ${form.team_stability}/5`}>
        <div className="flex items-center gap-3">
          <input
            type="range"
            min={1} max={5} step={1}
            value={form.team_stability}
            onChange={e => set('team_stability', parseInt(e.target.value))}
            className="flex-1 h-1.5 rounded-full appearance-none bg-[var(--border)] cursor-pointer accent-[var(--accent)]"
          />
        </div>
        <div className="flex justify-between text-xs text-[var(--text-muted)] mt-1">
          <span>High turnover</span><span>Highly stable</span>
        </div>
      </Field>

      {/* Third party */}
      <Field label="Does the project involve third-party suppliers?">
        <div className="flex gap-2">
          <button
            onClick={() => set('has_third_party', true)}
            className={`px-4 py-1.5 rounded-md text-sm font-medium border transition-colors ${
              form.has_third_party
                ? 'bg-blue-600 text-white border-blue-600'
                : 'bg-[var(--bg-primary)] text-[var(--text-muted)] border-[var(--border)] hover:bg-[var(--bg-hover)]'
            }`}
          >
            Yes
          </button>
          <button
            onClick={() => set('has_third_party', false)}
            className={`px-4 py-1.5 rounded-md text-sm font-medium border transition-colors ${
              !form.has_third_party
                ? 'bg-blue-600 text-white border-blue-600'
                : 'bg-[var(--bg-primary)] text-[var(--text-muted)] border-[var(--border)] hover:bg-[var(--bg-hover)]'
            }`}
          >
            No
          </button>
        </div>
      </Field>

      {/* Error */}
      {error && (
        <div className="p-3 rounded-md bg-red-900/30 border border-red-700/50 text-red-400 text-sm">
          {error}
        </div>
      )}

      {/* Submit */}
      <button
        onClick={handleSubmit}
        disabled={!canSubmit || loading}
        className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-[var(--accent)] text-white text-sm font-medium rounded-md hover:bg-[var(--accent-hover)] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {loading ? (
          <><Loader2 className="w-4 h-4 animate-spin" /> Matching archetype...</>
        ) : (
          'Match My Project'
        )}
      </button>
    </div>
  )
}

/** Labelled field wrapper */
function Field({ label, children }) {
  return (
    <div className="space-y-2">
      <label className="text-sm font-medium text-[var(--text-secondary)]">{label}</label>
      {children}
    </div>
  )
}

/** Single-select button group */
function ButtonGroup({ options, value, onChange }) {
  return (
    <div className="flex flex-wrap gap-2">
      {options.map(opt => (
        <button
          key={opt.value}
          onClick={() => onChange(opt.value)}
          className={`px-3 py-1.5 rounded-md text-sm border transition-colors ${
            value === opt.value
              ? 'bg-[var(--accent)] text-white border-[var(--accent)]'
              : 'bg-[var(--bg-primary)] text-[var(--text-muted)] border-[var(--border)] hover:bg-[var(--bg-hover)] hover:text-[var(--text-primary)]'
          }`}
        >
          {opt.label}
        </button>
      ))}
    </div>
  )
}
