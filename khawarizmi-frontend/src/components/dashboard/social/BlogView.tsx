"use client"
import React, { useState } from "react"
import { useSocial, BlogPost, BlogComment } from "@/hooks/useSocial"
import { BookOpen, Heart, Send, MessageCircle, Star } from "lucide-react"

function StarRating({ rating, onRate }: { rating: number; onRate: (v: number) => void }) {
  const [hover, setHover] = useState(0)
  return (
    <div className="flex items-center gap-0.5" dir="ltr">
      {[1, 2, 3, 4, 5].map((v) => (
        <button
          key={v}
          type="button"
          onClick={() => onRate(v)}
          onMouseEnter={() => setHover(v)}
          onMouseLeave={() => setHover(0)}
          className="transition-transform hover:scale-110"
        >
          <Star
            className={`w-4 h-4 ${v <= (hover || rating) ? "fill-amber-400 text-amber-400" : "text-slate-600"}`}
          />
        </button>
      ))}
    </div>
  )
}

function TimeAgo(dateStr: string): string {
  const seconds = Math.floor((Date.now() - new Date(dateStr).getTime()) / 1000)
  if (seconds < 60) return "الآن"
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `قبل ${minutes} د`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `قبل ${hours} س`
  const days = Math.floor(hours / 24)
  if (days < 30) return `قبل ${days} ي`
  return `قبل ${Math.floor(days / 30)} ش`
}

export function BlogView() {
  const { posts, fetchBlogPosts, createPost, toggleLike, ratePost, apiClient } = useSocial()
  const [newTitle, setNewTitle] = useState("")
  const [newContent, setNewContent] = useState("")
  const [isPosting, setIsPosting] = useState(false)
  const [commentInput, setCommentInput] = useState<Record<number, string>>({})
  const [likedPosts, setLikedPosts] = useState<Set<number>>(new Set())
  const [expandedComments, setExpandedComments] = useState<Set<number>>(new Set())

  async function handlePost() {
    if (!newTitle.trim() || !newContent.trim()) return
    setIsPosting(true)
    await createPost(newTitle, newContent)
    setNewTitle(""); setNewContent("")
    setIsPosting(false)
  }

  async function handleComment(postId: number) {
    const content = commentInput[postId]
    if (!content?.trim()) return
    await apiClient.request("/api/social/blog/comment", {
      method: "POST",
      body: JSON.stringify({ post_id: postId, content: content.trim() }),
    })
    setCommentInput({ ...commentInput, [postId]: "" })
    await fetchBlogPosts()
  }

  async function handleLike(pid: number) {
    setLikedPosts(prev => new Set(prev).add(pid))
    const liked = await toggleLike(pid)
    if (liked === false) {
      setLikedPosts(prev => { const next = new Set(prev); next.delete(pid); return next })
    }
  }

  async function handleRate(pid: number, rating: number) {
    await ratePost(pid, rating)
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
          {posts.map((post: BlogPost) => (
            <div key={post.id} className="bg-slate-900 border border-white/10 rounded-3xl p-6 hover:border-mint/30 transition-all shadow-lg">
              <div className="flex justify-between items-start mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-mint/20 text-mint flex items-center justify-center font-bold">
                    {post.author_name?.[0]}
                  </div>
                  <div>
                    <p className="text-white font-bold text-sm">{post.author_name}</p>
                    <p className="text-slate-500 text-[10px]">{TimeAgo(post.created_at)}</p>
                  </div>
                </div>
                {post.chapter_id && (
                  <span className="px-2 py-1 rounded-lg bg-slate-800 text-mint text-[10px] font-bold">
                    {post.chapter_id}
                  </span>
                )}
              </div>

              <h4 className="text-xl font-bold text-white mb-2">{post.title}</h4>
              <p className="text-slate-300 text-sm leading-relaxed mb-4 whitespace-pre-wrap">{post.content}</p>

              <div className="flex items-center gap-4 pt-4 border-t border-white/5">
                <button
                  onClick={() => handleLike(post.id)}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white/5 hover:bg-red-500/10 transition text-xs font-bold group"
                >
                  <Heart
                    className={`w-4 h-4 transition-colors ${
                      likedPosts.has(post.id)
                        ? "fill-red-500 text-red-500"
                        : "text-slate-400 group-hover:text-red-400"
                    }`}
                  />
                  <span className={likedPosts.has(post.id) ? "text-red-400" : "text-slate-400"}>
                    {post.likes_count}
                  </span>
                </button>

                <div className="flex items-center gap-2">
                  {post.rating_count > 0 && (
                    <span className="text-amber-400 text-xs font-bold">{post.avg_rating.toFixed(1)}</span>
                  )}
                  <StarRating
                    rating={0}
                    onRate={(v) => handleRate(post.id, v)}
                  />
                  {post.rating_count > 0 && (
                    <span className="text-slate-500 text-[10px]">({post.rating_count})</span>
                  )}
                </div>

                <button
                  onClick={() => setExpandedComments(prev => {
                    const next = new Set(prev)
                    if (next.has(post.id)) next.delete(post.id)
                    else next.add(post.id)
                    return next
                  })}
                  className="flex items-center gap-1.5 text-slate-500 hover:text-slate-300 transition text-xs font-bold mr-auto"
                >
                  <MessageCircle className="w-4 h-4" />
                  {post.comments?.length || 0}
                </button>
              </div>

              {expandedComments.has(post.id) && (
                <div className="mt-4 space-y-3">
                  {post.comments?.map((c: BlogComment) => (
                    <div key={c.id} className="flex gap-2 p-2.5 bg-white/5 rounded-xl">
                      <div className="w-6 h-6 rounded-full bg-slate-700 text-slate-300 flex items-center justify-center text-[9px] font-bold shrink-0">
                        {c.author_name?.[0]}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-slate-100 text-[11px]">{c.author_name}</span>
                          <span className="text-slate-600 text-[9px]">{TimeAgo(c.created_at)}</span>
                        </div>
                        <p className="text-slate-300 text-xs mt-0.5">{c.content}</p>
                      </div>
                    </div>
                  ))}
                  <div className="flex gap-2 mt-2">
                    <input
                      value={commentInput[post.id] || ""}
                      onChange={(e) => setCommentInput({ ...commentInput, [post.id]: e.target.value })}
                      onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleComment(post.id) } }}
                      placeholder="أضف تعليقاً..."
                      className="flex-1 rounded-lg bg-slate-800 border border-white/10 px-3 py-1.5 text-xs outline-none focus:border-mint text-white"
                      dir="rtl"
                      maxLength={500}
                    />
                    <button
                      onClick={() => handleComment(post.id)}
                      disabled={!commentInput[post.id]?.trim()}
                      className="p-1.5 rounded-lg bg-mint text-slate-deep transition disabled:opacity-40"
                    >
                      <Send className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
          {posts.length === 0 && (
            <p className="text-center text-slate-500 text-sm">لا توجد منشورات بعد. كن أول من يشارك!</p>
          )}
        </div>
      </div>
    </div>
  )
}
