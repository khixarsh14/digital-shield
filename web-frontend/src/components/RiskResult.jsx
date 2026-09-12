import { CircleCheck, TriangleAlert, CircleAlert, ExternalLink } from "lucide-react"
import ReasonList from "./ReasonList"
import ActionList from "./ActionList"

const riskIcons = { green: CircleCheck, yellow: TriangleAlert, red: CircleAlert }

export default function RiskResult({ result }) {
  const status = result.status
  const RiskIcon = riskIcons[status]
  return (
    <section className={`risk-result risk-${status}`} aria-label={`${result.label} result`}>
      <div className="report-top"><span className="eyebrow">Investigation report</span><span className="eyebrow">Findings & next steps</span></div>
      <div className="risk-heading"><RiskIcon size={26} aria-hidden="true" /><h2>{result.label}</h2></div>
      <p className="risk-summary">{result.summary}</p>
      <h3>Clues found</h3>
      <ReasonList reasons={result.reasons} />
      <h3>Recommended next steps</h3>
      <ActionList actions={result.actions} />
      <h3>Sources checked</h3>
      {result.sources.length > 0 ? <ul className="result-list source-list">{result.sources.map((source, index) =>
        <li key={index}><a href={source.url} target="_blank" rel="noopener noreferrer">{source.label}<ExternalLink size={15} aria-hidden="true" /></a></li>
      )}</ul> : <p className="source-note">No external sources were provided in this report.</p>}
      {result.needs_followup && result.followup_question && <>
        <h3>More information needed</h3>
        <p>{result.followup_question}</p>
      </>}
    </section>
  )
}
