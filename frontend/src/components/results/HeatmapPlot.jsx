/**
 * HeatmapPlot — Plotly heatmap of the viability grid.
 *
 * Renders gradient or binary sigmoid view with contour overlay,
 * floor lines, and position markers.
 */
import { useMemo } from 'react'
import createPlotlyComponent from 'react-plotly.js/factory'
import Plotly from 'plotly.js-cartesian-dist-min'

const Plot = createPlotlyComponent(Plotly)

// Colour scales matching the Python visualisation
const GRADIENT_COLOURSCALE = [
  [0.000, '#8B0000'], [0.125, '#CD5C5C'], [0.250, '#E88060'],
  [0.375, '#F0C0A0'], [0.500, '#FFFFCC'], [0.625, '#C0E8A0'],
  [0.750, '#4CAF50'], [0.875, '#2E7D32'], [1.000, '#1B5E20'],
]

const ZONE_COLOURSCALE = [
  [0.00, '#8B0000'], [0.25, '#CD5C5C'], [0.45, '#F0C0A0'],
  [0.50, '#FFFFCC'], [0.55, '#C0E8A0'], [0.75, '#4CAF50'],
  [1.00, '#1B5E20'],
]

const GRADIENT_CLIP = 4.0
const LAYER_NAMES = ['Viable', 'Sufficient', 'Sustainable', 'Combined']

