"use client"
import React, { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { MessageSquare, BookOpen, X, Users, FolderOpen } from "lucide-react"
import { MessengerView } from "./MessengerView"
import { BlogView } from "./BlogView"
import { LibraryView } from "./LibraryView"

export function SocialHubWidget() {
  const [isOpen, setIsOpen] = useState(false)
  const [activeTab, setActiveTab] = useState<"messenger" | "blog" | "library">("messenger")

  return (
    <>
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            className="fixed bottom-[calc(env(safe-area-inset-bottom)+6rem)] lg:bottom-24 left-4 lg:left-6 w-[calc(100vw-2rem)] lg:w-[600px] max-w-[calc(100vw-2rem)] z-[90] rounded-3xl shadow-2xl overflow-hidden flex flex-col"
            style={{ background: "#182730", border: "1px solid rgba(255,255,255,0.1)", height: "70vh" }}
          >
            <div className="p-4 flex items-center justify-between bg-slate-900/80 backdrop-blur-md border-b border-white/10">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-mint to-teal-600 flex items-center justify-center text-white shadow-lg"><Users className="w-6 h-6" /></div>
                <div><h3 className="text-white font-bold text-sm">مجتمع سينامايند</h3><p className="text-slate-400 text-[10px]">تواصل، تعلم، وابتكر</p></div>
              </div>
              <div className="flex items-center gap-2 bg-slate-800 p-1 rounded-xl border border-white/5">
                <button onClick={() => setActiveTab("messenger")} className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${activeTab === "messenger" ? "bg-mint text-slate-deep" : "text-slate-400"}`}><MessageSquare className="w-3.5 h-3.5" /> رسائل</button>
                <button onClick={() => setActiveTab("blog")} className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${activeTab === "blog" ? "bg-mint text-slate-deep" : "text-slate-400"}`}><BookOpen className="w-3.5 h-3.5" /> المدونة</button>
                <button onClick={() => setActiveTab("library")} className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${activeTab === "library" ? "bg-mint text-slate-deep" : "text-slate-400"}`}><FolderOpen className="w-3.5 h-3.5" /> الملفات</button>
              </div>
              <button onClick={() => setIsOpen(false)} className="w-8 h-8 rounded-full bg-white/5 hover:bg-white/10 flex items-center justify-center text-white transition-colors"><X className="w-4 h-4" /></button>
            </div>
            <div className="flex-1 overflow-hidden">
              {activeTab === "messenger" ? <MessengerView /> : activeTab === "blog" ? <BlogView /> : <LibraryView />}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
      <button onClick={() => setIsOpen(!isOpen)} className="social-trigger fixed bottom-[calc(env(safe-area-inset-bottom)+5.5rem)] lg:bottom-6 left-4 lg:left-6 w-14 h-14 rounded-full shadow-2xl flex items-center justify-center z-[90] transition-all hover:scale-110" style={{ background: "linear-gradient(135deg, #2DD4BF, #14B8A6, #F59E0B)", boxShadow: "0 8px 24px rgba(45,212,191,0.4)" }}>
        <span className="text-2xl" aria-hidden="true">{isOpen ? "✕" : "👥"}</span>
      </button>
    </>
  )
}
