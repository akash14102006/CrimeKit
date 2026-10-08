"use client";

import React, { useState, useRef, useMemo, useEffect } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, Stars } from "@react-three/drei";
import * as THREE from "three";
import { ForensicEntityNode } from "./ForensicEntityNode";
import { EvidenceConnection } from "./EvidenceConnection";
import { EvidencePulse } from "./EvidencePulse";
import type { GraphNode, GraphEdge } from "@/types/kg";

interface Props {
  nodes: GraphNode[];
  edges: GraphEdge[];
  caseId?: string;
  selectedNodeId: string | null;
  focusedNodeId: string | null;
  minConfidence: number;
  factClassificationFilter: string;
  nodeTypeFilter: string;
  searchQuery: string;
  isDark?: boolean;
  onNodeClick: (node: GraphNode) => void;
  onEdgeClick: (edge: GraphEdge) => void;
}

function ParticleField({ count = 400, color = "#7fa8ff" }: { count?: number; color?: string }) {
  const points = useRef<THREE.Points>(null);
  const positions = useMemo(() => {
    const arr = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      // Deterministic distribution to prevent SSR/CSR impurity warnings
      const r1 = Math.sin((i + 1) * 12.9898) * 43758.5453;
      const r2 = Math.sin((i + 1) * 78.233) * 43758.5453;
      const r3 = Math.sin((i + 1) * 45.164) * 43758.5453;
      arr[i * 3] = ((r1 - Math.floor(r1)) - 0.5) * 35;
      arr[i * 3 + 1] = ((r2 - Math.floor(r2)) - 0.5) * 22;
      arr[i * 3 + 2] = ((r3 - Math.floor(r3)) - 0.5) * 35;
    }
    return arr;
  }, [count]);

  useFrame((state) => {
    if (points.current) {
      points.current.rotation.y = state.clock.elapsedTime * 0.01;
    }
  });

  return (
    <points ref={points}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          args={[positions, 3]}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.025}
        color={color}
        transparent
        opacity={0.4}
        sizeAttenuation
        depthWrite={false}
      />
    </points>
  );
}

// Camera Flight Controller Component
function CameraRig({ targetPos }: { targetPos: [number, number, number] | null }) {
  useFrame((state) => {
    if (!targetPos) return;
    const camera = state.camera;
    const targetVec = new THREE.Vector3(targetPos[0], targetPos[1] + 1.2, targetPos[2] + 4.5);
    camera.position.lerp(targetVec, 0.05);
  });
  return null;
}

