# Monday BI Agent 🤖

A **Business Intelligence AI Agent** for [monday.com](https://monday.com), built with **Google Agent Development Kit (ADK)** and powered by **Gemini 2.5 Flash Lite**. The agent connects to your monday.com workspace via the official MCP (Model Context Protocol) server and answers founder-level business questions in plain language.

---

## How It Works

The agent uses a **Sequential (multi-agent) pipeline** made up of two specialised sub-agents:

```
User Query
    │
    ▼
┌──────────────┐      Clarifies which workspace & board the user
│  query_agent │ ───► wants to work with and stores the IDs.
└──────────────┘
    │
    ▼
┌───────────────┐     Uses ReAct reasoning (Think → Act → Observe)
│ extract_agent │ ───► to fetch live data via the monday MCP tools
└───────────────┘     and return a concise BI summary.
    │
    ▼
Business Insight
```

| Agent | Role |
|---|---|
| `query_agent` | Greets the user, lists available workspaces/boards, and captures the user's selection |
| `extract_agent` | Fetches live monday.com data, cleans it, and synthesises actionable business insights |
| `root_agent` | `SequentialAgent` that orchestrates both sub-agents in order |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Agent Framework | [Google ADK](https://google.github.io/adk-docs/) (`google-adk`) |
| LLM | Gemini 2.5 Flash Lite (via Vertex AI) |
| monday.com Integration | [monday.com MCP Server](https://mcp.monday.com/mcp) (Streamable HTTP) |
| Observability | OpenTelemetry (`opentelemetry-instrumentation-google-genai`) |
| Package Manager | [uv](https://github.com/astral-sh/uv) |
| Python | ≥ 3.11 |

---

## Project Structure

```
monday_bi_agent/
├── monday_bi_agent/
│   ├── agent.py                  # Core agent definitions & runner
│   ├── __init__.py
│   ├── .env                      # Environment variables (see setup)
│   └── .agent_engine_config.json # Vertex AI Agent Engine resource config
├── main.py                       # Entry point
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## Setup & Installation

### 1. Clone & Install Dependencies

```bash
git clone <your-repo-url>
cd monday_bi_agent

# Using uv (recommended)
uv sync

# Or using pip
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Edit `monday_bi_agent/.env` with your credentials:

```env
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_CLOUD_LOCATION=global
GOOGLE_GENAI_USE_VERTEXAI=1
your_monday_API_key=your_monday_api_key_here
```

> **Note:** Make sure your Google Cloud project has the **Vertex AI API** enabled and you are authenticated via `gcloud auth application-default login`.

### 3. Get Your monday.com API Key

1. Log in to [monday.com](https://monday.com)
2. Go to **Profile → Developers → My Access Tokens**
3. Copy your personal API token and paste it into the `.env` file

---

## Running the Agent

```bash
# Run with the ADK web UI (recommended for development)
adk web

# Or run directly
python main.py
```

---

## Key Features

- 🔍 **Workspace & Board Discovery** — Automatically lists all available workspaces and boards so the user can pick the right context
- 🧠 **ReAct Reasoning** — The extract agent reasons step-by-step before fetching data, minimising hallucinations
- 🔄 **Retry Logic** — Built-in exponential backoff for rate-limit errors (HTTP 429/500/503/504)
- 💬 **Resumable Sessions** — Conversations can be resumed across sessions via `ResumabilityConfig`
- ☁️ **Vertex AI Agent Engine Ready** — Includes resource config for cloud deployment (`min/max instances`, CPU, memory)

---

## Environment Variables Reference

| Variable | Description |
|---|---|
| `GOOGLE_CLOUD_PROJECT` | Your GCP project ID |
| `GOOGLE_CLOUD_LOCATION` | GCP region (e.g. `global`) |
| `GOOGLE_GENAI_USE_VERTEXAI` | Set to `1` to use Vertex AI instead of AI Studio |
| `your_monday_API_key` | Your monday.com personal API token |

---

## Deployment (Vertex AI Agent Engine)

The `.agent_engine_config.json` file configures the cloud deployment:

```json
{
  "min_instances": 0,
  "max_instances": 1,
  "resource_limits": {
    "cpu": "1",
    "memory": "1Gi"
  }
}
```

Deploy using the ADK CLI:

```bash
adk deploy agent_engine --project=$project_id --region=$region monday_bi_agent agent_engine_config=monday_bi_agent/.agent_engine_config.json
```

---

## License

This project is for personal/internal use. Feel free to adapt it to your needs.
