import os
import sys
import pickle
import datetime
import numpy as np
from flask import Flask, render_template, request, jsonify
from langchain_ollama import OllamaEmbeddings, OllamaLLM

app = Flask(__name__)

KNOWLEDGE_FILE = "knowledge.txt"
CACHE_FILE = "embeddings_cache.pkl"

embeddings_model = OllamaEmbeddings(model="nomic-embed-text")
llm = OllamaLLM(model="llama3.2:3b", temperature=0.3)

chunks = []
chunk_vectors = []

def cosine_similarity(v1, v2):
    dot = np.dot(v1, v2)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(dot / (norm1 * norm2))

def init_vector_store():
    global chunks, chunk_vectors
    if not os.path.exists(KNOWLEDGE_FILE):
        print(f"Error: {KNOWLEDGE_FILE} not found!", flush=True)
        sys.exit(1)

    with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as f:
        text = f.read()

    lines = [line.strip().lstrip("\ufeff") for line in text.splitlines() if line.strip()]

    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "rb") as f:
                data = pickle.load(f)
                if data.get("raw_text") == text:
                    chunks = data["chunks"]
                    chunk_vectors = data["vectors"]
                    print(f"Loaded {len(chunks)} knowledge vectors from cache.", flush=True)
                    return
        except Exception:
            pass

    print("Indexing knowledge document...", flush=True)
    chunks = lines
    chunk_vectors = [np.array(embeddings_model.embed_query(c), dtype=np.float32) for c in chunks]

    with open(CACHE_FILE, "wb") as f:
        pickle.dump({"raw_text": text, "chunks": chunks, "vectors": chunk_vectors}, f)

    print(f"Successfully indexed and cached {len(chunks)} chunks.", flush=True)

def retrieve_context(query: str, top_k: int = 3):
    if not chunks:
        return []
    q_vec = np.array(embeddings_model.embed_query(query), dtype=np.float32)
    scores = []
    for c, v in zip(chunks, chunk_vectors):
        sim = cosine_similarity(q_vec, v)
        scores.append((sim, c))
    scores.sort(key=lambda x: x[0], reverse=True)
    return [c for _, c in scores[:top_k]]

def query_rag(user_query: str) -> str:
    now = datetime.datetime.now()
    current_time_str = now.strftime("%I:%M %p")
    current_date_str = now.strftime("%A, %B %d, %Y")

    context_chunks = retrieve_context(user_query, top_k=3)
    context_str = "\n".join(context_chunks)

    prompt = f"""You are a smart, polite, and helpful AI assistant for the Intelligence Workspace.

Real-Time Environmental Context:
- Current Local Time: {current_time_str}
- Today's Date: {current_date_str}

Knowledge Base Document:
{context_str}

Instructions:
1. For general conversation (such as "hi", "hello", "how are you", greetings, small talk, questions about the current time or date), answer naturally, warmly, and politely.
2. For questions specifically asking about the project, architecture, creator, specifications, or documents, answer accurately using the Knowledge Base Document above.
3. If the user asks an obscure factual question about specific project details not in the document and outside general knowledge, politely state: "I don't have that specific information in the current knowledge document."
4. Keep answers clean, direct, and well-formatted.

User Message: {user_query}

Assistant Response:"""

    try:
        response = llm.invoke(prompt)
        return response.strip()
    except Exception as e:
        print(f"LLM Error: {e}", flush=True)
        return "An error occurred while generating the response. Please check local model connectivity."

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    query = data.get("query", "").strip()
    if not query:
        return jsonify({"error": "Query cannot be empty"}), 400

    answer = query_rag(query)
    return jsonify({"answer": answer})

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ready", "chunks_indexed": len(chunks)})

@app.route("/api/auth/demo-login", methods=["POST"])
def demo_login():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()
    
    if not email or not password:
        return jsonify({"success": False, "message": "Email and password required."}), 400

    name = email.split("@")[0].capitalize() if "@" in email else "User"
    return jsonify({
        "success": True,
        "message": "Authenticated",
        "user": {
            "name": name,
            "email": email,
            "role": "Administrator"
        }
    })

if __name__ == "__main__":
    init_vector_store()
    print("\n=======================================================")
    print("  Unified Webapp Online: http://localhost:5000")
    print("=======================================================\n", flush=True)
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
