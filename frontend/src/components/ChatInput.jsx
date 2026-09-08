import { useRef, useState } from "react";

function ChatInput({ onSend, disabled, visionMode, onStop }) {
  const [value, setValue] = useState("");
  const [image, setImage] = useState(null);

  const textareaRef = useRef(null);
  const fileInputRef = useRef(null);

  const handleChange = (event) => {
    setValue(event.target.value);

    const textarea = textareaRef.current;

    textarea.style.height = "auto";
    textarea.style.height = `${Math.min(textarea.scrollHeight, 180)}px`;
  };

  const handleImageChange = (event) => {
    const file = event.target.files?.[0];

    if (!file) return;

    const previewUrl = URL.createObjectURL(file);

    setImage({
      file,
      previewUrl,
    });
  };

  const handleSend = () => {
    if (!value.trim() || disabled) return;

    if (visionMode && !image) {
      return;
    }

    onSend(value.trim(), image?.file, image?.previewUrl);

    setValue("");
    setImage(null);

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }

    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="input-container">
      <div className="input-box">
        {visionMode && (
          <div className="image-attachment">
            {image ? (
              <div className="selected-image">
                <img
                  src={image.previewUrl}
                  alt="Selected attachment"
                  className="attachment-thumbnail"
                />

                <div className="attachment-info">
                  <span>{image.file.name}</span>
                </div>

                <button
                  type="button"
                  className="remove-attachment"
                  onClick={() => {
                    URL.revokeObjectURL(image.previewUrl);
                    setImage(null);

                    if (fileInputRef.current) {
                      fileInputRef.current.value = "";
                    }
                  }}
                >
                  ×
                </button>
              </div>
            ) : (
              <button
                type="button"
                className="attach-button"
                onClick={() => fileInputRef.current?.click()}
              >
                📎 Attach image
              </button>
            )}

            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleImageChange}
              hidden
            />
          </div>
        )}

        <textarea
          ref={textareaRef}
          value={value}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          placeholder={
            visionMode ? "Ask something about this image..." : "Ask anything..."
          }
          rows={1}
          disabled={disabled}
        />

        <div className="input-actions">
          <span className="input-hint">
            Enter to send · Shift + Enter for new line
          </span>

          {disabled ? (
            <button
              type="button"
              className="stop-button"
              onClick={onStop}
              title="Stop generation"
            >
              ■
            </button>
          ) : (
            <button
              type="button"
              className="send-button"
              disabled={!value.trim() || (visionMode && !image)}
              onClick={handleSend}
            >
              ↑
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default ChatInput;
