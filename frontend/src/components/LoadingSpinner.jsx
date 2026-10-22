export default function LoadingSpinner({ message = 'Loading...', size = 'default' }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '40px', gap: '16px' }}>
      <div className={`spinner ${size === 'sm' ? 'spinner-sm' : ''}`} />
      {message && <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>{message}</p>}
    </div>
  );
}
