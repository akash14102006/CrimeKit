"use client";

import React, { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Tube } from "@react-three/drei";
import * as THREE from "three";

export function buildArcCurve(from: [number, number, number], to: [number, number, number]) {
  const start = new THREE.Vector3(...from);
  const end = new THREE.Vector3(...to);
  const mid = start.clone().lerp(end, 0.5);
  mid.y += Math.abs(end.x - start.x) * 0.18 + 0.6;
  return new THREE.CatmullRomCurve3([start, mid, end]);
}

interface Props {
  from: [number, number, number];
  to: [number, number, number];
  active?: boolean;
  dimmed?: boolean;
  color?: string;
  isDark?: boolean;
  onHover?: (hovered: boolean) => void;
  onClick?: () => void;
}

export function EvidenceConnection({
  from,
  to,
  active = false,
  dimmed = false,
  color = "#7fd9ff",
  isDark = true,
  onHover,
  onClick,
}: Props) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const matRef = useRef<any>(null);
  const curve = useMemo(() => buildArcCurve(from, to), [from, to]);

  const tubeColor = useMemo(() => {
    if (isDark) return color;
    return color === "#38bdf8" || color === "#7fd9ff" ? "#0284c7" : color;
  }, [color, isDark]);

  useFrame((state) => {
    if (matRef.current) {
      const pulse = active
        ? isDark ? 0.6 + Math.sin(state.clock.elapsedTime * 4) * 0.25 : 0.85
        : dimmed
        ? isDark ? 0.05 : 0.1
        : isDark ? 0.22 : 0.45;
      matRef.current.opacity = pulse;
    }
  });

  return (
    <group>
      <Tube args={[curve, 32, active ? 0.025 : 0.016, 8, false]}>
        <meshBasicMaterial
          ref={matRef}
          color={tubeColor}
          transparent
          opacity={active ? 0.7 : dimmed ? 0.05 : isDark ? 0.22 : 0.45}
          toneMapped={false}
        />
      </Tube>
      {/* Hitbox Tube for mouse hover */}
      <Tube
        args={[curve, 16, 0.15, 6, false]}
        onPointerOver={(e) => {
          e.stopPropagation();
          document.body.style.cursor = "pointer";
          onHover?.(true);
        }}
        onPointerOut={(e) => {
          e.stopPropagation();
          document.body.style.cursor = "auto";
          onHover?.(false);
        }}
        onClick={(e) => {
          e.stopPropagation();
          onClick?.();
        }}
      >
        <meshBasicMaterial transparent opacity={0} depthWrite={false} />
      </Tube>
    </group>
  );
}
