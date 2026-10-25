# AI-Powered Student Assistant Chatbot

An AI-powered student assistance application built with **Python, Streamlit, LangChain, and Retrieval-Augmented Generation (RAG)**. It helps students ask questions about uploaded study materials and generate personalized study plans.

## Features

- **Document-based Q&A:** Upload supported study documents and ask questions about their contents.
- **RAG pipeline:** Retrieves relevant document context to support grounded responses.
- **AI Study Planner:** Generate a structured study plan based on your subject, current knowledge level, and available study time.
- **LLM integration:** Uses configured Groq and/or Google Gemini models, with fallback behavior where implemented.
- **Streamlit interface:** Simple interactive web application.

## Tech Stack

| Component | Technology |
| --- | --- |
| Language | Python |
| UI | Streamlit |
| LLM orchestration | LangChain |
| Language models | Groq / Google Gemini |
| Document Q&A | Retrieval-Augmented Generation (RAG) |
| Configuration | python-dotenv / environment variables |

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/somasekhar8/Student_Assistant_chatbot.git
cd Student_Assistant_chatbot
```

### 2. Create and activate a virtual environment

Using `uv` on Windows PowerShell:

```powershell
uv venv
.venv\Scripts\Activate.ps1
```

Alternatively, using Python:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the example configuration:

```powershell
Copy-Item .env.example .env
```

Open `.env` and enter the API keys required by your configured models. Check `.env.example` for the exact variable names used by this project. **Never commit `.env` or real API keys to GitHub.**

### 5. Run the application

```bash
streamlit run app.py
```

Open the local URL displayed in your terminal (typically `http://localhost:8501`).

## How It Works

1. Upload a supported study document in the Streamlit application.
2. The application processes its text and prepares it for retrieval.
3. Ask a question; the RAG pipeline retrieves relevant context and passes it to the configured language model.
4. Use the study planner to request a structured plan based on your learning needs.

## Project Structure

```text
student_assistant_chatbot/
├── app.py                 # Streamlit application
├── src/                   # Application modules and AI pipelines
├── test_models/           # Model-related tests or experiments
├── requirements.txt       # Python dependencies
├── .env.example           # Example environment configuration (no secrets)
├── .gitignore
└── README.md
```

## Security

- Store API keys in a local `.env` file or your deployment platform's secret manager.
- Keep `.env`, virtual environments, and cache files out of version control.
- Use placeholder values only in `.env.example`.

## Future Improvements

- Add automated tests for document ingestion and question answering.
- Expand supported document formats.
- Add deployment instructions and a live demo link once deployed.

## License

No license has been specified yet. Add a `LICENSE` file if you want to define reuse permissions.
