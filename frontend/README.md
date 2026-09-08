# 🤖 Local ChatGPT

> A beautiful, privacy-friendly ChatGPT-style frontend for interacting with locally hosted AI models.

A modern React-based chat interface built as the frontend for a **local AI playground**.

The application provides a familiar ChatGPT-like experience while keeping the architecture flexible enough to connect with locally running models, custom APIs, and eventually multiple AI capabilities such as text, image, and video generation.

---

## ✨ Features

### 💬 Chat Interface

- Clean, modern ChatGPT-inspired UI
- User and assistant messages displayed in separate cards
- Properly formatted multiline responses
- Responsive conversation layout
- Smooth loading experience while waiting for model responses

### 🧠 Local AI Integration

Designed to communicate with a locally running AI backend.

```text
React Frontend
      │
      ▼
   FastAPI
      │
      ▼
 Local AI Model

 The frontend is currently designed to work with the locally hosted Qwen model through the FastAPI backend.

📚 Chat Sessions
Create a new conversation
Maintain multiple chat sessions
View previous sessions from the left sidebar
Switch between conversations
Keep conversations organized independently
⌨️ Keyboard Friendly
Press Enter to send a message
Use Shift + Enter for a new line
Input area expands as the message becomes longer
⏳ Loading State

A dedicated loading indicator is displayed while the application waits for the AI response.

You
 │
 ├── Send message
 │
 ▼
⏳ Generating response...
 │
 ▼
🤖 AI response

🎨 Modern UI
ChatGPT-inspired layout
Professional sidebar
Distinct user/assistant message styling
Responsive message container
Expandable input box
Model-oriented application design

┌──────────────────────────────────────────────────────────────┐
│  🤖 Local ChatGPT                                  Qwen ▾    │
├───────────────┬──────────────────────────────────────────────┤
│               │                                              │
│  + New Chat   │              How can I help?                 │
│               │                                              │
│  Conversations│                                              │
│               │                                              │
│  React        │  ┌────────────────────────────────────────┐  │
│  Hydration    │  │ You                                    │  │
│               │  │ Explain React hydration                │  │
│  Git Help     │  └────────────────────────────────────────┘  │
│               │                                              │
│  Qwen Test    │  ┌────────────────────────────────────────┐  │
│               │  │ 🤖 Assistant                           │  │
│               │  │                                        │  │
│               │  │ Hydration is the process where...     │  │
│               │  └────────────────────────────────────────┘  │
│               │                                              │
│               │                                              │
│               │  ┌────────────────────────────────────────┐  │
│               │  │ Ask anything...                    ➤   │  │
│               │  └────────────────────────────────────────┘  │
└───────────────┴──────────────────────────────────────────────┘

🏗️ Architecture

The frontend is intentionally kept separate from the AI/model layer.

                       ┌─────────────────────┐
                       │     React App       │
                       │                     │
                       │  Chat UI            │
                       │  Sessions           │
                       │  Message rendering  │
                       │  Input handling     │
                       └──────────┬──────────┘
                                  │
                                  │ HTTP
                                  ▼
                       ┌─────────────────────┐
                       │      FastAPI        │
                       │      Backend        │
                       └──────────┬──────────┘
                                  │
                                  ▼
                       ┌─────────────────────┐
                       │   Local AI Model    │
                       │      Qwen           │
                       └─────────────────────┘


This separation allows the frontend to remain independent of the underlying AI model.

The backend can eventually switch between different models without requiring major changes to the UI.

📁 Project Structure
frontend/
│
├── public/
│
├── src/
│   │
│   ├── components/
│   │   ├── Chat/
│   │   ├── Sidebar/
│   │   ├── Message/
│   │   └── Input/
│   │
│   ├── services/
│   │   └── api.js
│   │
│   ├── App.jsx
│   ├── main.jsx
│   └── ...
│
├── package.json
├── package-lock.json
└── README.md


🚀 Getting Started
Prerequisites

Make sure you have:

Node.js
npm
A running FastAPI backend
A locally configured AI model

Verify Node.js:
node --version

Verify npm:
npm --version

1. Clone the repository
git clone <your-repository-url>

Navigate into the frontend project:

cd local-chat-gpt
2. Install dependencies
npm install
3. Start the development server
npm run dev

The application will normally be available at:

http://localhost:5173
🔌 Backend Configuration

The frontend communicates with the FastAPI backend through HTTP requests.

Example:

Frontend
   │
   │ POST /generate
   ▼
http://localhost:8000

The frontend should never directly communicate with the local model.

Instead:

❌ React → Qwen

✅ React → FastAPI → Qwen

This keeps the AI/model layer isolated from the UI.

💬 Chat Flow

When a user sends a message:

1. User enters prompt
        │
        ▼
2. React captures the message
        │
        ▼
3. Frontend sends API request
        │
        ▼
4. FastAPI processes request
        │
        ▼
5. Local Qwen model generates response
        │
        ▼
6. FastAPI returns response
        │
        ▼
7. React renders assistant message
🧠 Model Agnostic Design

Although the current application uses Qwen, the frontend is not intended to be tightly coupled to a specific model.

The long-term architecture is:

                    Local ChatGPT
                         │
                    Model Manager
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              ▼
        Qwen          Coding Model    Image Model
        Text             Code           Image

The UI can eventually allow users to select the capability/model they want to use.

🔮 Planned Features

The project is currently evolving into a local AI playground.

AI & Models
 Multiple local model support
 Model selector
 Dynamic model loading/unloading
 Model status indicator
 Memory usage monitoring
 Coding model integration
 Image generation
 Video generation
Chat
 Basic chat interface
 New Chat
 Chat history
 Session switching
 Loading indicator
 Enter-to-send
 Multiline input
 Streaming responses
 Markdown rendering
 Code syntax highlighting
 Copy response
 Regenerate response
 Edit prompt
 Delete conversation
 Rename conversation
Developer Experience
 API playground
 Model performance metrics
 Token usage information
 Response latency
 Local system memory dashboard
 Coding-agent integration
🔐 Privacy

One of the primary goals of this project is experimenting with local AI.

When using a locally hosted model:

Your Prompt
    │
    ▼
Your Mac
    │
    ▼
Local Model
    │
    ▼
Response

The application does not inherently require your conversations to be sent to a third-party AI provider.

Privacy characteristics ultimately depend on which backend/model/API configuration is being used.

🛠️ Development

Start the frontend in development mode:

npm run dev

Build the application:

npm run build

Preview the production build:

npm run preview
🧪 Development Philosophy

This project started as an experiment to understand how local AI applications work.

The goal is not simply to create another ChatGPT clone.

The goal is to understand the complete stack:

                    ┌───────────────┐
                    │   React UI    │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │   REST API    │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ Model Manager │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ Local Models  │
                    └───────────────┘

The application is being built incrementally to explore:

Local LLM inference
Model lifecycle management
REST APIs
React applications
AI agents
Multiple model orchestration
External API integrations
Local system resource monitoring
📌 Current Status

🟢 Frontend: Working

🟢 Chat UI: Working

🟢 Chat sessions: Working

🟢 FastAPI integration: Working

🟢 Local Qwen integration: Working

🟡 Multi-model support: In progress

🟡 External API integrations: In progress

🔴 Image/video generation: Planned

👨‍💻 Author

Built as a personal exploration into local AI, LLMs, agentic applications, and modern frontend development.

⭐ Project Vision

The ultimate goal is to turn this from a simple local ChatGPT clone into a personal AI workstation:

                    ┌──────────────────────────┐
                    │       LOCAL AI           │
                    │                          │
                    │   💬 Chat                │
                    │   👨‍💻 Coding             │
                    │   🎨 Images              │
                    │   🎬 Video               │
                    │   📊 System Monitor      │
                    │   🌐 External APIs       │
                    │                          │
                    └────────────┬─────────────┘
                                 │
                           Model Manager
                                 │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
                  Qwen       Coder Model   Image Model

One UI. Multiple capabilities. Local-first AI.