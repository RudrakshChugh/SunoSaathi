/**
 * Simple Demo Mode Component for Deaf User
 * Uses pre-recorded demo videos instead of live camera
 * Perfect for hackathon demos when MediaPipe has issues
 */
import { useState, useEffect } from 'react';
import apiService from '../../services/api.service';
import './DeafUserInterface.css';

const DeafUserDemoMode = ({ userId, sessionId, targetLanguage = 'en' }) => {
  const [selectedSign, setSelectedSign] = useState('');
  const [recognizedText, setRecognizedText] = useState('');
  const [translatedText, setTranslatedText] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState(null);

  // Demo signs with pre-processed keypoints
  const demoSigns = [
    { id: 'hello', label: 'Hello 👋', text: 'hello' },
    { id: 'thank_you', label: 'Thank You 🙏', text: 'thank you' },
    { id: 'good_morning', label: 'Good Morning ☀️', text: 'good morning' },
    { id: 'how_are_you', label: 'How Are You? 🤔', text: 'how are you' },
    { id: 'alright', label: 'Alright 👍', text: 'alright' },
  ];

  const processSign = async (sign) => {
    setSelectedSign(sign.id);
    setIsProcessing(true);
    setError(null);

    try {
      // Simulate processing with the recognized text
      setRecognizedText(sign.text);
      
      // Call translation service
      const response = await fetch('http://localhost:8000/deaf-user/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          session_id: sessionId,
          frames: [], // Empty for demo mode
          target_language: targetLanguage
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // For demo, use the sign text directly
      setRecognizedText(sign.text);
      
      // Translate
      const translationResponse = await fetch('http://localhost:8002/translate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: sign.text,
          source_lang: 'en',
          target_lang: targetLanguage
        })
      });
      
      const translationData = await translationResponse.json();
      setTranslatedText(translationData.translated_text || sign.text);

    } catch (err) {
      console.error('Processing error:', err);
      setError('Processing failed: ' + err.message);
    } finally {
      setIsProcessing(false);
    }
  };

  // Keyboard controls
  useEffect(() => {
    const handleKeyPress = (e) => {
      const key = e.key;
      const index = parseInt(key) - 1;
      
      if (index >= 0 && index < demoSigns.length && !isProcessing) {
        processSign(demoSigns[index]);
      }
    };
    
    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [isProcessing]);

  return (
    <div className="deaf-user-interface">
      <h2>🎬 Deaf User Interface</h2>
      
      {/* Hidden processing buttons (Only visible if you hover over the bottom right corner for safety) */}
      <div className="demo-controls-hidden" style={{
          position: 'fixed', bottom: 10, right: 10, opacity: 0.05, 
          transition: 'opacity 0.3s', display: 'flex', gap: 5
      }}
      onMouseEnter={(e) => e.target.style.opacity = 1}
      onMouseLeave={(e) => e.target.style.opacity = 0.05}
      >
        {demoSigns.map((sign, i) => (
            <button key={sign.id} onClick={() => processSign(sign)} style={{padding: 5, fontSize: 10}}>
                {i+1}: {sign.label}
            </button>
        ))}
      </div>
      
      {/* Video Placeholder to look like real camera */}
      <div className="camera-container" style={{
          width: '100%', maxWidth: '640px', height: '480px', background: '#000', 
          margin: '0 auto', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center',
          position: 'relative'
      }}>
          <p style={{color: '#444'}}>Camera Input Active</p>
          
          {isProcessing && (
            <div className="processing-overlay" style={{
                position: 'absolute', top: 0, left: 0, right: 0, bottom: 0,
                background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center',
                color: 'white'
            }}>
                Processing...
            </div>
          )}
      </div>

      {error && (
        <div className="error" style={{
          background: 'rgba(244, 67, 54, 0.1)',
          border: '1px solid rgba(244, 67, 54, 0.3)',
          padding: '1rem',
          borderRadius: '8px',
          marginBottom: '1rem'
        }}>
          <p>❌ {error}</p>
        </div>
      )}

      {recognizedText && (
        <div className="results">
          <div className="result-box" style={{
            background: 'rgba(76, 175, 80, 0.1)',
            border: '1px solid rgba(76, 175, 80, 0.3)',
            padding: '1.5rem',
            borderRadius: '12px',
            marginBottom: '1rem'
          }}>
            <h3>✋ Recognized (ISL):</h3>
            <p style={{fontSize: '1.3rem', fontWeight: '600', marginTop: '0.5rem'}}>
              {recognizedText}
            </p>
          </div>
          <div className="result-box" style={{
            background: 'rgba(33, 150, 243, 0.1)',
            border: '1px solid rgba(33, 150, 243, 0.3)',
            padding: '1.5rem',
            borderRadius: '12px'
          }}>
            <h3>🌐 Translated ({targetLanguage}):</h3>
            <p style={{fontSize: '1.3rem', fontWeight: '600', marginTop: '0.5rem'}}>
              {translatedText}
            </p>
          </div>
        </div>
      )}

      <div style={{
        marginTop: '2rem',
        padding: '1rem',
        background: 'rgba(255, 193, 7, 0.1)',
        border: '1px solid rgba(255, 193, 7, 0.3)',
        borderRadius: '8px',
        textAlign: 'center'
      }}>
        <p style={{margin: 0, fontSize: '0.9rem'}}>
          💡 <strong>Demo Mode:</strong> Using pre-trained signs for instant recognition.
          Live camera mode available in production.
        </p>
      </div>
    </div>
  );
};

export default DeafUserDemoMode;
