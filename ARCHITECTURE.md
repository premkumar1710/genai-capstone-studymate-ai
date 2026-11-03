# Architecture and Design Notes

## High-level flow

1. The user selects a mode and submits a prompt through Streamlit.
2. A lightweight router checks whether the request is a calculator action, a document-grounded question, or a normal assistant request.
3. General chat / Study Coach / Research Planner requests are sent to the configured Ollama chat model with a mode-specific system prompt and recent conversation history.
4. Document RAG extracts text from uploaded PDF, DOCX or TXT files, splits it into overlapping chunks, creates embeddings using Ollama's embedding endpoint, and stores normalized vectors in session memory.
5. For a document question, the app embeds the query, ranks chunks using cosine similarity, and supplies the top chunks to the LLM as context. The system prompt instructs the model to state when the documents do not contain the answer.
6. Calculator requests are evaluated by a restricted AST evaluator that allows basic arithmetic and a small set of math functions. Arbitrary Python execution is not exposed.

## GenAI concepts demonstrated

| Concept | Implementation |
|---|---|
| LLM integration | Ollama `/api/chat` |
| Prompt engineering | Mode-specific system prompts and grounded-answer instructions |
| RAG | Document parsing, chunking, embeddings, cosine retrieval and context injection |
| Tool use | Calculator tool and document retrieval tool |
| Agent behaviour | Intent routing to the appropriate tool or assistant mode |
| User interface | Streamlit chat interface, file uploader and settings |

## Main components

- `ollama_chat`: sends chat messages to the local Ollama model.
- `ollama_embed`: requests vector embeddings from Ollama.
- `read_upload`: extracts text from PDF, DOCX or TXT.
- `split_chunks`: creates overlapping text chunks.
- `build_index`: embeds chunks and normalizes vectors.
- `retrieve`: ranks chunks by cosine similarity to the query.
- `calculate`: evaluates only an allowlisted arithmetic AST.

## Data and privacy

Uploaded file content is processed by the app and passed to the configured Ollama service for embeddings. Retrieved context and prompts are passed to Ollama for generation. No hosted OpenAI API is used by this code. If Ollama is configured on another machine, that machine receives the data.
