import Navbar from "../components/Navbar"
import Hero from "../components/Hero"

function Home() {
  return (
    <div>

      <Navbar />

      <main className="page-container">
        <Hero />

        <section className="how-section">

          <h2>How Digital Shield works</h2>

          <div className="steps">

            <div className="step-card">
              <span>1</span>
              <h3>Send suspicious content</h3>
              <p>
                Paste a message, link, or upload a screenshot.
              </p>
            </div>

            <div className="step-card">
              <span>2</span>
              <h3>We investigate it</h3>
              <p>
                Digital Shield checks the content using the right verification tools.
              </p>
            </div>

            <div className="step-card">
              <span>3</span>
              <h3>Get a clear result</h3>
              <p>
                Receive a simple risk level and what you should do next.
              </p>
            </div>

          </div>

        </section>

      </main>

    </div>
  )
}

export default Home