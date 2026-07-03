import { useState, useEffect, useCallback } from "react"
import { apiClient } from "@/lib/api-client"

export interface BlogPost {
  id: number
  title: string
  content: string
  file_url?: string
  chapter_id?: string
  created_at: string
  author_name: string
  author_id: number
  likes_count: number
  avg_rating: number
  rating_count: number
  comments: BlogComment[]
}

export interface BlogComment {
  id: number
  post_id: number
  author_id: number
  author_name: string
  content: string
  created_at: string
}

export function useSocial() {
  const [conversations, setConversations] = useState<any[]>([])
  const [messages, setMessages] = useState<any[]>([])
  const [posts, setPosts] = useState<BlogPost[]>([])
  const [loading, setLoading] = useState(false)
  const [activeConvId, setActiveConvId] = useState<number | null>(null)

  async function fetchConversations() {
    try { const data = await apiClient.request<any[]>("/api/social/conversations"); setConversations(data) } catch {}
  }

  async function fetchMessages(cid: number) {
    setLoading(true)
    try { const data = await apiClient.request<any[]>(`/api/social/conversations/${cid}/messages`); setMessages(data) } catch {}
    finally { setLoading(false) }
  }

  useEffect(() => {
    let i: ReturnType<typeof setInterval>
    if (activeConvId) i = setInterval(() => fetchMessages(activeConvId), 5000)
    return () => clearInterval(i)
  }, [activeConvId])

  async function sendMessage(cid: number, content: string, fileUrl?: string, fileType?: string) {
    try {
      await apiClient.request("/api/social/messages", { method: "POST", body: JSON.stringify({ conversation_id: cid, content, file_url: fileUrl, file_type: fileType }) })
      await fetchMessages(cid)
    } catch {}
  }

  async function fetchBlogPosts(cid?: string) {
    try { const data = await apiClient.request<BlogPost[]>(cid ? `/api/social/blog?chapter_id=${cid}` : "/api/social/blog"); setPosts(data) } catch {}
  }

  async function createPost(title: string, content: string, fileUrl?: string, cid?: string) {
    try {
      await apiClient.request("/api/social/blog", { method: "POST", body: JSON.stringify({ title, content, file_url: fileUrl, chapter_id: cid }) })
      await fetchBlogPosts()
    } catch {}
  }

  async function toggleLike(pid: number) {
    try {
      const res = await apiClient.request<{ status: string; liked: boolean; likes_count: number }>(
        `/api/social/blog/${pid}/like`, { method: "POST" }
      )
      setPosts(prev => prev.map(p => p.id === pid ? { ...p, likes_count: res.likes_count } : p))
      return res.liked
    } catch {}
  }

  async function ratePost(pid: number, rating: number) {
    try {
      const res = await apiClient.request<{ status: string; avg_rating: number; rating_count: number }>(
        `/api/social/blog/${pid}/rate`, { method: "POST", body: JSON.stringify({ rating }) }
      )
      setPosts(prev => prev.map(p => p.id === pid ? { ...p, avg_rating: res.avg_rating, rating_count: res.rating_count } : p))
    } catch {}
  }

  useEffect(() => { fetchConversations(); fetchBlogPosts() }, [])

  return { conversations, messages, posts, loading, activeConvId, setActiveConvId, fetchConversations, fetchMessages, sendMessage, fetchBlogPosts, createPost, toggleLike, ratePost, apiClient }
}
