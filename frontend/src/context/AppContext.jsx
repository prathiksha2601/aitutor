import { createContext, useContext, useState, useEffect } from 'react';
import { generateUUID } from '../utils/uuid.js';

const AppContext = createContext(null);

export function AppProvider({ children }) {
  // Anonymous session management
  const [sessionId] = useState(() => {
    const stored = localStorage.getItem('eit_session_id');
    if (stored) return stored;
    const newId = generateUUID();
    localStorage.setItem('eit_session_id', newId);
    return newId;
  });

  // Auth state
  const [currentUser, setCurrentUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authToken, setAuthToken] = useState(() => localStorage.getItem('eit_auth_token'));

  // Lesson state
  const [currentLesson, setCurrentLesson] = useState(null);
  const [currentTopic, setCurrentTopic] = useState(null);

  // Webcam state
  const [webcamEnabled, setWebcamEnabled] = useState(false);
  const [webcamConsent, setWebcamConsent] = useState(() => {
    return localStorage.getItem('eit_webcam_consent') === 'true';
  });

  // Restore auth from localStorage
  useEffect(() => {
    const token = localStorage.getItem('eit_auth_token');
    if (token) {
      setAuthToken(token);
      setIsAuthenticated(true);
      // Could fetch /api/auth/me here to restore user profile
    }
  }, []);

  const login = (token, user) => {
    localStorage.setItem('eit_auth_token', token);
    setAuthToken(token);
    setCurrentUser(user);
    setIsAuthenticated(true);
  };

  const logout = () => {
    localStorage.removeItem('eit_auth_token');
    setAuthToken(null);
    setCurrentUser(null);
    setIsAuthenticated(false);
  };

  const grantWebcamConsent = () => {
    localStorage.setItem('eit_webcam_consent', 'true');
    setWebcamConsent(true);
  };

  const revokeWebcamConsent = () => {
    localStorage.setItem('eit_webcam_consent', 'false');
    setWebcamConsent(false);
    setWebcamEnabled(false);
  };

  const enableWebcam = () => setWebcamEnabled(true);
  const disableWebcam = () => setWebcamEnabled(false);

  return (
    <AppContext.Provider value={{
      sessionId,
      authToken,
      currentUser,
      isAuthenticated,
      currentLesson,
      currentTopic,
      webcamEnabled,
      webcamConsent,
      setCurrentLesson,
      setCurrentTopic,
      login,
      logout,
      enableWebcam,
      disableWebcam,
      grantWebcamConsent,
      revokeWebcamConsent,
    }}>
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
}
