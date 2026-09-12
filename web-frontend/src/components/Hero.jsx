import { ArrowRight, LockKeyhole } from "lucide-react"
import { useNavigate } from "react-router-dom"

export default function Hero() {
  const navigate = useNavigate()
  return (
    <section className="editorial-cover">
      <header className="masthead">
        <h1 className="hero-title">True Detective</h1>
        <p className="masthead-subtitle">Investigate before you trust.</p>
      </header>
      <div className="cover-statement">
        <h2>Every suspicious message leaves <em>a clue.</em></h2>
        <button className="primary-button" onClick={() => navigate("/verify")}>Start Investigation <ArrowRight size={18} aria-hidden="true" /></button>
      </div>
      <section className="case-spread" aria-label="Sample investigation">
        <div className="spread-heading"><span className="eyebrow">Case file: 001 / Sample evidence</span><span className="eyebrow">The anatomy of a suspicious message</span></div>
        <div className="case-grid">
          <article className="evidence-quote">
            <div className="quote-header"><span className="eyebrow">Evidence A</span><span className="eyebrow">Message excerpt</span></div>
            <blockquote>“Your account will be blocked <mark>today.</mark><br />Share your <mark>OTP</mark> to secure it.”</blockquote>
            <p className="evidence-caption">A sample, not a live investigation. A familiar warning can conceal an unfamiliar sender.</p>
            <span className="evidence-stamp">Pause before you act</span>
          </article>
          <aside className="field-notes">
            <span className="eyebrow">Field notes</span>
            <h3>Read between<br /><em>the lines.</em></h3>
            <dl className="sample-clues">
              <div><dt>Clue 01</dt><dd>Urgency</dd></div>
              <div><dt>Clue 02</dt><dd>OTP request</dd></div>
              <div><dt>Clue 03</dt><dd>Unverified source</dd></div>
            </dl>
          </aside>
          <aside className="source-reference"><span className="eyebrow">Source check</span><p>A name is not proof.<br /><strong>Verify the sender independently.</strong></p></aside>
          <div className="lens-accent" aria-hidden="true"><svg className="magnifier" viewBox="0 0 280 330" fill="none">
          <path d="M163 182L240 282" stroke="#211C17" strokeWidth="29" strokeLinecap="round" />
          <path d="M165 183L184 208" stroke="#B28A4A" strokeWidth="32" />
          <path d="M187 217L235 278" stroke="#554031" strokeWidth="9" strokeLinecap="round" />
          <circle cx="114" cy="116" r="85" fill="#8FAFBD" fillOpacity=".12" stroke="#7D6238" strokeWidth="13" />
          <circle cx="114" cy="116" r="86" stroke="#D4B06A" strokeWidth="4" />
          <circle cx="114" cy="116" r="76" stroke="#B28A4A" strokeWidth="2" />
          <path d="M58 103A59 59 0 0 1 110 58" stroke="#FFFDF8" strokeWidth="6" strokeLinecap="round" />
        </svg><span className="eyebrow">Look closer.</span></div>
        </div>
        <p className="spread-footer"><LockKeyhole size={14} aria-hidden="true" /> Only the content you submit is analyzed.</p>
      </section>
    </section>
  )
}
