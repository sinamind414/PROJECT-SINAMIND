/**
 * Service preuves / erreurs / gate FSRS — localStorage (contrat Kunz).
 * L'UI ne mute jamais evidence/error/recall directement.
 * Le scheduling FSRS réel reste côté backend (reviewVerb / evaluate).
 */

import type { DocumentTrace, SessionOutcome } from "./tunnelTypes"
import {
  outcomeAllowsDocumentRecall,
  outcomeAllowsMethodMastery,
} from "./tunnelTypes"
import type { SessionEffect, SessionSnapshot } from "./sessionReduce"

const EVIDENCE_KEY = "khawarizmi.evidence.v1"
const ERRORS_KEY = "khawarizmi.learning_errors.v1"
const RECALL_GATE_KEY = "khawarizmi.recall_gate.v1"
const SESSION_KEY = "khawarizmi.lesson_session.v1"

export type EvidenceKind = "document" | "method"

export type EvidenceRecord = {
  id: string
  kind: EvidenceKind
  lessonId: string
  verbSlug: string | null
  score: number
  createdAt: string
  /** Idempotence : une preuve par lesson+kind tant que non invalidée */
  key: string
}

export type LearningErrorRecord = {
  id: string
  lessonId: string
  verbSlug: string | null
  source: "document" | "bac"
  createdAt: string
  updatedAt: string
  resolved: boolean
}

export type RecallGateRecord = {
  lessonId: string
  verbSlug: string | null
  allowed: boolean
  reason: "document_evidence"
  createdAt: string
}

/** Mémoire de process (tests + SSR) — localStorage si navigateur */
const memoryStore = new Map<string, string>()

function isBrowser() {
  return typeof window !== "undefined" && typeof window.localStorage !== "undefined"
}

function uid() {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID()
  }
  return `id_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`
}

function readJson<T>(key: string, fallback: T): T {
  try {
    let raw: string | null = null
    if (isBrowser()) {
      raw = window.localStorage.getItem(key)
    } else {
      raw = memoryStore.get(key) ?? null
    }
    if (!raw) return fallback
    return JSON.parse(raw) as T
  } catch {
    return fallback
  }
}

function writeJson(key: string, value: unknown) {
  const raw = JSON.stringify(value)
  if (isBrowser()) {
    window.localStorage.setItem(key, raw)
    // Notifie dashboard / progress / coach (live)
    if (
      key === EVIDENCE_KEY ||
      key === ERRORS_KEY ||
      key === RECALL_GATE_KEY ||
      key === SESSION_KEY
    ) {
      window.dispatchEvent(new Event("khawarizmi-contract-updated"))
      window.dispatchEvent(new Event("sinamind-progress-updated"))
    }
  } else {
    memoryStore.set(key, raw)
  }
}

/** Tests uniquement */
export function __resetEvidenceStoreForTests() {
  memoryStore.clear()
  if (isBrowser()) {
    window.localStorage.removeItem(EVIDENCE_KEY)
    window.localStorage.removeItem(ERRORS_KEY)
    window.localStorage.removeItem(RECALL_GATE_KEY)
    window.localStorage.removeItem(SESSION_KEY)
  }
}

export function listEvidences(): EvidenceRecord[] {
  return readJson<EvidenceRecord[]>(EVIDENCE_KEY, [])
}

export function listLearningErrors(): LearningErrorRecord[] {
  return readJson<LearningErrorRecord[]>(ERRORS_KEY, [])
}

export function listRecallGates(): RecallGateRecord[] {
  return readJson<RecallGateRecord[]>(RECALL_GATE_KEY, [])
}

export function evidenceKey(kind: EvidenceKind, lessonId: string): string {
  return `${kind}:${lessonId}`
}

