import { ShieldCheck } from "lucide-react"
import { useNavigate } from "react-router-dom"

function Hero() {

  const navigate = useNavigate()

  return (
    <section className="hero">

      <div className="hero-badge">
        <ShieldCheck size={16} />
        Digital Safety Assistant
      </div>

      <h1>
        Check before you trust.
      </h1>

      <p>
        Digital Shield investigates suspicious messages,
        links and screenshots and gives you a simple
        safety result.
      </p>

      <button
        className="primary-button"
        onClick={() => navigate("/verify")}
      >
        Verify Something
      </button>

      <span className="hero-note">
        Forward → Verify → Stay Safe
      </span>

    </section>
  )
}

export default Hero