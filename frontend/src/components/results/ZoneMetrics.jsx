/**
 * ZoneMetrics — summary stats about the viable zone.
 */
import { Target, ArrowLeftRight, ArrowUpDown, Percent } from 'lucide-react'

export default function ZoneMetrics({ zoneArea, capRange, opsRange, capFloor, opsFloor }) {
  if (zoneArea == null) return null

  const items = [
    { icon: Percent, label: 'Zone Area', value: `${zoneArea}%`, desc: 'of grid is viable' },
    { icon: ArrowLeftRight, label: 'Cap Range', value: `${(capRange[0]*100).toFixed(0)}–${(capRange[1]*100).toFixed(0)}%`, desc: 'viable capability' },
    { icon: ArrowUpDown, label: 'Ops Range', value: `${(opsRange[0]*100).toFixed(0)}–${(opsRange[1]*100).toFixed(0)}%`, desc: 'viable operational' },
    { icon: Target, label: 'Cap Floor', value: `${(capFloor*100).toFixed(0)}%`, desc: 'minimum capability' },
    { icon: Target, label: 'Ops Floor', value: `${(opsFloor*100).toFixed(0)}%`, desc: 'minimum operational' },
  ]

  return (
    <div className="grid grid-cols-5 gap-2">
      {items.map(item => (
        <div key={item.label} className="bg-[var(--bg-card)] border border-[var(--border)] rounded-md p-2.5 text-center">
          <item.icon className="w-4 h-4 mx-auto mb-1 text-[var(--text-muted)]" />
          <div className="text-sm font-bold text-[var(--text-primary)]">{item.value}</div>
          <div className="text-[10px] text-[var(--text-muted)]">{item.desc}</div>
        </div>
      ))}
    </div>
  )
}
