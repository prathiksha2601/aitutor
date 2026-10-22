import { useState, useEffect } from 'react';
import { api } from '../services/api.js';
import TopicCard from '../components/TopicCard.jsx';
import LessonCard from '../components/LessonCard.jsx';
import LoadingSpinner from '../components/LoadingSpinner.jsx';
import ErrorMessage from '../components/ErrorMessage.jsx';
import EmptyState from '../components/EmptyState.jsx';
import '../styles/dashboard.css';

export default function Dashboard() {
  const [topics, setTopics] = useState([]);
  const [lessons, setLessons] = useState([]);
  const [progressMap, setProgressMap] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [topicsRes, lessonsRes, progressRes] = await Promise.all([
        api.getTopics(),
        api.getLessons(),
        api.getProgress(),
      ]);

      setTopics(topicsRes.data || []);
      setLessons(lessonsRes.data || []);

      // Build progress lookup map by lesson_id
      const pMap = {};
      if (progressRes.data?.progress) {
        progressRes.data.progress.forEach((p) => {
          pMap[p.lesson_id] = p;
        });
      }
      setProgressMap(pMap);
    } catch (err) {
      setError(err.message || 'Failed to load dashboard curriculum data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Compute actual completed lessons from stored records
  const completedCount = Object.values(progressMap).filter(
    (p) => p.completion_status === 'completed'
  ).length;

  const inProgressCount = Object.values(progressMap).filter(
    (p) => p.completion_status === 'in_progress'
  ).length;

  // Find first lesson for each topic
  const getFirstLessonForTopic = (topicId) => {
    const topicLessons = lessons.filter((l) => l.topic_id === topicId);
    return topicLessons.length > 0 ? topicLessons[0]._id : null;
  };

  // Compute topic progress from real lesson records
  const getTopicProgress = (topicId) => {
    const topicLessons = lessons.filter((l) => l.topic_id === topicId);
    if (topicLessons.length === 0) return { percent: 0, completed: 0, total: 0 };

    const completed = topicLessons.filter(
      (l) => progressMap[l._id]?.completion_status === 'completed'
    ).length;

    return {
      percent: Math.round((completed / topicLessons.length) * 100),
      completed,
      total: topicLessons.length,
    };
  };

  // Recent in-progress or completed lessons
  const recentLessons = lessons.filter((l) => progressMap[l._id]);

  if (loading) {
    return (
      <div className="container" style={{ padding: '80px 0' }}>
        <LoadingSpinner message="Loading curriculum from database..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="container" style={{ padding: '60px 0' }}>
        <ErrorMessage message={error} onRetry={fetchData} />
      </div>
    );
  }

  return (
    <div className="dashboard-page">
      <div className="container">
        <div className="dashboard-header">
          <h1>Learning Dashboard</h1>
          <p>Explore curriculum tracks, resume active sessions, and track your verified progress.</p>
        </div>

        {/* Real Stats Row */}
        <div className="stats-row">
          <div className="stat-card">
            <div className="stat-icon">📚</div>
            <div className="stat-info">
              <h4>{topics.length}</h4>
              <p>Topics Available</p>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">✅</div>
            <div className="stat-info">
              <h4>{completedCount}</h4>
              <p>Lessons Completed</p>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">⏳</div>
            <div className="stat-info">
              <h4>{inProgressCount}</h4>
              <p>Lessons In Progress</p>
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        {recentLessons.length > 0 && (
          <div style={{ marginBottom: '48px' }}>
            <h2 className="section-label">⚡ Continue Learning</h2>
            <div className="grid-2">
              {recentLessons.slice(0, 4).map((lesson) => (
                <LessonCard
                  key={lesson._id}
                  lesson={lesson}
                  progress={progressMap[lesson._id]}
                />
              ))}
            </div>
          </div>
        )}

        {/* Topics Grid */}
        <div>
          <h2 className="section-label">📖 Core Computer Science Tracks</h2>
          {topics.length === 0 ? (
            <EmptyState
              title="No topics found"
              description="Make sure MongoDB is seeded with demo curriculum."
              actionText="Retry"
              onAction={fetchData}
            />
          ) : (
            <div className="grid-3">
              {topics.map((topic) => (
                <TopicCard
                  key={topic._id}
                  topic={topic}
                  progress={getTopicProgress(topic._id)}
                  firstLessonId={getFirstLessonForTopic(topic._id)}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