export default function HeatmapPlot({
  gridData,
  gradientData,
  viewMode = 'gradient',
  layerIndex = 3,
  inspectCap,
  inspectOps,
  defaultCap,
  defaultOps,
  assessedCap,
  assessedOps,
  capFloor,
  opsFloor,
  showFloors = true,
  showDefault = true,
  onClickPosition,
}) {
  const { data, layout } = useMemo(() => {
    if (!gridData || !gradientData) return { data: [], layout: {} }

    const n = gridData.length
    const axis = Array.from({ length: n }, (_, i) => i)

    // Build z matrix
    let z, colourscale, zmin, zmax
    if (viewMode === 'gradient') {
      // Gradient view: raw margins clipped to [-4, +4], normalised to [0, 1]
      z = gradientData.map(row =>
        row.map(cell => {
          const val = cell[3] // combined margin
          const clipped = Math.max(-GRADIENT_CLIP, Math.min(GRADIENT_CLIP, val))
          return (clipped + GRADIENT_CLIP) / (2 * GRADIENT_CLIP)
        })
      )
      colourscale = GRADIENT_COLOURSCALE
      zmin = 0
      zmax = 1
    } else {
      // Sigmoid view for a specific layer
      z = gridData.map(row => row.map(cell => cell[layerIndex]))
      colourscale = ZONE_COLOURSCALE
      zmin = 0
      zmax = 1
    }

    const traces = []

    // Heatmap trace
    traces.push({
      type: 'heatmap',
      z,
      x: axis,
      y: axis,
      colorscale: colourscale,
      zmin,
      zmax,
      showscale: false,
      hovertemplate: 'Cap: %{x}%<br>Ops: %{y}%<br>Score: %{z:.3f}<extra></extra>',
    })

    // Contour overlay (viable zone boundary at 0.5 on combined layer)
    const combinedZ = gridData.map(row => row.map(cell => cell[3]))
    traces.push({
      type: 'contour',
      z: combinedZ,
      x: axis,
      y: axis,
      contours: { start: 0.5, end: 0.5, size: 0.1, coloring: 'none' },
      line: { color: 'white', width: 2, dash: 'dash' },
      showscale: false,
      showlegend: false,
      hoverinfo: 'skip',
    })

    // Floor lines
    if (showFloors && capFloor != null && opsFloor != null) {
      const capFloorPx = Math.round(capFloor * 100)
      const opsFloorPx = Math.round(opsFloor * 100)

      traces.push({
        type: 'scatter',
        x: [capFloorPx, capFloorPx],
        y: [0, 100],
        mode: 'lines',
        line: { color: 'rgba(255,255,255,0.4)', width: 1, dash: 'dot' },
        showlegend: false,
        hoverinfo: 'skip',
      })
      traces.push({
        type: 'scatter',
        x: [0, 100],
        y: [opsFloorPx, opsFloorPx],
        mode: 'lines',
        line: { color: 'rgba(255,255,255,0.4)', width: 1, dash: 'dot' },
        showlegend: false,
        hoverinfo: 'skip',
      })
    }

    // Default position marker
    if (showDefault && defaultCap != null && defaultOps != null) {
      traces.push({
        type: 'scatter',
        x: [Math.round(defaultCap * 100)],
        y: [Math.round(defaultOps * 100)],
        mode: 'markers',
        marker: { symbol: 'star', size: 14, color: '#FFD700', line: { color: 'white', width: 1 } },
        name: 'Default',
        showlegend: false,
        hovertemplate: `Default: Cap ${Math.round(defaultCap * 100)}%, Ops ${Math.round(defaultOps * 100)}%<extra></extra>`,
      })
    }

    // Assessed position marker (user's maturity assessment result)
    if (assessedCap != null && assessedOps != null) {
      traces.push({
        type: 'scatter',
        x: [Math.round(assessedCap * 100)],
        y: [Math.round(assessedOps * 100)],
        mode: 'markers',
        marker: { symbol: 'circle', size: 13, color: '#00CED1', line: { color: 'white', width: 2 } },
        name: 'Assessed',
        showlegend: false,
        hovertemplate: `Assessed: Cap ${Math.round(assessedCap * 100)}%, Ops ${Math.round(assessedOps * 100)}%<extra></extra>`,
      })
    }

    // Inspect position marker
    if (inspectCap != null && inspectOps != null) {
      traces.push({
        type: 'scatter',
        x: [Math.round(inspectCap * 100)],
        y: [Math.round(inspectOps * 100)],
        mode: 'markers',
        marker: { symbol: 'diamond', size: 12, color: '#FF6B6B', line: { color: 'white', width: 2 } },
        name: 'Inspect',
        showlegend: false,
        hovertemplate: `Inspect: Cap ${Math.round(inspectCap * 100)}%, Ops ${Math.round(inspectOps * 100)}%<extra></extra>`,
      })
    }

    const plotLayout = {
      xaxis: {
        title: { text: 'Capability %', font: { color: '#94a3b8', size: 12 } },
        tickfont: { color: '#64748b', size: 10 },
        gridcolor: 'rgba(255,255,255,0.05)',
        range: [0, 100],
        fixedrange: true,
      },
      yaxis: {
        title: { text: 'Operational %', font: { color: '#94a3b8', size: 12 } },
        tickfont: { color: '#64748b', size: 10 },
        gridcolor: 'rgba(255,255,255,0.05)',
        range: [0, 100],
        fixedrange: true,
      },
      showlegend: false,
      paper_bgcolor: 'rgba(0,0,0,0)',
      plot_bgcolor: 'rgba(0,0,0,0)',
      margin: { l: 40, r: 10, t: 10, b: 40 },
      width: 550,
      height: 550,
    }

    return { data: traces, layout: plotLayout }
  }, [gridData, gradientData, viewMode, layerIndex, inspectCap, inspectOps,
      defaultCap, defaultOps, assessedCap, assessedOps, capFloor, opsFloor, showFloors, showDefault])

  function handleClick(event) {
    if (!onClickPosition || !event.points || !event.points[0]) return
    const pt = event.points[0]
    if (pt.x != null && pt.y != null) {
      onClickPosition(pt.x / 100, pt.y / 100)
    }
  }

  if (!gridData) {
    return (
      <div className="h-[550px] flex items-center justify-center text-[var(--text-muted)]">
        Loading grid...
      </div>
    )
  }

  return (
    <Plot
      data={data}
      layout={layout}
      config={{ responsive: false, displayModeBar: false, scrollZoom: false }}
      onClick={handleClick}
      style={{ width: '550px', height: '550px' }}
    />
  )
}
