import { useState } from "react";
import Sidebar from "./components/Sidebar";
import ChatWindow from "./components/ChatWindow";
import "./App.css";

function App() {
  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [selectedModel, setSelectedModel] = useState("qwen");
  const [modelLoading, setModelLoading] = useState(false);

  const [lastLatency, setLastLatency] = useState(null);
  const activeSession = sessions.find(
    (session) => session.id === activeSessionId,
  );

  const handleNewChat = () => {
    setActiveSessionId(null);
  };

  const handleModelChange = async (model) => {
    setSelectedModel(model);
    setModelLoading(true);

    try {
      const response = await fetch("http://localhost:8000/models/switch", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          model,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error: ${response.status}`);
      }

      const data = await response.json();

      console.log(`Model ready: ${data.model}`);
    } catch (error) {
      console.error("Model switching failed:", error);
    } finally {
      setModelLoading(false);
    }
  };

  return (
    <div className="app">
      <Sidebar
        sessions={sessions}
        activeSessionId={activeSessionId}
        onSelectSession={setActiveSessionId}
        onNewChat={handleNewChat}
        selectedModel={selectedModel}
        onModelChange={handleModelChange}
        modelLoading={modelLoading}
        lastLatency={lastLatency}
      />

      <ChatWindow
        session={activeSession}
        setSessions={setSessions}
        setActiveSessionId={setActiveSessionId}
        selectedModel={selectedModel}
        setLastLatency={setLastLatency}
        modelLoading={modelLoading}

      />
    </div>
  );
}

export default App;
