"use client";

import React, { useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Environment, Grid, Sphere, Cylinder, Text } from '@react-three/drei';
import * as THREE from 'three';

interface RadarVisualizationProps {
  positions: number[];
}

const AntennaElement = ({ position, index }: { position: [number, number, number], index: number }) => {
  const meshRef = useRef<THREE.Group>(null);
  
  useFrame((state) => {
    if (meshRef.current) {
      // Subtle hovering animation
      meshRef.current.position.y = position[1] + Math.sin(state.clock.elapsedTime * 2 + index) * 0.05;
    }
  });

  return (
    <group position={position} ref={meshRef}>
      {/* Base */}
      <Cylinder args={[0.1, 0.1, 0.5, 16]} position={[0, 0.25, 0]}>
        <meshStandardMaterial color="#3b82f6" metalness={0.8} roughness={0.2} />
      </Cylinder>
      {/* Top sphere (sensor) */}
      <Sphere args={[0.15, 32, 32]} position={[0, 0.55, 0]}>
        <meshStandardMaterial color="#60a5fa" emissive="#3b82f6" emissiveIntensity={0.5} />
      </Sphere>
      {/* Label */}
      <Text position={[0, 0.8, 0]} fontSize={0.2} color="white" anchorX="center" anchorY="middle">
        {`Antenna ${index + 1}`}
      </Text>
      <Text position={[0, -0.2, 0]} fontSize={0.15} color="#cbd5e1" anchorX="center" anchorY="middle">
        {`${position[0].toFixed(2)}m`}
      </Text>
    </group>
  );
};

export default function RadarVisualization({ positions }: RadarVisualizationProps) {
  // Center the array visualization around 0
  const totalLength = positions.length > 0 ? positions[positions.length - 1] : 0;
  const offsetX = -totalLength / 2;

  return (
    <div className="w-full h-[400px] md:h-[500px] glass-panel rounded-xl overflow-hidden relative">
      <div className="absolute top-4 left-4 z-10 bg-slate-900/50 px-3 py-1 rounded-full border border-slate-700/50 backdrop-blur-md">
        <span className="text-xs font-semibold tracking-wider text-blue-300 uppercase">Interactive 3D Array</span>
      </div>
      <Canvas camera={{ position: [0, 3, 5], fov: 45 }}>
        <color attach="background" args={['#0f172a']} />
        <ambientLight intensity={0.4} />
        <directionalLight position={[10, 10, 5]} intensity={1} />
        <pointLight position={[-10, -10, -5]} intensity={0.5} color="#9333ea" />
        
        <Environment preset="city" />
        
        {/* Baseline structure */}
        {positions.length > 0 && (
          <Cylinder 
            args={[0.02, 0.02, totalLength + 0.4, 16]} 
            position={[0, 0, 0]} 
            rotation={[0, 0, Math.PI / 2]}
          >
            <meshStandardMaterial color="#475569" metalness={0.9} roughness={0.1} />
          </Cylinder>
        )}

        {positions.map((pos, i) => (
          <AntennaElement key={i} position={[pos + offsetX, 0, 0]} index={i} />
        ))}
        
        <Grid 
          infiniteGrid 
          fadeDistance={20} 
          sectionColor="#3b82f6" 
          cellColor="#1e293b" 
          position={[0, -0.5, 0]} 
        />
        <OrbitControls enablePan={true} enableZoom={true} enableRotate={true} />
      </Canvas>
    </div>
  );
}
