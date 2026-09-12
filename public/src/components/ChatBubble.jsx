function ChatBubble({ scenario }) {
  return (
    <div className="message-row user-row">
      <div className="chat-bubble user-bubble">

        {scenario.type === "image" && (
          <img
            src={scenario.image}
            alt="Shared content"
            className="shared-image"
          />
        )}

        <p>{scenario.message}</p>

        <span className="timestamp">10:42 AM</span>
      </div>
    </div>
  )
}

export default ChatBubble