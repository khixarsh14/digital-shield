import { useState } from "react"
import Navbar from "../components/Navbar"

function Verify() {

  const [content, setContent] = useState("")
  const [type, setType] = useState("message")

  const handleVerify = () => {
    console.log({
      type,
      content
    })
  }

  return (
    <div>

      <Navbar />

      <main className="verify-page">

        <div className="verify-header">

          <h1>Verify suspicious content</h1>

          <p>
            Paste a message, link, or screenshot and Digital Shield will investigate it.
          </p>

        </div>

        <div className="verify-card">

          <div className="verify-tabs">

            <button
              className={type === "message" ? "active-tab" : ""}
              onClick={() => setType("message")}
            >
              Message
            </button>

            <button
              className={type === "link" ? "active-tab" : ""}
              onClick={() => setType("link")}
            >
              Link
            </button>

            <button
              className={type === "image" ? "active-tab" : ""}
              onClick={() => setType("image")}
            >
              Screenshot
            </button>

          </div>

          {type !== "image" && (
            <textarea
              placeholder={
                type === "link"
                  ? "Paste suspicious link here..."
                  : "Paste suspicious message here..."
              }
              value={content}
              onChange={(e) => setContent(e.target.value)}
            />
          )}

          {type === "image" && (
            <div className="upload-box">

              <p>Upload screenshot or image</p>

              <input
                type="file"
                accept="image/*"
              />

            </div>
          )}

          <button
            className="primary-button full-width"
            onClick={handleVerify}
          >
            Verify Content
          </button>

        </div>

      </main>

    </div>
  )
}

export default Verify