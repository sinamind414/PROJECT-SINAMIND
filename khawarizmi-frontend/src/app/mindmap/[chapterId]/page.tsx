"use client"

import { useEffect, useState, useMemo, useCallback } from "react"
import { useParams } from "next/navigation"
import Link from "next/link"

import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  Edge,
  Node
} from "@xyflow/react"
import "@xyflow/react/dist/style.css"

import apiClient from "@/lib/api-client"
import { useAuth } from "@/lib/auth-context"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { UI_AR, trAr } from "@/lib/translations"
import {
  MindMap as MindMapType,
  MindMapNode,
  Chapter,
  Programme,
  MAITRISE_COLORS
} from "@/lib/types"
import CustomMindMapNode from "@/components/mindmap/CustomMindMapNode"

const PROGRESS_LABELS: Record<string, string> = {
  init: "جاري التهيئة...",
  rag: "البحث في الدروس...",
  llm: "التوليد بالذكاء الاصطناعي...",
  save: "جاري الحفظ...",
  flashcards: "إنشاء البطاقات...",
  done: "تم !"
}

const nodeTypes = { mindMapNode: CustomMindMapNode }

function slugifyChapter(value: string): string {
  return value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
}

function layoutTree(
  node: MindMapNode,
  x = 0,
  yStart = 0,
  spacingX = 320,
  spacingY = 110
): { nodes: Node[]; edges: Edge[]; nextY: number } {
  const nodes: Node[] = []
  const edges: Edge[] = []
  const children = node.enfants || []

  if (children.length > 0) {
    let currentY = yStart

    for (const child of children) {
      const result = layoutTree(child, x + spacingX, currentY, spacingX, spacingY)
      nodes.push(...result.nodes)
      edges.push(...result.edges)

      edges.push({
        id: `edge-${node.id}-${child.id}`,
        source: node.id,
        target: child.id,
        type: "smoothstep",
        animated: true,
        style: { stroke: node.couleur || "#475569", strokeWidth: 2 }
      })

      currentY = result.nextY
    }

    const firstChildNode = nodes.find((n) => n.id === children[0].id)
    const lastChildNode = nodes.find((n) => n.id === children[children.length - 1].id)
    const firstChildY = firstChildNode ? (firstChildNode.position as { y: number }).y : yStart
    const lastChildY = lastChildNode ? (lastChildNode.position as { y: number }).y : yStart
    const parentY = (firstChildY + lastChildY) / 2

    nodes.push({
      id: node.id,
      type: "mindMapNode",
      position: { x, y: parentY },
      data: { node }
    })

    return { nodes, edges, nextY: currentY }
  } else {
    nodes.push({
      id: node.id,
      type: "mindMapNode",
      position: { x, y: yStart },
      data: { node }
    })
    return { nodes, edges, nextY: yStart + spacingY }
  }
}

function flattenNodes(node: MindMapNode, list: MindMapNode[] = []): MindMapNode[] {
  list.push(node)
  if (node.enfants) {
    for (const child of node.enfants) {
      flattenNodes(child, list)
    }
  }
  return list
}

function resolveMindmapErrorMessage(error: unknown): string {
  const message = error instanceof Error ? error.message : ""

  if (message.includes("no_context")) {
    return "لا توجد بيانات كافية لهذا الفصل بعد. جرّب فصلا آخر مثل تركيب البروتينات."
  }
  if (message.includes("chapitre") || message.includes("introuvable")) {
    return "تعذر العثور على الفصل المطلوب. تحقق من الرابط أو من بيانات البرنامج."
  }
  if (message.includes("timeout") || message.includes("timeout_mindmap_generation")) {
    return "الخريطة قيد الإنشاء في الخلفية. أعد تحميل الصفحة بعد 30 ثانية."
  }
  if (message.includes("503") || message.includes("Service IA non configuré")) {
    return "خدمة الذكاء الاصطناعي غير مهيأة حاليا. تحقق من مفاتيح API."
  }
  return UI_AR.erreur_chargement_mindmap
}

export default function MindMapPage() {
  return (
    <AuthGuard>
      <MindMapContent />
    </AuthGuard>
  )
}

