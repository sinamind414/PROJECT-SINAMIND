"use client"
import React, { useState } from "react"
import { useSocial } from "@/hooks/useSocial"
import { BookOpen, ThumbsUp, Send, MessageCircle } from "lucide-react"

export function BlogView() {
  const { posts, fetchBlogPosts, createPost, votePost, apiClient } = useSocial()
  const [newTitle, setNewTitle] = useState("")
  const [newContent, setNewContent] = useState("")
  const [isPosting, setIsPosting] = useState(false)
  const [commentInput, setCommentInput] = useState<Record<number, string>>({})

  async function handlePost() {
    if (!newTitle.trim() || !newContent.trim()) return
    setIsPosting(true)
    await createPost(newTitle, newContent)
    setNewTitle(""); setNewContent("")
    setIsPosting(false)
  }

  async function handleComment(postId: number) {
    const content = commentInput[postId]
    if (!content) return
    await apiClient.request("/api/social/blog/comment", {
      method: "POST",
      body: JSON.stringify({ post_id: postId, content }),
    })
    setCommentInput({ ...commentInput, [postId]: "" })
    await fetchBlogPosts()
  }

  return (
    <div className="flex h-full bg-slate-950 text-slate-100 p-6 overflow-y-auto" dir="rtl">
      <div className="max-w-3xl mx-auto w-full space-y-8">
        <section className="bg-slate-900 border border-white/10 rounded-3xl p-6 shadow-2xl">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2"><BookOpen className="text-mint" /> شارك معرفتك مع زملائك</h2>
          <div className="space-y-3">
            <input value={newTitle} onChange={(e) => setNewTitle(e.target.value)} placeholder="عنوان الموضوع..." className="w-full rounded-xl bg-slate-800 border border-white/10 px-4 py-2 text-sm outline-none focus:border-mint text-white" />
            <textarea value={newContent} onChange={(e) => setNewContent(e.target.value)} placeholder="اكتب نصيحتك..." rows={3} className="w-full rounded-xl bg-slate-800 border border-white/10 px-4 py-2 text-sm outline-none focus:border-mint text-white" />
            <button onClick={handlePost} disabled={isPosting} className="px-6 py-2 rounded-xl bg-mint text-slate-deep font-bold text-sm hover:bg-mint-soft transition disabled:opacity-50">
              {isPosting ? "جاري النشر..." : "نشر في المجتمع 🚀"}
            </button>
          </div>
        </section>
        <div className="space-y-6">
          {posts.map((post: any) => (
            <div key={post.id} className="bg-slate-900 border border-white/10 rounded-3xl p-6 hover:border-mint/30 transition-all shadow-lg">
              <div className="flex justify-between items-start mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-mint/20 text-mint flex items-center justify-center font-bold">{post.author_name?.[0]}</div>
                  <p className="text-white font-bold text-sm">{post.author_name}</p>
                </div>
                {post.chapter_id && <span className="px-2 py-1 rounded-lg bg-slate-800 text-mint text-[10px] font-bold">{post.chapter_id}</span>}
              </div>
              <h4 className="text-xl font-bold text-white mb-2">{post.title}</h4>
              <p className="text-slate-300 text-sm leading-relaxed mb-4">{post.content}</p>
              <div className="flex items-center gap-4 pt-4 border-t border-white/5">
                <button onClick={() => votePost(post.id)} className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 text-slate-400 hover:text-mint transition text-xs font-bold">
                  <ThumbsUp className="w-4 h-4" /> {post.votes || 0}
                </button>
                <div className="flex items-center gap-2 text-slate-500 text-xs">
                  <MessageCircle className="w-4 h-4" /> {post.comments?.length || 0} تعليق
                </div>
              </div>
              <div className="mt-4 space-y-3">
                {post.comments?.map((c: any, i: number) => (
                  <div key={i} className="flex gap-2 p-2 bg-white/5 rounded-xl text-xs">
                    <span className="font-bold text-slate-100">{c.author_name}</span>: {c.content}
                  </div>
                ))}
                <div className="flex gap-2 mt-2">
                  <input
                    value={commentInput[post.id] || ""}
                    onChange={(e) => setCommentInput({ ...commentInput, [post.id]: e.target.value })}
                    placeholder="أضف تعليقاً..."
                    className="flex-1 rounded-lg bg-slate-800 border border-white/10 px-3 py-1.5 text-xs outline-none focus:border-mint text-white"
                    dir="rtl"
                  />
                  <button onClick={() => handleComment(post.id)} className="p-1.5 rounded-lg bg-mint text-slate-deep transition">
                    <Send className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>
          ))}
          {posts.length === 0 && (
            <p className="text-center text-slate-500 text-sm">Aucun post pour le moment. Sois le premier à partager !</p>
          )}
        </div>
      </div>
    </div>
  )
}
