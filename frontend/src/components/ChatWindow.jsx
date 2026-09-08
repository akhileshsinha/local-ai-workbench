import Message from "./Message";
import Loader from "./Loader";
import ChatInput from "./ChatInput";
import { useEffect, useRef, useState } from "react";

function ChatWindow({
  session,
  setSessions,
  setActiveSessionId,
  selectedModel,
  setLastLatency,
  modelLoading,
}) {
  const [loading, setLoading] = useState(false);

  const messagesEndRef = useRef(null);
  const abortControllerRef = useRef(null);

  const messages = session?.messages || [];

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading]);

  const handleStop = () => {
    if (!abortControllerRef.current) {
      return;
    }

    abortControllerRef.current.abort();
    abortControllerRef.current = null;
    setLoading(false);
  };

  const handleSend = async (text, image, imagePreview) => {
    let sessionId = session?.id;

    if (!sessionId) {
      sessionId = crypto.randomUUID();

      const newSession = {
        id: sessionId,
        title: text,
        messages: [],
      };

      setSessions((previous) => [newSession, ...previous]);

      setActiveSessionId(sessionId);
    }

    const userMessage = {
      role: "user",
      content: text,
      timestamp: new Date().toISOString(),
      image: imagePreview || null,
    };

    setSessions((previous) =>
      previous.map((item) =>
        item.id === sessionId
          ? {
              ...item,
              messages: [...item.messages, userMessage],
            }
          : item,
      ),
    );

    setLoading(true);

    const startTime = performance.now();

    const controller = new AbortController();

    abortControllerRef.current = controller;

    try {
      let response;

      /*
       * Vision model
       */
      if (selectedModel === "qwen-vision") {
        const formData = new FormData();

        formData.append("prompt", text);

        if (image) {
          formData.append("image", image);
        }

        response = await fetch("http://localhost:8000/generate-image", {
          method: "POST",
          body: formData,
          signal: controller.signal,
        });
      } else if (selectedModel === "qwen-coder") {
        /*
         * Coding model
         */
        response = await fetch("http://localhost:8000/generate-code", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            prompt: text,
          }),
          signal: controller.signal,
        });
      } else {
        /*
         * General Qwen model
         */
        response = await fetch("http://localhost:8000/generate", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            prompt: text,
          }),
          signal: controller.signal,
        });
      }

      if (!response.ok) {
        throw new Error(`HTTP error: ${response.status}`);
      }

      const data = await response.json();

      const latency = (performance.now() - startTime) / 1000;

      setLastLatency(latency.toFixed(2));

      const assistantMessage = {
        role: "assistant",
        content: data.response,
        timestamp: new Date().toISOString(),
        latency: latency.toFixed(2),
      };

      setSessions((previous) =>
        previous.map((item) =>
          item.id === sessionId
            ? {
                ...item,
                messages: [...item.messages, assistantMessage],
              }
            : item,
        ),
      );
    } catch (error) {
      if (error.name === "AbortError") {
        console.log("Generation stopped by user.");
        return;
      }

      console.error(error);

      const errorMessage = {
        role: "assistant",
        content: "Sorry, something went wrong while processing your request.",
        timestamp: new Date().toISOString(),
      };

      setSessions((previous) =>
        previous.map((item) =>
          item.id === sessionId
            ? {
                ...item,
                messages: [...item.messages, errorMessage],
              }
            : item,
        ),
      );
    } finally {
      setLoading(false);
      abortControllerRef.current = null;
    }
  };

  const modelName =
    selectedModel === "qwen-vision"
      ? "Qwen3-VL-2B"
      : selectedModel === "qwen-coder"
        ? "Qwen2.5-Coder-7B"
        : "Qwen3-4B";

  return (
    <main className="chat-window">
      <header className="chat-header">
        <div>
          <h2>{session?.title || "Nisum"}</h2>

          <span>{modelName}</span>
        </div>
      </header>

      <section className="messages">
        {!session && (
          <div className="welcome">
            <div className="welcome-icon">✦</div>

            <h1>How can I help you?</h1>

            <p>Ask anything. Keep your conversations and data within Nisum</p>
          </div>
        )}

        {messages.map((message, index) => (
          <Message key={index} message={message} />
        ))}

        {loading && <Loader />}

        <div ref={messagesEndRef} />
      </section>

      <ChatInput
        onSend={handleSend}
        disabled={loading || modelLoading}
        onStop={handleStop}
        visionMode={selectedModel === "qwen-vision"}
      />
    </main>
  );
}

export default ChatWindow;
