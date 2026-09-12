import { useEffect, useRef, useState } from "react"
import Navbar from "../components/Navbar"
import AnalysisLoader from "../components/AnalysisLoader"
import RiskResult from "../components/RiskResult"
import PrivacyNotice from "../components/PrivacyNotice"
import { mockResult } from "../data/mockResult"

export default function Verify() {
  const [content, setContent] = useState("")
  const [type, setType] = useState("message")
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [result, setResult] = useState(null)
  const timer = useRef(null)
  const resultRef = useRef(null)
  useEffect(() => () => window.clearTimeout(timer.current), [])
  useEffect(() => { if (result) resultRef.current?.focus() }, [result])

  function handleVerify(event) {
    event.preventDefault()
    if (!content.trim() || isAnalyzing) return
    setResult(null)
    setIsAnalyzing(true)
    timer.current = window.setTimeout(() => {
      setResult(mockResult)
      setIsAnalyzing(false)
    }, 1800)
  }

  return (
    <div>
      <Navbar />
      <main className="verify-page">
        <div className="verify-header">
          <h1>Verify suspicious content</h1>
          <p>Paste a message or link and Digital Shield will investigate it.</p>
        </div>
        <form className="verify-card" onSubmit={handleVerify}>
          <div className="verify-tabs" role="group" aria-label="Content type">
            {["message", "link"].map((option) => (
              <button key={option} type="button" className={type === option ? "active-tab" : ""}
                aria-pressed={type === option} disabled={isAnalyzing}
                onClick={() => { setType(option); setResult(null) }}>
                {option === "message" ? "Message" : "Link"}
              </button>
            ))}
          </div>
          <label className="content-label" htmlFor="verification-content">{type === "link" ? "Suspicious link" : "Suspicious message"}</label>
          <textarea id="verification-content" aria-describedby="privacy-description demo-notice"
            placeholder={`Paste suspicious ${type} here...`} value={content} disabled={isAnalyzing} required
            onChange={(event) => { setContent(event.target.value); setResult(null) }} />
          <PrivacyNotice />
          <button className="primary-button full-width" disabled={!content.trim() || isAnalyzing}>
            {isAnalyzing ? "Investigating..." : "Verify Content"}
          </button>
          <p className="demo-notice" id="demo-notice">Demo mode: every submission shows the same sample result.</p>
        </form>
        {isAnalyzing && <AnalysisLoader />}
        {result && <div ref={resultRef} tabIndex={-1} className="result-focus" aria-label="Verification result"><RiskResult result={result} /></div>}
      </main>
    </div>
  )
}