export function Forensic3DScene({
  nodes,
  edges,
  caseId,
  selectedNodeId,
  focusedNodeId,
  minConfidence,
  factClassificationFilter,
  nodeTypeFilter,
  searchQuery,
  isDark = true,
  onNodeClick,
  onEdgeClick,
}: Props) {
  const [, setHoveredNode] = useState<GraphNode | null>(null);
  const [pulses, setPulses] = useState<Array<{ id: string; from: [number, number, number]; to: [number, number, number] }>>([]);

  // Inject Case Core Anchor at (0, 0, 0)
  const caseCoreNode: GraphNode = useMemo(() => ({
    id: `case-core-${caseId || "anchor"}`,
    label: "CASE WORKSPACE",
    type: "case_core",
    fact_classification: "OBSERVED",
    confidence: 1.0,
    val: 14,
    color: "#0284c7",
    x: 0,
    y: 0,
    z: 0,
  }), [caseId]);

  // Map nodes to 3D positions with spatial dispersion
  const positionedNodes = useMemo(() => {
    const list = nodes.filter((n) => {
      if (nodeTypeFilter !== "all" && n.type !== nodeTypeFilter) return false;
      if (factClassificationFilter !== "ALL" && n.fact_classification !== factClassificationFilter) return false;
      if (searchQuery) {
        const q = searchQuery.toLowerCase();
        const matchLabel = n.label.toLowerCase().includes(q);
        const matchType = (n.type || "").toLowerCase().includes(q);
        if (!matchLabel && !matchType) return false;
      }
      return true;
    });

    const all = [caseCoreNode, ...list];
    const numNodes = all.length;

    return all.map((n, idx) => {
      if (n.type === "case_core") {
        return { ...n, pos3d: [0, 0, 0] as [number, number, number] };
      }
      if (n.x !== undefined && n.y !== undefined && n.z !== undefined && (n.x !== 0 || n.y !== 0 || n.z !== 0)) {
        return { ...n, pos3d: [n.x / 15, n.y / 15, n.z / 15] as [number, number, number] };
      }
      // Spherical distribution around Case Core
      const phi = Math.acos(-1 + (2 * idx) / Math.max(numNodes, 1));
      const theta = Math.sqrt(numNodes * Math.PI) * phi;
      const radius = 4 + (idx % 3) * 2.2;
      const x = radius * Math.cos(theta) * Math.sin(phi);
      const y = radius * Math.sin(theta) * Math.sin(phi);
      const z = radius * Math.cos(phi);
      return { ...n, pos3d: [x, y, z] as [number, number, number] };
    });
  }, [nodes, nodeTypeFilter, factClassificationFilter, searchQuery, caseCoreNode]);

  const nodePosMap = useMemo(() => {
    const map = new Map<string, [number, number, number]>();
    positionedNodes.forEach((n) => map.set(n.id, n.pos3d));
    return map;
  }, [positionedNodes]);

  // Filter edges and calculate positions
  const validEdges = useMemo(() => {
    return edges
      .filter((e) => {
        const sId = typeof e.source === "string" ? e.source : (e.source as GraphNode).id;
        const tId = typeof e.target === "string" ? e.target : (e.target as GraphNode).id;
        if (!nodePosMap.has(sId) || !nodePosMap.has(tId)) return false;
        if (e.confidence !== undefined && e.confidence < minConfidence) return false;
        if (factClassificationFilter !== "ALL" && e.fact_classification && e.fact_classification !== factClassificationFilter) return false;
        return true;
      })
      .map((e) => {
        const sId = typeof e.source === "string" ? e.source : (e.source as GraphNode).id;
        const tId = typeof e.target === "string" ? e.target : (e.target as GraphNode).id;
        return {
          ...e,
          sId,
          tId,
          fromPos: nodePosMap.get(sId)!,
          toPos: nodePosMap.get(tId)!,
        };
      });
  }, [edges, nodePosMap, minConfidence, factClassificationFilter]);

  // Periodic evidence pulses along edges
  useEffect(() => {
    if (validEdges.length === 0) return;
    const interval = setInterval(() => {
      const randomEdge = validEdges[Math.floor(Math.random() * validEdges.length)];
      if (randomEdge) {
        const pId = `pulse-${Date.now()}-${Math.random()}`;
        setPulses((prev) => [...prev.slice(-10), { id: pId, from: randomEdge.fromPos, to: randomEdge.toPos }]);
      }
    }, 1800);
    return () => clearInterval(interval);
  }, [validEdges]);

  // Target camera focus position
  const targetPos = useMemo(() => {
    const targetId = focusedNodeId || selectedNodeId;
    if (!targetId) return null;
    return nodePosMap.get(targetId) || null;
  }, [focusedNodeId, selectedNodeId, nodePosMap]);

  const bgCanvasColor = isDark ? "#05070d" : "#f8fafc";
  const fogColor = isDark ? "#05070d" : "#f8fafc";
  const particleColor = isDark ? "#7fa8ff" : "#475569";

  return (
    <div className="relative w-full h-full overflow-hidden select-none" style={{ backgroundColor: bgCanvasColor }}>
      <Canvas camera={{ position: [0, 4, 16], fov: 50 }} gl={{ antialias: true, preserveDrawingBuffer: true }}>
        <color attach="background" args={[bgCanvasColor]} />
        <fog attach="fog" args={[fogColor, 14, 45]} />

        {/* Lighting */}
        <ambientLight intensity={isDark ? 0.35 : 0.85} />
        <directionalLight position={[8, 14, 8]} intensity={isDark ? 0.6 : 1.1} color={isDark ? "#bcd4ff" : "#ffffff"} />

        {/* Deep Space / Light Ambient Background */}
        {isDark && <Stars radius={60} depth={30} count={1600} factor={2} fade speed={0.4} />}
        <ParticleField count={isDark ? 450 : 250} color={particleColor} />

        {/* Camera Flight Controller */}
        <CameraRig targetPos={targetPos} />

        {/* Orbit Controls */}
        <OrbitControls enableDamping dampingFactor={0.05} maxDistance={40} minDistance={2} />

        {/* Nodes */}
        {positionedNodes.map((node) => (
          <ForensicEntityNode
            key={node.id}
            node={node}
            position={node.pos3d}
            selected={node.id === selectedNodeId}
            active={node.id === selectedNodeId || node.id === focusedNodeId}
            isDark={isDark}
            onHover={setHoveredNode}
            onSelect={(n) => {
              if (n.type !== "case_core") onNodeClick(n);
            }}
          />
        ))}

        {/* Connections (Curved Bezier Tubes) */}
        {validEdges.map((edge) => (
          <EvidenceConnection
            key={edge.id}
            from={edge.fromPos}
            to={edge.toPos}
            active={edge.sId === selectedNodeId || edge.tId === selectedNodeId}
            dimmed={selectedNodeId !== null && edge.sId !== selectedNodeId && edge.tId !== selectedNodeId}
            color={(edge as { color?: string }).color || "#38bdf8"}
            isDark={isDark}
            onClick={() => onEdgeClick(edge as GraphEdge)}
          />
        ))}

        {/* Traveling Evidence Pulses */}
        {pulses.map((p) => (
          <EvidencePulse
            key={p.id}
            from={p.from}
            to={p.to}
            duration={1200}
            isDark={isDark}
            onComplete={() => setPulses((prev) => prev.filter((item) => item.id !== p.id))}
          />
        ))}
      </Canvas>
    </div>
  );
}
