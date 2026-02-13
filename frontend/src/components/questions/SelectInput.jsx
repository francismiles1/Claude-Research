/**
 * SelectInput — button group for ordered option selection.
 * Colours grade from red (first/low) → green (last/high) when selected.
 */
export default function SelectInput({ value, onChange, options }) {
  if (!options || options.length === 0) return null

  function getSelectedColour(idx) {
    const count = options.length
    if (count <= 1) return 'bg-green-600 text-white border-green-600'
    const pos = idx / (count - 1)
    if (pos <= 0.25) return 'bg-red-600 text-white border-red-600'
    if (pos <= 0.5) return 'bg-amber-600 text-white border-amber-600'
    if (pos <= 0.75) return 'bg-yellow-500 text-white border-yellow-500'
    return 'bg-green-600 text-white border-green-600'
  }

  return (
    <div className="flex flex-wrap gap-2">
      {options.map((opt, idx) => {
        const isSelected = value === opt.value
        return (
          <button
            key={String(opt.value)}
            onClick={() => onChange(opt.value)}
            className={`px-3 py-1.5 rounded-md text-sm font-medium border transition-colors ${
              isSelected
                ? getSelectedColour(idx)
                : 'bg-[var(--bg-primary)] text-[var(--text-muted)] border-[var(--border)] hover:bg-[var(--bg-hover)] hover:text-[var(--text-primary)]'
            }`}
          >
            {opt.label}
          </button>
        )
      })}
    </div>
  )
}
