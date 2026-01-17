import { useState, useEffect, useRef } from 'react';
import apiService from '../../services/api.service';

const VideoProcessor = () => {
  const videoRef = useRef(null);
  const [manifest, setManifest] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [processingStatus, setProcessingStatus] = useState('Initializing...');
  const [logs, setLogs] = useState([]);
  const [holistic, setHolistic] = useState(null);
  const currentFramesRef = useRef([]); // Store frames for current video
  const frameIdRef = useRef(0);

  // Initialize MediaPipe
  const initMediaPipe = async () => {
    try {
      setProcessingStatus('Initializing MediaPipe...');
      
      const mpModule = await import('@mediapipe/holistic');
      // console.log('MediaPipe Module:', mpModule); // Causing TypeError: Cannot convert object to primitive value
      
      // Flexible import strategy
      let HolisticClass = mpModule.Holistic;
      if (!HolisticClass && mpModule.default) {
          if (typeof mpModule.default === 'function') HolisticClass = mpModule.default;
          else if (mpModule.default.Holistic) HolisticClass = mpModule.default.Holistic;
      }
      
      if (!HolisticClass && window.Holistic) HolisticClass = window.Holistic;

      if (!HolisticClass) {
        throw new Error(`Holistic class not found. Keys: ${Object.keys(mpModule).join(', ')}`);
      }

      console.log('Using Holistic Class');
      
      const h = new HolisticClass({
        locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/holistic/${file}`
      });

      h.setOptions({
        modelComplexity: 1,
        smoothLandmarks: true,
        enableSegmentation: false,
        refineFaceLandmarks: false
      });

      h.onResults(handleResults);
      setHolistic(h);
      addLog('MediaPipe initialized successfully');
      setProcessingStatus('Ready to start');
    } catch (err) {
      console.error('MediaPipe Init Error:', err);
      addLog(`Error initializing MediaPipe: ${err.message}`);
      setProcessingStatus('Initialization Failed');
    }
  };

  useEffect(() => {
    initMediaPipe();
  }, []);

  // Load Manifest
  useEffect(() => {
    fetch('/video_manifest.json')
      .then(res => res.json())
      .then(data => {
        setManifest(data);
        addLog(`Loaded manifest with ${data.length} videos`);
        setProcessingStatus('Ready to start');
      })
      .catch(err => addLog(`Error loading manifest: ${err.message}`));
  }, []);

  const addLog = (msg) => {
    setLogs(prev => [`[${new Date().toLocaleTimeString()}] ${msg}`, ...prev].slice(0, 50));
  };

  const handleResults = (results) => {
    // Extract keypoints
    const keypoints = [];
    
    // Helper to extract points
    const addPoints = (landmarks, count) => {
      if (landmarks) {
        landmarks.forEach(lm => keypoints.push([lm.x, lm.y, lm.z]));
      } else {
        for(let i=0; i<count; i++) keypoints.push([0,0,0]);
      }
    };

    addPoints(results.poseLandmarks, 33);
    addPoints(results.leftHandLandmarks, 21);
    addPoints(results.rightHandLandmarks, 21);
    // Face (skip for now or include? The Python script included it. Let's include it to match)
    // Wait, the Python script used 468? Yes.
    // But earlier I verified the Python verification script checks for 543 points.
    // 33 + 21 + 21 + 468 = 543.
    addPoints(results.faceLandmarks, 468); 

    currentFramesRef.current.push({
      frame_id: frameIdRef.current++,
      keypoints: keypoints
    });
  };

  const processNextVideo = async () => {
    if (!holistic || currentIndex >= manifest.length) {
      setProcessingStatus('Processing Complete!');
      return;
    }

    const videoItem = manifest[currentIndex];
    setProcessingStatus(`Processing (${currentIndex + 1}/${manifest.length}): ${videoItem.filename}`);
    
    // Reset output buffer
    currentFramesRef.current = [];
    frameIdRef.current = 0;

    // Load video
    if (videoRef.current) {
      videoRef.current.crossOrigin = "anonymous";
      videoRef.current.muted = true;
      videoRef.current.playbackRate = 1.5; 
      
      const playVideo = async (retryCount = 0) => {
        try {
          if (retryCount > 3) throw new Error("Max retries exceeded");
          
          await new Promise(resolve => setTimeout(resolve, 500)); 
          await videoRef.current.play();
          processVideoFrames(videoItem);
          
          // Safety timeout
          setTimeout(() => {
            if (currentIndex === manifest.indexOf(videoItem)) {
                if (currentFramesRef.current.length === 0) {
                    console.warn(`Timeout 0 frames, retrying ${videoItem.filename}`);
                    playVideo(retryCount + 1);
                } else {
                    console.warn('Timeout with frames, forcing save');
                    saveResults(videoItem).then(() => setCurrentIndex(idx => idx + 1));
                }
            }
          }, 12000); 

        } catch (err) {
          addLog(`Error playing ${videoItem.filename}: ${err.message}`);
          
          // If interrupted, retry immediately
          if (err.message.includes('interrupted')) {
              console.log('Interrupted, retrying...');
              setTimeout(() => playVideo(retryCount + 1), 300);
          } else {
              setTimeout(() => setCurrentIndex(prev => prev + 1), 1000);
          }
        }
      };
      playVideo();
    }
  };

  const processVideoFrames = (videoItem) => {
    const processFrame = async () => {
      if (!videoRef.current) return;

      // Check if video actually ended or if we manually moved on
      if (videoRef.current.ended || videoRef.current.paused) {
        
        // CRITICAL: Only move on if we have frames
        if (currentFramesRef.current.length > 0) { 
             await saveResults(videoItem);
             if (currentIndex === manifest.indexOf(videoItem)) {
                setCurrentIndex(prev => prev + 1);
             }
        } else {
            // No frames? Retry this video!
            addLog(`❌ No frames for ${videoItem.filename} - RETRYING`);
            currentFramesRef.current = [];
            videoRef.current.currentTime = 0;
            try {
                await videoRef.current.play();
                processFrame(); // Restart loop
            } catch(e) {
                console.error("Retry failed", e);
            }
            return;
        }
        return;
      }

      await holistic.send({ image: videoRef.current });
      requestAnimationFrame(processFrame);
    };
    processFrame();
  };

  // Add listener for 'ended' event as primary trigger
  useEffect(() => {
    const videoEl = videoRef.current;
    if (!videoEl) return;

    const onEnded = () => {
        console.log('Video ended event fired');
    };
    
    videoEl.addEventListener('ended', onEnded);
    return () => videoEl.removeEventListener('ended', onEnded);
  }, []);

  const saveResults = async (videoItem) => {
    if (currentFramesRef.current.length === 0) {
      addLog(`Warning: No frames extracted for ${videoItem.filename}`);
      return;
    }

    try {
      await fetch('http://localhost:8000/save_training_sample', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          sign_label: videoItem.sign_label,
          frames: currentFramesRef.current,
          source_video: videoItem.filename
        }),
      });
      addLog(`Saved ${videoItem.filename} (${currentFramesRef.current.length} frames)`);
    } catch (err) {
      addLog(`Error saving ${videoItem.filename}: ${err.message}`);
    }
  };

  // Trigger next video when currentIndex changes
  useEffect(() => {
    if (currentIndex > 0 && currentIndex < manifest.length) {
      processNextVideo();
    } else if (currentIndex === 0 && manifest.length > 0 && processingStatus === 'Started') {
        processNextVideo();
    }
  }, [currentIndex, processingStatus]);

  const startProcessing = () => {
    setProcessingStatus('Started');
    setCurrentIndex(0);
  };

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h1>🎥 Video Training Data Processor</h1>
      
      <div style={{ marginBottom: '20px' }}>
        <button 
          onClick={startProcessing}
          disabled={!holistic || manifest.length === 0 || processingStatus === 'Started'}
          style={{
            padding: '10px 20px', 
            fontSize: '16px', 
            backgroundColor: '#646cff', 
            color: 'white', 
            border: 'none', 
            borderRadius: '4px',
            cursor: 'pointer',
            marginRight: '10px'
          }}
        >
          Start Processing {manifest.length} Videos
        </button>

        <button 
          onClick={() => setCurrentIndex(prev => Math.min(prev + 1, manifest.length - 1))}
          style={{ padding: '10px 20px', fontSize: '16px', marginRight: '10px' }}
        >
          Skip Next ⏭️
        </button>
        
        <button 
          onClick={() => setCurrentIndex(prev => Math.max(prev - 1, 0))}
          style={{ padding: '10px 20px', fontSize: '16px' }}
        >
          ⏮️ Prev
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        <div>
          <h3>Current Video</h3>
          <p>{processingStatus}</p>
          <video 
            ref={videoRef} 
            width="320" 
            height="240" 
            controls 
            style={{ backgroundColor: '#000' }}
          />
        </div>
        
        <div>
          <h3>Logs</h3>
          <div style={{ 
            height: '300px', 
            overflowY: 'auto', 
            background: '#f1f1f1', 
            padding: '10px',
            borderRadius: '4px',
            fontFamily: 'monospace',
            fontSize: '12px'
          }}>
            {logs.map((log, i) => <div key={i}>{log}</div>)}
          </div>
        </div>
      </div>
    </div>
  );
};

export default VideoProcessor;
