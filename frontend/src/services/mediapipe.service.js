/**
 * MediaPipe Service for ISL Keypoint Extraction
 */
import { Holistic } from '@mediapipe/holistic';
import { Camera } from '@mediapipe/camera_utils';

class MediaPipeService {
  constructor() {
    this.holistic = null;
    this.camera = null;
    this.onResults = null;
    this.isInitialized = false;
  }

  /**
   * Initialize MediaPipe Holistic
   */
  async initialize(videoElement, onResultsCallback) {
    try {
      this.onResults = onResultsCallback;

      // Initialize Holistic
      this.holistic = new Holistic({
        locateFile: (file) => {
          return `https://cdn.jsdelivr.net/npm/@mediapipe/holistic/${file}`;
        }
      });

      this.holistic.setOptions({
        modelComplexity: 1,
        smoothLandmarks: true,
        enableSegmentation: false,
        smoothSegmentation: false,
        refineFaceLandmarks: false,
        minDetectionConfidence: 0.5,
        minTrackingConfidence: 0.5
      });

      this.holistic.onResults(this.handleResults.bind(this));

      // Initialize camera
      this.camera = new Camera(videoElement, {
        onFrame: async () => {
          if (this.holistic) {
            await this.holistic.send({ image: videoElement });
          }
        },
        width: 640,
        height: 480
      });

      this.isInitialized = true;
      console.log('MediaPipe initialized successfully');
    } catch (error) {
      console.error('Error initializing MediaPipe:', error);
      throw error;
    }
  }

  /**
   * Handle MediaPipe results
   */
  handleResults(results) {
    if (this.onResults) {
      // Extract keypoints
      const keypoints = this.extractKeypoints(results);
      this.onResults(keypoints, results);
    }
  }

  /**
   * Extract keypoints from MediaPipe results
   */
  extractKeypoints(results) {
    const keypoints = [];

    // Pose landmarks (33 points)
    if (results.poseLandmarks) {
      results.poseLandmarks.forEach(landmark => {
        keypoints.push([landmark.x, landmark.y, landmark.z]);
      });
    } else {
      // Add zeros if no pose detected
      for (let i = 0; i < 33; i++) {
        keypoints.push([0, 0, 0]);
      }
    }

    // Left hand landmarks (21 points)
    if (results.leftHandLandmarks) {
      results.leftHandLandmarks.forEach(landmark => {
        keypoints.push([landmark.x, landmark.y, landmark.z]);
      });
    } else {
      for (let i = 0; i < 21; i++) {
        keypoints.push([0, 0, 0]);
      }
    }

    // Right hand landmarks (21 points)
    if (results.rightHandLandmarks) {
      results.rightHandLandmarks.forEach(landmark => {
        keypoints.push([landmark.x, landmark.y, landmark.z]);
      });
    } else {
      for (let i = 0; i < 21; i++) {
        keypoints.push([0, 0, 0]);
      }
    }

    // Face landmarks (468 points) - optional, can be excluded for performance
    if (results.faceLandmarks) {
      results.faceLandmarks.forEach(landmark => {
        keypoints.push([landmark.x, landmark.y, landmark.z]);
      });
    } else {
      for (let i = 0; i < 468; i++) {
        keypoints.push([0, 0, 0]);
      }
    }

    return keypoints;
  }

  /**
   * Start camera
   */
  async start() {
    if (this.camera && this.isInitialized) {
      await this.camera.start();
      console.log('Camera started');
    } else {
      throw new Error('MediaPipe not initialized');
    }
  }

  /**
   * Stop camera
   */
  stop() {
    if (this.camera) {
      this.camera.stop();
      console.log('Camera stopped');
    }
  }

  /**
   * Cleanup
   */
  cleanup() {
    this.stop();
    if (this.holistic) {
      this.holistic.close();
    }
    this.holistic = null;
    this.camera = null;
    this.isInitialized = false;
  }
}

export default new MediaPipeService();
