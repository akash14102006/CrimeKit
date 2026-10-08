"use client";

import React, { useRef, useState, useMemo } from "react";
import { useFrame } from "@react-three/fiber";
import { Text, Billboard } from "@react-three/drei";
import * as THREE from "three";
import type { GraphNode } from "@/types/kg";

interface Props {
  node: GraphNode;
  position: [number, number, number];
  active?: boolean;
  dimmed?: boolean;
  selected?: boolean;
  isDark?: boolean;
  onHover?: (node: GraphNode | null) => void;
  onSelect?: (node: GraphNode) => void;
}

export function ForensicEntityNode({
  node,
  position,
  active = false,
  dimmed = false,
  selected = false,
  isDark = true,
  onHover,
  onSelect,
}: Props) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const groupRef = useRef<any>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const ringRef = useRef<any>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const shellRef = useRef<any>(null);
  const [hovered, setHovered] = useState(false);

  const isCaseCore = node.type === "case_core";
  const defaultNodeColor = isCaseCore ? "#0284c7" : (node.color || "#00f0ff");
  const color = useMemo(() => new THREE.Color(defaultNodeColor), [defaultNodeColor]);

  // Fact classification color ring
  const classColor = useMemo(() => {
    if (node.fact_classification === "OBSERVED") return isDark ? "#10b981" : "#047857";
    if (node.fact_classification === "DERIVED") return isDark ? "#6366f1" : "#4338ca";
    if (node.fact_classification === "HYPOTHESIS") return isDark ? "#f59e0b" : "#b45309";
    if (node.fact_classification === "CANDIDATE") return isDark ? "#ec4899" : "#be185d";
    return isDark ? "#38bdf8" : "#0284c7";
  }, [node.fact_classification, isDark]);

  useFrame((state, delta) => {
    const t = state.clock.elapsedTime;
    if (ringRef.current) {
      ringRef.current.rotation.z += delta * (active ? 1.5 : 0.35);
      ringRef.current.rotation.x = Math.PI / 2.4 + Math.sin(t * 0.3) * 0.06;
    }
    if (shellRef.current) {
      shellRef.current.rotation.y += delta * (active ? 0.7 : 0.18);
    }
    if (groupRef.current) {
      const targetScale = hovered || selected ? 1.2 : 1;
      groupRef.current.scale.lerp(
        new THREE.Vector3(targetScale, targetScale, targetScale),
        0.15
      );
      // Gentle floating bob
      groupRef.current.position.y =
        position[1] + Math.sin(t * 0.6 + position[0]) * 0.08;
    }
  });

  const emissiveIntensity = isDark
    ? (active ? 2.2 : hovered || selected ? 1.5 : dimmed ? 0.15 : 0.7)
    : (active ? 1.2 : hovered || selected ? 0.9 : dimmed ? 0.2 : 0.5);

  const labelColor = isDark
    ? (hovered || selected || active ? "#ffffff" : "#9fb3d9")
    : (hovered || selected || active ? "#0284c7" : "#0f172a");

  return (
    <group
      ref={groupRef}
      position={position}
      onPointerOver={(e) => {
        e.stopPropagation();
        setHovered(true);
        onHover?.(node);
        document.body.style.cursor = "pointer";
      }}
      onPointerOut={(e) => {
        e.stopPropagation();
        setHovered(false);
        onHover?.(null);
        document.body.style.cursor = "auto";
      }}
      onClick={(e) => {
        e.stopPropagation();
        onSelect?.(node);
      }}
    >
      {/* Inner Glowing Core */}
      <mesh>
        <icosahedronGeometry args={[isCaseCore ? 0.75 : 0.44, 1]} />
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={emissiveIntensity}
          roughness={0.25}
          metalness={0.6}
          toneMapped={false}
        />
      </mesh>

      {/* Outer Wireframe Shell */}
      <mesh ref={shellRef}>
        <icosahedronGeometry args={[isCaseCore ? 0.95 : 0.64, 1]} />
        <meshBasicMaterial
          color={isDark ? color : new THREE.Color("#334155")}
          wireframe
          transparent
          opacity={active ? 0.9 : dimmed ? 0.1 : isDark ? 0.4 : 0.6}
        />
      </mesh>

      {/* Rotating Orbit Ring */}
      <mesh ref={ringRef} rotation={[Math.PI / 2.4, 0, 0]}>
        <torusGeometry args={[isCaseCore ? 1.25 : 0.88, 0.014, 8, 64]} />
        <meshBasicMaterial
          color={new THREE.Color(classColor)}
          transparent
          opacity={active ? 0.95 : dimmed ? 0.12 : isDark ? 0.5 : 0.7}
          toneMapped={false}
        />
      </mesh>

      {/* Emissive Point Light */}
      <pointLight
        color={color}
        intensity={isDark ? (active ? 3 : 1.2) : (active ? 1.5 : 0.6)}
        distance={4.5}
        decay={2}
      />

      {/* Camera-Facing 3D Text Label */}
      <Billboard position={[0, isCaseCore ? 1.4 : 1.05, 0]}>
        <Text
          fontSize={isCaseCore ? 0.28 : 0.22}
          color={labelColor}
          anchorX="center"
          anchorY="middle"
          letterSpacing={0.05}
        >
          {node.label}
        </Text>
        {node.fact_classification && !isCaseCore && (active || selected || hovered) && (
          <Text
            position={[0, -0.26, 0]}
            fontSize={0.12}
            color={classColor}
            anchorX="center"
            anchorY="middle"
          >
            {node.fact_classification}
          </Text>
        )}
      </Billboard>
    </group>
  );
}
