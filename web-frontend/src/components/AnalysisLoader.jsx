import { useEffect, useState } from "react"

const steps = ["Reading evidence", "Identifying suspicious patterns", "Inspecting links", "Reviewing findings"]

export default function AnalysisLoader() {
  const [activeStep, setActiveStep] = useState(0)
  useEffect(() => {
    const timer = window.setInterval(() => setActiveStep((step) => Math.min(step + 1, steps.length - 1)), 450)
    return () => window.clearInterval(timer)
  }, [])
  return (
    <section className="analysis-loader" aria-label="Investigation progress">
      <span className="eyebrow">Investigation in progress</span><h2>Following the clues.</h2><div className="investigation-track" aria-hidden="true"><span /></div>
      <p role="status" aria-live="polite" aria-atomic="true">{steps[activeStep]}</p>
      <ol className="analysis-steps">
        {steps.map((step, index) => (
          <li key={step} className={index <= activeStep ? "step-active" : ""} aria-current={index === activeStep ? "step" : undefined}>
            <span className="step-marker" aria-hidden="true">{index < activeStep ? "✓" : index + 1}</span>{step}
          </li>
        ))}
      </ol>
    </section>
  )
}

