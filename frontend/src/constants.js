/**
 * Shared constants for the assessment platform.
 */

/** Minimum percentage of visible questions that must be answered before submission is allowed. */
export const MINIMUM_ANSWER_PCT = 0.5

/**
 * Compute the answer completion fraction.
 * Returns 0 if no questions are visible (avoids division by zero).
 */
export function getAnswerPct(answered, visible) {
  if (!visible || visible === 0) return 0
  return answered / visible
}

/**
 * Colour band for answer progress.
 * Returns a CSS variable reference suitable for inline styles.
 */
export function answerPctColour(pct) {
  if (pct >= MINIMUM_ANSWER_PCT) return 'var(--accent)'   // green
  if (pct >= 0.4) return 'var(--warning)'                  // amber
  return 'var(--danger)'                                    // red
}
