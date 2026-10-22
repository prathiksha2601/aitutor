export default function EmptyState({ title = 'No items found', description = '', actionText, onAction }) {
  return (
    <div style={{ textAlign: 'center', padding: '60px 20px', background: 'var(--surface)', borderRadius: 'var(--radius-lg)', border: '1px dashed var(--border)' }}>
      <h3 style={{ fontSize: '1.25rem', fontWeight: '700', marginBottom: '8px' }}>{title}</h3>
      {description && <p style={{ color: 'var(--text-muted)', maxWidth: '440px', margin: '0 auto 20px', fontSize: '0.95rem' }}>{description}</p>}
      {actionText && onAction && (
        <button onClick={onAction} className="btn btn-primary btn-sm">
          {actionText}
        </button>
      )}
    </div>
  );
}
