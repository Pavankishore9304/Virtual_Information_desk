import React, { Suspense, useEffect, useRef } from 'react';
import { useLoader, useFrame } from '@react-three/fiber/native';
import { GLTFLoader } from 'three-stdlib';
import { Canvas } from '@react-three/fiber/native';
import { OrbitControls, useAnimations } from '@react-three/drei/native';
import * as THREE from 'three';

const avatarUrl = 'https://models.readyplayer.me/6897a00b275d5cb37290b303.glb';

const Model = ({ isSpeaking }) => {
  const group = useRef<THREE.Group>(null);
  const gltf = useLoader(GLTFLoader, avatarUrl);
  const { actions, names } = useAnimations(gltf.animations, group);

  useEffect(() => {
    const idleAnimation = actions['idle'];
    const talkAnimation = actions['talk'];

    if (isSpeaking && talkAnimation) {
      idleAnimation?.stop();
      talkAnimation.play();
    } else {
      talkAnimation?.stop();
      idleAnimation?.play();
    }
  }, [isSpeaking, actions]);

  return (
    <group ref={group}>
      <primitive 
        object={gltf.scene} 
        scale={1.0} 
        position={[0, -1.65, 0]} 
      />
    </group>
  );
};

export default function Avatar({ isSpeaking }) {
  return (
    <Canvas camera={{ position: [0, 0.2, 2.5], fov: 45 }}>
      <ambientLight intensity={1.5} />
      <directionalLight position={[0, 2, 5]} intensity={3.5} />
      <Suspense fallback={null}>
        <Model isSpeaking={isSpeaking} />
      </Suspense>
    </Canvas>
  );
}
