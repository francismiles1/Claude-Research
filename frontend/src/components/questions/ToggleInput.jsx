/**
 * ToggleInput — Yes/No button pair for boolean questions.
 */
export default function ToggleInput({ value, onChange, options }) {
  const opts = options || [
    { value: true, label: 'Yes' },
    { value: false, label: 'No' },
  ]

  return (
    <div className="flex flex-wrap gap-2">
      {opts.map(opt => {
        const isSelected = value === opt.value
        const isYes = opt.value === true
        return (
          <button
            key={String(opt.value)}
            onClick={() => onChange(opt.value)}
            className={`px-4 py-1.5 rounded-md text-sm font-medium border transition-colors ${
              isSelected
                ? isYes
                  ? 'bg-green-600 text-white border-green-600'
                  : 'bg-red-600 text-white border-red-600'
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
