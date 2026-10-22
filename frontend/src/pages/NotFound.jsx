import { Link } from 'react-router-dom';

export default function NotFound() {
  return (
    <div className="container" style={{ textAlign: 'center', padding: '100px 24px' }}>
      <h1 style={{ fontSize: '4rem', fontWeight: '900', color: 'var(--primary)', marginBottom: '8px' }}>
        404
      </h1>
      <h2 style={{ fontSize: '1.8rem', fontWeight: '700', marginBottom: '16px' }}>
        Page Not Found
      </h2>
      <p style={{ color: 'var(--text-muted)', maxWidth: '440px', margin: '0 auto 28px' }}>
        The learning page or lesson you were looking for could not be found.
      </p>
      <Link to="/" className="btn btn-primary">
        Return Home
      </Link>
    </div>
  );
}
