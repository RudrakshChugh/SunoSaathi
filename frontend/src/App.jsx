import { useState, useEffect } from 'react';
import DeafUserInterface from './components/DeafUserInterface/DeafUserInterface';
import HearingUserInterface from './components/HearingUserInterface/HearingUserInterface';
import VideoProcessor from './components/Training/VideoProcessor';
import DatasetProcessor from './components/DatasetProcessor';
import './App.css';

function App() {
  const [userType, setUserType] = useState(null);
  const [userId] = useState(`user_${Date.now()}`);
  const [sessionId] = useState(`session_${Date.now()}`);
  const [targetLanguage, setTargetLanguage] = useState('en');
  const [isTraining, setIsTraining] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);



  if (isTraining) {
    return <VideoProcessor />;
  }

  if (isProcessing) {
    return <DatasetProcessor />;
  }


  const languages = [
    { code: 'en', name: 'English' },
    { code: 'hi', name: 'Hindi' },
    { code: 'bn', name: 'Bengali' },
    { code: 'ta', name: 'Tamil' },
    { code: 'te', name: 'Telugu' },
    { code: 'mr', name: 'Marathi' }
  ];

  return (
    <div className="app">
      {!userType && (
        <header className="app-header">
          <h1>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{verticalAlign: 'middle', marginRight: '8px'}}>
              <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>
              <circle cx="9" cy="7" r="4"/>
              <path d="M22 21v-2a4 4 0 0 0-3-3.87"/>
              <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
            </svg>
            SunoSaathi
          </h1>
          <p className="tagline">Bridging Communication, Breaking Barriers</p>
        </header>
      )}

      {!userType ? (
        <div className="user-selection">
          <h2>Welcome! Please select your profile:</h2>
          <div className="user-type-cards">
            <div
              className="user-type-card"
              onClick={() => setUserType('deaf')}
            >
              <div className="card-icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M7 10v12"/>
                  <path d="M15 5.88 14 10h5.83a2 2 0 0 1 1.92 2.56l-2.33 8A2 2 0 0 1 17.5 22H4a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h2.76a2 2 0 0 0 1.79-1.11L12 2h0a3.13 3.13 0 0 1 3 3.88Z"/>
                </svg>
              </div>
              <h3>Deaf User</h3>
              <p>Use sign language to communicate</p>
            </div>
            <div
              className="user-type-card"
              onClick={() => setUserType('hearing')}
            >
              <div className="card-icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/>
                  <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                  <line x1="12" x2="12" y1="19" y2="22"/>
                </svg>
              </div>
              <h3>Hearing User</h3>
              <p>Use voice to communicate</p>
            </div>
          </div>

          <div className="language-selector">
            <label htmlFor="language">Preferred Language:</label>
            <select
              id="language"
              value={targetLanguage}
              onChange={(e) => setTargetLanguage(e.target.value)}
            >
              {languages.map(lang => (
                <option key={lang.code} value={lang.code}>
                  {lang.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      ) : userType === 'deaf' ? (
        <DeafUserInterface
          userId={userId}
          sessionId={sessionId}
          targetLanguage={targetLanguage}
        />
      ) : (
        <HearingUserInterface
          userId={userId}
          sessionId={sessionId}
          targetLanguage={targetLanguage}
        />
      )}

      <footer className="app-footer">
        <p>
          Built with{' '}
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" style={{verticalAlign: 'middle', color: '#ef4444'}}>
            <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
          </svg>
          {' '}for accessibility | Responsible AI Principles
        </p>
        <p className="privacy-note">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{verticalAlign: 'middle', marginRight: '4px'}}>
            <rect width="18" height="11" x="3" y="11" rx="2" ry="2"/>
            <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
          </svg>
          Your privacy matters: No audio/video data is stored
        </p>
      </footer>
    </div>
  );
}

export default App;
