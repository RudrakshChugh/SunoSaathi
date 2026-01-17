import { useState, useEffect, useRef } from 'react';
import Avatar3D from '../Avatar3D/Avatar3D';
import './HearingUserInterface.css';

function HearingUserInterface({ userId, sessionId, targetLanguage }) {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [translatedText, setTranslatedText] = useState('');
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);
  const [isSpeechSupported, setIsSpeechSupported] = useState(true);
  
  const recognitionRef = useRef(null);

  useEffect(() => {
    // Check if Web Speech API is supported
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
      setIsSpeechSupported(false);
      setError('Speech recognition is not supported in this browser. Please use Chrome, Edge, or Safari.');
      return;
    }

    // Initialize Web Speech API
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US'; // Default to English
    
    recognition.onresult = (event) => {
      const text = event.results[0][0].transcript;
      setTranscript(text);
      setIsListening(false);
      handleSendMessage(text);
    };
    
    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      setError(`Speech recognition error: ${event.error}`);
      setIsListening(false);
    };
    
    recognition.onend = () => {
      setIsListening(false);
    };
    
    recognitionRef.current = recognition;
  }, []);

  const startListening = () => {
    if (recognitionRef.current && !isListening) {
      setError(null);
      setIsListening(true);
      try {
        recognitionRef.current.start();
      } catch (err) {
        console.error('Failed to start recognition:', err);
        setError('Failed to start speech recognition');
        setIsListening(false);
      }
    }
  };

  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    }
  };

  const handleSendMessage = async (text) => {
    if (!text.trim()) return;
    
    setError(null);
    
    try {
      // Send to backend for processing
      const response = await fetch('http://localhost:8000/hearing-user/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          session_id: sessionId,
          text: text,
          source_language: 'en',
          target_language: targetLanguage
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setResponse(data);
      
      // Use the first sign from the signs array for avatar display
      if (data.signs && data.signs.length > 0) {
        setTranslatedText(data.signs[0]); // Show first sign to avatar
      } else {
        setTranslatedText(data.translated_text || text);
      }
      
    } catch (err) {
      console.error('Error processing message:', err);
      setError(`Failed to process message: ${err.message}`);
    }
  };

  const handleTextSubmit = (e) => {
    e.preventDefault();
    handleSendMessage(transcript);
  };

  return (
    <div className="hearing-user-interface">
      <div className="interface-header">
        <h2>🗣️ Hearing User Interface</h2>
        <p>Speak or type your message to communicate in sign language</p>
      </div>

      <div className="main-content">
        {/* 3D Avatar Section */}
        <div className="avatar-section">
          <Avatar3D signText={translatedText} />
        </div>

        {/* Controls Section */}
        <div className="controls-section">
          <div className="speech-controls">
            <h3>Voice Input</h3>
            
            {!isSpeechSupported ? (
              <div className="warning-message">
                ⚠️ Speech recognition not supported. Please use text input.
              </div>
            ) : (
              <div className="voice-buttons">
                <button
                  className={`btn-voice ${isListening ? 'listening' : ''}`}
                  onClick={isListening ? stopListening : startListening}
                  disabled={!isSpeechSupported}
                >
                  {isListening ? (
                    <>
                      <span className="pulse-icon">🎤</span>
                      <span>Listening...</span>
                    </>
                  ) : (
                    <>
                      <span>🎤</span>
                      <span>Start Speaking</span>
                    </>
                  )}
                </button>
              </div>
            )}
          </div>

          <div className="text-input-section">
            <h3>Text Input</h3>
            <form onSubmit={handleTextSubmit}>
              <textarea
                value={transcript}
                onChange={(e) => setTranscript(e.target.value)}
                placeholder="Or type your message here..."
                rows="4"
                className="text-input"
              />
              <button type="submit" className="btn-send" disabled={!transcript.trim()}>
                📤 Send Message
              </button>
            </form>
          </div>

          {/* Error Display */}
          {error && (
            <div className="error-message">
              ⚠️ {error}
            </div>
          )}

          {/* Response Display */}
          {response && (
            <div className="response-section">
              <h3>Translation & Signs</h3>
              <div className="response-card">
                <div className="response-item">
                  <strong>Original:</strong> {response.original_text}
                </div>
                <div className="response-item">
                  <strong>Translated ({targetLanguage}):</strong> {response.translated_text}
                </div>
                {response.signs && response.signs.length > 0 && (
                  <div className="response-item">
                    <strong>Detected Signs:</strong> 
                    <div className="signs-list">
                      {response.signs.map((sign, idx) => (
                        <span key={idx} className="sign-badge">
                          {sign.replace('_', ' ')}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                {response.is_safe !== undefined && (
                  <div className="response-item">
                    <strong>Safety:</strong> {response.is_safe ? '✅ Safe' : '⚠️ Filtered'}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="interface-footer">
        <p className="info-text">
          💡 <strong>Tip:</strong> Click the microphone button and speak clearly, or type your message in the text box.
        </p>
      </div>
    </div>
  );
}

export default HearingUserInterface;
