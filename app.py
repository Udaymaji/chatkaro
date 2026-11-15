import os
import sys
import datetime
from flask import Flask, render_template, request, jsonify

# Current directory where app.py resides
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
KNOWLEDGE_FILE = os.path.join(BASE_DIR, "knowledge.txt")

app = Flask(__name__, template_folder=TEMPLATE_DIR)

# Load knowledge file
knowledge_content = ""
if os.path.exists(KNOWLEDGE_FILE):
    try:
        with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as f:
            knowledge_content = f.read()
    except Exception:
        pass

def query_rag(user_query: str) -> str:
    now = datetime.datetime.now()
    current_time_str = now.strftime("%I:%M %p")
    current_date_str = now.strftime("%A, %B %d, %Y")

    q_lower = user_query.strip().lower()

    # Instant response for greetings
    if q_lower in ["hi", "hello", "hey", "hola", "namaste", "hi there", "hello there"]:
        return "Hello! Welcome to the Intelligence Workspace. How can I help you today?"

    # Instant response for time & date
    if any(k in q_lower for k in ["what time", "current time", "time now", "tell me the time"]):
        return f"The current local time is {current_time_str} ({current_date_str})."
        
    if any(k in q_lower for k in ["what date", "today's date", "current date", "what is today"]):
        return f"Today is {current_date_str}."

    # Specific knowledge questions
    if "who created" in q_lower or "creator" in q_lower or "author" in q_lower:
        return "This project was created by Uday Maji as a high-performance offline local RAG system."
    elif "hardware" in q_lower or "ram" in q_lower or "spec" in q_lower:
        return "Supported Hardware: Runs smoothly on 8GB to 16GB RAM setups with quantized 3B models (Llama 3.2 / Qwen 2.5)."
    elif "what is this project" in q_lower or "project" in q_lower or "about" in q_lower:
        return "Project Name: Local Core RAG (Antigravity Workspace). Architecture: Completely offline RAG system using Ollama, ChromaDB, and LangChain."
    else:
        return f"I received your inquiry: '{user_query}'. For deep local language model inferences, run Ollama locally or connect an LLM endpoint."

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
