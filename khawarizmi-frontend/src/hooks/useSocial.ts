import { useState, useEffect } from "react"
import { apiClient } from "@/lib/api-client"

export function useSocial() {
  const [conversations, setConversations] = useState<any[]>([])
  const [messages, setMessages] = useState<any[]>([])
  const [posts, setPosts] = useState<any[]>([])
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
    try { const data = await apiClient.request<any[]>(cid ? `/api/social/blog?chapter_id=${cid}` : "/api/social/blog"); setPosts(data) } catch {}
  }

  async function createPost(title: string, content: string, fileUrl?: string, cid?: string) {
    try {
      await apiClient.request("/api/social/blog", { method: "POST", body: JSON.stringify({ title, content, file_url: fileUrl, chapter_id: cid }) })
      await fetchBlogPosts()
    } catch {}
  }

  async function votePost(pid: number) {
    try { await apiClient.request(`/api/social/blog/${pid}/vote`, { method: "POST" }); await fetchBlogPosts() } catch {}
  }

  useEffect(() => { fetchConversations(); fetchBlogPosts() }, [])

  return { conversations, messages, posts, loading, activeConvId, setActiveConvId, fetchConversations, fetchMessages, sendMessage, fetchBlogPosts, createPost, votePost, apiClient }
}
