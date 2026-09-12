import { useEffect, useRef, useState } from "react"
import Navbar from "../components/Navbar"
import AnalysisLoader from "../components/AnalysisLoader"
import RiskResult from "../components/RiskResult"
import PrivacyNotice from "../components/PrivacyNotice"
import { verifyContent } from "../services/api"

function Verify() {
  const [content, setContent] = useState("")
  const [type, setType] = useState("message")
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const requestRef = useRef(null)
  const resultRef = useRef(null)
  useEffect(() => () => requestRef.current?.abort(), [])
  useEffect(() => { if (result) resultRef.current?.focus() }, [result])

  async function handleVerify(event) {
    event.preventDefault()
    if (!content.trim() || requestRef.current) return
    const controller = new AbortController()
    requestRef.current = controller
    setResult(null)
    setError(null)
    setIsAnalyzing(true)
    try {
      const response = await verifyContent(content, { signal: controller.signal })
      if (!controller.signal.aborted) setResult(response)
    } catch (failure) {
      if (!controller.signal.aborted) setError(failure.message)
    } finally {
      if (!controller.signal.aborted) setIsAnalyzing(false)
      if (requestRef.current === controller) requestRef.current = null
    }
  }

  return (
    <div>
      <Navbar />
      <main className="verify-page">
        <div className="verify-header">
          <span className="eyebrow">Evidence intake / New case</span><h1>Open a New Investigation</h1>
          <p>Submit only the content you want us to investigate.</p><PrivacyNotice />
        </div>
        <form className="verify-card" onSubmit={handleVerify}>
          <div className="verify-tabs" role="group" aria-label="Content type">
            {["message", "link"].map((option) => (
              <button key={option} type="button" className={type === option ? "active-tab" : ""}
                aria-pressed={type === option} disabled={isAnalyzing}
                onClick={() => { setType(option); setResult(null); setError(null) }}>
                {option === "message" ? "Message" : "Link"}
              </button>
            ))}<button type="button" disabled aria-describedby="screenshot-note">Screenshot</button>
          </div>
          <p className="intake-note" id="screenshot-note">Screenshot investigation is not available yet.</p><label className="content-label" htmlFor="verification-content">{type === "link" ? "Suspicious link" : "Suspicious message"}</label>
          <textarea id="verification-content" aria-describedby="privacy-description"
            placeholder={`Paste suspicious ${type} here...`} value={content} disabled={isAnalyzing} required
            onChange={(event) => { setContent(event.target.value); setResult(null); setError(null) }} />

          <button className="primary-button full-width" disabled={!content.trim() || isAnalyzing}>
            {isAnalyzing ? "Investigating..." : "Investigate"}
          </button>
          {error && <p className="verification-error" role="alert">{error}</p>}
        </form>
        {isAnalyzing && <AnalysisLoader />}
        {result && <div ref={resultRef} tabIndex={-1} className="result-focus" aria-label="Investigation report"><RiskResult result={result} /></div>}
      </main>
    </div>
  )
}

export default Verify

