// src/app/mindmap/[chapterId]/page.tsx
// Page de consultation interactive du Mind Map (Pilier 4)

"use client"

import { useEffect, useState, useMemo } from "react"
import { useParams, useRouter } from "next/navigation"
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

// Define custom node types for React Flow
const nodeTypes = {
  mindMapNode: CustomMindMapNode
}

// Layout helper: Dynamic horizontal tree placement
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
    
    // Layout all children first
    for (const child of children) {
      const result = layoutTree(child, x + spacingX, currentY, spacingX, spacingY)
      nodes.push(...result.nodes)
      edges.push(...result.edges)

      // Connect parent to child
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

    // Position parent at the exact vertical midpoint of its children
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
    // Leaf node layout
    nodes.push({
      id: node.id,
      type: "mindMapNode",
      position: { x, y: yStart },
      data: { node }
    })
    return { nodes, edges, nextY: yStart + spacingY }
  }
}

// Recursive function to update a node's mastery in the nested tree structure
function updateNodeInTree(
  root: MindMapNode,
  id: string,
  newMaitrise: 0 | 1 | 2
): boolean {
  if (root.id === id) {
    root.maitrise_eleve = newMaitrise
    return true
  }
  if (root.enfants) {
    for (const child of root.enfants) {
      if (updateNodeInTree(child, id, newMaitrise)) {
        return true
      }
    }
  }
  return false
}

// Flatten all nodes from tree helper (useful for weak nodes panel)
function flattenNodes(node: MindMapNode, list: MindMapNode[] = []): MindMapNode[] {
  list.push(node)
  if (node.enfants) {
    for (const child of node.enfants) {
      flattenNodes(child, list)
    }
  }
  return list
}

export default function MindMapPage() {
  return (
    <AuthGuard>
      <MindMapContent />
    </AuthGuard>
  )
}

