import { useState, useEffect, useRef, useCallback } from "react"
import { apiClient } from "@/lib/api-client"
import type { TuteurResponse, ChatCard, ChatHistoryMessage } from "@/lib/types"

export type FeedbackType = "understood" | "partial" | "confused" | "example" | "quiz"

export type DisplayMessage = {
  id: number
  role: "user" | "assistant"
  content: string
  cartes?: ChatCard[]
  type?: string
  fallback?: boolean
  feedbackGiven?: FeedbackType
}

export type UserAchievements = {
  totalMessages: number
  topicsExplored: string[]
  badges: string[]
  consecutiveDays: number
  lastVisit: string
}

export interface UseChatbotReturn {
  messages: DisplayMessage[]
  input: string
  loading: boolean
  badge: number
  isOpen: boolean
  isTutorMode: boolean
  achievements: UserAchievements
  newBadge: string | null
  scrollRef: React.RefObject<HTMLDivElement | null>
  setInput: (v: string) => void
  sendMessage: (text?: string) => Promise<void>
  openChat: () => void
  closeChat: () => void
  handleFeedback: (msgId: number, type: FeedbackType) => void
  toggleTutorMode: () => void
  handleSuggestion: (text: string) => void
  dismissBadge: () => void
}

const ACHIEVEMENTS_KEY = "khawarizmi-achievements"

const FEEDBACK_MESSAGES: Record<FeedbackType, string> = {
  understood: "فهمت شكرا!",
  partial: "هل يمكنك تبسيط الشرح أكثر مع مثال من الحياة اليومية؟",
  confused: "لم أفهم! اشرح بطريقة مختلفة تماماً كأنني طفل صغير 😅",
  example: "أعطني مثالاً آخر مختلفاً من الحياة اليومية",
  quiz: "اختبرني على هذا المفهوم",
}

const BADGE_THRESHOLDS = [
  {
    name: "débutant",
    label: "المبتدئ",
    minMessages: 5,
    minTopics: 0,
    minDays: 0,
  },
  {
    name: "apprenti",
    label: "المتدرب",
    minMessages: 10,
    minTopics: 3,
    minDays: 0,
  },
  {
    name: "scientifique",
    label: "العالِم",
    minMessages: 25,
    minTopics: 5,
    minDays: 0,
  },
  {
    name: "maître",
    label: "السيّد",
    minMessages: 50,
    minTopics: 10,
    minDays: 7,
  },
]

function loadAchievements(): UserAchievements {
  if (typeof window === "undefined") {
    return { totalMessages: 0, topicsExplored: [], badges: [], consecutiveDays: 0, lastVisit: "" }
  }
  try {
    const raw = localStorage.getItem(ACHIEVEMENTS_KEY)
    if (raw) return JSON.parse(raw)
  } catch {}
  return { totalMessages: 0, topicsExplored: [], badges: [], consecutiveDays: 0, lastVisit: "" }
}

function saveAchievements(data: UserAchievements) {
  if (typeof window === "undefined") return
  localStorage.setItem(ACHIEVEMENTS_KEY, JSON.stringify(data))
}

function detectTopic(pathname: string): string | null {
  const match = pathname.match(/\/cours\/([^/]+)/)
  return match ? decodeURIComponent(match[1]) : null
}

function checkBadges(achievements: UserAchievements): string | null {
  for (const threshold of BADGE_THRESHOLDS) {
    if (
      achievements.badges.includes(threshold.name)
    ) continue

    if (
      achievements.totalMessages >= threshold.minMessages &&
      achievements.topicsExplored.length >= threshold.minTopics &&
      achievements.consecutiveDays >= threshold.minDays
    ) {
      return threshold.name
    }
  }
  return null
}

function updateConsecutiveDays(achievements: UserAchievements): UserAchievements {
  const today = new Date().toISOString().slice(0, 10)
  if (achievements.lastVisit === today) return achievements

  const yesterday = new Date(Date.now() - 86400000).toISOString().slice(0, 10)
  const consecutiveDays = achievements.lastVisit === yesterday
    ? achievements.consecutiveDays + 1
    : 1

  return { ...achievements, consecutiveDays, lastVisit: today }
}

