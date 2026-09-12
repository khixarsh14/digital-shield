const API_URL = (import.meta.env.VITE_API_URL || "http://127.0.0.1:8000").replace(/\/+$/, "")
const ERROR_MESSAGE = "We couldn't verify this content right now. Please try again."

function isVerifyResponse(result) {
  return result && ["green", "yellow", "red"].includes(result.status)
    && typeof result.label === "string" && typeof result.summary === "string"
    && [result.reasons, result.actions].every((items) => Array.isArray(items) && items.every((item) => typeof item === "string"))
    && Array.isArray(result.sources) && result.sources.every((source) =>
      source && typeof source.label === "string" && typeof source.url === "string" && /^https?:\/\//i.test(source.url))
    && typeof result.needs_followup === "boolean"
    && (result.followup_question === null || typeof result.followup_question === "string")
    && ["en", "ur"].includes(result.language)
}

export async function verifyContent(content, { signal } = {}) {
  try {
    const response = await fetch(`${API_URL}/verify`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content: content.trim(), language: "en" }),
      signal: AbortSignal.any([AbortSignal.timeout(30000), ...(signal ? [signal] : [])]),
    })
    if (!response.ok) throw new Error(ERROR_MESSAGE)
    const result = await response.json()
    if (!isVerifyResponse(result)) throw new Error(ERROR_MESSAGE)
    return result
  } catch {
    throw new Error(ERROR_MESSAGE)
  }
}
