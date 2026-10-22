import { Link } from 'react-router-dom';

export default function PrivacyPage() {
  return (
    <div className="container" style={{ padding: '60px 24px', maxWidth: '860px' }}>
      <div style={{ marginBottom: '32px' }}>
        <h1 style={{ fontSize: '2.4rem', fontWeight: '800', marginBottom: '8px' }}>
          Privacy, Data & Ethical AI Policy
        </h1>
        <p style={{ color: 'var(--text-muted)' }}>
          Last updated: October 2026 &bull; AI-Driven Emotional Intelligence Tutor (EIT)
        </p>
      </div>

      <div className="card" style={{ padding: '32px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
        <section>
          <h2 style={{ fontSize: '1.4rem', fontWeight: '700', marginBottom: '8px' }}>
            1. Core Ethical Principles
          </h2>
          <p style={{ color: 'var(--text-muted)', lineHeight: '1.7' }}>
            Facial expressions, micro-movements, and gaze do <strong>not</strong> establish a person's true emotional state,
            comprehension level, intelligence, or academic engagement. At EIT, computer-vision predictions are treated strictly as
            <strong> noisy, optional, and secondary hints</strong>. We never diagnose students, label their psychological states,
            or penalize them based on model inference.
          </p>
        </section>

        <section>
          <h2 style={{ fontSize: '1.4rem', fontWeight: '700', marginBottom: '8px' }}>
            2. Camera Use and Consent
          </h2>
          <ul style={{ paddingLeft: '20px', color: 'var(--text-muted)', lineHeight: '1.8' }}>
            <li><strong>Disabled by Default:</strong> The webcam is never activated automatically.</li>
            <li><strong>Explicit Consent:</strong> You must click an explicit consent button before any webcam analysis runs.</li>
            <li><strong>Instant Shutdown:</strong> Disabling the camera immediately releases all hardware tracks. Leaving the lesson screen automatically terminates the stream.</li>
            <li><strong>Zero Raw Frame Storage:</strong> Video frames are processed transiently in memory and are never saved to disk or persistent databases.</li>
            <li><strong>No Third-Party Transmission:</strong> Raw images are never sent to external AI providers (such as OpenAI).</li>
          </ul>
        </section>

        <section>
          <h2 style={{ fontSize: '1.4rem', fontWeight: '700', marginBottom: '8px' }}>
            3. Data Collected & Stored
          </h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '8px' }}>
            <div style={{ background: 'var(--surface-alt)', padding: '14px', borderRadius: 'var(--radius)' }}>
              <strong>Learning Progress:</strong> Lesson completion status and video timestamps to enable playback resume.
            </div>
            <div style={{ background: 'var(--surface-alt)', padding: '14px', borderRadius: 'var(--radius)' }}>
              <strong>Tutor Conversations:</strong> Questions and responses exchanged with the AI Tutor to maintain multi-turn context (limited to recent messages).
            </div>
            <div style={{ background: 'var(--surface-alt)', padding: '14px', borderRadius: 'var(--radius)' }}>
              <strong>Aggregated Expression Summaries:</strong> Stored only when explicit consent is provided, containing high-level category counts with a 7-day TTL expiration.
            </div>
          </div>
        </section>

        <section>
          <h2 style={{ fontSize: '1.4rem', fontWeight: '700', marginBottom: '8px' }}>
            4. Full Usability Without Camera
          </h2>
          <p style={{ color: 'var(--text-muted)', lineHeight: '1.7' }}>
            Every educational feature of EIT—video lectures, quizzes, step-by-step explanations, code walkthroughs,
            and progress tracking—remains 100% available without enabling the camera.
          </p>
        </section>
      </div>

      <div style={{ marginTop: '32px' }}>
        <Link to="/dashboard" className="btn btn-primary">
          &larr; Return to Dashboard
        </Link>
      </div>
    </div>
  );
}
