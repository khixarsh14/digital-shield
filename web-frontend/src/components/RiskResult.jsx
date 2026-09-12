import ReasonList from "./ReasonList"
import ActionList from "./ActionList"

const riskStates = {
  green: { label: "Looks Safe", icon: "✓" },
  yellow: { label: "Verify First", icon: "!" },
  red: { label: "High Risk", icon: "!" },
}

export default function RiskResult({ result }) {
  const status = Object.hasOwn(riskStates, result.status) ? result.status : "yellow"
  const state = riskStates[status]
  return (
    <section className={`risk-result risk-${status}`} aria-label={`${state.label} result`}>
      <div className="risk-heading"><span className="risk-icon" aria-hidden="true">{state.icon}</span><h2>{state.label}</h2></div>
      <p className="risk-summary">{result.summary}</p>
      <h3>Why?</h3>
      <ReasonList reasons={result.reasons} />
      <h3>What should you do?</h3>
      <ActionList actions={result.actions} />
    </section>
  )
}
