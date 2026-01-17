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
      <header className="app-header">
        <h1>🤝 SunoSaathi</h1>
        <p className="tagline">Bridging Communication, Breaking Barriers</p>
      </header>

      {!userType ? (
        <div className="user-selection">
          <h2>Welcome! Please select your profile:</h2>
          <div className="user-type-cards">
            <div
              className="user-type-card"
              onClick={() => setUserType('deaf')}
            >
              <div className="card-icon">👋</div>
              <h3>Deaf User</h3>
              <p>Use sign language to communicate</p>
            </div>
            <div
              className="user-type-card"
              onClick={() => setUserType('hearing')}
            >
              <div className="card-icon">🗣️</div>
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
        <p>Built with ❤️ for accessibility | Responsible AI Principles</p>
        <p className="privacy-note">
          🔒 Your privacy matters: No audio/video data is stored
        </p>
      </footer>
    </div>
  );
}

export default App;
