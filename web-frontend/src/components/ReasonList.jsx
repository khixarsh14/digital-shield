export default function ReasonList({ reasons = [] }) {
  return <ul className="result-list clue-list">{reasons.map((reason, index) => <li key={index}><span className="eyebrow">Clue {String(index + 1).padStart(2, "0")}</span><span>{reason}</span></li>)}</ul>
}
