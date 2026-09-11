import type { GraphNode, GraphEdge } from "@/types/kg";

export function exportGraphToJSON(nodes: GraphNode[], edges: GraphEdge[]): string {
  return JSON.stringify({ nodes, edges }, null, 2);
}

export function downloadFile(content: string, filename: string, mimeType: string) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