function MindMapContent() {
  const { chapterId } = useParams()
  const { user } = useAuth()

  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [progress, setProgress] = useState<string>("init")

  const [chapter, setChapter] = useState<Chapter | null>(null)
  const [mindmap, setMindmap] = useState<MindMapType | null>(null)
  const [selectedNode, setSelectedNode] = useState<MindMapNode | null>(null)

  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([])
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([])

  const pollTask = useCallback(async (taskId: string): Promise<MindMapType> => {
    const maxAttempts = 60
    for (let i = 0; i < maxAttempts; i++) {
      const task = await apiClient.getMindMapTaskStatus(taskId)
      setProgress(task.progress || "running")
      if (task.status === "completed" && task.mindmap) {
        return task.mindmap
      }
      if (task.status === "failed") {
        throw new Error(task.error || "تعذر إنشاء الخريطة الذهنية")
      }
      await new Promise(r => setTimeout(r, 2000))
    }
    throw new Error("timeout_mindmap_generation")
  }, [])

  const handleNodeClick = (_event: React.MouseEvent, node: Node) => {
    const rawNode = node.data?.node as MindMapNode
    if (rawNode) {
      setSelectedNode(rawNode)
    }
  }

  useEffect(() => {
    setSelectedNode(null)
  }, [selectedNode?.id])

  const loadChapterAndMindmap = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const matiere = "SVT"
      const filiere = user?.filiere || "Sciences Experimentales"
      const prog: Programme = await apiClient.getProgramme(matiere, filiere)

      const routeChapterId = String(chapterId)

      let foundChapter: Chapter | null = null
      for (const d of prog.domains) {
        for (const u of d.units) {
          const match = u.chapters.find((c) => {
            const idMatch = String(c.id) === routeChapterId
            const slugMatch = slugifyChapter(c.titre_fr) === routeChapterId
            return idMatch || slugMatch
          })
          if (match) {
            foundChapter = match
            break
          }
        }
        if (foundChapter) break
      }

      if (!foundChapter) {
        throw new Error(UI_AR.chapitre_introuvable)
      }
      setChapter(foundChapter)

      setGenerating(true)
      setProgress("init")
      const res = await apiClient.generateMindMap({
        matiere,
        filiere,
        chapitre: foundChapter.titre_fr,
        niveau_detail: "standard"
      })

      if (res.status === "no_context") {
        throw new Error(`no_context: لا توجد بيانات RAG لهذا الفصل بعد.`)
      }

      let mindmapData: MindMapType
      if (res.status === "pending") {
        try {
          mindmapData = await pollTask(res.task_id)
        } catch (e) {
          const msg = e instanceof Error ? e.message : ""
          if (msg.includes("مهلة") || msg.includes("timeout")) {
            throw new Error("الخريطة قيد الإنشاء في الخلفية. أعد تحميل الصفحة بعد 30 ثانية.")
          }
          throw e
        }
      } else {
        mindmapData = res.mindmap
      }

      if (!mindmapData || !mindmapData.racine) {
        throw new Error("بنية الخريطة الذهنية غير صالحة")
      }

      setMindmap(mindmapData)

      const layout = layoutTree(mindmapData.racine)

      const transversalEdges: Edge[] = (mindmapData.liens_transversaux || []).map((link, idx) => ({
        id: `transversal-${idx}`,
        source: link.source,
        target: link.target,
        label: link.relation,
        type: "bezier",
        animated: true,
        style: { stroke: "#e2e8f0", strokeWidth: 1.5, strokeDasharray: "4 4" },
        labelStyle: { fill: "#94a3b8", fontSize: 9, fontWeight: 500 }
      }))

      setNodes(layout.nodes)
      setEdges([...layout.edges, ...transversalEdges])

      setSelectedNode(mindmapData.racine)

    } catch (err) {
      console.error("Mindmap load failed", err)
      setError(resolveMindmapErrorMessage(err))
    } finally {
      setLoading(false)
      setGenerating(false)
    }
  }, [user, chapterId, setEdges, setNodes, pollTask])

  useEffect(() => {
    if (user && chapterId) {
      void loadChapterAndMindmap()
    }
  }, [user, chapterId, loadChapterAndMindmap])

  const importanceLabels: Record<string, string> = {
    critique: UI_AR.critique,
    haute: "مهم",
    moyenne: "متوسط"
  }

  const typeLabels: Record<string, string> = {
    concept: UI_AR.concept,
    processus: "عملية",
    definition: "تعريف",
    formule: "صيغة",
    exception: "استثناء"
  }

  const weakNodes = useMemo(() => {
    if (!mindmap) return []
    const flat = flattenNodes(mindmap.racine)
    return flat
      .filter((n) => n.maitrise_eleve === 0)
      .sort((a, b) => {
        const order: Record<string, number> = { critique: 1, haute: 2, moyenne: 3 }
        return (order[a.importance] || 3) - (order[b.importance] || 3)
      })
  }, [mindmap])

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-slate-950 text-white space-y-4">
        <div className="w-12 h-12 border-4 border-mint border-t-transparent rounded-full animate-spin" />
        <p className="text-slate-400 text-sm font-medium">
          {generating ? UI_AR.generation_mindmap_ia : UI_AR.chargement}
        </p>
        {generating && (
          <div className="flex items-center gap-2 mt-2">
            <span className="w-2 h-2 bg-mint rounded-full animate-pulse" />
            <span className="text-xs text-slate-500">
              {PROGRESS_LABELS[progress] || progress}
            </span>
          </div>
        )}
      </div>
    )
  }

  if (error || !mindmap || !chapter) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-slate-950 p-6">
        <div className="bg-red-500/10 border border-red-500/30 rounded-2xl p-8 max-w-md text-center space-y-4">
          <p className="text-4xl">⚠️</p>
          <h3 className="text-red-300 font-bold text-lg">{UI_AR.erreur_chargement}</h3>
          <p className="text-slate-300 text-sm leading-relaxed">{error || UI_AR.impossible_charger_donnees}</p>
          <div className="flex justify-center gap-3">
            <Link
              href="/dashboard"
              className="px-4 py-2 bg-slate-800 text-slate-300 border border-slate-700 rounded-lg hover:bg-slate-700 text-sm transition"
            >
              {UI_AR.retour_dashboard}
            </Link>
            <button
              onClick={loadChapterAndMindmap}
              className="px-4 py-2 bg-mint text-slate-deep rounded-lg hover:bg-mint-soft text-sm transition"
            >
              {UI_AR.reessayer}
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <main className="flex flex-col h-screen bg-slate-950 overflow-hidden text-slate-100">
      <header className="border-b border-slate-900 bg-slate-950/80 backdrop-blur px-6 py-4 flex justify-between items-center z-10">
        <div className="flex items-center gap-4">
          <Link href="/dashboard" className="text-slate-400 hover:text-white transition">
            {UI_AR.retour_dashboard}
          </Link>
          <div className="h-4 w-px bg-slate-800" />
          <div>
            <h1 className="text-base sm:text-lg font-bold text-white leading-tight">
              {trAr(chapter.titre_fr)}
            </h1>
            <p className="text-xs text-slate-400">
              {UI_AR.chapitre_label} {chapter.numero} • {UI_AR.svt_terminale}
            </p>
          </div>
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden relative">
        <div className="flex-1 h-full relative bg-slate-950">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            nodeTypes={nodeTypes}
            onNodeClick={handleNodeClick}
            fitView
            minZoom={0.2}
            maxZoom={1.5}
          >
            <Background color="#334155" gap={20} size={1} />
            <Controls className="!bg-slate-900 !border-slate-800 !text-slate-200 fill-slate-200 [&_button]:!border-slate-800 hover:[&_button]:!bg-slate-800" />
            <MiniMap
              nodeColor={(n) => {
                const rawNode = n.data?.node as MindMapNode
                return rawNode?.couleur || "#475569"
              }}
              maskColor="rgba(2, 6, 23, 0.7)"
              className="!bg-slate-900 !border-slate-800"
            />
          </ReactFlow>
        </div>

        <aside className="w-80 border-l border-slate-900 bg-slate-950/90 backdrop-blur-md p-6 overflow-y-auto space-y-6 flex flex-col justify-between h-full z-10 shadow-2xl">
          <div className="space-y-6">

            {selectedNode ? (
              <section className="space-y-4">
                <div className="flex items-start justify-between gap-3">
                  <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest">
                    {UI_AR.details_noeud}
                  </h3>
                  {selectedNode.bac_frequent && (
                    <span className="text-[9px] font-bold px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/25">
                      {UI_AR.frequent_bac}
                    </span>
                  )}
                </div>

                <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4 space-y-3">
                  <h4 className="text-base font-bold text-white leading-snug">
                    {trAr(selectedNode.label)}
                  </h4>

                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800/40">
                      <span className="text-[10px] text-slate-500 block mb-0.5">{UI_AR.type}</span>
                      <span className="font-semibold text-slate-300 capitalize">
                        {typeLabels[selectedNode.type] || selectedNode.type}
                      </span>
                    </div>

                    <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800/40">
                      <span className="text-[10px] text-slate-500 block mb-0.5">{UI_AR.importance}</span>
                      <span className="font-semibold capitalize" style={{ color: selectedNode.couleur }}>
                        {importanceLabels[selectedNode.importance] || selectedNode.importance}
                      </span>
                    </div>
                  </div>

                  <div className="bg-slate-900/40 border border-slate-800/40 rounded-lg p-2.5">
                    <span className="text-[10px] text-slate-500 block mb-1">{UI_AR.niveau_maitrise}</span>
                    <div className="flex items-center gap-2">
                      <span
                        className="w-2.5 h-2.5 rounded-full"
                        style={{ backgroundColor: MAITRISE_COLORS[selectedNode.maitrise_eleve] }}
                      />
                      <span className="text-xs font-semibold text-slate-300">
                        {[UI_AR.non, UI_AR.en_cours, UI_AR.maitrisee][selectedNode.maitrise_eleve]}
                      </span>
                    </div>
                  </div>
                </div>

                <Link
                  href="/drill"
                  className="block w-full py-2.5 bg-slate-800/50 border border-slate-700 rounded-xl text-center text-xs font-bold text-mint hover:bg-slate-800 transition"
                >
                  🎯 راجع هذا الفصل في المراجعة السريعة ←
                </Link>
              </section>
            ) : (
              <div className="bg-slate-900/40 border border-slate-800/50 rounded-xl p-4 text-center text-sm text-slate-500">
                {UI_AR.selectionne_noeud}
              </div>
            )}

            <section className="space-y-3 pt-4 border-t border-slate-900">
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest flex items-center justify-between">
                <span>{UI_AR.noeuds_faibles}</span>
                <span className="bg-red-500/15 text-red-400 text-[10px] px-2 py-0.5 rounded-full font-bold">
                  {weakNodes.length}
                </span>
              </h3>

              {weakNodes.length > 0 ? (
                <div className="space-y-2 max-h-[200px] overflow-y-auto pr-1">
                  {weakNodes.map((n) => (
                    <button
                      key={n.id}
                      onClick={() => setSelectedNode(n)}
                      className="w-full text-left p-2.5 rounded-lg bg-slate-900/30 border border-slate-900 hover:border-slate-800 transition flex items-center justify-between gap-2 cursor-pointer group"
                    >
                      <span className="text-slate-300 text-xs font-medium truncate group-hover:text-white transition-colors">
                        {trAr(n.label)}
                      </span>
                      <span
                        className="text-[9px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded"
                        style={{
                          backgroundColor: `${n.couleur}10`,
                          color: n.couleur,
                          border: `1px solid ${n.couleur}25`
                        }}
                      >
                        {importanceLabels[n.importance] || n.importance}
                      </span>
                    </button>
                  ))}
                </div>
              ) : (
                <div className="bg-green-500/10 border border-green-500/20 rounded-xl p-4 text-center text-xs text-green-400">
                  {UI_AR.tous_maitrises}
                </div>
              )}
            </section>

          </div>

          <div className="pt-4 border-t border-slate-900">
            <Link
              href="/drill"
              className="w-full py-3 bg-gradient-to-r from-mint to-emerald-400 text-slate-deep text-center rounded-xl font-semibold text-sm hover:opacity-95 transition block cursor-pointer shadow-lg hover:shadow-mint/20"
            >
              {UI_AR.lancer_session_revision}
            </Link>
          </div>

        </aside>
      </div>

    </main>
  )
}
