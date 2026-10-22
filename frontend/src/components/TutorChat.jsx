import { useState, useRef, useEffect } from 'react';
import { api } from '../services/api.js';
import LoadingSpinner from './LoadingSpinner.jsx';

const TEACHING_MODES = [
  { id: 'simple', label: 'Simple' },
  { id: 'step_by_step', label: 'Step-by-Step' },
  { id: 'example', label: 'Example' },
  { id: 'programming', label: 'Code' },
  { id: 'quiz', label: 'Quiz' },
  { id: 'summary', label: 'Summary' },
];

export default function TutorChat({
  sessionId,
  lessonId,
  topicId,
  expressionContext = null,
  activePrompt = null,
}) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "Hello! I'm your AI Emotional Intelligence Tutor. How can I help you understand this lesson today?",
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);
  const [input, setInput] = useState('');
  const [selectedMode, setSelectedMode] = useState('simple');
  const [loading, setLoading] = useState(false);
  const [quizQuestion, setQuizQuestion] = useState(null);
  const messagesEndRef = useRef(null);

  // Auto-scroll
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  // Handle external suggestions triggered from LearningSupport overlay
  useEffect(() => {
    if (activePrompt) {
      handleSend(activePrompt);
    }
  }, [activePrompt]);

  const handleSend = async (messageText = null) => {
    const textToSend = messageText || input;
    if (!textToSend.trim() || loading || !sessionId) return;

    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const userMsg = { role: 'user', content: textToSend, time };
    setMessages((prev) => [...prev, userMsg]);
    if (!messageText) setInput('');
    setLoading(true);

    try {
      let res;
      if (selectedMode === 'quiz' && quizQuestion) {
        // Feedback mode
        res = await api.tutorFeedback({
          session_id: sessionId,
          lesson_id: lessonId,
          topic_id: topicId,
          question: quizQuestion,
          submitted_answer: textToSend,
        });
        setQuizQuestion(null);
        setMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            content: res.data?.feedback || 'Thank you for your answer!',
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          },
        ]);
      } else if (selectedMode === 'quiz') {
        res = await api.tutorQuiz({
          session_id: sessionId,
          lesson_id: lessonId,
          topic_id: topicId,
        });
        const qText = res.data?.question || 'Quiz question ready.';
        setQuizQuestion(qText);
        setMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            content: `${qText}\n\n*(Type your answer below)*`,
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          },
        ]);
      } else {
        // Chat / Explain mode
        res = await api.tutorChat({
          session_id: sessionId,
          lesson_id: lessonId,
          topic_id: topicId,
          message: textToSend,
          response_mode: selectedMode,
          expression_context: expressionContext,
        });
        setMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            content: res.data?.response || "I'm ready for your next question!",
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          },
        ]);
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: err.message || 'Sorry, I had trouble generating a response. Please try again.',
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          isError: true,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-panel">
      <div className="chat-header">
        <div className="chat-header-title">
          <span>🤖 AI Tutor</span>
        </div>
        <span className="badge badge-primary">EIT Assistant</span>
      </div>

      <div className="chat-modes">
        {TEACHING_MODES.map((mode) => (
          <button
            key={mode.id}
            onClick={() => {
              setSelectedMode(mode.id);
              if (mode.id === 'quiz') {
                handleSend('Generate a quiz question for this lesson.');
              }
            }}
            className={`chat-mode-btn ${selectedMode === mode.id ? 'active' : ''}`}
          >
            {mode.label}
          </button>
        ))}
      </div>

      <div className="chat-messages">
        {messages.map((m, idx) => (
          <div
            key={idx}
            className={`message-bubble ${m.role === 'user' ? 'message-user' : 'message-tutor'}`}
            style={m.isError ? { borderColor: 'var(--danger)', background: 'var(--danger-light)' } : {}}
          >
            <div style={{ whiteSpace: 'pre-wrap' }}>{m.content}</div>
            <div className="message-time">{m.time}</div>
          </div>
        ))}

        {loading && (
          <div className="message-bubble message-tutor">
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <LoadingSpinner size="sm" message="" />
              <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Thinking...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-area">
        <textarea
          rows={1}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={quizQuestion ? 'Type your answer to the quiz question...' : 'Ask the AI tutor anything...'}
          className="chat-textarea"
          disabled={loading}
        />
        <button
          onClick={() => handleSend()}
          disabled={!input.trim() || loading}
          className="btn btn-primary btn-sm"
        >
          Send
        </button>
      </div>
    </div>
  );
}
