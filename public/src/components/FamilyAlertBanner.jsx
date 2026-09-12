import { useState } from "react"

function FamilyAlertBanner() {

  const [sent, setSent] = useState(false)

  const notifyFamily = () => {
    setSent(true)
  }

  return (
    <div className="family-section">

      {!sent ? (
        <button
          className="family-button"
          onClick={notifyFamily}
        >
          👤 Alert Trusted Contact
        </button>
      ) : (
        <div className="family-alert">
          ✓ Trusted contact notified
        </div>
      )}

    </div>
  )
}

export default FamilyAlertBanner