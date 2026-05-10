"use client";

import React, { useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { 
  OrbitControls, 
  PerspectiveCamera, 
  Html, 
  Grid, 
  ContactShadows, 
  Environment,
  Float,
  Text,
  Cylinder,
  Sphere
} from '@react-three/drei';

interface RadarVisualizationProps {
  positions: number[];
}

const AntennaElement = ({ position, index, actualPos }: { position: [number, number, number], index: number, actualPos: number }) => {
  const [hovered, setHovered] = useState(false);
  
  return (
    <group 
      position={position} 
      onPointerOver={() => setHovered(true)}
      onPointerOut={() => setHovered(false)}
    >
      <Float speed={2} rotationIntensity={0.5} floatIntensity={0.5}>
        <Cylinder args={[0.08, 0.08, 0.6, 32]}>
          <meshStandardMaterial 
            color={hovered ? "#60a5fa" : "#3b82f6"} 
            emissive={hovered ? "#3b82f6" : "#1d4ed8"}
            emissiveIntensity={0.5}
            roughness={0.2}
            metalness={0.8}
          />
        </Cylinder>
      </Float>
      
      {/* Label */}
      <Text
        position={[0, 0.6, 0]}
        fontSize={0.15}
        color="white"
        anchorX="center"
        anchorY="middle"
      >
        {`A${index + 1}`}
      </Text>

      {/* 3D Tooltip */}
      {hovered && (
        <Html distanceFactor={10} position={[0, 1, 0]}>
          <div className="bg-slate-900/90 backdrop-blur-md border border-blue-500/50 p-3 rounded-lg shadow-2xl min-w-[140px] pointer-events-none animate-in zoom-in-95 duration-200">
            <p className="text-[10px] font-bold text-blue-400 uppercase tracking-widest mb-1">Antenna Element {index + 1}</p>
            <div className="flex justify-between items-center">
              <span className="text-slate-400 text-[10px]">Position X:</span>
              <span className="text-white font-mono text-xs font-bold">{actualPos.toFixed(4)}m</span>
            </div>
            <div className="mt-1 h-1 w-full bg-slate-800 rounded-full overflow-hidden">
               <div className="h-full bg-blue-500" style={{ width: `${(actualPos/1.0)*100}%` }}></div>
            </div>
          </div>
        </Html>
      )}
    </group>
  );
};

const Radome = () => {
  return (
    <mesh position={[1.5, 0, 0]} rotation={[0, 0, 0]}>
      <Sphere args={[2.5, 64, 64]} >
        <meshPhysicalMaterial 
          color="#3b82f6"
          transmission={0.95}
          thickness={0.5}
          roughness={0.05}
          envMapIntensity={1}
          transparent
          opacity={0.08}
          metalness={0}
        />
      </Sphere>
    </mesh>
  );
};

const ArrayElements = ({ positions }: { positions: number[] }) => {
  if (!positions || positions.length === 0) return null;
  return (
    <>
      {positions.map((pos, i) => (
        <AntennaElement key={i} index={i} position={[pos, 0, 0]} actualPos={pos} />
      ))}
    </>
  );
};

export default function RadarVisualization({ positions }: RadarVisualizationProps) {
  return (
    <div className="w-full h-[450px] cursor-grab active:cursor-grabbing">
      <Canvas shadows>
        <PerspectiveCamera makeDefault position={[5, 3, 8]} />
        <OrbitControls 
          enablePan={false} 
          minDistance={3} 
          maxDistance={15}
          maxPolarAngle={Math.PI / 2.1}
          autoRotate={!positions || positions.length === 0}
          autoRotateSpeed={0.5}
        />
        
        {/* Advanced Lighting & Environment */}
        <ambientLight intensity={0.5} />
        <spotLight position={[10, 10, 10]} angle={0.15} penumbra={1} intensity={2} castShadow />
        <pointLight position={[-10, -10, -10]} intensity={1} color="#3b82f6" />
        <Environment preset="city" />

        <group position={[-1.5, 0, 0]}>
          <ArrayElements positions={positions} />
          <Radome />
        </group>

        {/* Visual Ground Plane */}
        <Grid 
          infiniteGrid 
          fadeDistance={30} 
          fadeStrength={5} 
          cellSize={0.5} 
          sectionSize={2.5} 
          sectionColor="#3b82f6" 
          cellColor="#1e293b"
          position={[0, -0.3, 0]}
        />
        <ContactShadows 
          position={[0, -0.3, 0]} 
          opacity={0.4} 
          scale={20} 
          blur={2} 
          far={4.5} 
        />
      </Canvas>
    </div>
  );
}
