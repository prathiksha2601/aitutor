export default function ProgressBar({ percent = 0, label, height = 8, color = 'var(--primary)' }) {
  const clamped = Math.min(100, Math.max(0, percent || 0));

  return (
    <div style={{ width: '100%' }}>
      {label && (
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', fontWeight: '600', color: 'var(--text-muted)', marginBottom: '4px' }}>
          <span>{label}</span>
          <span>{Math.round(clamped)}%</span>
        </div>
      )}
      <div style={{ width: '100%', height: `${height}px`, background: 'var(--surface-alt)', borderRadius: '9999px', overflow: 'hidden' }}>
        <div
          style={{
            width: `${clamped}%`,
            height: '100%',
            backgroundColor: color,
            borderRadius: '9999px',
            transition: 'width 0.3s ease',
          }}
        />
      </div>
    </div>
  );
}
