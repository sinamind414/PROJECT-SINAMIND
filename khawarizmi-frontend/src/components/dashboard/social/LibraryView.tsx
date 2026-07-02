"use client"
import React, { useEffect, useState } from "react"
import { useSocial } from "@/hooks/useSocial"
import { FileText, Image, File, Download } from "lucide-react"

export function LibraryView() {
  const { apiClient } = useSocial()
  const [files, setFiles] = useState<any[]>([])

  useEffect(() => {
    apiClient.request<any[]>("/api/social/files").then(setFiles).catch(() => {})
  }, [])

  const fileIcon = (type?: string) => {
    if (type?.startsWith("image")) return <Image className="w-5 h-5 text-mint" />
    if (type?.startsWith("text") || type?.includes("pdf")) return <FileText className="w-5 h-5 text-amber-400" />
    return <File className="w-5 h-5 text-slate-400" />
  }

  return (
    <div className="h-full bg-slate-950 text-slate-100 p-6 overflow-y-auto" dir="rtl">
      <div className="max-w-3xl mx-auto">
        <h2 className="text-xl font-bold mb-6 flex items-center gap-2"><FileText className="text-mint" /> الملفات المشتركة</h2>
        {files.length === 0 && (
          <p className="text-slate-500 text-sm text-center mt-12">لا توجد ملفات مشاركة بعد. ابدأ بمشاركة ملفاتك مع زملائك!</p>
        )}
        <div className="space-y-3">
          {files.map((f, i) => (
            <div key={i} className="flex items-center gap-4 bg-slate-900 border border-white/10 rounded-2xl p-4 hover:border-mint/30 transition-all">
              {fileIcon(f.file_type)}
              <div className="flex-1 min-w-0">
                <p className="text-sm font-bold truncate">{f.file_url?.split("/").pop() || "Fichier"}</p>
                <p className="text-[10px] text-slate-500">Partagé par {f.shared_by}</p>
              </div>
              <a href={f.file_url} target="_blank" rel="noopener noreferrer" className="p-2 rounded-lg bg-mint/10 text-mint hover:bg-mint/20 transition"><Download className="w-4 h-4" /></a>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
