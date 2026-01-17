import { useState, useEffect, useRef } from 'react';
import * as holisticModule from '@mediapipe/holistic';
import * as cameraModule from '@mediapipe/camera_utils';

const DatasetProcessor = () => {

  const [videos, setVideos] = useState([]);
  const [processedCount, setProcessedCount] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);
  const [logs, setLogs] = useState([]);
  const holisticRef = useRef(null);
  
  const addLog = (msg) => setLogs(prev => [...prev.slice(-4), msg]);

  useEffect(() => {
    // Initial setup
    createHolisticInstance();
    fetchVideos();
    
    return () => {
      if (holisticRef.current) holisticRef.current.close();
    };
  }, []);

  const createHolisticInstance = async () => {
    if (holisticRef.current) {
        try { await holisticRef.current.close(); } catch(e) {}
    }
    
    const Holistic = window.Holistic || holisticModule.Holistic;
    const holistic = new Holistic({
      locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/holistic/${file}`
    });
    
    holistic.setOptions({
      modelComplexity: 1,
      smoothLandmarks: true,
      enableSegmentation: false,
      smoothSegmentation: false,
      refineFaceLandmarks: false,
      minDetectionConfidence: 0.5,
      minTrackingConfidence: 0.5
    });
    
    holisticRef.current = holistic;
    console.log("MediaPipe (Re)Initialized");
  };

  const fetchVideos = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/list-videos');
      const data = await res.json();
      setVideos(data.videos || []);
      addLog(`Found ${data.count} videos`);
    } catch (err) {
      addLog(`Error fetching videos: ${err.message}`);
    }
  };

  const startProcessing = async () => {
      setIsProcessing(true);
      setProcessedCount(0);
      
      for (const video of videos) {
          try {
              // Re-init every 10 videos or on error to clear memory
              if (processedCount > 0 && processedCount % 20 === 0) {
                  await createHolisticInstance();
              }
              
              await processVideoSimple(video);
              setProcessedCount(prev => prev + 1);
              
              // Small delay to let UI update and GC run
              await new Promise(r => setTimeout(r, 100));
          } catch (e) {
              addLog(`Failed ${video.filename}: ${e}`);
              // If crash, try to re-init for next video
              await createHolisticInstance();
          }
      }
      setIsProcessing(false);
      addLog("All Processing Complete!");
  };

  const processVideoSimple = (video) => {
      return new Promise((resolve, reject) => {
          const videoEl = document.createElement('video');
          videoEl.crossOrigin = "anonymous";
          videoEl.src = `http://localhost:8000${video.url}`;
          videoEl.muted = true;
          videoEl.playbackRate = 1.0;

          const frames = [];
          let frameId = 0;
          let isProcessingFrame = false;
          
          // Use Canvas for stability
          const canvas = document.createElement('canvas');
          const ctx = canvas.getContext('2d');

          // Setup result handler
          // We need a way to deregister this callback later if we wanted to be super clean, 
          // but replacing holistic instance handles that.
          // For now, we update the onResults handler for the CURRENT instance.
          if (holisticRef.current) {
              holisticRef.current.onResults((results) => {
                  const keypoints = extractKeypoints(results);
                  frames.push({ frame_id: frameId++, keypoints });
                  isProcessingFrame = false;
              });
          }

          videoEl.onloadeddata = () => {
             canvas.width = videoEl.videoWidth;
             canvas.height = videoEl.videoHeight;
          };

          videoEl.onended = async () => {
              addLog(`Finished ${video.filename}: ${frames.length} frames`);
              if (frames.length > 0) {
                  await saveData(video, frames);
              } else {
                  addLog(`WARNING: 0 frames for ${video.filename}`);
              }
              resolve();
          };
          
          videoEl.onerror = () => {
              addLog(`Error loading ${video.filename}`);
              resolve(); // Skip
          };

          const processNextFrame = async () => {
              if (videoEl.paused || videoEl.ended) return;

              if (!isProcessingFrame && holisticRef.current) {
                  isProcessingFrame = true;
                  try {
                      // Draw to canvas first (more stable for WASM)
                      ctx.drawImage(videoEl, 0, 0);
                      await holisticRef.current.send({ image: canvas });
                  } catch (e) {
                      console.error("MediaPipe send error:", e);
                      isProcessingFrame = false;
                      // Fatal error for this video
                      videoEl.pause();
                      addLog(`Crash on ${video.filename}`);
                      resolve(); // Skip to next (parent loop will re-init)
                      return;
                  }
              }
              
              if (videoEl.requestVideoFrameCallback) {
                  videoEl.requestVideoFrameCallback(processNextFrame);
              } else {
                  requestAnimationFrame(processNextFrame);
              }
          };

          videoEl.onplay = () => processNextFrame();
          
          videoEl.play().catch(e => {
              addLog(`Play error: ${e.message}`);
              resolve();
          });
      });
  };

  const saveData = async (video, frames) => {
      try {
          await fetch('http://localhost:8000/api/save-processed-data', {
              method: 'POST',
              headers: {'Content-Type': 'application/json'},
              body: JSON.stringify({
                  filename: video.filename,
                  sign_label: video.sign_label,
                  frames: frames,
                  source_video: video.filename
              })
          });
      } catch (e) {
          console.error(e);
      }
  };

  const extractKeypoints = (results) => {
    const keypoints = [];
    if (results.poseLandmarks) results.poseLandmarks.forEach(l => keypoints.push([l.x, l.y, l.z]));
    else for(let i=0; i<33; i++) keypoints.push([0,0,0]);
    
    // Face (468) - default even if refined is false
    if (results.faceLandmarks) results.faceLandmarks.forEach(l => keypoints.push([l.x, l.y, l.z]));
    else for(let i=0; i<468; i++) keypoints.push([0,0,0]);
    
    if (results.leftHandLandmarks) results.leftHandLandmarks.forEach(l => keypoints.push([l.x, l.y, l.z]));
    else for(let i=0; i<21; i++) keypoints.push([0,0,0]);
    
    if (results.rightHandLandmarks) results.rightHandLandmarks.forEach(l => keypoints.push([l.x, l.y, l.z]));
    else for(let i=0; i<21; i++) keypoints.push([0,0,0]);
    
    return keypoints;
  };

  return (
    <div style={{padding: 20, background: '#1a1a2e', color: 'white', minHeight: '100vh'}}>
      <h2>Dataset Processor (Hackathon Fix)</h2>
      <button onClick={startProcessing} disabled={isProcessing} style={{
          padding: '10px 20px', background: '#e94560', border: 'none', color: 'white', borderRadius: 5, fontSize: 16, cursor: 'pointer'
      }}>
        {isProcessing ? 'Processing Videos...' : 'Start Extraction'}
      </button>
      
      <div style={{marginTop: 20}}>
        Progress: {processedCount} / {videos.length} videos
        <div style={{width: '100%', height: 20, background: '#333', borderRadius: 10, marginTop: 10}}>
            <div style={{
                width: `${(processedCount / Math.max(videos.length, 1)) * 100}%`,
                height: '100%', background: '#4CAF50', borderRadius: 10, transition: 'width 0.3s'
            }}></div>
        </div>
      </div>
      
      <div style={{marginTop: 20, fontFamily: 'monospace', background: '#000', padding: 10, borderRadius: 5}}>
          {logs.map((l, i) => <div key={i}>{l}</div>)}
      </div>
    </div>
  );
};
export default DatasetProcessor;
