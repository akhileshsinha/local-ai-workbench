import ReactMarkdown from "react-markdown";

function Message({ message }) {
  const isUser = message.role === "user";

  const formattedTime = message.timestamp
    ? new Date(message.timestamp).toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      })
    : "";

  return (
    <div
      className={`message-row ${
        isUser ? "user-row" : "assistant-row"
      }`}
    >
      <div
        className={`message-card ${
          isUser
            ? "user-message"
            : "assistant-message"
        }`}
      >
        <div className="message-label">
          {isUser ? "You" : "Qwen"}
        </div>

        {message.image && (
          <img
            src={message.image}
            alt="Attachment"
            className="message-image"
          />
        )}

        <ReactMarkdown>
          {message.content}
        </ReactMarkdown>

        <div className="message-meta">
  {formattedTime && (
    <span className="message-timestamp">
      {formattedTime}
    </span>
  )}

  {message.latency && (
    <span className="message-latency">
      {message.latency}s
    </span>
  )}
</div>
      </div>
    </div>
  );
}

export default Message;