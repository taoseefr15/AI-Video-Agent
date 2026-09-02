🌌 NEXUS.AI — Media Intelligence

AI-powered Video & Meeting Assistant that transforms YouTube videos or uploaded recordings into searchable, structured meeting intelligence.

NEXUS.AI processes video/audio content through a speech-to-text pipeline, generates an AI summary and meeting insights, and builds a Retrieval-Augmented Generation (RAG) interface so users can ask questions grounded in the transcript.

✨ What It Does

NEXUS.AI supports two input modes:

🔗 YouTube URL

📁 Local video/audio upload

After processing, the application provides:

📝 AI-generated meeting summary

📌 Automatically generated meeting title

✅ Action items

🔑 Key decisions

❓ Open questions

💬 Transcript-grounded conversational Q&A using RAG

🌐 English and Hinglish processing modes

🎨 Premium Streamlit interface for interactive analysis

The Streamlit frontend is wired to the backend through run_pipeline() and ask_question(). The pipeline processes the source, transcribes it, generates the title and summary, extracts structured insights, and creates a RAG chain over the transcript.

🏗️ Architecture

                     ┌──────────────────────┐
                     │       User           │
                     └──────────┬───────────┘
                                │
                    YouTube URL / Upload File
                                │
                                ▼
                     ┌──────────────────────┐
                     │   Streamlit UI       │
                     │      app.py          │
                     └──────────┬───────────┘
                                │
                                ▼
                     ┌──────────────────────┐
                     │  Input Processing    │
                     │  audio_processor     │
                     └──────────┬───────────┘
                                │
                                ▼
                     ┌──────────────────────┐
                     │ Speech-to-Text       │
                     │ Local Whisper /      │
                     │ Sarvam STT           │
                     └──────────┬───────────┘
                                │
                                ▼
                     ┌──────────────────────┐
                     │     Transcript       │
                     └──────────┬───────────┘
                                │
              ┌─────────────────┼──────────────────┐
              │                 │                  │
              ▼                 ▼                  ▼
       ┌────────────┐    ┌─────────────┐    ┌─────────────┐
       │ Summary &  │    │ Structured  │    │    RAG      │
       │ Title      │    │ Insights    │    │ Pipeline    │
       └────────────┘    │ Actions     │    │ ChromaDB +  │
                         │ Decisions   │    │ Embeddings  │
                         │ Questions   │    └──────┬──────┘
                         └─────────────┘           │
                                                  ▼
                                         ┌────────────────┐
                                         │ Transcript-    │
                                         │ Grounded Chat  │
                                         └────────────────┘

🔄 End-to-End Pipeline

The backend pipeline follows this sequence:

Input
  ↓
process_input()
  ↓
Audio / Video chunks
  ↓
transcribe_all()
  ↓
Transcript
  ↓
generate_title()
  ↓
summarize()
  ↓
extract_action_items()
  ↓
extract_key_decisions()
  ↓
extract_questions()
  ↓
build_rag_chain()
  ↓
Structured Meeting Intelligence + RAG Chat

The orchestration is implemented in main.py.

🧠 RAG-Based Meeting Q&A

The project uses a RAG architecture to make the transcript queryable.

At a high level:

Transcript
    ↓
Document chunks
    ↓
Embeddings
    ↓
ChromaDB Vector Store
    ↓
Retriever
    ↓
Relevant transcript context
    ↓
LLM
    ↓
Answer

This allows users to ask questions such as:

"What were the main decisions?"
"Who was assigned the next task?"
"What problems were discussed?"
"What are the unresolved questions?"

The frontend explicitly describes the chat as being grounded in the meeting transcript.

🎙️ Speech-to-Text

The project supports speech transcription using:

OpenAI Whisper for English processing

Sarvam STT for Hinglish processing

The selected language is passed through the pipeline from the UI/backend.

The dependency configuration includes openai-whisper, torch, and the Sarvam-related environment configuration used by the project.

🤖 AI Processing

The application uses an LLM pipeline to generate:

Meeting Title

Creates a concise title from the transcript.

Summary

Converts the raw transcript into a more useful meeting summary.

Action Items

Extracts tasks or follow-up work identified in the meeting.

Key Decisions

Extracts important decisions made during the conversation.

Open Questions

Identifies unresolved questions or topics requiring further clarification.

The backend exposes these results as structured fields returned by run_pipeline().

🖥️ User Interface

The frontend is built with Streamlit and provides:

YouTube URL input

File upload for mp4, mp3, wav, m4a, and mov

English / Hinglish language selection

Meeting analysis action

Summary tab

Action Items tab

Key Decisions tab

Open Questions tab

RAG-powered Chat tab

The UI uses a custom dark cyberpunk/glassmorphism design with responsive cards, tabs, metrics, and a chat interface.

🛠️ Tech Stack

Component

Technology

Frontend

Streamlit

Speech-to-Text

OpenAI Whisper / Sarvam STT

LLM

Mistral AI

LLM Orchestration

LangChain

RAG

LangChain + ChromaDB

Embeddings

HuggingFace Sentence Transformers

Video/Audio Download

yt-dlp

Audio Processing

pydub

Translation

deep-translator

Environment Management

python-dotenv

Export

