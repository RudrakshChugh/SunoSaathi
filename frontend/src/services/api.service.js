/**
 * API Service for backend communication
 */
import axios from 'axios';

const VOICE_API_URL = import.meta.env.VITE_VOICE_API_URL || 'http://localhost:8005';
const ISL_API_URL = import.meta.env.VITE_ISL_API_URL || 'http://localhost:8001';

const voiceClient = axios.create({
  baseURL: VOICE_API_URL,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' }
});

const islClient = axios.create({
  baseURL: ISL_API_URL,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' }
});

class APIService {
  /**
   * Set user preferences
   */
  async setUserPreferences(userId, preferences) {
    const response = await voiceClient.post('/users/preferences', {
      user_id: userId,
      ...preferences
    });
    return response.data;
  }

  /**
   * Log user consent
   */
  async logConsent(userId, consentType, granted) {
    // Only logging to voice backend for now as it handles user data
    const response = await voiceClient.post('/users/consent', {
      user_id: userId,
      consent_type: consentType,
      granted: granted
    });
    return response.data;
  }

  /**
   * Process deaf user message (ISL keypoints)
   * Sends to ISL Recognition Service (Port 8001)
   */
  async processDeafUserMessage(userId, sessionId, frames, targetLanguage = 'en') {
    // Frames are already in correct format: [{frame_id: 0, keypoints: [[x,y,z], ...]}, ...]
    // Just pass them directly
    const response = await islClient.post('/recognize', {
      user_id: userId,
      frames: frames
    });
    
    // Map backend response to frontend expected format
    return {
      status: response.data.text ? 'success' : 'partial',
      recognized_text: response.data.text,
      predictions: response.data.predictions, // [{sign, confidence}]
      translated_text: response.data.text // Determine translation logic later
    };
  }

  /**
   * Process hearing user message (text/speech)
   */
  async processHearingUserMessage(userId, sessionId, text, sourceLang = 'en', targetLang = 'en') {
    const response = await voiceClient.post('/translate-text', {
      text: text
    });
    
    // Map response to frontend format
    return {
      translated_text: response.data.clean_text,
      sequence: response.data.sequence
    };
  }

  /**
   * Health check
   */
  async healthCheck() {
    const response = await apiClient.get('/health');
    return response.data;
  }
}

export default new APIService();
