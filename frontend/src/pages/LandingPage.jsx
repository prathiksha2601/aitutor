import { Link } from 'react-router-dom';
import '../styles/landing.css';

export default function LandingPage() {
  return (
    <div className="landing-page">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="container">
          <div className="hero-badge">
            <span>✨ AI-Powered Personalized Education</span>
          </div>
          <h1 className="hero-title">
            Master Technical Skills with an <span>Empathetic AI Tutor</span>
          </h1>
          <p className="hero-subtitle">
            An intelligent learning platform that adapts explanations to your pace.
            Explore interactive lessons in Java, OOP, Data Structures, SQL, OS, and Networks
            with personalized AI guidance and optional, privacy-respecting facial cue analysis.
          </p>
          <div className="hero-cta">
            <Link to="/dashboard" className="btn btn-primary btn-lg">
              Start Learning Now &rarr;
            </Link>
            <a href="#how-it-works" className="btn btn-outline btn-lg">
              How It Works
            </a>
          </div>
        </div>
      </section>

      {/* Feature Grid */}
      <section className="section">
        <div className="container">
          <div className="section-header">
            <h2 className="section-title">Engineered for Better Learning</h2>
            <p className="section-subtitle">
              Combining evidence-based pedagogy, generative AI, and computer vision with strict privacy controls.
            </p>
          </div>

          <div className="grid-3">
            <div className="card feature-card">
              <div className="feature-icon">📚</div>
              <h3>Curated Curriculum</h3>
              <p>Comprehensive video modules covering Java, OOP, Data Structures, SQL, Operating Systems, and Networks.</p>
            </div>

            <div className="card feature-card">
              <div className="feature-icon">🤖</div>
              <h3>Multi-Mode AI Tutor</h3>
              <p>Request explanations in simple terms, step-by-step walkthroughs, real-world analogies, code snippets, or revision quizzes.</p>
            </div>

            <div className="card feature-card">
              <div className="feature-icon">👁️</div>
              <h3>Optional Visual Signals</h3>
              <p>Lightweight MobileNetV2 inference detects if you may be finding a concept difficult and gently suggests simpler explanations.</p>
            </div>

            <div className="card feature-card">
              <div className="feature-icon">📊</div>
              <h3>Real Progress Tracking</h3>
              <p>Tracks your actual lesson completions and video timestamps in MongoDB. Never invents progress percentages.</p>
            </div>

            <div className="card feature-card">
              <div className="feature-icon">🔒</div>
              <h3>Privacy by Design</h3>
              <p>Webcam is off by default. Video frames are processed in-memory and never stored. Full user control over learning data.</p>
            </div>

            <div className="card feature-card">
              <div className="feature-icon">⚡</div>
              <h3>Works Everywhere</h3>
              <p>The platform remains 100% functional when the camera is off, the ML model is offline, or AI credentials are unconfigured.</p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="section" style={{ background: 'var(--surface)' }}>
        <div className="container">
          <div className="section-header">
            <h2 className="section-title">How EIT Works</h2>
            <p className="section-subtitle">A seamless feedback loop designed to support your understanding.</p>
          </div>

          <div className="grid-3">
            <div className="card step-card">
              <div className="step-number">1</div>
              <h3 style={{ marginBottom: '8px' }}>Select a Topic</h3>
              <p style={{ color: 'var(--text-muted)' }}>Choose from computer science disciplines and resume where you left off.</p>
            </div>

            <div className="card step-card">
              <div className="step-number">2</div>
              <h3 style={{ marginBottom: '8px' }}>Watch & Interact</h3>
              <p style={{ color: 'var(--text-muted)' }}>Watch curated educational videos while the AI Tutor stands by to answer questions in real time.</p>
            </div>

            <div className="card step-card">
              <div className="step-number">3</div>
              <h3 style={{ marginBottom: '8px' }}>Adaptive Assistance</h3>
              <p style={{ color: 'var(--text-muted)' }}>Receive context-aware analogies, code examples, or practice quizzes whenever you need help.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Privacy Notice Banner */}
      <section className="section">
        <div className="container">
          <div className="privacy-banner">
            <div>
              <h3>Your Privacy is Non-Negotiable</h3>
              <p>
                Facial analysis is strictly optional and consent-gated.
                Computer vision signals are treated as uncertain hints — never as proof of emotion or comprehension.
                No raw camera frames are ever persisted.
              </p>
            </div>
            <Link to="/privacy" className="btn btn-secondary">
              Read Privacy Policy
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
