import { Link } from 'react-router-dom';
import { formatDuration } from '../utils/format.js';

export default function LessonCard({ lesson, isCurrent = false, progress = null }) {
  const isCompleted = progress?.completion_status === 'completed';
  const inProgress = progress?.completion_status === 'in_progress';

  return (
    <div
      className="card"
      style={{
        padding: '16px 20px',
        borderLeft: isCurrent ? '4px solid var(--primary)' : '1px solid var(--border)',
        marginBottom: '12px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '16px',
      }}
    >
      <div style={{ flex: 1 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '4px' }}>
          <span style={{ fontSize: '0.8rem', fontWeight: '700', color: 'var(--text-muted)' }}>
            #{lesson.sequence_number}
          </span>
          <h4 style={{ fontSize: '1rem', fontWeight: '700' }}>{lesson.title}</h4>
          {isCompleted && <span className="badge badge-success">Completed</span>}
          {inProgress && <span className="badge badge-warning">In Progress</span>}
        </div>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{lesson.description}</p>
        <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '4px', display: 'inline-block' }}>
          Duration: {formatDuration(lesson.duration_seconds)}
        </span>
      </div>
      <div>
        <Link
          to={`/lesson/${lesson._id}`}
          className={`btn btn-sm ${isCurrent ? 'btn-secondary' : 'btn-outline'}`}
        >
          {isCurrent ? 'Now Playing' : isCompleted ? 'Review' : inProgress ? 'Resume' : 'Start'}
        </Link>
      </div>
    </div>
  );
}
