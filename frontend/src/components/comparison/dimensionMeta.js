/**
 * Shared dimension metadata — used by DimensionProfile and DimensionComparison.
 */

export const DIMENSIONS = [
  {
    key: 'D1', label: 'Consequence', inverted: false,
    lo: 'Trivial', hi: 'Catastrophic',
    tooltip: 'What happens if the project fails or delivers poorly? A low score means failure is ' +
      'inconvenient but recoverable (e.g. internal tooling). A high score means failure has serious ' +
      'business, safety, or reputational consequences (e.g. medical devices, financial systems).',
  },
  {
    key: 'D2', label: 'Market Pressure', inverted: false,
    lo: 'None', hi: 'Extreme',
    tooltip: 'How much external time pressure is the project under? Low means the team sets its own ' +
      'pace (e.g. internal platform). High means competitors, contracts, or market windows are forcing ' +
      'delivery speed — often at the expense of quality investment.',
  },
  {
    key: 'D3', label: 'Complexity', inverted: false,
    lo: 'Simple', hi: 'Extreme',
    tooltip: 'Technical and integration complexity of the system being built. This covers architecture ' +
      'scope, number of integration points, domain difficulty, and emergent behaviour. A monolithic CRUD ' +
      'app scores low; a distributed system with real-time processing and third-party integrations scores high.',
  },
  {
    key: 'D4', label: 'Regulation', inverted: false,
    lo: 'None', hi: 'Strict',
    tooltip: 'External compliance, audit, and governance requirements. Low means no regulatory body ' +
      'cares about your process (e.g. a hobby project). High means mandatory audits, certifications, ' +
      'legal sign-offs, and formal evidence trails (e.g. ISO 13485, SOX, PCI-DSS). This is the single ' +
      'most influential dimension across all capacity sliders.',
  },
  {
    key: 'D5', label: 'Team Stability', inverted: true,
    lo: 'High churn', hi: 'Very stable',
    tooltip: 'How stable and retained is the delivery team? Low means frequent contractor rotation, ' +
      'knowledge loss, and constant onboarding. High means long-tenured staff with deep domain expertise ' +
      'and institutional memory. Stable teams need less investment to maintain capability because ' +
      'knowledge is retained rather than rebuilt.',
  },
  {
    key: 'D6', label: 'Outsourcing', inverted: false,
    lo: 'In-house', hi: 'Fully outsourced',
    tooltip: 'How much of the delivery is performed by external parties? Low means the entire team is ' +
      'co-located employees. High means significant or total outsourcing, with contract boundaries, ' +
      'handoff overhead, and split accountability. Outsourced delivery demands more investment in ' +
      'coordination and governance.',
  },
  {
    key: 'D7', label: 'Lifecycle', inverted: false,
    lo: 'Greenfield', hi: 'End of life',
    tooltip: 'Where is the system in its lifecycle? Greenfield projects are building from scratch with ' +
      'no legacy constraints. End-of-life systems are in maintenance mode with declining investment. ' +
      'Mid-lifecycle is the most common state — established enough to have technical debt, young enough ' +
      'to justify continued investment.',
  },
  {
    key: 'D8', label: 'Coherence', inverted: true,
    lo: 'Fragmented', hi: 'Fully coherent',
    tooltip: 'How well-aligned are the architecture, process, and team structure? Low means siloed ' +
      'teams with no shared standards, conflicting toolchains, and duplicated effort. High means a ' +
      'unified architecture with consistent practices across teams. Coherence amplifies the effect of ' +
      'every other investment — it is the multiplier dimension.',
  },
]

export const VALUE_LABELS = {
  Consequence:       { 1: 'Trivial', 2: 'Minor', 3: 'Moderate', 4: 'Serious', 5: 'Catastrophic' },
  'Market Pressure': { 1: 'None', 2: 'Relaxed', 3: 'Normal', 4: 'Competitive', 5: 'Extreme' },
  Complexity:        { 1: 'Simple', 2: 'Low', 3: 'Moderate', 4: 'High', 5: 'Extreme' },
  Regulation:        { 1: 'None', 2: 'Light', 3: 'Moderate', 4: 'Heavy', 5: 'Strict' },
  'Team Stability':  { 1: 'High churn', 2: 'Unstable', 3: 'Some stability', 4: 'Stable', 5: 'Very stable' },
  Outsourcing:       { 1: 'In-house', 2: 'Mostly in-house', 3: 'Mixed', 4: 'Mostly outsourced', 5: 'Fully outsourced' },
  Lifecycle:         { 1: 'Greenfield', 2: 'Early', 3: 'Mid-lifecycle', 4: 'Late stage', 5: 'End of life' },
  Coherence:         { 1: 'Fragmented', 2: 'Weak', 3: 'Moderate', 4: 'Well-aligned', 5: 'Fully coherent' },
}

export function barColour(value, inverted) {
  if (inverted) {
    if (value >= 4) return 'bg-green-500'
    if (value >= 3) return 'bg-yellow-500'
    return 'bg-red-500'
  }
  if (value <= 2) return 'bg-green-500'
  if (value <= 3) return 'bg-yellow-500'
  return 'bg-red-500'
}
