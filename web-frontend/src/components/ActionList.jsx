export default function ActionList({ actions = [] }) {
  return <ul className="result-list">{actions.map((action, index) => <li key={index}>{action}</li>)}</ul>
}
