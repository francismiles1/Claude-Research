/**
 * NoteModal — reusable modal for per-category comments/suggestions.
 *
 * Backdrop click or Cancel discards changes.
 * Save calls onSave with the trimmed text (or empty string to clear).
 */
import { useState, useEffect, useRef } from 'react'
import { X } from 'lucide-react'

const MAX_LENGTH = 1000

export default function NoteModal({ isOpen, onClose, onSave, categoryName, initialValue }) {
  const [text, setText] = useState(initialValue || '')
  const textareaRef = useRef(null)

  // Reset text when modal opens with new value
  useEffect(() => {
    if (isOpen) {
      setText(initialValue || '')
      // Focus textarea after render
      setTimeout(() => textareaRef.current?.focus(), 50)
    }
  }, [isOpen, initialValue])

  // Close on Escape
  useEffect(() => {
    if (!isOpen) return
    function handleKey(e) {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', handleKey)
    return () => window.removeEventListener('keydown', handleKey)
  }, [isOpen, onClose])

  if (!isOpen) return null

  function handleSave() {
    onSave(text.trim())
    onClose()
  }

  function handleBackdropClick(e) {
    if (e.target === e.currentTarget) onClose()
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60"
      onClick={handleBackdropClick}
    >
      <div className="w-full max-w-lg mx-4 bg-[var(--bg-primary)] border border-[var(--border)] rounded-lg shadow-xl">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-3 border-b border-[var(--border)]">
          <div>
            <h3 className="text-sm font-semibold text-[var(--text-primary)]">
              Note: {categoryName}
            </h3>
            <p className="text-xs text-[var(--text-muted)]">
              Comments, suggestions, or corrections for this category
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-md text-[var(--text-muted)] hover:bg-[var(--bg-hover)] transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Body */}
        <div className="px-5 py-4 space-y-2">
          <textarea
            ref={textareaRef}
            value={text}
            onChange={e => setText(e.target.value.slice(0, MAX_LENGTH))}
            maxLength={MAX_LENGTH}
            rows={5}
            className="w-full bg-[var(--bg-card)] border border-[var(--border)] rounded-md px-3 py-2 text-sm text-[var(--text-primary)] placeholder:text-[var(--text-muted)] focus:outline-none focus:ring-1 focus:ring-[var(--accent)] resize-y"
            placeholder="Is this category relevant to your project? Are the questions missing something? Do you disagree with the scoring? Reference question IDs (e.g. GOV-C1) if specific."
          />
          <p className="text-xs text-[var(--text-muted)] text-right">
            {text.length} / {MAX_LENGTH}
          </p>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-2 px-5 py-3 border-t border-[var(--border)]">
          <button
            onClick={onClose}
            className="px-3 py-1.5 text-sm text-[var(--text-muted)] border border-[var(--border)] rounded-md hover:bg-[var(--bg-hover)] transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="px-3 py-1.5 text-sm bg-[var(--accent)] text-white rounded-md hover:bg-[var(--accent-hover)] transition-colors"
          >
            Save Note
          </button>
        </div>
      </div>
    </div>
  )
}
