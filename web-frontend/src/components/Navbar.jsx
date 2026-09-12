import { ShieldCheck } from "lucide-react"

function Navbar() {
  return (
    <nav className="navbar">

      <div className="brand">
        <div className="brand-icon">
          <ShieldCheck size={22} />
        </div>

        <div>
          <h3>Digital Shield</h3>
          <span>Stay safer online</span>
        </div>
      </div>

      <div className="nav-actions">
        <button className="language-button">
          EN
        </button>

        <button className="language-button">
          اردو
        </button>
      </div>

    </nav>
  )
}

export default Navbar