/** Idempotent : ne crée pas de double preuve document pour la même leçon */
export function createDocumentEvidence(input: {
  lessonId: string
  verbSlug: string | null
  score: number
  nowIso?: string
}): EvidenceRecord {
  const key = evidenceKey("document", input.lessonId)
  const all = listEvidences()
  const existing = all.find((e) => e.key === key)
  if (existing) return existing

  const record: EvidenceRecord = {
    id: uid(),
    kind: "document",
    lessonId: input.lessonId,
    verbSlug: input.verbSlug,
    score: input.score,
    createdAt: input.nowIso ?? new Date().toISOString(),
    key,
  }
  writeJson(EVIDENCE_KEY, [...all, record])
  return record
}

export function createMethodEvidence(input: {
  lessonId: string
  verbSlug: string | null
  bacScore: number
  nowIso?: string
}): EvidenceRecord {
  const key = evidenceKey("method", input.lessonId)
  const all = listEvidences()
  const existing = all.find((e) => e.key === key)
  if (existing) return existing

  const record: EvidenceRecord = {
    id: uid(),
    kind: "method",
    lessonId: input.lessonId,
    verbSlug: input.verbSlug,
    score: input.bacScore,
    createdAt: input.nowIso ?? new Date().toISOString(),
    key,
  }
  writeJson(EVIDENCE_KEY, [...all, record])
  return record
}

export function upsertLearningError(input: {
  lessonId: string
  verbSlug: string | null
  source: "document" | "bac"
  nowIso?: string
}): LearningErrorRecord {
  const all = listLearningErrors()
  const now = input.nowIso ?? new Date().toISOString()
  const existing = all.find(
    (e) =>
      e.lessonId === input.lessonId &&
      e.source === input.source &&
      !e.resolved
  )
  if (existing) {
    const updated = { ...existing, updatedAt: now, verbSlug: input.verbSlug }
    writeJson(
      ERRORS_KEY,
      all.map((e) => (e.id === existing.id ? updated : e))
    )
    return updated
  }
  const record: LearningErrorRecord = {
    id: uid(),
    lessonId: input.lessonId,
    verbSlug: input.verbSlug,
    source: input.source,
    createdAt: now,
    updatedAt: now,
    resolved: false,
  }
  writeJson(ERRORS_KEY, [...all, record])
  return record
}

/**
 * Gate FSRS : autorise un rappel lié à une preuve document.
 * N'appelle PAS le scheduler FSRS backend — le runner d'effets / evaluate le fera.
 */
export function openRecallGate(input: {
  lessonId: string
  verbSlug: string | null
  reason: "document_evidence"
  nowIso?: string
}): RecallGateRecord {
  const all = listRecallGates()
  const existing = all.find((g) => g.lessonId === input.lessonId && g.allowed)
  if (existing) return existing

  const record: RecallGateRecord = {
    lessonId: input.lessonId,
    verbSlug: input.verbSlug,
    allowed: true,
    reason: input.reason,
    createdAt: input.nowIso ?? new Date().toISOString(),
  }
  writeJson(RECALL_GATE_KEY, [...all, record])
  return record
}

export function canScheduleRecallForLesson(lessonId: string): boolean {
  return listRecallGates().some((g) => g.lessonId === lessonId && g.allowed)
}

/** Gate FSRS : true seulement si preuve/gate ouverte pour ce verbe ou leçon */
export function canScheduleRecallForVerb(verbSlug: string): boolean {
  const gates = listRecallGates().filter((g) => g.allowed)
  if (gates.some((g) => g.verbSlug === verbSlug)) return true
  // leçons verb:slug créées par practiceOutcome
  return gates.some((g) => g.lessonId === `verb:${verbSlug}` || g.lessonId.endsWith(`:${verbSlug}`))
}

export function getContractSnapshot(): {
  evidences: EvidenceRecord[]
  errors: LearningErrorRecord[]
  recallGates: RecallGateRecord[]
  documentCount: number
  methodCount: number
  openErrorCount: number
  openRecallCount: number
} {
  const evidences = listEvidences()
  const errors = listLearningErrors()
  const recallGates = listRecallGates()
  return {
    evidences,
    errors,
    recallGates,
    documentCount: evidences.filter((e) => e.kind === "document").length,
    methodCount: evidences.filter((e) => e.kind === "method").length,
    openErrorCount: errors.filter((e) => !e.resolved).length,
    openRecallCount: recallGates.filter((g) => g.allowed).length,
  }
}

