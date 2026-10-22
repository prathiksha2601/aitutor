import { Link } from 'react-router-dom';
import ProgressBar from './ProgressBar.jsx';

export default function TopicCard({ topic, progress = null, firstLessonId = null }) {
  const percent = progress?.percent || 0;

  return (
    <div className="card topic-card">
      <div className="topic-card-body">
        <div className="topic-card-header">
          <h3 className="topic-card-title">{topic.title}</h3>
          <span className="badge badge-primary">{topic.category}</span>
        </div>
        <p className="topic-card-desc">{topic.description}</p>
        <ProgressBar percent={percent} label="Completion" />
      </div>
      <div className="topic-card-meta">
        <span>{topic.is_active ? 'Active Topic' : 'Archived'}</span>
        {firstLessonId ? (
          <Link to={`/lesson/${firstLessonId}`} className="btn btn-primary btn-sm">
            {percent > 0 ? 'Resume Learning' : 'Start Learning'}
          </Link>
        ) : (
          <Link to={`/dashboard?topic=${topic._id}`} className="btn btn-outline btn-sm">
            View Lessons
          </Link>
        )}
      </div>
    </div>
  );
}
