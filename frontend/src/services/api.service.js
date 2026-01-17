/**
 * API Service for backend communication
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
});

class APIService {
  /**
   * Set user preferences
   */
  async setUserPreferences(userId, preferences) {
    const response = await apiClient.post('/users/preferences', {
      user_id: userId,
      ...preferences
    });
    return response.data;
  }

  /**
   * Log user consent
   */
  async logConsent(userId, consentType, granted) {
    const response = await apiClient.post('/users/consent', {
      user_id: userId,
      consent_type: consentType,
      granted: granted
    });
    return response.data;
  }

  /**
   * Process deaf user message (ISL keypoints)
   */
  async processDeafUserMessage(userId, sessionId, frames, targetLanguage = 'en') {
    const response = await apiClient.post('/deaf-user/process', {
      user_id: userId,
      session_id: sessionId,
      frames: frames,
      target_language: targetLanguage
    });
    return response.data;
  }

  /**
   * Process hearing user message (text/speech)
   */
  async processHearingUserMessage(userId, sessionId, text, sourceLang = 'en', targetLang = 'en') {
    const response = await apiClient.post('/hearing-user/process', {
      user_id: userId,
      session_id: sessionId,
      text: text,
      source_language: sourceLang,
      target_language: targetLang
    });
    return response.data;
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