export function useChatbot(): UseChatbotReturn {
  const [messages, setMessages] = useState<DisplayMessage[]>([])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const [badge, setBadge] = useState(0)
  const [isOpen, setIsOpen] = useState(false)
  const [isTutorMode, setIsTutorMode] = useState(false)
  const [achievements, setAchievements] = useState<UserAchievements>(loadAchievements)
  const [newBadge, setNewBadge] = useState<string | null>(null)

  const scrollRef = useRef<HTMLDivElement | null>(null)
  const historyRef = useRef<ChatHistoryMessage[]>([])
  const initSent = useRef(false)

  const addAssistantMessage = useCallback((resp: TuteurResponse) => {
    const display: DisplayMessage = {
      id: Date.now() + 1,
      role: "assistant",
      content: resp.reponse,
      cartes: resp.cartes,
      type: resp.type,
      fallback: resp.fallback_active,
    }
    setMessages((prev) => [...prev, display])
  }, [])

  const sendInit = useCallback(async () => {
    setLoading(true)
    try {
      const resp = await apiClient.sendTuteurMessage({
        message: "__init__",
        context: {
          page_source: typeof window !== "undefined" ? window.location.pathname : undefined,
        },
      })
      addAssistantMessage(resp)
      if (resp.cartes.length > 0) {
        setBadge(resp.cartes.length)
      }
    } catch {
      addAssistantMessage({
        reponse: "مرحبا! كيف يمكنني مساعدتك اليوم؟",
        type: "orientation",
        cartes: [],
        flashcards_suggerees: [],
        fallback_active: true,
      })
    } finally {
      setLoading(false)
    }
  }, [addAssistantMessage])

  const openChat = useCallback(() => {
    setIsOpen(true)
    setBadge(0)
    if (!initSent.current) {
      initSent.current = true
      sendInit()
    }
  }, [sendInit])

  const closeChat = useCallback(() => {
    setIsOpen(false)
  }, [])

  const sendMessage = useCallback(async (text?: string) => {
    const msg = (text ?? input).trim()
    if (!msg || loading) return
    setInput("")

    const userDisplay: DisplayMessage = {
      id: Date.now(),
      role: "user",
      content: msg,
    }
    setMessages((prev) => [...prev, userDisplay])

    const newHistory: ChatHistoryMessage[] = [
      ...historyRef.current,
      { role: "user", content: msg },
    ]
    historyRef.current = newHistory

    const topic = detectTopic(typeof window !== "undefined" ? window.location.pathname : "/")

    setLoading(true)
    try {
      const resp = await apiClient.sendTuteurMessage({
        message: msg,
        context: {
          page_source: typeof window !== "undefined" ? window.location.pathname : undefined,
          chapitre: topic ?? undefined,
          history: newHistory.slice(-6),
        },
      })
      addAssistantMessage(resp)
      historyRef.current = [
        ...historyRef.current,
        { role: "assistant", content: resp.reponse },
      ]

      setAchievements((prev) => {
        const updated = updateConsecutiveDays({
          ...prev,
          totalMessages: prev.totalMessages + 1,
          topicsExplored: topic && !prev.topicsExplored.includes(topic)
            ? [...prev.topicsExplored, topic]
            : prev.topicsExplored,
        })
        const badgeName = checkBadges(updated)
        if (badgeName && !updated.badges.includes(badgeName)) {
          updated.badges = [...updated.badges, badgeName]
          setNewBadge(badgeName)
        }
        saveAchievements(updated)
        return updated
      })
    } catch {
      addAssistantMessage({
        reponse: "صعيب عليك التركيز الآن. حاول مرة أخرى أو راجع الدروس مباشرة.",
        type: "refus",
        cartes: [],
        flashcards_suggerees: [],
        fallback_active: true,
      })
    } finally {
      setLoading(false)
    }
  }, [input, loading, addAssistantMessage])

  const handleFeedback = useCallback(async (msgId: number, type: FeedbackType) => {
    setMessages((prev) =>
      prev.map((m) => (m.id === msgId ? { ...m, feedbackGiven: type } : m))
    )

    const feedbackText = FEEDBACK_MESSAGES[type]
    const userDisplay: DisplayMessage = {
      id: Date.now(),
      role: "user",
      content: feedbackText,
    }
    setMessages((prev) => [...prev, userDisplay])

    const newHistory: ChatHistoryMessage[] = [
      ...historyRef.current,
      { role: "user", content: feedbackText },
    ]
    historyRef.current = newHistory

    setLoading(true)
    try {
      const resp = await apiClient.sendTuteurMessage({
        message: feedbackText,
        context: {
          page_source: typeof window !== "undefined" ? window.location.pathname : undefined,
          history: newHistory.slice(-6),
        },
      })
      addAssistantMessage(resp)
      historyRef.current = [
        ...historyRef.current,
        { role: "assistant", content: resp.reponse },
      ]
    } catch {
      addAssistantMessage({
        reponse: "حاول مرة أخرى أو اكتب سؤالك مباشرة.",
        type: "refus",
        cartes: [],
        flashcards_suggerees: [],
        fallback_active: true,
      })
    } finally {
      setLoading(false)
    }
  }, [addAssistantMessage])

  const toggleTutorMode = useCallback(async () => {
    if (!isTutorMode) {
      setLoading(true)
      try {
        await apiClient.sendTuteurMessage({
          message: "__activate_tutor__",
          context: {
            page_source: typeof window !== "undefined" ? window.location.pathname : undefined,
          },
        })
        setIsTutorMode(true)
        addAssistantMessage({
          reponse: "تم تفعيل وضع المدرس الشخصي 🎓. سأساعدك بطريقة تعليمية مخصصة.",
          type: "orientation",
          cartes: [],
          flashcards_suggerees: [],
          fallback_active: false,
        })
      } catch {
        addAssistantMessage({
          reponse: "تعذر تفعيل وضع المدرس. حاول مرة أخرى.",
          type: "refus",
          cartes: [],
          flashcards_suggerees: [],
          fallback_active: true,
        })
      } finally {
        setLoading(false)
      }
    } else {
      setIsTutorMode(false)
      const exitMsg = "خرجت من وضع المدرس الشخصي"
      const userDisplay: DisplayMessage = {
        id: Date.now(),
        role: "user",
        content: exitMsg,
      }
      setMessages((prev) => [...prev, userDisplay])
      historyRef.current = [
        ...historyRef.current,
        { role: "user", content: exitMsg },
      ]
      setLoading(true)
      try {
        const resp = await apiClient.sendTuteurMessage({
          message: exitMsg,
          context: {
            page_source: typeof window !== "undefined" ? window.location.pathname : undefined,
            history: historyRef.current.slice(-6),
          },
        })
        addAssistantMessage(resp)
      } catch {
        addAssistantMessage({
          reponse: "تم إيقاف وضع المدرس.",
          type: "orientation",
          cartes: [],
          flashcards_suggerees: [],
          fallback_active: false,
        })
      } finally {
        setLoading(false)
      }
    }
  }, [isTutorMode, addAssistantMessage])

  const handleSuggestion = useCallback((text: string) => {
    setInput(text)
    sendMessage(text)
  }, [sendMessage])

  const dismissBadge = useCallback(() => {
    setNewBadge(null)
  }, [])

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages])

  return {
    messages,
    input,
    loading,
    badge,
    isOpen,
    isTutorMode,
    achievements,
    newBadge,
    scrollRef,
    setInput,
    sendMessage,
    openChat,
    closeChat,
    handleFeedback,
    toggleTutorMode,
    handleSuggestion,
    dismissBadge,
  }
}

export default useChatbot
