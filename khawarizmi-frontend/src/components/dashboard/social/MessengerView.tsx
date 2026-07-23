"use client"
import React, { useState, useEffect, useRef } from "react"
import { useSocial } from "@/hooks/useSocial"
import { Send, MessageSquare, UserPlus, X } from "lucide-react"

interface SearchUserResult {
  id: number
  nom?: string
  strong_verb?: string
}

interface SuggestedPartner {
  id: number
  nom?: string
  strong_verb?: string
}

export function MessengerView() {
  const { conversations, messages, loading, activeConvId, setActiveConvId, fetchMessages, sendMessage, apiClient } = useSocial()
  const [input, setInput] = useState("")
  const [searchQuery, setSearchQuery] = useState("")
  const [searchResults, setSearchResults] = useState<SearchUserResult[]>([])
  const [suggestedPartners, setSuggestedPartners] = useState<SuggestedPartner[]>([])
  const [isSearching, setIsSearching] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (activeConvId) fetchMessages(activeConvId)
  }, [activeConvId])

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight
  }, [messages])

  useEffect(() => {
    apiClient.request<{ partners: SuggestedPartner[] }>("/api/social/suggested-partners")
      .then(res => setSuggestedPartners(res.partners || []))
      .catch(() => {})
  }, [])

  const handleSend = async () => {
    if (!input.trim() || !activeConvId) return
    const text = input; setInput("")
    await sendMessage(activeConvId, text)
  }

  const handleSearch = async () => {
    if (!searchQuery.trim()) return
    setIsSearching(true)
    try {
      const results = await apiClient.request<SearchUserResult[]>(
        `/api/social/users/search?q=${encodeURIComponent(searchQuery)}`
      )
      setSearchResults(results)
    } catch {}
  }

  const startChat = async (userId: number) => {
    try {
      const res = await apiClient.request<{ conversation_id: number }>("/api/social/conversations", {
        method: "POST",
        body: JSON.stringify({ member_ids: [userId], is_group: false }),
      })
      setActiveConvId(res.conversation_id)
      setSearchQuery(""); setSearchResults([]); setIsSearching(false)
    } catch {}
  }

  return (
    <div className="flex h-full text-slate-100 bg-slate-950">
      <div className="w-1/3 border-r border-white/10 bg-slate-900/80 flex flex-col overflow-hidden">
        <div className="p-4 space-y-3 bg-slate-900">
          <div className="flex items-center justify-between">
            <h2 className="font-bold text-sm text-slate-400 uppercase tracking-widest">Messages</h2>
            <button onClick={() => setIsSearching(true)} className="p-2 rounded-full bg-mint/10 text-mint hover:bg-mint/20 transition"><UserPlus className="w-4 h-4" /></button>
          </div>
          {isSearching && (
            <div className="relative">
              <input value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} onKeyDown={(e) => e.key === "Enter" && handleSearch()} placeholder="Rechercher..." className="w-full rounded-xl bg-slate-800 border border-white/10 px-4 py-2 text-xs outline-none focus:border-mint text-white" dir="rtl" />
              <button onClick={() => setIsSearching(false)} className="absolute left-2 top-1/2 -translate-y-1/2 text-slate-500"><X className="w-3 h-3" /></button>
            </div>
          )}
        </div>
        <div className="flex-1 overflow-y-auto">
          {isSearching && searchResults.map(u => (
            <button key={u.id} onClick={() => startChat(u.id)} className="w-full p-2 flex items-center gap-3 hover:bg-white/5 rounded-lg transition text-right">
              <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center text-xs">{u.nom?.[0]}</div>
              <div className="text-right"><p className="text-xs font-bold">{u.nom}</p></div>
            </button>
          ))}
          {!isSearching && suggestedPartners.map(u => (
            <button key={u.id} onClick={() => startChat(u.id)} className="w-full p-2 flex items-center gap-3 hover:bg-mint/10 rounded-lg transition text-right border-b border-mint/10">
              <div className="w-8 h-8 rounded-full bg-mint/30 text-mint flex items-center justify-center text-xs font-bold">{u.nom?.[0]}</div>
              <div className="text-right"><p className="text-xs font-bold text-white">{u.nom}</p><p className="text-[10px] text-mint/60">{u.strong_verb}</p></div>
            </button>
          ))}
          {!isSearching && conversations.map((conv) => (
            <button key={conv.id} onClick={() => { setActiveConvId(conv.id); setIsSearching(false) }} className={`w-full p-4 flex items-center gap-3 transition-all border-b border-white/5 ${activeConvId === conv.id ? "bg-mint/20 text-mint" : "hover:bg-white/5 text-slate-300"}`}>
              <div className="w-10 h-10 rounded-full bg-slate-700 flex items-center justify-center font-bold">{conv.title ? conv.title[0] : "U"}</div>
              <div className="flex-1 text-right overflow-hidden"><p className="font-bold truncate text-sm">{conv.title || "Membres"}</p></div>
            </button>
          ))}
        </div>
      </div>
      <div className="flex-1 flex flex-col bg-slate-800/30 relative">
        {activeConvId ? (
          <>
            <div className="p-4 border-b border-white/10 flex items-center justify-between bg-slate-800/50 backdrop-blur-md">
              <div className="flex items-center gap-2"><div className="w-8 h-8 rounded-full bg-mint/20 text-mint flex items-center justify-center text-xs font-bold"># {activeConvId}</div><span className="text-xs font-bold text-slate-300">Discussion active</span></div>
            </div>
            <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4" dir="rtl">
              {loading && <p className="text-center text-slate-500 text-xs">Chargement...</p>}
              {messages.map((msg) => (
                <div key={msg.id} className={`flex ${msg.sender_id === 1 ? "justify-start" : "justify-end"}`}>
                  <div className={`max-w-[80%] p-3 rounded-2xl text-sm ${msg.sender_id === 1 ? "bg-slate-700 text-white rounded-tr-none" : "bg-mint text-slate-deep font-medium rounded-tl-none"}`}>
                    <p className="text-[10px] opacity-60 mb-1 font-bold">{msg.sender_name}</p>
                    <p>{msg.content}</p>
                  </div>
                </div>
              ))}
            </div>
            <div className="p-4 bg-slate-900/50 border-t border-white/10 flex gap-2 items-center">
              <input value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => e.key === "Enter" && handleSend()} placeholder="Écris un message..." className="flex-1 rounded-xl bg-slate-800 border border-white/10 px-4 py-2 text-sm outline-none focus:border-mint text-white" dir="rtl" />
              <button onClick={handleSend} className="p-2 rounded-lg bg-mint text-slate-deep hover:bg-mint-soft transition"><Send className="w-5 h-5" /></button>
            </div>
          </>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center text-slate-500 text-center p-8">
            <MessageSquare className="w-12 h-12 mb-4 opacity-20" />
            <p className="text-sm font-medium">Bienvenue dans le Hub Social</p>
          </div>
        )}
      </div>
    </div>
  )
}
