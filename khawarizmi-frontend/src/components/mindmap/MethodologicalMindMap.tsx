"use client";

import { useState } from "react";

export interface MethodologyInfo {
  verbe?: string;
  type?: string;
  conseil?: string;
}

export interface MindMapNode {
  id: string;
  label: string;
  methodology?: MethodologyInfo;
  enfants?: MindMapNode[];
}

export interface MethodologicalMindMapData {
  titre?: string;
  methodology?: {
    verbes_detectes?: string[];
    points_methodologie?: number;
    structure_recommandee?: string;
  };
  racine?: MindMapNode;
}

interface MethodologicalMindMapProps {
  mindmap: MethodologicalMindMapData;
  onNodeClick?: (node: MindMapNode) => void;
}

export default function MethodologicalMindMap({ mindmap, onNodeClick }: MethodologicalMindMapProps) {
  const [expandedNodes, setExpandedNodes] = useState<string[]>([]);

  const toggleNode = (nodeId: string) => {
    setExpandedNodes(prev =>
      prev.includes(nodeId) ? prev.filter(id => id !== nodeId) : [...prev, nodeId]
    );
  };

  const renderNode = (node: MindMapNode, depth = 0) => {
    const isExpanded = expandedNodes.includes(node.id);
    const hasChildren = node.enfants && node.enfants.length > 0;

    return (
      <div key={node.id} className="ml-4">
        <div
          className={`flex items-center gap-2 p-2 rounded-lg hover:bg-slate-800 cursor-pointer ${depth === 0 ? "font-bold" : ""}`}
          onClick={() => {
            if (hasChildren) toggleNode(node.id);
            onNodeClick?.(node);
          }}
        >
          {hasChildren && <span className="text-indigo-400">{isExpanded ? "▼" : "▶"}</span>}
          <span>{node.label}</span>
          {node.methodology?.verbe && (
            <span className="ml-2 px-2 py-0.5 text-xs rounded-full bg-indigo-600/20 text-indigo-400 border border-indigo-600/30">
              {node.methodology.verbe}
            </span>
          )}
        </div>

        {node.methodology?.conseil && (
          <div className="ml-8 text-xs text-slate-400 italic mb-1">
            💡 {node.methodology.conseil}
          </div>
        )}

        {isExpanded && hasChildren && (
          <div className="border-l border-slate-700 ml-2">
            {node.enfants!.map(child => renderNode(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="bg-slate-900 rounded-2xl p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-bold text-xl">الخريطة المنهجية</h3>
        {mindmap.methodology?.verbes_detectes && (
          <div className="text-sm text-indigo-400">
            {mindmap.methodology.verbes_detectes.length} أفعال مكتشفة
          </div>
        )}
      </div>

      {mindmap.racine && renderNode(mindmap.racine)}
    </div>
  );
}
