import { useEffect, useRef, useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera } from '@react-three/drei';
import * as THREE from 'three';
import './Avatar3D.css';

// Simple humanoid avatar component
function HumanoidAvatar({ signText }) {
  const groupRef = useRef();
  const [animationPhase, setAnimationPhase] = useState(0);

  useEffect(() => {
    // Simple animation when signText changes
    if (signText) {
      let phase = 0;
      const interval = setInterval(() => {
        phase += 0.1;
        setAnimationPhase(phase);
      }, 50);

      return () => clearInterval(interval);
    }
  }, [signText]);

  // Animate arms based on sign text
  const leftArmRotation = signText ? [0, 0, Math.sin(animationPhase) * 0.5] : [0, 0, 0.3];
  const rightArmRotation = signText ? [0, 0, -Math.sin(animationPhase) * 0.5] : [0, 0, -0.3];

  return (
    <group ref={groupRef} position={[0, -1, 0]}>
      {/* Head */}
      <mesh position={[0, 1.6, 0]}>
        <sphereGeometry args={[0.15, 32, 32]} />
        <meshStandardMaterial color="#ffdbac" />
      </mesh>

      {/* Body */}
      <mesh position={[0, 1, 0]}>
        <boxGeometry args={[0.4, 0.8, 0.2]} />
        <meshStandardMaterial color="#4a90e2" />
      </mesh>

      {/* Left Arm */}
      <group position={[-0.25, 1.2, 0]} rotation={leftArmRotation}>
        <mesh position={[0, -0.3, 0]}>
          <cylinderGeometry args={[0.05, 0.05, 0.6, 16]} />
          <meshStandardMaterial color="#4a90e2" />
        </mesh>
        {/* Left Hand */}
        <mesh position={[0, -0.65, 0]}>
          <sphereGeometry args={[0.08, 16, 16]} />
          <meshStandardMaterial color="#ffdbac" />
        </mesh>
      </group>

      {/* Right Arm */}
      <group position={[0.25, 1.2, 0]} rotation={rightArmRotation}>
        <mesh position={[0, -0.3, 0]}>
          <cylinderGeometry args={[0.05, 0.05, 0.6, 16]} />
          <meshStandardMaterial color="#4a90e2" />
        </mesh>
        {/* Right Hand */}
        <mesh position={[0, -0.65, 0]}>
          <sphereGeometry args={[0.08, 16, 16]} />
          <meshStandardMaterial color="#ffdbac" />
        </mesh>
      </group>

      {/* Left Leg */}
      <mesh position={[-0.12, 0.2, 0]}>
        <cylinderGeometry args={[0.08, 0.08, 0.8, 16]} />
        <meshStandardMaterial color="#2c3e50" />
      </mesh>

      {/* Right Leg */}
      <mesh position={[0.12, 0.2, 0]}>
        <cylinderGeometry args={[0.08, 0.08, 0.8, 16]} />
        <meshStandardMaterial color="#2c3e50" />
      </mesh>
    </group>
  );
}

function Avatar3D({ signText }) {
  return (
    <div className="avatar-3d-container">
      <div className="avatar-canvas">
        <Canvas>
          <PerspectiveCamera makeDefault position={[0, 1, 3]} />
          <OrbitControls 
            enableZoom={true}
            enablePan={false}
            minDistance={2}
            maxDistance={5}
            target={[0, 1, 0]}
          />
          
          {/* Lighting */}
          <ambientLight intensity={0.5} />
          <directionalLight position={[5, 5, 5]} intensity={1} />
          <directionalLight position={[-5, 5, -5]} intensity={0.5} />
          
          {/* Avatar */}
          <HumanoidAvatar signText={signText} />
          
          {/* Ground */}
          <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.2, 0]} receiveShadow>
            <planeGeometry args={[10, 10]} />
            <meshStandardMaterial color="#34495e" opacity={0.3} transparent />
          </mesh>
        </Canvas>
      </div>
      
      <div className="avatar-info">
        {signText ? (
          <>
            <div className="sign-indicator">
              <span className="pulse-dot"></span>
              <span>Signing: <strong>{signText}</strong></span>
            </div>
          </>
        ) : (
          <div className="placeholder-text">
            <span>👋</span>
            <p>Avatar will display sign language here</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default Avatar3D;
