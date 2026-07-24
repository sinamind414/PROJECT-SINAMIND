import type {
  MethodChecklist,
  MethodErrorCode,
  MethodRunState,
  MethodStep,
  MethodVerdictResult,
} from "./methodChecklistTypes"

export function normalize(s: string): string {
  return s
    .trim()
    .toLowerCase()
    .normalize("NFD")
    .replace(/\p{M}/gu, "")
}

export function hasMinimalTextProof(raw: string): boolean {
  const t = raw.trim()
  if (t.length < 8) return false
  return t.split(/\s+/).filter(Boolean).length >= 3
}

function isEmptyProof(proof: string | string[] | undefined): boolean {
  if (proof == null) return true
  if (typeof proof === "string") return proof.trim() === ""
  return proof.length === 0
}

function matchesKeyword(token: string, keyword: string): boolean {
  return token === keyword || token.includes(keyword)
}

export function evalStepProof(
  step: MethodStep,
  proof: string | string[]
): MethodErrorCode[] {
  const codes: MethodErrorCode[] = []

  switch (step.proofKind) {
    case "short_text": {
      if (!hasMinimalTextProof(String(proof))) {
        codes.push("PROOF_WEAK")
      }
      break
    }

    case "keywords": {
      const tokens = normalize(String(proof))
        .split(/\s+/)
        .filter(Boolean)
      const expected = (step.expected?.keywords ?? []).map(normalize)
      const need =
        step.expected?.keywordsRequired ?? Math.ceil(expected.length / 2)
      const hits = expected.filter((k) =>
        tokens.some((t) => matchesKeyword(t, k))
      ).length
      if (hits < need) codes.push("PROOF_WEAK")
      break
    }

    case "order": {
      const got = Array.isArray(proof) ? proof : [String(proof)]
      if (
        JSON.stringify(got) !==
        JSON.stringify(step.expected?.orderIds ?? [])
      ) {
        codes.push("PROOF_WEAK")
      }
      break
    }

    case "choice": {
      const correct = new Set(
        (step.expected?.choices ?? [])
          .filter((c) => c.correct)
          .map((c) => c.id)
      )
      const got = Array.isArray(proof)
        ? proof
        : [String(proof)]
      const valid =
        [...correct].every((id) => got.includes(id)) &&
        got.every((id) => correct.has(id))
      if (!valid) codes.push("PROOF_WEAK")
      break
    }

    case "confirm": {
      if (!String(proof).trim()) codes.push("NO_EVIDENCE")
      break
    }
  }

  return codes
}

function detectOrderSkipped(
  steps: MethodStep[],
  committed: Record<string, boolean>
): boolean {
  for (let i = 1; i < steps.length; i++) {
    if (
      committed[steps[i].id] &&
      !committed[steps[i - 1].id]
    ) {
      return true
    }
  }
  return false
}

export function detectRushed(input: {
  durationMs: number
  minExpectedMs: number
  hintsUsed: number
  weakOrEmptyProofs: number
}): boolean {
  const fast = input.durationMs < input.minExpectedMs
  return fast && (input.hintsUsed >= 2 || input.weakOrEmptyProofs >= 2)
}

export function buildMethodOutcome(input: {
  checklist: MethodChecklist
  state: MethodRunState
  contentWeakSelf?: boolean
  durationMs: number
}): MethodVerdictResult {
  const { checklist, state } = input
  const steps = checklist.steps
  const n = steps.length
  const codes: MethodErrorCode[] = []
  let committedCount = 0
  let weakOrEmpty = 0

  if (detectOrderSkipped(steps, state.committed)) {
    codes.push("ORDER_SKIPPED")
  }

  for (const step of steps) {
    const isCommitted = !!state.committed[step.id]
    if (!isCommitted) continue
    committedCount++

    const proof = state.proofs[step.id]

    if (isEmptyProof(proof)) {
      codes.push("NO_EVIDENCE")
      weakOrEmpty++
      continue
    }

    const stepCodes = evalStepProof(step, proof)
    codes.push(...stepCodes)
    if (stepCodes.length > 0) weakOrEmpty++

    const sc = state.selfCheck[step.id]
    if (sc) {
      const abs = sc.absent?.length ?? 0
      const pres = sc.present?.length ?? 0
      if (abs >= 2 && abs >= pres) {
        codes.push("SELF_CHECK_GAP")
      }
    }
  }

  if (committedCount < n) {
    codes.push("CHECKLIST_PARTIAL")
    weakOrEmpty += n - committedCount
  }

  const rushed = detectRushed({
    durationMs: input.durationMs,
    minExpectedMs: checklist.minExpectedMs,
    hintsUsed: state.hintsUsed,
    weakOrEmptyProofs: weakOrEmpty,
  })
  if (rushed) codes.push("RUSHED")

  const unique = [...new Set(codes)]

  const hardFail = unique.some(
    (c) =>
      c === "ORDER_SKIPPED" ||
      c === "CHECKLIST_PARTIAL"
  )

  const noEvidenceCount = codes.filter(
    (c) => c === "NO_EVIDENCE"
  ).length

  const proofFailCount = codes.filter(
    (c) => c === "PROOF_WEAK" || c === "NO_EVIDENCE"
  ).length

  if (hardFail || proofFailCount >= Math.ceil(n / 2) || noEvidenceCount >= 2) {
    return { outcome: "failed", codes: unique }
  }

  const softFlags =
    input.contentWeakSelf ||
    unique.includes("SELF_CHECK_GAP") ||
    (unique.includes("RUSHED") && weakOrEmpty > 0)

  if (softFlags) {
    const finalCodes = input.contentWeakSelf
      ? [...new Set([...unique, "METHOD_OK_CONTENT_WEAK" as MethodErrorCode])]
      : unique
    return { outcome: "doc_only", codes: finalCodes }
  }

  return { outcome: "passed", codes: unique }
}
