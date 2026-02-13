/**
 * MultiSelectInput — checkbox-style button group for multi-value questions.
 */
import { Check } from 'lucide-react'

export default function MultiSelectInput({ value, onChange, options }) {
  if (!options || options.length === 0) return null

  const selected = Array.isArray(value) ? value : []

  function toggle(optValue) {
    if (selected.includes(optValue)) {
      onChange(selected.filter(v => v !== optValue))
    } else {
      onChange([...selected, optValue])
    }
  }

  return (
    <div className="flex flex-wrap gap-2">
      {options.map(opt => {
        const isSelected = selected.includes(opt.value)
        return (
          <button
            key={String(opt.value)}
            onClick={() => toggle(opt.value)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium border transition-colors ${
              isSelected
                ? 'bg-blue-600 text-white border-blue-600'
                : 'bg-[var(--bg-primary)] text-[var(--text-muted)] border-[var(--border)] hover:bg-[var(--bg-hover)] hover:text-[var(--text-primary)]'
            }`}
          >
            {isSelected && <Check className="w-3.5 h-3.5" />}
            {opt.label}
          </button>
        )
      })}
    </div>
  )
}
