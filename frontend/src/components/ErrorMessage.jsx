export default function ErrorMessage({ message, onRetry }) {
  return (
    <div className="alert alert-error" style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <strong>Error:</strong>
        <span>{message || 'An unexpected error occurred.'}</span>
      </div>
      {onRetry && (
        <button
          onClick={onRetry}
          className="btn btn-sm btn-outline"
          style={{ alignSelf: 'flex-start', background: 'white' }}
        >
          Try Again
        </button>
      )}
    </div>
  );
}