function MindMapContent() {
  const router = useRouter()
  const { chapterId } = useParams()
  const { user } = useAuth()

  // State management
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const [chapter, setChapter] = useState<Chapter | null>(null)
  const [mindmap, setMindmap] = useState<MindMapType | null>(null)
  const [selectedNode, setSelectedNode] = useState<MindMapNode | null>(null)
  
  // React Flow state
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([])
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([])

  // Load chapter information and the mindmap
  useEffect(() => {
    if (user && chapterId) {
      loadChapterAndMindmap()
    }
  }, [user, chapterId])

  const loadChapterAndMindmap = async () => {
    setLoading(true)
    setError(null)
    try {
      // 1. Resolve chapter name from programme
      const matiere = "SVT"
      const filiere = user?.filiere || "Sciences Experimentales"
      const prog: Programme = await apiClient.getProgramme(matiere, filiere)

      let foundChapter: Chapter | null = null
      for (const d of prog.domains) {
        for (const u of d.units) {
          const match = u.chapters.find((c) => c.id === chapterId)
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

      // 2. Request/Generate mindmap (async — non-bloquant)
      setGenerating(true)
      const res = await apiClient.generateMindMap({
        matiere,
        filiere,
        chapitre: foundChapter.titre_fr,
        niveau_detail: "standard"
      })

      // Cas 1 : Mind Map déjà en cache → affichage direct
      if (res.status === "success" && res.mindmap) {
        applyMindMap(res.mindmap)
        return
      }

      // Cas 2 : no_context → erreur RAG strict
      if (res.status === "no_context") {
        throw new Error(res.message || UI_AR.aucun_contenu_mindmap)
      }

      // Cas 3 : pending → polling jusqu'à completion
      if (res.status === "pending" && res.task_id) {
        const taskId = res.task_id
        const maxAttempts = 60
        for (let i = 0; i < maxAttempts; i++) {
          await new Promise((r) => setTimeout(r, 1500))
          const task = await apiClient.pollMindMapTask(taskId)

          if (task.status === "completed" && task.mindmap) {
            applyMindMap(task.mindmap)
            return
          }
          if (task.status === "failed") {
            throw new Error(task.error === "no_context"
              ? UI_AR.aucun_contenu_mindmap
              : UI_AR.erreur_chargement_mindmap)
          }
          // status === "running" ou "pending" → continuer le polling
        }
        throw new Error("Délai de génération dépassé. Réessaie.")
      }

      throw new Error(UI_AR.erreur_chargement_mindmap)

    } catch (err) {
      const msg = err instanceof Error ? err.message : UI_AR.erreur_chargement_mindmap
      setError(msg)
    } finally {
      setLoading(false)
      setGenerating(false)
    }
  }

  // Applique le Mind Map au canvas React Flow
  const applyMindMap = (mm: MindMapType) => {
    setMindmap(mm)
    const layout = layoutTree(mm.racine)
    const transversalEdges: Edge[] = (mm.liens_transversaux || []).map((link, idx) => ({
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
    setSelectedNode(mm.racine)
  }

  // Lazy loading : étendre un nœud à la demande
  const handleExpandNode = async (node: MindMapNode) => {
    if (!mindmap || !chapter || node.expanded) return
    try {
      const res = await apiClient.expandMindMapNode({
        node_id: node.id,
        node_label: node.label,
        chapitre: chapter.titre_fr,
        matiere: "SVT"
      })
      if (res.enfants && res.enfants.length > 0) {
        // Mettre à jour l'arbre localement
        const updatedTree = { ...mindmap.racine }
        injectChildren(updatedTree, node.id, res.enfants)
        setMindmap({ ...mindmap, racine: updatedTree })
        const layout = layoutTree(updatedTree)
        setNodes(layout.nodes)
      }
    } catch (err) {
      console.error("Expansion échouée:", err)
    }
  }

  // Helper : injecter les enfants dans l'arbre
  const injectChildren = (root: MindMapNode, targetId: string, enfants: MindMapNode[]) => {
    if (root.id === targetId) {
      root.enfants = enfants
      root.expanded = true
      return
    }
    for (const child of root.enfants) {
      injectChildren(child, targetId, enfants)
    }
  }

  // Handle node selection click on the canvas
  const handleNodeClick = (_event: React.MouseEvent, node: Node) => {
    const rawNode = node.data?.node as MindMapNode
    if (rawNode) {
      setSelectedNode(rawNode)
    }
  }

  // Update mastery level of the selected node
  const handleUpdateMaitrise = async (newMaitrise: 0 | 1 | 2) => {
    if (!mindmap || !selectedNode) return

    try {
      // Update backend
      await apiClient.updateNodeMaitrise(selectedNode.id, newMaitrise)

      // Recursively update locally in the tree
      const updatedTree = { ...mindmap.racine }
      updateNodeInTree(updatedTree, selectedNode.id, newMaitrise)
      
      // Update selected node state locally
      setSelectedNode((prev) => prev ? { ...prev, maitrise_eleve: newMaitrise } : null)

      // Refresh overall mindmap root state
      const updatedMindmap = { ...mindmap, racine: updatedTree }
      setMindmap(updatedMindmap)

      // Re-layout and push to React Flow state
      const layout = layoutTree(updatedTree)
      const transversalEdges: Edge[] = (updatedMindmap.liens_transversaux || []).map((link, idx) => ({
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

    } catch (err) {
      alert(UI_AR.erreur_mise_a_jour_maitrise)
    }
  }

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

  // Compute weak nodes from the current mindmap structure dynamically
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
      
      {/* Top Navigation Header */}
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

      {/* Workspace Area: Canvas + Sidebar */}
      <div className="flex-1 flex overflow-hidden relative">
        
        {/* React Flow Mind Map Workspace */}
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

        {/* Interactive Sidebar Panel */}
        <aside className="w-80 border-l border-slate-900 bg-slate-950/90 backdrop-blur-md p-6 overflow-y-auto space-y-6 flex flex-col justify-between h-full z-10 shadow-2xl">
          <div className="space-y-6">
            
            {/* 1. Selected Node Inspector */}
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
                </div>

                {/* 2. Mastery Controls */}
                <div className="space-y-2.5">
                  <label className="text-xs font-semibold text-slate-400 block">
                    {UI_AR.niveau_maitrise}
                  </label>

                  <div className="grid grid-cols-3 gap-2">
                    {([0, 1, 2] as const).map((level) => {
                      const isActive = selectedNode.maitrise_eleve === level
                      const activeColor = MAITRISE_COLORS[level]
                      const labels = [UI_AR.non, UI_AR.en_cours, UI_AR.maitrisee]
                      const label = labels[level]

                      return (
                        <button
                          key={level}
                          onClick={() => handleUpdateMaitrise(level)}
                          style={{
                            borderColor: isActive ? activeColor : "transparent",
                            backgroundColor: isActive ? `${activeColor}15` : "rgba(30, 41, 59, 0.4)",
                            color: isActive ? "#ffffff" : "#94a3b8"
                          }}
                          className={`py-2 px-1 text-center rounded-lg border text-[11px] font-bold
                                      hover:bg-slate-800/30 transition-all cursor-pointer`}
                        >
                          <span
                            className="w-1.5 h-1.5 rounded-full inline-block mr-1"
                            style={{ backgroundColor: activeColor }}
                          />
                          {label}
                        </button>
                      )
                    })}
                  </div>
                </div>
              </section>
            ) : (
              <div className="bg-slate-900/40 border border-slate-800/50 rounded-xl p-4 text-center text-sm text-slate-500">
                {UI_AR.selectionne_noeud}
              </div>
            )}

            {/* 3. Weak Nodes Panel */}
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
                      onClick={() => {
                        setSelectedNode(n)
                        // Trigger Flow to center node
                      }}
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

          {/* Revision Call-to-Action */}
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