export function hasDocumentEvidence(lessonId: string): boolean {
  return listEvidences().some(
    (e) => e.lessonId === lessonId && e.kind === "document"
  )
}

export function hasMethodEvidence(lessonId: string): boolean {
  return listEvidences().some(
    (e) => e.lessonId === lessonId && e.kind === "method"
  )
}

export function persistSessionSnapshot(snapshot: SessionSnapshot) {
  if (!isBrowser()) return
  writeJson(SESSION_KEY, snapshot)
}

export function loadSessionSnapshot(): SessionSnapshot | null {
  return readJson<SessionSnapshot | null>(SESSION_KEY, null)
}

export function clearSessionSnapshot(lessonId: string) {
  const current = loadSessionSnapshot()
  if (current?.context.lessonId === lessonId) {
    if (isBrowser()) {
      window.localStorage.removeItem(SESSION_KEY)
    } else {
      memoryStore.delete(SESSION_KEY)
    }
  }
}

/**
 * Applique les effets de la machine Session.
 * Pure côté règles métier ; persistance localStorage.
 */
export function runSessionEffects(
  effects: SessionEffect[],
  ctx: {
    documentScore?: number | null
    bacScore?: number | null
  } = {}
): { evidenceIds: string[]; errorIds: string[]; recallOpened: boolean } {
  const evidenceIds: string[] = []
  const errorIds: string[] = []
  let recallOpened = false

  for (const effect of effects) {
    switch (effect.op) {
      case "recordDocumentTrace":
        // Trace déjà dans le snapshot ; optionnel log
        break
      case "createDocumentEvidence": {
        const rec = createDocumentEvidence({
          lessonId: effect.lessonId,
          verbSlug: effect.verbSlug,
          score: ctx.documentScore ?? 0,
        })
        evidenceIds.push(rec.id)
        break
      }
      case "createMethodEvidence": {
        const rec = createMethodEvidence({
          lessonId: effect.lessonId,
          verbSlug: effect.verbSlug,
          bacScore: effect.bacScore,
        })
        evidenceIds.push(rec.id)
        break
      }
      case "upsertLearningError": {
        const rec = upsertLearningError({
          lessonId: effect.lessonId,
          verbSlug: effect.verbSlug,
          source: effect.source,
        })
        errorIds.push(rec.id)
        break
      }
      case "scheduleSpacedRecall": {
        openRecallGate({
          lessonId: effect.lessonId,
          verbSlug: effect.verbSlug,
          reason: effect.reason,
        })
        recallOpened = true
        break
      }
      case "persistSession":
        persistSessionSnapshot(effect.snapshot)
        break
      case "clearSession":
        clearSessionSnapshot(effect.lessonId)
        break
      default: {
        const _e: never = effect
        void _e
      }
    }
  }

  return { evidenceIds, errorIds, recallOpened }
}

/** Garde UI : badge maîtrise méthodo seulement si outcome passed */
export function uiMayShowMethodMastery(outcome: SessionOutcome | null): boolean {
  return outcomeAllowsMethodMastery(outcome)
}

export function uiMayShowDocumentSuccess(outcome: SessionOutcome | null): boolean {
  return outcomeAllowsDocumentRecall(outcome) || outcome === "passed"
}

/** Validation pure (tests / evaluate local) */
export function validateDocumentAttempt(
  trace: DocumentTrace,
  score: number
): { valid: boolean; reasons: string[] } {
  const reasons: string[] = []
  if (!trace.observation.trim()) reasons.push("missing_observation")
  if (!trace.mechanism.trim()) reasons.push("missing_mechanism")
  if (!trace.conclusion.trim()) reasons.push("missing_conclusion")
  if (score < 70) reasons.push("score_below_70")
  return { valid: reasons.length === 0, reasons }
}
