# StudyMate AI — GenAI Capstone Project

A local-first Generative AI study, document and research assistant built with **Streamlit + Ollama**. It demonstrates prompt engineering, local LLM integration, Retrieval-Augmented Generation (RAG), and a lightweight tool-using agent.

## Features

- **Local LLM chat:** connect to Ollama; no OpenAI API key or paid LLM API required.
- **Prompt-engineered modes:** General Chat, Study Coach and Research Planner use different system instructions.
- **RAG document assistant:** upload PDF, DOCX or TXT files, split them into overlapping chunks, create Ollama embeddings, retrieve relevant chunks by cosine similarity, and answer using retrieved context.
- **Tool-using agent:** routes calculation requests to a restricted Python AST calculator; document questions invoke retrieval; other requests use the selected assistant mode.
- **Study productivity:** generate study plans, explanations, revision tasks, quizzes and research plans.
- **Privacy-conscious local workflow:** prompts and documents are sent to the Ollama server configured by the user, not to OpenAI.

## Requirements

- Python 3.10 or newer
- Ollama installed and running
- At least one Ollama chat model (example: `llama3.2`)
- Embedding model `nomic-embed-text` for RAG

## Run locally (Windows)

1. Install Ollama from the official website: https://ollama.com/download
2. Open Command Prompt or PowerShell and download the models:

   ```bash
   ollama pull llama3.2
   ollama pull nomic-embed-text
   ```

3. Extract this project folder and open a terminal inside it.
4. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

5. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

6. Start the application:

   ```bash
   streamlit run app.py
   ```

7. The app opens in your browser, usually at `http://localhost:8501`.
8. In the sidebar, keep Ollama URL as `http://localhost:11434` and model as `llama3.2` (or select a model you downloaded).
9. For RAG: select **Document RAG**, upload one or more PDF/DOCX/TXT files, and click **Build / Refresh RAG Index**. Then ask questions about those files.

## Try these prompts

- `Explain SDLC and STLC with a simple example.`
- `Create a 7-day study plan for Python and SQL.`
- `Generate 10 multiple-choice questions about machine learning, with answers.`
- `Calculate (125 * 8) / 5`
- Switch to **Document RAG** and ask: `Summarize the main objective of this document.`
- Switch to **Research Planner** and ask: `Plan a mini project to compare RAG and normal LLM chat.`

## Architecture

```text
                 ┌────────────────────────────┐
                 │       Streamlit UI         │
                 │ Chat · Modes · File Upload │
                 └─────────────┬──────────────┘
                               │
                    ┌──────────▼──────────┐
                    │ Prompt / Tool Router│
                    └──────┬────────┬─────┘
                           │        │
              ┌────────────▼─┐   ┌──▼────────────────┐
              │ Ollama Chat  │   │ RAG Pipeline      │
              │ LLM + Prompts│   │ Parse → Chunk     │
              └──────────────┘   │ → Embed → Retrieve│
                                 └────────┬───────────┘
                                          │
                                  ┌───────▼────────┐
                                  │ Ollama Embedding│
                                  │ + Cosine Search │
                                  └────────────────┘

      Calculator tool ───────────► Restricted AST evaluator
```

## Project structure

```text
studymate-ai/
├── app.py                 # Streamlit app, Ollama client, RAG and tools
├── requirements.txt       # Python dependencies
├── README.md              # Setup, usage and architecture
├── ARCHITECTURE.md        # Architecture and design notes
├── DEMO_SCRIPT.md         # Suggested project demonstration
├── .gitignore
└── architecture.svg       # Architecture diagram for report/PPT
```

## GitHub submission

Create a new public GitHub repository named `studymate-ai-genai-capstone`, then upload the contents of this folder. Do not upload private documents, API keys, passwords, or your virtual environment.

## Live deployment note

This project is designed for local Ollama inference. Streamlit Community Cloud does not automatically have access to Ollama running on your personal computer. For a public demo, deploy the Streamlit UI to a server that can reach a secured Ollama instance, or use a secure private tunnel for a temporary demonstration. Do not expose an unauthenticated Ollama port to the public internet.

## Limitations / future improvements

- Current document index is held in Streamlit session memory and must be rebuilt after a fresh session.
- PDF extraction works best with text-based PDFs; scanned PDFs need OCR.
- Add persistent vector storage, source/page-level citations, authentication, tests and deployment configuration for a production release.
- The agent uses a simple transparent router rather than autonomous multi-step planning; this keeps tool execution predictable and safe.

## License

MIT — add a `LICENSE` file if you choose to publish this project under the MIT license.
