# AI Instructions Generator - Reverse Engineering Human Expertise

A breakthrough system that automatically generates AI instructions by analyzing how human experts successfully extract information from legal documents. Instead of manually writing extraction rules, this system studies successful human decisions and reverse engineers them into reusable, precise AI instructions.

## 🎯 Key Features
- Reverse Engineering Intelligence - Learns from human success patterns
- 8-Section Instruction Format - Comprehensive structured approach
- Semantic Gap Analysis - Advanced failure diagnosis and refinement
- Cross-Validation Framework - Ensures instruction quality preservation
- LangGraph Workflow Engine - Sophisticated state management and routing
- Production Web Interface - Gradio/Streamlit frontend with Flask API backend

## 🔧 Technology Stack
- Backend: Flask, LangChain, LangGraph, PostgreSQL, Redis
- Frontend: Gradio/Streamlit with real-time progress tracking
- AI Models: OpenAI O3 (generation), GPT-4 (extraction/evaluation)
- Infrastructure: Docker, Docker Compose, multi-stage containerization

## 🚀 Use Cases
- Legal document processing and OCG (Outside Counsel Guidelines) analysis
- Expert knowledge capture and democratization
- AI instruction quality assurance and refinement
- Legal compliance automation and document intelligence

## 📦 Project Structure
```
ai_instructions_app/
├── api/                 # Flask blueprints for workflow and health endpoints
├── config/              # Application and logging configuration
├── models/              # SQLAlchemy models and database helpers
├── services/            # Workflow orchestration and business logic
├── utils/               # Shared helpers for validation and file handling
├── workflow/            # LangGraph state definitions and structured models
└── tests/               # Pytest-based automated tests
```

## ⚙️ Getting Started

### 1. Install Dependencies
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

### 2. Configure Environment
Copy `.env.example` to `.env` and populate the values for your environment (database URLs, API keys, etc.).

### 3. Run the Application
```bash
flask --app ai_instructions_app.app run --debug
```

### 4. Execute Tests
```bash
pytest
```

## 🐳 Docker

Build and run the full stack with PostgreSQL and Redis using Docker Compose:
```bash
docker compose up --build
```
The web service is available on `http://localhost:5000`.

## 🛠️ Workflow Fidelity

The `WebWorkflowService` in `ai_instructions_app/services/workflow_service.py` mirrors the exact LangGraph workflow structure defined in the original system, including:
- Identical node definitions and routing logic (`route_after_evaluation`, `route_after_verification`)
- Structured output models for each workflow stage
- Memory checkpointing via LangGraph's `MemorySaver`
- Placeholder node implementations ready for integration with the original prompt logic and LLM calls

## 📈 Next Steps
- Integrate the original prompt templates for each node
- Implement LangChain calls to O3 and GPT-4 per the specification
- Extend the frontend with Gradio or Streamlit for interactive monitoring
- Add persistence via the SQLAlchemy models and Redis-based caching

Perfect for legal professionals, AI researchers, and organizations seeking to automate expert-level document analysis while maintaining human-quality accuracy.
