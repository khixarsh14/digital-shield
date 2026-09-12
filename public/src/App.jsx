import { useState } from "react"

import scenarios from "./data/scenarios.json"

import ChatHeader from "./components/ChatHeader"
import ChatBubble from "./components/ChatBubble"
import TrustSignalCard from "./components/TrustSignalCard"

import "./styles/whatsapp.css"

function App() {

  const [selectedScenario, setSelectedScenario] = useState(null)
  const [scanning, setScanning] = useState(false)
  const [showResult, setShowResult] = useState(false)

  const runScenario = (scenario) => {

    setSelectedScenario(scenario)

    setScanning(true)
    setShowResult(false)

    setTimeout(() => {
      setScanning(false)
      setShowResult(true)
    }, 1800)
  }

  return (
    <div className="app-page">

      <div className="demo-selector">

        <h1>Digital Shield Demo</h1>

        <p>
          Select a scenario to simulate how the system protects users.
        </p>

        <div className="scenario-buttons">

          {scenarios.map((scenario) => (
            <button
              key={scenario.id}
              onClick={() => runScenario(scenario)}
            >
              {scenario.title}
            </button>
          ))}

        </div>

      </div>

      <div className="phone">

        <ChatHeader />

        <div className="chat-area">

          {!selectedScenario && (
            <div className="welcome-message">
              <h3>🛡️ Digital Shield</h3>

              <p>
                Share suspicious content here to check whether it can be trusted.
              </p>
            </div>
          )}

          {selectedScenario && (
            <>
              <ChatBubble scenario={selectedScenario} />

              {scanning && (
                <div className="message-row">
                  <div className="scan-box">

                    <div className="scanner"></div>

                    <p>Checking source...</p>

                    <span>
                      Analyzing digital signals
                    </span>

                  </div>
                </div>
              )}

              {showResult && (
                <TrustSignalCard
                  scenario={selectedScenario}
                />
              )}

            </>
          )}

        </div>

        <div className="chat-input">

          <button>＋</button>

          <div className="fake-input">
            Share message, image or link...
          </div>

          <button>➤</button>

        </div>

      </div>

    </div>
  )
}

export default App