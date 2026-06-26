import { Handle, Position } from "@xyflow/react"
import { MindMapNode, TYPE_EMOJI, MAITRISE_COLORS } from "@/lib/types"
import { UI_AR, trAr } from "@/lib/translations"

export type NodeAction = "quiz" | "flashcard" | "ask" | "mastery_up" | "mastery_down"

interface CustomMindMapNodeProps {
  data: {
    node: MindMapNode
    onAction?: (action: NodeAction, node: MindMapNode) => void
  }
}

export function CustomMindMapNode({ data }: CustomMindMapNodeProps) {
  const { node, onAction } = data

  if (!node) return null

  const typeEmoji = node.type ? TYPE_EMOJI[node.type as keyof typeof TYPE_EMOJI] || "💡" : "💡"
  const masteryColor = MAITRISE_COLORS[node.maitrise_eleve] || "#64748b"
  const masteryLabels = [UI_AR.non, UI_AR.en_cours, UI_AR.maitrisee]
  const masteryLabel = masteryLabels[node.maitrise_eleve] || UI_AR.non

  const actions: { icon: string; action: NodeAction; color: string; title: string }[] = [
    { icon: "⚡", action: "quiz", color: "#8B5CF6", title: "اختبار سريع" },
    { icon: "🎴", action: "flashcard", color: "#F59E0B", title: "بطاقة مراجعة" },
    { icon: "🤖", action: "ask", color: "#3B82F6", title: "اسأل الخوارزمي" },
    { icon: "✅", action: "mastery_up", color: "#10B981", title: "أتقن" },
    { icon: "❌", action: "mastery_down", color: "#EF4444", title: "أتعثر" },
  ]

  const handleAction = (e: React.MouseEvent, act: NodeAction) => {
    e.stopPropagation()
    onAction?.(act, node)
  }

  return (
    <div
      className="px-4 py-3.5 rounded-xl bg-slate-900/90 border border-slate-800/80
                 backdrop-blur-md shadow-lg min-w-[200px] max-w-[280px]
                 hover:shadow-xl hover:border-slate-700/80 transition-all group relative"
      style={{
        borderLeft: `4px solid ${node.couleur || "#475569"}`
      }}
    >
      {node.niveau > 0 && (
        <Handle
          type="target"
          position={Position.Left}
          className="!w-2.5 !h-2.5 !bg-blue-400 !border-slate-900"
        />
      )}

      <div className="flex flex-col gap-2">
        <div className="flex items-center justify-between gap-2">
          <span className="text-lg flex-shrink-0" title={node.type}>
            {typeEmoji}
          </span>

          {node.bac_frequent && (
            <span className="text-[10px] font-bold uppercase tracking-wider
                             px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-400
                             border border-amber-500/20"
                  title={UI_AR.frequent_bac}>
              {UI_AR.bac_label}
            </span>
          )}
        </div>

        <h4 className="text-sm font-semibold text-slate-200 group-hover:text-white
                       leading-snug transition-colors line-clamp-2">
          {trAr(node.label)}
        </h4>

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

        {/* Gen Z action buttons */}
        {onAction && (
          <div className="flex items-center justify-center gap-1 pt-1 border-t border-slate-800/60">
            {actions.map((a) => (
              <button
                key={a.action}
                className="nodrag nopan w-7 h-7 flex items-center justify-center rounded-lg
                           bg-slate-800/50 hover:bg-slate-700/80 text-sm transition-all
                           cursor-pointer hover:scale-110"
                style={{ color: a.color }}
                title={a.title}
                onClick={(e) => handleAction(e, a.action)}
              >
                {a.icon}
              </button>
            ))}
          </div>
        )}
      </div>

      {node.enfants && node.enfants.length > 0 && (
        <Handle
          type="source"
          position={Position.Right}
          className="!w-2.5 !h-2.5 !bg-mint-soft !border-slate-900"
        />
      )}
    </div>
  )
}
export default CustomMindMapNode
