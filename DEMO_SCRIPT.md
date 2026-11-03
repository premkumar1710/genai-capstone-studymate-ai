# 3–5 Minute Demo Script

1. **Introduction (30 sec):** “StudyMate AI is a local-first GenAI assistant for learning, document understanding and research planning. It uses Ollama, prompt engineering, RAG and tools.”
2. **General chat (40 sec):** Ask “Explain SDLC and STLC with a simple example.” Show the response.
3. **Prompt engineering (40 sec):** Select Study Coach and ask for a 7-day Python and SQL plan. Explain how the system prompt changes the assistant's behaviour.
4. **Tool use (30 sec):** Ask “Calculate (125 * 8) / 5”. Explain that the router sends the expression to the restricted calculator tool.
5. **RAG (90 sec):** Select Document RAG, upload a text-based PDF or DOCX, build the index, then ask a question whose answer is present in the document. Explain parsing, chunking, embeddings, cosine retrieval and context-grounded generation.
6. **Research agent mode (30 sec):** Select Research Planner and ask it to plan a small AI project.
7. **Conclusion (20 sec):** Mention local inference, no OpenAI key, GitHub repository, and future improvements such as persistent vector storage and page-level citations.

## Suggested viva questions

- **What is an LLM?** A model trained on large amounts of text to understand and generate language.
- **What is prompt engineering?** Designing instructions and context to guide an LLM toward a useful response.
- **What is RAG?** Retrieval-Augmented Generation retrieves relevant external information and provides it to an LLM as context before generation.
- **Why chunk documents?** Smaller chunks improve retrieval granularity and fit within the model's context window.
- **What are embeddings?** Numeric vectors that represent semantic meaning and allow similarity search.
- **Why cosine similarity?** It compares the direction of vectors to estimate semantic similarity.
- **What is an agent/tool?** An agent-like workflow chooses a tool for a task; a tool performs a bounded action such as calculation or retrieval.
- **Why Ollama?** It makes it possible to run supported LLMs locally without requiring a hosted OpenAI API key.
