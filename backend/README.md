# ⚙️ Local ChatGPT — Backend

> A FastAPI-based backend for running local AI models, exposing them through REST APIs, and integrating external services.

This is the backend component of the **Local ChatGPT** project.

The backend acts as the bridge between the React frontend, locally hosted AI models, system resources, and external APIs.

---

# 🧠 What This Backend Does

The backend currently provides APIs for:

- 🤖 Local LLM inference
- 💬 Chat generation
- 🧠 Local model management
- 🔄 Model loading and unloading
- 🌐 External API integration through RapidAPI
- 💼 Job search data retrieval
- 📊 Future system/resource monitoring

The architecture is designed to support multiple AI models while keeping only the required model loaded in memory.

---

# 🏗️ Architecture

```text
                         ┌─────────────────────┐
                         │     React App       │
                         │      Frontend       │
                         └──────────┬──────────┘
                                    │
                                    │ HTTP / REST
                                    ▼
                         ┌─────────────────────┐
                         │       FastAPI       │
                         │       Backend       │
                         └──────────┬──────────┘
                                    │
                 ┌──────────────────┼──────────────────┐
                 │                  │                  │
                 ▼                  ▼                  ▼
          ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
          │   Model     │    │   External  │    │   System    │
          │   Manager   │    │   Services   │    │   Services  │
          └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
                 │                  │                  │
                 ▼                  ▼                  ▼
             Local LLM          RapidAPI             macOS
               Qwen              Services          Resources


🚀 Getting Started
Prerequisites

Recommended environment:

macOS
Apple Silicon Mac
Python 3.x
pip
Virtual environment
Local AI model
RapidAPI account (only required for external API integrations)
1. Clone the Repository
git clone <your-repository-url>

Navigate to the backend:

cd backend
2. Create a Virtual Environment
python3 -m venv venv

Activate it:

source venv/bin/activate

You should see something similar to:

(venv)

in your terminal.

3. Install Dependencies
pip install -r requirements.txt

If dependencies have changed:

pip freeze > requirements.txt
4. Configure Environment Variables

Create:

.env

Example:

RAPIDAPI_KEY=your_key_here
RAPIDAPI_HOST=linkedin-job-search-api.p.rapidapi.com
5. Start FastAPI

Run:

uvicorn main:app --reload

The backend will normally be available at:

http://localhost:8000
6. Open API Documentation

Open:

http://localhost:8000/docs

You can test the APIs directly from the Swagger interface.          