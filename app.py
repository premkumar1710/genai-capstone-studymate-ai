import ast
import io
import json
import math
import re
from typing import List, Dict

import numpy as np
import requests
import streamlit as st
from pypdf import PdfReader
from docx import Document

st.set_page_config(page_title="StudyMate AI | GenAI Capstone", page_icon="🧠", layout="wide")

# ---------- Ollama client ----------
def ollama_chat(base_url: str, model: str, messages: list, temperature: float = 0.3) -> str:
    url = base_url.rstrip("/") + "/api/chat"
    payload = {"model": model, "messages": messages, "stream": False,
               "options": {"temperature": temperature}}
    response = requests.post(url, json=payload, timeout=180)
    response.raise_for_status()
    return response.json().get("message", {}).get("content", "")


def ollama_embed(base_url: str, model: str, text: str):
    response = requests.post(base_url.rstrip("/") + "/api/embeddings",
                             json={"model": model, "prompt": text}, timeout=120)
    response.raise_for_status()
    return response.json()["embedding"]

# ---------- Document processing / RAG ----------
def read_upload(upload) -> str:
    name = upload.name.lower()
    raw = upload.getvalue()
    if name.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(raw))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if name.endswith(".docx"):
        doc = Document(io.BytesIO(raw))
        return "\n".join(p.text for p in doc.paragraphs)
    return raw.decode("utf-8", errors="ignore")


def split_chunks(text: str, chunk_size: int = 850, overlap: int = 120) -> List[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    chunks, start = [], 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        if end < len(text):
            boundary = text.rfind(". ", start, end)
            if boundary > start + chunk_size // 2:
                end = boundary + 1
        chunks.append(text[start:end].strip())
        if end == len(text):
            break
        start = max(start + 1, end - overlap)
    return chunks


def build_index(chunks, base_url, embedding_model):
    vectors = []
    for chunk in chunks:
        vectors.append(ollama_embed(base_url, embedding_model, chunk))
    matrix = np.asarray(vectors, dtype=np.float32)
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    matrix = matrix / np.maximum(norms, 1e-12)
    return matrix


def retrieve(question, chunks, matrix, base_url, embedding_model, top_k=4):
    q = np.asarray(ollama_embed(base_url, embedding_model, question), dtype=np.float32)
    q = q / max(float(np.linalg.norm(q)), 1e-12)
    scores = matrix @ q
    indices = np.argsort(scores)[::-1][:top_k]
    return [(chunks[int(i)], float(scores[int(i)])) for i in indices]

# ---------- Safe calculator tool ----------
_ALLOWED = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant, ast.Add, ast.Sub,
            ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow, ast.USub, ast.UAdd,
            ast.Load, ast.Call, ast.Name)
_ALLOWED_FUNCS = {"sqrt": math.sqrt, "abs": abs, "round": round, "ceil": math.ceil, "floor": math.floor}

def calculate(expression: str):
    tree = ast.parse(expression, mode="eval")
    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED):
            raise ValueError("Only basic arithmetic and sqrt/abs/round/ceil/floor are allowed.")
        if isinstance(node, ast.Call) and (not isinstance(node.func, ast.Name) or node.func.id not in _ALLOWED_FUNCS):
            raise ValueError("Unsupported calculator function.")
        if isinstance(node, ast.Name) and node.id not in _ALLOWED_FUNCS:
            raise ValueError("Unsupported name.")
    return eval(compile(tree, "<calculator>", "eval"), {"__builtins__": {}}, _ALLOWED_FUNCS)

# ---------- Session state ----------
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! I'm StudyMate AI. Ask me anything, or upload a document and switch on Document RAG to ask questions grounded in your files."}]
if "chunks" not in st.session_state:
    st.session_state.chunks = []
if "vectors" not in st.session_state:
    st.session_state.vectors = None
if "doc_names" not in st.session_state:
    st.session_state.doc_names = []

# ---------- Sidebar ----------
st.sidebar.title("🧠 StudyMate AI")
st.sidebar.caption("GenAI Capstone · Local-first · Powered by Ollama")
base_url = st.sidebar.text_input("Ollama URL", "http://localhost:11434")
model = st.sidebar.text_input("Chat model", "llama3.2")
embedding_model = st.sidebar.text_input("Embedding model", "nomic-embed-text")
temperature = st.sidebar.slider("Creativity", 0.0, 1.0, 0.3, 0.1)
mode = st.sidebar.selectbox("Assistant mode", ["General Chat", "Document RAG", "Study Coach", "Research Planner"])
st.sidebar.divider()
st.sidebar.subheader("📚 Add knowledge")
uploads = st.sidebar.file_uploader("Upload PDF, DOCX, or TXT", type=["pdf", "docx", "txt"], accept_multiple_files=True)
if st.sidebar.button("Build / Refresh RAG Index", use_container_width=True, disabled=not uploads):
    try:
        all_chunks, names = [], []
        for file in uploads:
            content = read_upload(file)
            pieces = split_chunks(content)
            all_chunks.extend(pieces)
            names.append(file.name)
        if not all_chunks:
            st.sidebar.error("No readable text found in the uploaded files.")
        else:
            with st.spinner(f"Creating embeddings for {len(all_chunks)} text chunks..."):
                vectors = build_index(all_chunks, base_url, embedding_model)
            st.session_state.chunks = all_chunks
            st.session_state.vectors = vectors
            st.session_state.doc_names = names
            st.sidebar.success(f"Indexed {len(all_chunks)} chunks from {len(names)} file(s).")
    except requests.exceptions.ConnectionError:
        st.sidebar.error("Cannot reach Ollama. Start Ollama and pull the embedding model first.")
    except Exception as exc:
        st.sidebar.error(f"Indexing failed: {exc}")

