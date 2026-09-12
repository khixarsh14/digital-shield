export default function ReasonList({ reasons = [] }) {
  return <ul className="result-list">{reasons.map((reason, index) => <li key={index}>{reason}</li>)}</ul>
}
