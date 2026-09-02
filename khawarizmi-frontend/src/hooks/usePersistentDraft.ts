"use client"

/**
 * Brouillon qui survit au changement de page (F38).
 *
 * Le défaut réparé : les huit ateliers gardaient le texte écrit par l'élève dans un `useState`
 * local — « اكتب التحليل، 8–12 أسطر » disparaissait dès qu'on sortait de l'écran. Rien n'était
 * enregistré, donc rien ne pouvait être comparé deux semaines plus tard.
 *
 * Règle de conservation : le texte est écrit sur l'appareil (localStorage), la version d'un jour
 * précédent est archivée et devient comparable. Aucun envoi réseau, aucune note.
 */

import { useCallback, useEffect, useRef, useState } from "react"
import { archiveDraft, commitDraft, defaultStorage, openDraft, type DraftVersion } from "@/lib/local-evidence"

/** Délai de frappe avant écriture : on n'écrit pas à chaque caractère dans le stockage. */
const SAVE_DELAY_MS = 400

export type PersistentDraft = {
  /** false = pas de clé persistante (le composant reste utilisable, juste sans mémoire). */
  persistent: boolean
  text: string
  setText: (value: string) => void
  savedAt: string | null
  history: DraftVersion[]
  /** false = le navigateur refuse l'écriture (quota, mode privé) : rien ne survivra à l'onglet. */
  persisted: boolean
  previous: DraftVersion | null
  archive: () => void
}

export function usePersistentDraft(key: string | null, label: string): PersistentDraft {
  const [text, setTextState] = useState("")
  const [savedAt, setSavedAt] = useState<string | null>(null)
  const [history, setHistory] = useState<DraftVersion[]>([])
  const [persisted, setPersisted] = useState(true)
  /** Dernière valeur réellement écrite dans le stockage : évite une écriture à chaque rendu. */
  const saved = useRef<string | null>(null)
  const latest = useRef("")
  const dirty = useRef(false)

  useEffect(() => {
    if (!key) return
    const opened = openDraft(defaultStorage, key, label)
    setTextState(opened.text)
    setSavedAt(opened.savedAt || null)
    setHistory(opened.history)
    saved.current = opened.text
    latest.current = opened.text
    dirty.current = false
  }, [key, label])

  useEffect(() => {
    if (!key || !dirty.current || text === saved.current) return
    const timer = setTimeout(() => {
      const record = commitDraft(defaultStorage, key, label, text)
      saved.current = record.text
      dirty.current = false
      setSavedAt(record.savedAt)
      setHistory(record.history)
      setPersisted(record.persisted !== false)
    }, SAVE_DELAY_MS)
    return () => clearTimeout(timer)
  }, [text, key, label])

  // Sortie de page : on n'attend pas le délai, sinon la dernière phrase tapée est perdue — exactement
  // le geste qui coûtait tout dans le défaut d'origine.
  useEffect(() => {
    return () => {
      if (key && dirty.current) {
        commitDraft(defaultStorage, key, label, latest.current)
        dirty.current = false
      }
    }
  }, [key, label])

  const setText = useCallback((value: string) => {
    latest.current = value
    dirty.current = true
    setTextState(value)
  }, [])

  const archive = useCallback(() => {
    if (!key) return
    commitDraft(defaultStorage, key, label, latest.current)
    dirty.current = false
    const record = archiveDraft(defaultStorage, key, label)
    saved.current = record.text
    setHistory(record.history)
    setSavedAt(record.savedAt || null)
    setPersisted(record.persisted !== false)
  }, [key, label])

  return {
    persistent: !!key,
    persisted,
    text,
    setText,
    savedAt,
    history,
    previous: history[0] ?? null,
    archive,
  }
}
