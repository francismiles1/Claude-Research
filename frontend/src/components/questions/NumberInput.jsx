/**
 * NumberInput — numeric text field with optional unit and min/max.
 */
export default function NumberInput({ value, onChange, min = 0, max = 100, unit = '' }) {
  return (
    <div className="flex items-center gap-2">
      <input
        type="number"
        min={min}
        max={max}
        value={value ?? ''}
        onChange={e => {
          const val = e.target.value === '' ? null : parseFloat(e.target.value)
          if (val !== null && (val < min || val > max)) return
          onChange(val)
        }}
        className="w-24 bg-[var(--bg-primary)] border border-[var(--border)] rounded-md px-3 py-1.5 text-sm text-center text-[var(--text-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent)]"
      />
      {unit && <span className="text-sm text-[var(--text-muted)]">{unit}</span>}
    </div>
  )
}