fpdf2 / Python file I/O

Core Language

Python

The dependency file specifies Streamlit, yt-dlp, pydub, Whisper, Torch, deep-translator, LangChain, Mistral integration, ChromaDB, HuggingFace embeddings, sentence-transformers, fpdf2, python-dotenv, NumPy and requests.

📁 Project Structure

AI-Video-Agent/
│
├── app.py
├── main.py
├── test.py
├── requirements.txt
│
├── core/
│   ├── extractor.py
│   ├── rag_engine.py
│   ├── summarizer.py
│   ├── transcriber.py
│   └── vector_store.py
│
├── utils/
│   └── audio_processor.py
│
├── .env.example
├── .gitignore
│
└── vector_db/              # Generated locally; NOT committed

⚙️ Installation

1. Clone the repository

git clone https://github.com/taoseefr15/AI-Video-Agent.git
cd AI-Video-Agent

2. Create a virtual environment

Windows PowerShell:

python -m venv .venv
.venv\Scripts\Activate.ps1

macOS / Linux:

python3 -m venv .venv
source .venv/bin/activate

3. Install Python dependencies

pip install -r requirements.txt

4. Install FFmpeg

yt-dlp and pydub require the FFmpeg binary for audio/video processing.

Windows example:

choco install ffmpeg

For Linux:

sudo apt install ffmpeg

For macOS:

brew install ffmpeg

Verify:

ffmpeg -version

🔐 Environment Variables

Create a local .env file in the project root.

Example:

MISTRAL_API_KEY=your_mistral_api_key
WHISPER_MODEL=small
SARVAM_API_KEY=your_sarvam_api_key
SARVAM_STT_MODEL=saaras:v2.5

🚨 Security

Never commit .env to GitHub.

The project intentionally excludes:

.venv/        → local Python virtual environment
.env          → API keys and environment secrets
vector_db/    → locally generated vector database

These exclusions are configured in .gitignore.

If you are publishing this repository, use .env.example with placeholders rather than real credentials.

Important: If a real API key has ever been committed to a public repository, immediately revoke/rotate that key in the provider dashboard and replace it with a new secret.

▶️ Running the Application

Streamlit UI

streamlit run app.py

The application provides the complete interactive workflow:

Choose source
    ↓
YouTube URL / Upload recording
    ↓
Select language
    ↓
Analyze Meeting
    ↓
Transcript + Summary + Insights
    ↓
Ask questions using RAG Chat

CLI Mode

The backend also exposes a CLI entry point through main.py.

python main.py

It asks for:

Enter YouTube URL or local file path:
Language (english/hinglish):

After processing, it prints the title, summary, action items, key decisions, open questions, and provides an interactive RAG chat loop.

🧪 Testing

The repository currently contains test.py for testing the processing pipeline.

Run:

python test.py

For future production hardening, the test suite can be expanded into structured pytest tests covering:

Audio extraction

Transcription

Translation

Summarization

Structured extraction

Vector-store creation

Retrieval quality

RAG responses

Error handling

🔒 GitHub & Repository Hygiene

The repository is configured so generated/local resources are not uploaded.

Intentionally NOT tracked

.venv/
.env
vector_db/
__pycache__/
*.pyc
downloades/

Why?

Resource

Reason

.venv/

Machine-specific Python environment

.env

Contains sensitive API credentials

vector_db/

Generated local vector-store data

__pycache__/

Python-generated cache

*.pyc

Compiled Python cache files

downloades/

Local downloaded/generated files

This keeps the Git repository smaller, safer, and reproducible.

🎯 Key Engineering Concepts Demonstrated

This project brings together several practical AI engineering concepts:

Multimodal media ingestion

Video/audio preprocessing

Speech-to-text

Language-aware transcription

LLM-powered summarization

Information extraction

Vector embeddings

Vector databases

Retrieval-Augmented Generation

LangChain orchestration

Interactive AI applications

Environment/secrets management

Modular Python architecture

🚀 Future Improvements

Potential next iterations include:

Speaker diarization

Timestamp-aware transcript citations

Better source attribution in RAG answers

Streaming transcription

Async/background processing

Persistent user/session management

Authentication and authorization

Production vector database

Evaluation framework for RAG quality

Automated hallucination/grounding evaluation

Docker deployment

Cloud deployment

API layer for programmatic access

Observability and latency/token monitoring

💡 Example Use Cases

Meeting Intelligence

Upload a recorded meeting and quickly identify:

Summary
↓
Decisions
↓
Action Items
↓
Open Questions
↓
Ask Questions

Educational Content

Use a YouTube lecture or recorded lesson and query the transcript conversationally.

Knowledge Extraction

Turn long-form video/audio content into structured, searchable information.

📌 Current Project Status

Status: 🚧 Active development

The current implementation focuses on the complete ingestion → transcription → analysis → RAG conversation workflow.

The repository is intended as a practical AI/ML engineering project demonstrating how multiple AI components can be composed into a single application.

👨‍💻 Author

Taoseef Raza

GitHub:
https://github.com/taoseefr15

Project:
https://github.com/taoseefr15/AI-Video-Agent

⭐ If You Find This Project Useful

Consider giving the repository a ⭐ on GitHub and following the project as it evolves.
