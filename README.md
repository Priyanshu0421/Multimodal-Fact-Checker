# 🧠 Multimodal Fact-Checker

An AI-powered system that extracts and verifies factual claims from **text** and **images**, helping users detect misinformation in real time.

## 🚀 Features

- ✅ **Claim Extraction** using LLaMA 3.2 via Ollama
- 🔍 **Claim Verification** using Wikipedia and Transformer models
- 📊 **Credibility Scoring** (0–100 scale with source explanations)
- 🌐 FastAPI-powered **REST API**
- 📦 Docker-ready for easy deployment

## 🧱 Architecture

User Input (Text/Image)
↓
Claim Extractor (LLaMA/Ollama)
↓
Claim Verifier (Wikipedia + Transformers)
↓
Credibility Score + Source URLs

markdown
Copy
Edit

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI, asyncio
- **AI Models**: Ollama (LLaMA 3.2), HuggingFace Transformers
- **APIs**: Wikipedia API
- **Deployment**: Docker

## 📦 Installation

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
cd YOUR-REPO-NAME
pip install -r requirements.txt
🧪 Running Locally
Start the FastAPI server:

bash
Copy
Edit
uvicorn main:app --reload
Example endpoint:

http
Copy
Edit
POST /analyze/text
{
  "text": "Is banana a fruit or a vegetable?"
}
📋 Sample Response
json
Copy
Edit
{
  "original_text": "Is banana a fruit or a vegetable?",
  "claims": [
    {
      "text": "Banana is a fruit",
      "confidence": 0.98,
      "credibility_score": 94,
      "sources": ["https://en.wikipedia.org/wiki/Banana"]
    }
  ]
}
📈 Future Improvements
🎥 Video-based claim extraction

🌍 Integration with news APIs for cross-verification

🧩 Browser extension for real-time checks

🧑‍💻 Author
Priyanshu Mishra — GitHub

⚠️ This is a research prototype and not a production-grade fact-checking tool.
