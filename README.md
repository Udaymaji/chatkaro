# Chatkaro - Intelligence Workspace

A high-end, minimal web application for offline & edge RAG (Retrieval-Augmented Generation).

## Features
- **Modern Unified Frontend:** High-end glassmorphism design with single-page tabs (Workspace, About, Demo Account).
- **Conversational AI:** Answers greetings ("hi", "hello"), real-time dynamic time/date queries, and domain-specific knowledge questions.
- **Vercel Serverless Ready:** Deployable directly to Vercel via `@vercel/python` serverless runtime.
- **Local RAG Integration:** Powered by local Ollama (`llama3.2:3b` and `nomic-embed-text`) with instant retrieval fallback.

## Author
**Uday Maji**

## Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the local application
python api/index.py
# or
python local-rag-antigravity/rag_bot.py
```
Open [http://localhost:5000](http://localhost:5000) in your browser.

## Deployment on Vercel
1. Push this repository to GitHub.
2. Import the repository in [Vercel](https://vercel.com).
3. Vercel will automatically detect `vercel.json` and deploy `api/index.py`.
