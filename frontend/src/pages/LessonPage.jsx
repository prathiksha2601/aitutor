import { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../services/api.js';
import { useWebcam } from '../hooks/useWebcam.js';
import VideoPlayer from '../components/VideoPlayer.jsx';
import TutorChat from '../components/TutorChat.jsx';
import WebcamPanel from '../components/WebcamPanel.jsx';
import LearningSupport from '../components/LearningSupport.jsx';
import LoadingSpinner from '../components/LoadingSpinner.jsx';
import ErrorMessage from '../components/ErrorMessage.jsx';
import '../styles/lesson.css';
import '../styles/webcam.css';

export default function LessonPage() {
  const { lessonId } = useParams();

  const [lesson, setLesson] = useState(null);
  const [topic, setTopic] = useState(null);
  const [siblingLessons, setSiblingLessons] = useState([]);
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Learning support suggestion state
  const [suggestion, setSuggestion] = useState(null);
  const [activePrompt, setActivePrompt] = useState(null);
  const [recentExpressions, setRecentExpressions] = useState([]);

  // Webcam hook
  const webcam = useWebcam();
  const sessionRef = useRef(null);

  // Fetch lesson, topic, sibling lessons, and initialize session
  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    setError(null);

    async function initLesson() {
      try {
        const lessonRes = await api.getLesson(lessonId);
        const currentLesson = lessonRes.data?.lesson;
        if (!currentLesson) throw new Error('Lesson not found.');

        if (!isMounted) return;
        setLesson(currentLesson);

        // Fetch sibling lessons in the same topic
        if (currentLesson.topic_id) {
          const siblingsRes = await api.getLessons(currentLesson.topic_id);
          if (isMounted) {
            setSiblingLessons(siblingsRes.data || []);
          }
        }

        // Create learning session
        const sessRes = await api.createSession({
          lesson_id: currentLesson._id,
          topic_id: currentLesson.topic_id,
        });

        if (isMounted) {
          const newSession = sessRes.data?.session;
          setSession(newSession);
          sessionRef.current = newSession;
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message || 'Unable to load lesson details.');
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    }

    initLesson();

    // Cleanup: end session and ensure webcam shuts down
    return () => {
      isMounted = false;
      webcam.disable();
      if (sessionRef.current?._id) {
        api.endSession(sessionRef.current._id).catch(() => {});
      }
    };
  }, [lessonId]);

  // Periodic progress update
  const handleTimeUpdate = (seconds) => {
    if (!session?._id || !lesson?._id) return;

    // Update session timestamp
    api.updateSession(session._id, { last_position_seconds: seconds }).catch(() => {});

    // Save progress event
    const isCompleted = lesson.duration_seconds && seconds >= lesson.duration_seconds * 0.9;
    api.updateProgress({
      lesson_id: lesson._id,
      topic_id: lesson.topic_id,
      last_position_seconds: seconds,
      completion_status: isCompleted ? 'completed' : 'in_progress',
    }).catch(() => {});
  };

  // Video completed
  const handleVideoEnded = () => {
    if (!lesson?._id) return;
    api.updateProgress({
      lesson_id: lesson._id,
      topic_id: lesson.topic_id,
      last_position_seconds: lesson.duration_seconds || 0,
      completion_status: 'completed',
    }).catch(() => {});
  };

  // Handle temporal expression aggregation for learning support
  const handleExpressionUpdate = (exp) => {
    setRecentExpressions((prev) => {
      const updated = [...prev.slice(-9), exp];

      // Check if multiple recent frames show struggle signals
      const struggleCount = updated.filter((e) =>
        ['sad', 'fear', 'angry'].includes(e.category)
      ).length;

      if (struggleCount >= 3 && !suggestion) {
        setSuggestion({
          text: 'Would you like a simpler breakdown or a practical example of this concept?',
          options: [
            'Explain more simply.',
            'Give a practical example.',
            'Ask me a practice question.',
            'Continue learning.',
          ],
        });
      }

      return updated;
    });
  };

  // User clicked an option on the learning support overlay
  const handleSelectSupportOption = (option) => {
    setSuggestion(null);
    if (option === 'Continue learning.') return;
    setActivePrompt(`Please ${option.toLowerCase()}`);
  };

  if (loading) {
    return (
      <div className="container" style={{ padding: '80px 0' }}>
        <LoadingSpinner message="Setting up your learning environment..." />
      </div>
    );
  }

  if (error || !lesson) {
    return (
      <div className="container" style={{ padding: '60px 0' }}>
        <ErrorMessage message={error || 'Lesson not found.'} />
        <Link to="/dashboard" className="btn btn-outline" style={{ marginTop: '16px' }}>
          &larr; Back to Dashboard
        </Link>
      </div>
    );
  }

  return (
    <div className="lesson-page">
      <div className="container">
        {/* Breadcrumb Navigation */}
        <div style={{ marginBottom: '16px', fontSize: '0.9rem', color: 'var(--text-muted)' }}>
          <Link to="/dashboard">Dashboard</Link>
          <span style={{ margin: '0 8px' }}>/</span>
          <span>{lesson.title}</span>
        </div>

        <div className="lesson-layout">
          {/* Left Column: Video and Lesson Context */}
          <div>
            <VideoPlayer
              videoUrl={lesson.video_url}
              videoType={lesson.video_type}
              title={lesson.title}
              initialPosition={session?.last_position_seconds || 0}
              onTimeUpdate={handleTimeUpdate}
              onEnded={handleVideoEnded}
            />

            <div className="lesson-info">
              <h1>{lesson.title}</h1>
              <p>{lesson.description}</p>
            </div>

            {/* Sibling Lessons Navigation */}
            {siblingLessons.length > 1 && (
              <div style={{ marginTop: '36px' }}>
                <h3 style={{ fontSize: '1.15rem', fontWeight: '700', marginBottom: '14px' }}>
                  Lessons in this Track
                </h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {siblingLessons.map((sib) => (
                    <Link
                      key={sib._id}
                      to={`/lesson/${sib._id}`}
                      className="card"
                      style={{
                        padding: '12px 16px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        textDecoration: 'none',
                        color: 'inherit',
                        borderLeft: sib._id === lesson._id ? '4px solid var(--primary)' : '1px solid var(--border)',
                      }}
                    >
                      <span style={{ fontWeight: sib._id === lesson._id ? '700' : '500', fontSize: '0.95rem' }}>
                        #{sib.sequence_number} {sib.title}
                      </span>
                      {sib._id === lesson._id && (
                        <span className="badge badge-primary">Current</span>
                      )}
                    </Link>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Right Column: AI Tutor Chat & Optional Visual Feedback */}
          <div>
            <TutorChat
              sessionId={session?._id}
              lessonId={lesson._id}
              topicId={lesson.topic_id}
              expressionContext={recentExpressions.length > 0 ? {
                dominant_expression: recentExpressions[recentExpressions.length - 1].category,
                confidence: recentExpressions[recentExpressions.length - 1].confidence,
                observation_count: recentExpressions.length,
              } : null}
              activePrompt={activePrompt}
            />

            {/* Adaptive Learning Support Overlay */}
            <LearningSupport
              suggestion={suggestion}
              onSelectOption={handleSelectSupportOption}
              onDismiss={() => setSuggestion(null)}
            />

            {/* Optional Webcam Panel */}
            <WebcamPanel
              webcam={webcam}
              onExpressionUpdate={handleExpressionUpdate}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
