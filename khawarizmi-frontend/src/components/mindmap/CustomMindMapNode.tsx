// src/components/mindmap/CustomMindMapNode.tsx

import { Handle, Position } from "@xyflow/react"
import { MindMapNode, TYPE_EMOJI, MAITRISE_COLORS, MAITRISE_LABELS } from "@/lib/types"

interface CustomMindMapNodeProps {
  data: {
    node: MindMapNode
  }
}

export function CustomMindMapNode({ data }: CustomMindMapNodeProps) {
  const { node } = data

  if (!node) return null

  const typeEmoji = node.type ? TYPE_EMOJI[node.type as keyof typeof TYPE_EMOJI] || "💡" : "💡"
  const masteryColor = MAITRISE_COLORS[node.maitrise_eleve] || "#64748b"
  const masteryLabel = MAITRISE_LABELS[node.maitrise_eleve] || "Non commencé"

  return (
    <div
      className="px-4 py-3.5 rounded-xl bg-slate-900/90 border border-slate-800/80
                 backdrop-blur-md shadow-lg min-w-[200px] max-w-[280px]
                 hover:shadow-xl hover:border-slate-700/80 transition-all group relative"
      style={{
        borderLeft: `4px solid ${node.couleur || "#475569"}`
      }}
    >
      {/* Target handle on the left (except for root) */}
      {node.niveau > 0 && (
        <Handle
          type="target"
          position={Position.Left}
          className="!w-2.5 !h-2.5 !bg-blue-400 !border-slate-900"
        />
      )}

      {/* Node content */}
      <div className="flex flex-col gap-2">
        <div className="flex items-center justify-between gap-2">
          {/* Node Type and Label */}
          <span className="text-lg flex-shrink-0" title={node.type}>
            {typeEmoji}
          </span>

          {node.bac_frequent && (
            <span className="text-[10px] font-bold uppercase tracking-wider
                             px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-400
                             border border-amber-500/20"
                  title="Très fréquent au BAC">
              BAC
            </span>
          )}
        </div>

        {/* Node Label */}
        <h4 className="text-sm font-semibold text-slate-200 group-hover:text-white
                       leading-snug transition-colors line-clamp-2">
          {node.label}
        </h4>

        {/* Mastery indicator */}
        <div className="flex items-center gap-2 mt-1 border-t border-slate-800/60 pt-2 text-[10px] text-slate-400">
          <span
            className="w-2 h-2 rounded-full inline-block animate-pulse"
            style={{
              backgroundColor: masteryColor,
              boxShadow: `0 0 8px ${masteryColor}`
            }}
          />
          <span className="font-medium tracking-wide">
            {masteryLabel}
          </span>
        </div>
      </div>

      {/* Source handle on the right (except if no children, but always safe to render) */}
      {node.enfants && node.enfants.length > 0 && (
        <Handle
          type="source"
          position={Position.Right}
          className="!w-2.5 !h-2.5 !bg-purple-400 !border-slate-900"
        />
      )}
    </div>
  )
}
export default CustomMindMapNode
