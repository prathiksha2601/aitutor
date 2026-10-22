import { Link, useLocation } from 'react-router-dom';

export default function NavBar() {
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <header className="navbar">
      <div className="container navbar-container">
        <Link to="/" className="navbar-brand">
          <div className="navbar-brand-logo">EIT</div>
          <span>Emotional Intelligence Tutor</span>
        </Link>
        <nav>
          <ul className="navbar-links">
            <li>
              <Link to="/" className={`navbar-link ${isActive('/') ? 'active' : ''}`}>
                Home
              </Link>
            </li>
            <li>
              <Link to="/dashboard" className={`navbar-link ${isActive('/dashboard') ? 'active' : ''}`}>
                Dashboard
              </Link>
            </li>
            <li>
              <Link to="/privacy" className={`navbar-link ${isActive('/privacy') ? 'active' : ''}`}>
                Privacy & Data
              </Link>
            </li>
          </ul>
        </nav>
      </div>
    </header>
  );
}
