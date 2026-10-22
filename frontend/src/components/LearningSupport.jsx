export default function LearningSupport({ suggestion, onSelectOption, onDismiss }) {
  if (!suggestion) return null;

  const defaultOptions = [
    'Explain more simply.',
    'Give a practical example.',
    'Ask me a practice question.',
    'Continue learning.',
  ];

  const options = suggestion.options || defaultOptions;

  return (
    <div className="support-overlay">
      <div className="support-overlay-header">
        <div className="support-title">
          <span>💡 Learning Assistant Suggestion</span>
        </div>
        <button onClick={onDismiss} className="support-close-btn" title="Dismiss">
          &times;
        </button>
      </div>

      <p style={{ fontSize: '0.88rem', color: '#1e3a8a', marginBottom: '12px' }}>
        {suggestion.text || 'Would you like some extra help with this concept?'}
      </p>

      <div className="support-options-grid">
        {options.map((opt, i) => (
          <button
            key={i}
            onClick={() => onSelectOption(opt)}
            className="support-option-btn"
          >
            {opt}
          </button>
        ))}
      </div>
    </div>
  );
}