if st.session_state.doc_names:
    st.sidebar.success("Indexed: " + ", ".join(st.session_state.doc_names))
    if st.sidebar.button("Clear document index", use_container_width=True):
        st.session_state.chunks, st.session_state.vectors, st.session_state.doc_names = [], None, []
        st.rerun()
if st.sidebar.button("Clear chat", use_container_width=True):
    st.session_state.messages = [{"role": "assistant", "content": "Chat cleared. What would you like to work on?"}]
    st.rerun()
st.sidebar.divider()
st.sidebar.caption("Tools: calculator · document retrieval · study-plan generation · quiz generation")

# ---------- Main interface ----------
st.title("StudyMate AI")
st.markdown("Your local AI study, document and research assistant")
col1, col2, col3 = st.columns(3)
col1.metric("Knowledge files", len(st.session_state.doc_names))
col2.metric("RAG chunks", len(st.session_state.chunks))
col3.metric("Active mode", mode)

with st.expander("✨ Quick prompts", expanded=False):
    examples = ["Explain SDLC and STLC with a simple example.",
                "Create a 7-day study plan for Python and SQL.",
                "Generate 10 multiple-choice questions about machine learning.",
                "Help me plan research on retrieval-augmented generation."]
    cols = st.columns(2)
    for i, prompt in enumerate(examples):
        if cols[i % 2].button(prompt, key=f"quick_{i}", use_container_width=True):
            st.session_state.pending_prompt = prompt

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask StudyMate AI...")
if "pending_prompt" in st.session_state:
    prompt = st.session_state.pop("pending_prompt")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        try:
            answer = ""
            # Lightweight tool router / agent behaviour
            calc_match = re.search(r"(?:calculate|compute)\s+(.+)$", prompt, re.I)
            if calc_match:
                try:
                    result = calculate(calc_match.group(1).strip().rstrip("?"))
                    answer = f"**Calculator tool result:** `{result}`"
                except Exception:
                    answer = "I couldn't safely evaluate that expression. Try something like `calculate (25 * 4) / 2`."
            elif mode == "Document RAG":
                if st.session_state.vectors is None:
                    answer = "Please upload PDF/DOCX/TXT files and click **Build / Refresh RAG Index** in the sidebar first."
                else:
                    with st.spinner("Searching your documents and generating an answer..."):
                        hits = retrieve(prompt, st.session_state.chunks, st.session_state.vectors,
                                        base_url, embedding_model)
                        context = "\n\n".join(f"[Source chunk {i+1} | relevance {score:.3f}] {chunk}" for i, (chunk, score) in enumerate(hits))
                        answer = ollama_chat(base_url, model, [
                            {"role": "system", "content": "You are a careful document assistant. Answer using the supplied context. If the answer is not present, say that the uploaded documents do not provide enough information. Do not invent citations. Refer to source chunk numbers when useful.\n\nCONTEXT:\n" + context},
                            {"role": "user", "content": prompt}], temperature)
                        answer += "\n\n---\n**Retrieved context:** " + ", ".join(f"Chunk {i+1} ({score:.2f})" for i, (_, score) in enumerate(hits))
            else:
                system = "You are StudyMate AI, a helpful and accurate learning assistant. Explain concepts in simple English, use examples, and structure answers clearly."
                if mode == "Study Coach":
                    system += " Act as a study coach. Break topics into manageable steps, include revision and practice tasks, and adapt to a beginner."
                elif mode == "Research Planner":
                    system += " Act as a research planning agent. Help define the problem, objectives, methodology, tools, evaluation metrics, risks and deliverables. Never fabricate academic references."
                history = [{"role": "system", "content": system}] + st.session_state.messages[-12:]
                with st.spinner("Thinking with Ollama..."):
                    answer = ollama_chat(base_url, model, history, temperature)
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except requests.exceptions.ConnectionError:
            answer = "**Ollama connection failed.** Open Ollama, then run `ollama pull llama3.2` and `ollama pull nomic-embed-text` in your terminal. Check the Ollama URL in the sidebar."
            st.error(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except requests.exceptions.HTTPError as exc:
            answer = f"Ollama returned an error: `{exc}`. Confirm that the selected model is installed (`ollama list`)."
            st.error(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as exc:
            answer = f"Something went wrong: `{exc}`"
            st.error(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})

st.caption("Privacy note: documents and prompts are processed through your configured Ollama server. This app does not send them to OpenAI or another hosted LLM provider.")
