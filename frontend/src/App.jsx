import { Routes, Route } from 'react-router-dom';
import NavBar from './components/NavBar.jsx';
import LandingPage from './pages/LandingPage.jsx';
import Dashboard from './pages/Dashboard.jsx';
import LessonPage from './pages/LessonPage.jsx';
import PrivacyPage from './pages/PrivacyPage.jsx';
import NotFound from './pages/NotFound.jsx';

function App() {
  return (
    <div className="app">
      <NavBar />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/lesson/:lessonId" element={<LessonPage />} />
          <Route path="/privacy" element={<PrivacyPage />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
