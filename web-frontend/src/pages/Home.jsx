import Navbar from "../components/Navbar"
import Hero from "../components/Hero"

export default function Home() {
  return (
    <div>
      <Navbar />
      <main className="page-container">
        <Hero />
        <section className="editorial-process" id="how-it-works">
          <header className="process-intro"><span className="eyebrow">The method</span><h2>From first clue<br />to next step.</h2><p>No guesswork about what to do next. A simple investigation, in three parts.</p><span className="process-motto">Investigate → Verify → Decide</span></header>
          <ol className="investigation-sequence">
            <li className="investigation-step"><span className="step-number">01</span><div><h3>Submit the evidence</h3><p>Paste the message or link that made you pause. Submit only what you want checked.</p></div></li>
            <li className="investigation-step"><span className="step-number">02</span><div><h3>We investigate</h3><p>True Detective examines message patterns and link warning signs for relevant clues.</p></div></li>
            <li className="investigation-step"><span className="step-number">03</span><div><h3>You decide safely</h3><p>Read a clear risk report, understand the findings, and choose your next step with care.</p></div></li>
          </ol>
        </section>
        <footer className="page-footer"><span>True Detective</span><p>A little scrutiny goes a long way.</p><span className="eyebrow">Digital safety, with a human touch.</span></footer>
      </main>
    </div>
  )
}
