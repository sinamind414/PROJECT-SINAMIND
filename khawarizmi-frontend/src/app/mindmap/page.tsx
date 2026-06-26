"use client";

import { useState } from "react";

import apiClient from "@/lib/api-client";
import { AuthGuard } from "@/components/auth/AuthGuard";
import { AppShell } from "@/components/layout/AppShell";
import MethodologicalMindMap, { type MethodologicalMindMapData } from "@/components/mindmap/MethodologicalMindMap";
import ActionButton from "@/components/gamification/ActionButton";

type MethodologicalMindMapResponse = {
  status: string;
  mindmap: MethodologicalMindMapData;
};

export default function MindMapMethodologyPage() {
  const [mindmap, setMindmap] = useState<MethodologicalMindMapData | null>(null);
  const [loading, setLoading] = useState(false);

  const generateMethodologicalMindMap = async () => {
    setLoading(true);
    try {
      const data = await apiClient.request<MethodologicalMindMapResponse>("/api/mindmap/generate-methodological", {
        method: "POST",
        body: JSON.stringify({
          matiere: "SVT",
          chapitre: "Les Protéines",
          filiere: "Sciences Expérimentales",
        }),
      });
      if (data.status === "success" && data.mindmap) {
        setMindmap(data.mindmap);
      }
    } catch {
      const fallback: MethodologicalMindMapData = {
        titre: "البروتينات",
        racine: {
          id: "root",
          label: "البروتينات",
          enfants: [
            { id: "acides-amines", label: "الأحماض الأمينية" },
            { id: "liaisons-peptidiques", label: "الروابط الببتيدية" },
            { id: "structures", label: "التركيب (1° إلى 4°)" },
            { id: "roles", label: "الأدوار البيولوجية" },
          ],
        },
      };
      setMindmap(fallback);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthGuard>
      <AppShell>
        <div className="p-6 max-w-5xl mx-auto">
          <div className="flex justify-between items-center mb-8">
            <div>
              <h1 className="text-3xl font-black">الخريطة المنهجية</h1>
              <p className="text-slate-400">إنشاء خريطة ذهنية مُثرّاة بأفعال البكالوريا</p>
            </div>

            <ActionButton
              label="إنشاء خريطة ذهنية منهجية"
              icon="🧠"
              onClick={generateMethodologicalMindMap}
              variant="primary"
            />
          </div>

          {loading && (
            <div className="text-center py-12">
              <div className="animate-spin w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full mx-auto mb-4" />
              <p>جاري إنشاء الخريطة المنهجية...</p>
            </div>
          )}

          {!loading && !mindmap && (
            <div className="text-center py-12 text-slate-400">
              <p>لم يتم إنشاء خريطة منهجية بعد.</p>
              <p className="mt-2">اضغط على الزر لإنشاء واحدة.</p>
            </div>
          )}

          {mindmap && mindmap.racine && (
            <div className="space-y-6">
              <MethodologicalMindMap mindmap={mindmap} />
              {(mindmap.methodology?.points_methodologie ?? 0) > 0 && (
                <div className="bg-emerald-600/10 border border-emerald-600/30 rounded-2xl p-4 text-emerald-400">
                  🎉 +{mindmap.methodology?.points_methodologie ?? 0} نقاط منهجية !
                </div>
              )}
            </div>
          )}
        </div>
      </AppShell>
    </AuthGuard>
  );
}
