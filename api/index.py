import os
import sys
import datetime
from flask import Flask, render_template, request, jsonify

# Set root directory for templates
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
KNOWLEDGE_FILE = os.path.join(BASE_DIR, "knowledge.txt")

app = Flask(__name__, template_folder=TEMPLATE_DIR)

# Load knowledge lines
knowledge_content = ""
if os.path.exists(KNOWLEDGE_FILE):
    with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as f:
        knowledge_content = f.read()
elif os.path.exists("knowledge.txt"):
    with open("knowledge.txt", "r", encoding="utf-8") as f:
        knowledge_content = f.read()

def query_rag(user_query: str) -> str:
    now = datetime.datetime.now()
    current_time_str = now.strftime("%I:%M %p")
    current_date_str = now.strftime("%A, %B %d, %Y")

    q_lower = user_query.strip().lower()

    # Instant response for common greetings & time
    if q_lower in ["hi", "hello", "hey", "hola", "namaste", "hi there", "hello there"]:
        return f"Hello! Welcome to the Intelligence Workspace. How can I help you today?"
    
    if any(k in q_lower for k in ["what time", "current time", "time now", "tell me the time"]):
        return f"The current local time is {current_time_str} ({current_date_str})."
        
    if any(k in q_lower for k in ["what date", "today's date", "current date", "what is today"]):
        return f"Today is {current_date_str}."

    # Try local Ollama if available
    try:
        from langchain_ollama import OllamaLLM
        llm = OllamaLLM(model="llama3.2:3b", temperature=0.3, timeout=10)
        
        prompt = f"""You are a smart, polite, and helpful AI assistant for the Intelligence Workspace.

Real-Time Environmental Context:
- Current Local Time: {current_time_str}
- Today's Date: {current_date_str}

Knowledge Base Document:
{knowledge_content}

Instructions:
1. For general greetings or time/date questions, answer naturally and politely.
2. For questions specifically about the project, creator, or hardware specifications, answer accurately using the Knowledge Base Document.
3. If not in the document, politely reply: "I don't have that specific information in the current knowledge document."

User Message: {user_query}
Assistant Response:"""
        
        res = llm.invoke(prompt)
        return res.strip()
    except Exception:
        # Fallback response if Ollama is not accessible on cloud/Vercel serverless
        if "who created" in q_lower or "creator" in q_lower or "author" in q_lower:
            return "This project was created by Uday Maji as a high-performance offline local RAG system."
        elif "hardware" in q_lower or "ram" in q_lower or "spec" in q_lower:
            return "Supported Hardware: Runs smoothly on 8GB to 16GB RAM setups with quantized 3B models (Llama 3.2 / Qwen 2.5)."
        elif "what is this project" in q_lower or "project" in q_lower or "about" in q_lower:
            return "Project Name: Local Core RAG (Antigravity Workspace). Architecture: Completely offline RAG system utilizing Ollama, LangChain, and fast vectorized embeddings."
        else:
            return f"Received: '{user_query}'. (Running in serverless edge mode. For full local LLM inference, connect to a running local Ollama instance)."

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
    return jsonify({"status": "ready", "vercel_ready": True})

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
    app.run(host="0.0.0.0", port=5000, debug=False)
