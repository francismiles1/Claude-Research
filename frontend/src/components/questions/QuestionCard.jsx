/**
 * QuestionCard — wraps a question with its input control.
 * Dispatches to the correct input component based on question.type.
 * Hover-to-expand shows contextual help text when available.
 */
import { useState } from 'react'
import { CheckCircle, GitBranch, GitFork } from 'lucide-react'
import ToggleInput from './ToggleInput'
import SelectInput from './SelectInput'
import SliderInput from './SliderInput'
import MultiSelectInput from './MultiSelectInput'
import NumberInput from './NumberInput'

export default function QuestionCard({ question, value, onChange }) {
  const isAnswered = value !== undefined && value !== null
  const [hovered, setHovered] = useState(false)

  function renderInput() {
    switch (question.type) {
      case 'toggle':
        return <ToggleInput value={value} onChange={onChange} options={question.options} />
      case 'select':
        return <SelectInput value={value} onChange={onChange} options={question.options} />
      case 'slider':
        return (
          <SliderInput
            value={value}
            onChange={onChange}
            min={question.min ?? 0}
            max={question.max ?? 100}
            unit={question.unit || ''}
            labels={question.labels}
          />
        )
      case 'multiselect':
        return <MultiSelectInput value={value} onChange={onChange} options={question.options} />
      case 'number':
        return (
          <NumberInput
            value={value}
            onChange={onChange}
            min={question.min ?? 0}
            max={question.max ?? 100}
            unit={question.unit || ''}
          />
        )
      default:
        return <SelectInput value={value} onChange={onChange} options={question.options} />
    }
  }

  return (
    <div
      className="flex gap-3 p-3 rounded-lg bg-[var(--bg-card)] border border-[var(--border)] hover:border-[var(--text-muted)] transition-colors"
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      {/* Question ID + status */}
      <div className="flex-shrink-0 mt-0.5 flex items-center gap-1.5">
        {isAnswered && <CheckCircle className="w-3.5 h-3.5 text-green-500" />}
        <span className={`text-xs font-mono ${
          isAnswered ? 'text-[var(--text-secondary)]' : 'text-[var(--text-muted)]'
        }`}>
          {question.id}
        </span>
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0 space-y-2">
        <div className="flex items-start justify-between gap-2">
          <p className={`text-sm text-[var(--text-primary)]${question.help ? ' cursor-help' : ''}`}>{question.text}</p>
          <div className="flex items-center gap-1.5 flex-shrink-0">
            {question.trigger && (
              <span className="flex items-center gap-0.5 text-xs px-1.5 py-0.5 rounded bg-purple-900/30 text-purple-400" title="Your answer controls which questions appear next">
                <GitFork className="w-3 h-3" />
              </span>
            )}
            {question.adaptive && (
              <span className="flex items-center gap-0.5 text-xs px-1.5 py-0.5 rounded bg-amber-900/30 text-amber-400" title="Adaptive — appeared based on another answer">
                <GitBranch className="w-3 h-3" />
              </span>
            )}
            <span className={`text-xs px-1.5 py-0.5 rounded ${
              question.dimension === 'capability'
                ? 'bg-blue-900/30 text-blue-400'
                : 'bg-emerald-900/30 text-emerald-400'
            }`}>
              {question.dimension === 'capability' ? 'Cap' : 'Ops'}
            </span>
          </div>
        </div>
        {hovered && question.help && (
          <p className="text-xs text-[var(--text-secondary)] leading-relaxed -mt-1">{question.help}</p>
        )}
        {renderInput()}
      </div>
    </div>
  )
}
