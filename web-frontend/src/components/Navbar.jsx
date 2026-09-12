import { LockKeyhole, Search } from "lucide-react"
import { Link } from "react-router-dom"

export default function Navbar() {
  return (
    <nav className="navbar" aria-label="Main navigation">
      <Link className="brand" to="/" aria-label="True Detective home">
        <span className="brand-icon"><Search size={28} strokeWidth={1.5} /></span>
        <span className="brand-copy"><strong>True Detective</strong></span>
      </Link>
      <div className="nav-actions">
        <span className="nav-privacy"><LockKeyhole size={14} aria-hidden="true" /> Private by design</span>
        <div className="languages" aria-label="Language">
          <button className="language-button" aria-label="English">EN</button>
          <span aria-hidden="true">/</span>
          <button className="language-button" lang="ur" disabled title="Urdu interface coming soon">اردو</button>
        </div>
      </div>
    </nav>
  )
}

