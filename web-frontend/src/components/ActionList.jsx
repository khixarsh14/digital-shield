import { ArrowRight } from "lucide-react"

export default function ActionList({ actions = [] }) {
  return <ul className="result-list action-list">{actions.map((action, index) => <li key={index}><ArrowRight size={17} aria-hidden="true" /><span>{action}</span></li>)}</ul>
}
