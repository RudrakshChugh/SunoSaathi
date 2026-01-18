import { useState, useEffect, useRef } from 'react';
import './HearingUserInterface.css';

function HearingUserInterface({ userId, sessionId, targetLanguage }) {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [liveCaption, setLiveCaption] = useState(''); // Real-time interim captions
  const [translatedText, setTranslatedText] = useState('');
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);
  const [isSpeechSupported, setIsSpeechSupported] = useState(true);
  const [volumeLevel, setVolumeLevel] = useState(0); // 0-100 for volume bar

  // ISL Sign display state
  const [currentSignIndex, setCurrentSignIndex] = useState(0);
  const [signSequence, setSignSequence] = useState([]);
  const [isPlayingSequence, setIsPlayingSequence] = useState(false);

  const recognitionRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const animationRef = useRef(null);
  const volumeBarRef = useRef(null);

  // Scroll to top on component mount
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  // Play sign sequence when response changes
  useEffect(() => {
    if (response && response.signs && response.signs.length > 0) {
      playSignSequence(response.signs);
    }
  }, [response]);

  // Function to play sign sequence with auto-advance
  const playSignSequence = async (signs) => {
    if (!signs || signs.length === 0 || isPlayingSequence) return;

    setIsPlayingSequence(true);
    setSignSequence(signs);

    for (let i = 0; i < signs.length; i++) {
      setCurrentSignIndex(i);
      await new Promise(resolve => setTimeout(resolve, 1500)); // Show each sign for 1.5 seconds
    }

    setIsPlayingSequence(false);
  };

  useEffect(() => {
    // Check if Web Speech API is supported
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setIsSpeechSupported(false);
      setError('Speech recognition is not supported in this browser. Please use Chrome, Edge, or Safari.');
      return;
    }

    // Initialize Web Speech API with interim results for live captions
    const recognition = new SpeechRecognition();
    recognition.continuous = true; // Keep listening
    recognition.interimResults = true; // Enable live captions
    recognition.lang = 'en-US';

    recognition.onresult = (event) => {
      let interimTranscript = '';
      let finalTranscript = '';

      // Process all results
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalTranscript += transcript + ' ';
        } else {
          interimTranscript += transcript;
        }
      }

      // Update live caption with interim results
      if (interimTranscript) {
        setLiveCaption(interimTranscript);
      }

      // Update final transcript
      if (finalTranscript) {
        setTranscript(prev => prev + finalTranscript);
        setLiveCaption(''); // Clear interim after final
      }
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      // Only show errors that matter to the user
      if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
        setError('Microphone access denied. Please allow microphone access and try again.');
        setIsListening(false);
        stopVolumeMeter();
      }
    };

    recognition.onend = () => {
      // Auto-restart if user is still listening
      if (recognitionRef.current && isListening) {
        try {
          recognitionRef.current.start();
        } catch (err) {
          // Silent fail - user probably stopped manually
        }
      }
    };

    recognitionRef.current = recognition;

    // Cleanup on unmount
    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (err) {
          // Ignore
        }
      }
    };
  }, []); // Only run once on mount

  // Start volume meter (using proven working formula)
  const startVolumeMeter = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      await audioContext.resume(); // Explicitly resume context

      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 256;

      const microphone = audioContext.createMediaStreamSource(stream);
      microphone.connect(analyser);

      audioContextRef.current = audioContext;
      analyserRef.current = analyser;

      const dataArray = new Uint8Array(analyser.frequencyBinCount);

      const updateVolume = () => {
        analyser.getByteFrequencyData(dataArray);
        let sum = 0;
        for (let i = 0; i < dataArray.length; i++) {
          sum += dataArray[i];
        }
        // Use exact formula from working code
        const average = sum / dataArray.length;
        const volumePercent = Math.min(100, average * 1.2);
        if (volumeBarRef.current) {
          volumeBarRef.current.style.width = volumePercent + '%';
        }
        animationRef.current = requestAnimationFrame(updateVolume);
      };

      updateVolume();
    } catch (err) {
      console.error('Failed to start volume meter:', err);
      setError('Could not access microphone. Please check permissions.');
    }
  };

  // Stop volume meter
  const stopVolumeMeter = () => {
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
      animationRef.current = null;
    }
    if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }
    setVolumeLevel(0);
    if (volumeBarRef.current) {
      volumeBarRef.current.style.width = '0%';
    }
  };

  const startListening = () => {
    if (recognitionRef.current && !isListening) {
      setError(null);
      setTranscript('');
      setLiveCaption('Listening...');
      setIsListening(true);
      startVolumeMeter(); // Start volume visualization
      try {
        recognitionRef.current.start();
      } catch (err) {
        console.error('Failed to start recognition:', err);
        setError('Failed to start speech recognition');
        setIsListening(false);
        stopVolumeMeter();
      }
    }
  };

  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
      stopVolumeMeter();
      setLiveCaption('Processing...');

      // Process final transcript via HTTP (keep this simple for now)
      if (transcript.trim()) {
        handleSendMessage(transcript);
      }
    }
  };

  const handleSendMessage = async (text) => {
    if (!text.trim()) return;

    setError(null);
    setResponse(null);

    try {
      const response = await fetch('http://localhost:8005/translate-text', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: text
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // Map backend response to expected format
      const mappedResponse = {
        original_text: data.raw_text || text,
        translated_text: data.clean_text || text,
        signs: data.sequence || [],
        keywords: data.keywords || [],
        is_safe: true
      };

      setResponse(mappedResponse);
      setLiveCaption('');

      // Use the first sign from the sequence for avatar display
      if (data.sequence && data.sequence.length > 0) {
        setTranslatedText(data.sequence[0]);
      } else {
        setTranslatedText(text);
      }

    } catch (err) {
      console.error('Error processing message:', err);
      setError(`Failed to process message: ${err.message}`);
      setLiveCaption('');
    }
  };

  const handleTextSubmit = (e) => {
    e.preventDefault();

    if (!transcript.trim()) return;

    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
      stopVolumeMeter();
      setLiveCaption('');
    }

    handleSendMessage(transcript);
    setTranscript('');
  };

  return (
    <div className="hearing-user-interface">
      <div className="interface-header">
        <button className="back-btn" onClick={() => window.location.reload()}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M19 12H5" />
            <path d="M12 19l-7-7 7-7" />
          </svg>
          Back
        </button>
        <h1 className="page-title">Voice to Sign Language</h1>
      </div>

      <div className="main-content">
        {/* ISL Sign Display Section */}
        <div className="avatar-section">
          {signSequence.length > 0 ? (
            <div className="sign-display">
              {/* Main large sign image */}
              <img
                src={`/assets/${signSequence[currentSignIndex]}.png`}
                alt={`ISL sign for ${signSequence[currentSignIndex]}`}
                className="main-sign-image"
                onError={(e) => {
                  e.target.src = '/assets/placeholder.png'; // Fallback image
                  e.target.alt = 'Sign not available';
                }}
              />
              <div className="sign-label">{signSequence[currentSignIndex]}</div>

              {/* Thumbnail strip */}
              {signSequence.length > 1 && (
                <div className="isl-strip-container">
                  <div className="isl-strip">
                    {signSequence.map((sign, idx) => (
                      <img
                        key={idx}
                        src={`/assets/${sign}.png`}
                        alt={sign}
                        className={`isl-thumb ${idx === currentSignIndex ? 'active' : ''}`}
                        onClick={() => setCurrentSignIndex(idx)}
                        onError={(e) => {
                          e.target.src = '/assets/placeholder.png';
                        }}
                      />
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="sign-placeholder">
              <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <path d="M7 10v12" />
                <path d="M15 5.88 14 10h5.83a2 2 0 0 1 1.92 2.56l-2.33 8A2 2 0 0 1 17.5 22H4a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h2.76a2 2 0 0 0 1.79-1.11L12 2h0a3.13 3.13 0 0 1 3 3.88Z" />
              </svg>
              <p>ISL signs will appear here</p>
            </div>
          )}
        </div>

        <div className="controls-section">
          <div className="speech-controls">
            <h3>Voice Input</h3>

            {!isSpeechSupported ? (
              <div className="warning-message">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" style={{ verticalAlign: 'middle', marginRight: '4px', color: '#ff9800' }}>
                  <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
                  <line x1="12" y1="9" x2="12" y2="13" />
                  <line x1="12" y1="17" x2="12.01" y2="17" />
                </svg>
                Speech recognition not supported. Please use text input.
              </div>
            ) : (
              <>
                <div className="voice-buttons">
                  <button
                    className={`btn-voice ${isListening ? 'listening' : ''}`}
                    onClick={isListening ? stopListening : startListening}
                    disabled={!isSpeechSupported}
                  >
                    {isListening ? (
                      <>
                        <span className="pulse-icon">
                          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" />
                            <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                          </svg>
                        </span>
                        <span>Listening...</span>
                      </>
                    ) : (
                      <>
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" style={{ marginRight: '8px' }}>
                          <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" />
                          <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                        </svg>
                        <span>Start Speaking</span>
                      </>
                    )}
                  </button>
                </div>

                {/* Live Caption Display */}
                {(isListening || liveCaption) && (
                  <div className="live-caption-box">
                    <div className="caption-label">Live Caption:</div>
                    <div className="caption-text">
                      {liveCaption || transcript || 'Speak now...'}
                    </div>
                  </div>
                )}

                {/* Volume Bar */}
                {isListening && (
                  <div className="volume-meter">
                    <div className="volume-label">Volume:</div>
                    <div className="volume-bar-container">
                      <div
                        className="volume-bar"
                        ref={volumeBarRef}
                      />
                    </div>
                  </div>
                )}
              </>
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
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ verticalAlign: 'middle', marginRight: '4px' }}>
                  <line x1="22" x2="11" y1="2" y2="13" />
                  <polygon points="22 2 15 22 11 13 2 9 22 2" />
                </svg>
                Send Message
              </button>
            </form>
          </div>

          {/* Error Display */}
          {error && (
            <div className="error-message">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" style={{ verticalAlign: 'middle', marginRight: '4px', color: '#ff9800' }}>
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
                <line x1="12" y1="9" x2="12" y2="13" />
                <line x1="12" y1="17" x2="12.01" y2="17" />
              </svg>
              {error}
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
                    <strong>Safety:</strong> {response.is_safe ? (
                      <span style={{ color: '#10b981' }}>
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" style={{ verticalAlign: 'middle', marginLeft: '4px' }}>
                          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                          <polyline points="22 4 12 14.01 9 11.01" />
                        </svg>
                        Safe
                      </span>
                    ) : (
                      <span style={{ color: '#ff9800' }}>
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" style={{ verticalAlign: 'middle', marginLeft: '4px' }}>
                          <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
                        </svg>
                        Filtered
                      </span>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="interface-footer">
        <p className="info-text">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" style={{ verticalAlign: 'middle', marginRight: '4px', color: '#fbbf24' }}>
            <circle cx="12" cy="12" r="10" />
            <path d="M12 16v-4" style={{ stroke: '#18181b', strokeWidth: '2' }} />
            <path d="M12 8h.01" style={{ stroke: '#18181b', strokeWidth: '2' }} />
          </svg>
          <strong>Tip:</strong> Click the microphone button and speak clearly, or type your message in the text box.
        </p>
      </div>
    </div>
  );
}

export default HearingUserInterface;
