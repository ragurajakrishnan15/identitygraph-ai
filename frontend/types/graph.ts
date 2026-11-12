export interface GraphNode {
  id: string;
  type: string;
  label: string;
  is_focus: boolean;
  flagged: boolean;
  degree: number;
}
export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  relation: string;
}
export interface NetworkResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
  summary: { entity_id: string; kind: string; label: string; degree: number; linked_applications: number; component_size: number };
  note: string;
}
export interface EntityHit {
  entity_id: string;
  kind: string;
  label: string;
  degree: number;
}
