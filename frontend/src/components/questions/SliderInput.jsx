/**
 * SliderInput — range slider with value display and optional labels.
 */
export default function SliderInput({ value, onChange, min = 0, max = 100, unit = '', labels }) {
  const current = value ?? min

  return (
    <div className="space-y-1">
      <div className="flex items-center gap-3">
        <input
          type="range"
          min={min}
          max={max}
          step={max <= 10 ? 1 : 5}
          value={current}
          onChange={e => onChange(parseFloat(e.target.value))}
          className="flex-1 h-1.5 rounded-full appearance-none bg-[var(--border)] cursor-pointer accent-[var(--accent)]"
        />
        <span className="w-16 text-right text-sm font-medium text-[var(--text-primary)]">
          {current}{unit}
        </span>
      </div>
      {labels && (
        <div className="flex justify-between text-xs text-[var(--text-muted)]">
          <span>{labels.min || min}</span>
          <span>{labels.max || max}</span>
        </div>
      )}
    </div>
  )
}
