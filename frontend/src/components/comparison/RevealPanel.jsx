/**
 * RevealPanel — post-selection reveal comparing user's choice vs system match.
 *
 * Three states:
 * 1. Agreement — user and system chose the same archetype
 * 2. Disagreement — different choices, show both with analysis
 * 3. None match — user says no archetype fits, show system match + description
 */
import { CheckCircle, AlertTriangle, Sparkles } from 'lucide-react'
import DimensionComparison from './DimensionComparison'

const CONFIDENCE_STYLES = {
  strong:     { bg: 'bg-green-900/30', text: 'text-green-400', border: 'border-green-700/50' },
  reasonable: { bg: 'bg-yellow-900/30', text: 'text-yellow-400', border: 'border-yellow-700/50' },
  ambiguous:  { bg: 'bg-red-900/30', text: 'text-red-400', border: 'border-red-700/50' },
}

export default function RevealPanel({
  userChoice,
  systemMatch,
  systemDistance,
  confidence,
  userDimensions,
  archetypeData,
  noneMatchDesc,
}) {
  const isAgreement = userChoice === systemMatch
  const isNoneMatch = !userChoice
  const confStyle = CONFIDENCE_STYLES[confidence] || CONFIDENCE_STYLES.ambiguous

  const systemArch = archetypeData?.[systemMatch]
  const userArch = userChoice ? archetypeData?.[userChoice] : null

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-start gap-3">
        {isNoneMatch ? (
          <Sparkles className="w-5 h-5 text-amber-400 mt-0.5 flex-shrink-0" />
        ) : isAgreement ? (
          <CheckCircle className="w-5 h-5 text-green-400 mt-0.5 flex-shrink-0" />
        ) : (
          <AlertTriangle className="w-5 h-5 text-yellow-400 mt-0.5 flex-shrink-0" />
        )}
        <div>
          <h3 className="text-sm font-semibold text-[var(--text-primary)]">
            {isNoneMatch
              ? 'Potential new archetype pattern'
              : isAgreement
                ? 'Your assessment aligns with the system match'
                : 'Your choice differs from the system match'
            }
          </h3>
          <p className="text-sm text-[var(--text-muted)] mt-0.5">
            {isNoneMatch
              ? 'You indicated that none of the 15 archetypes match your project. ' +
                'This is one of the most valuable research signals — it suggests a structural ' +
                'pattern the model may not have captured.'
              : isAgreement
                ? `Both you and the system identified your project as ${systemMatch}. ` +
                  'This strengthens confidence in the archetype taxonomy.'
                : `You chose ${userChoice}, but the system matched you to ${systemMatch}. ` +
                  'This divergence helps us understand where the model\'s structural assumptions ' +
                  'differ from real-world experience.'
            }
          </p>
        </div>
      </div>

      {/* System match card */}
      <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-lg p-4 space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-[var(--text-muted)]">System match</p>
            <p className="text-sm font-semibold text-[var(--text-primary)]">{systemMatch}</p>
          </div>
          <div className="flex items-center gap-2">
            <span className={`px-2 py-0.5 rounded text-sm font-medium ${confStyle.bg} ${confStyle.text} border ${confStyle.border}`}>
              {confidence}
            </span>
            <span className="text-sm text-[var(--text-muted)] tabular-nums">
              distance: {systemDistance.toFixed(2)}
            </span>
          </div>
        </div>
        {systemArch?.description && (
          <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
            {systemArch.description}
          </p>
        )}
        <DimensionComparison
          userDimensions={userDimensions}
          archetypeDimensions={systemArch?.dimensions}
          archetypeName={systemMatch}
        />
      </div>

      {/* User choice card (if different) */}
      {!isAgreement && !isNoneMatch && userArch && (
        <div className="bg-[var(--bg-card)] border border-[var(--accent)]/30 rounded-lg p-4 space-y-3">
          <div>
            <p className="text-sm text-[var(--text-muted)]">Your choice</p>
            <p className="text-sm font-semibold text-[var(--accent)]">{userChoice}</p>
          </div>
          {userArch.description && (
            <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
              {userArch.description}
            </p>
          )}
          <DimensionComparison
            userDimensions={userDimensions}
            archetypeDimensions={userArch.dimensions}
            archetypeName={userChoice}
          />
        </div>
      )}

      {/* None match description */}
      {isNoneMatch && noneMatchDesc && (
        <div className="bg-amber-900/20 border border-amber-700/30 rounded-lg p-4 space-y-2">
          <p className="text-sm font-medium text-amber-400">Your description</p>
          <p className="text-sm text-[var(--text-secondary)] leading-relaxed italic">
            "{noneMatchDesc}"
          </p>
          <p className="text-sm text-[var(--text-muted)]">
            This has been recorded for analysis. When enough "none match" responses cluster
            around similar structural patterns, we can identify new archetypes to add to the model.
          </p>
        </div>
      )}
    </div>
  )
}
