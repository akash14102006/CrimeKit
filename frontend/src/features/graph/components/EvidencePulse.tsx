"use client";

import React, { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";
import { buildArcCurve } from "./EvidenceConnection";

interface Props {
  from: [number, number, number];
  to: [number, number, number];
  duration?: number;
  delay?: number;
  color?: string;
  isDark?: boolean;
  onComplete?: () => void;
}

export function EvidencePulse({
  from,
  to,
  duration = 1000,
  delay = 0,
  color = "#9fe8ff",
  isDark = true,
  onComplete,
}: Props) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const meshRef = useRef<any>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const lightRef = useRef<any>(null);
  const curve = useMemo(() => buildArcCurve(from, to), [from, to]);
  const elapsed = useRef(-delay);
  const done = useRef(false);

  const pulseColor = isDark ? color : "#0284c7";

  useFrame((_, delta) => {
    if (done.current) return;
    elapsed.current += delta * 1000;

    if (elapsed.current < 0) {
      if (meshRef.current) meshRef.current.visible = false;
      return;
    }

    const t = Math.min(elapsed.current / duration, 1);
    const point = curve.getPoint(t);

    if (meshRef.current) {
      meshRef.current.visible = true;
      meshRef.current.position.copy(point);
    }
    if (lightRef.current) {
      lightRef.current.position.copy(point);
    }

    if (t >= 1) {
      done.current = true;
      if (onComplete) onComplete();
    }
  });

  return (
    <group>
      <mesh ref={meshRef} visible={false}>
        <sphereGeometry args={[0.09, 12, 12]} />
        <meshBasicMaterial color={pulseColor} toneMapped={false} />
      </mesh>
      <pointLight ref={lightRef} color={pulseColor} intensity={isDark ? 1.8 : 2.5} distance={3} decay={2} />
    </group>
  );
}
