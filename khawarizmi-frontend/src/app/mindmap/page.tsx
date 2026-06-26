"use client";

import { useState } from "react";

import apiClient from "@/lib/api-client";
import MethodologicalMindMap from "@/components/mindmap/MethodologicalMindMap";
import { ActionButton } from "@/components/gamification/ActionButton";

export default function MindMapMethodologyPage() {
  const [mindmap, setMindmap] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const generateMethodologicalMindMap = async () => {
    setLoading(true);
    try {
      const data = await apiClient.request<any>("/api/mindmap/generate-methodological", {
        method: "POST",
        body: JSON.stringify({
          matiere: "SVT",
          chapitre: "Les Protéines",
          filiere: "Sciences Expérimentales",
        }),
      });
      setMindmap(data.mindmap);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-black">Mind Map Méthodologique</h1>
          <p className="text-slate-400">Génère un Mind Map enrichi avec les verbes du Bac</p>
        </div>

        <ActionButton
          label="Générer un Mind Map Méthodologique"
          icon="🧠"
          onClick={generateMethodologicalMindMap}
          variant="primary"
        />
      </div>

      {loading && (
        <div className="text-center py-12">
          <div className="animate-spin w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full mx-auto mb-4" />
          <p>Génération du Mind Map méthodologique en cours...</p>
        </div>
      )}

      {!loading && !mindmap && (
        <div className="text-center py-12 text-slate-400">
          <p>Aucun Mind Map méthodologique généré pour le moment.</p>
          <p className="mt-2">Clique sur le bouton pour en créer un.</p>
        </div>
      )}

      {mindmap && (
        <div className="space-y-6">
          <MethodologicalMindMap mindmap={mindmap} />
          {mindmap.methodology?.points_methodologie > 0 && (
            <div className="bg-emerald-600/10 border border-emerald-600/30 rounded-2xl p-4 text-emerald-400">
              🎉 +{mindmap.methodology.points_methodologie} points méthodologiques !
            </div>
          )}
        </div>
      )}
    </div>
  );
}
