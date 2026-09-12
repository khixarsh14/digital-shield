import AudioPlayer from "./AudioPlayer"
import FamilyAlertBanner from "./FamilyAlertBanner"

function TrustSignalCard({ scenario }) {

  const icons = {
    red: "🔴",
    yellow: "🟡",
    green: "🟢"
  }

  return (
    <div className={`trust-card ${scenario.result}`}>

      <div className="trust-top">

        <span className="trust-icon">
          {icons[scenario.result]}
        </span>

        <div>
          <span className="trust-label">
            {scenario.label}
          </span>

          <h2>{scenario.heading}</h2>
        </div>

      </div>

      <p className="trust-description">
        {scenario.explanation}
      </p>

      <AudioPlayer audio={scenario.audio} />

      {scenario.notifyFamily && (
        <FamilyAlertBanner />
      )}

    </div>
  )
}

export default TrustSignalCard