# EduGenie: Google Gemini Powered Learning Assistant

EduGenie is a lightweight, full-stack AI-powered educational assistant designed to support students and lifelong learners with five core capabilities:

1. **Question & Answer**: Answers student homework and conceptual questions with educational clarity using Google Gemini.
2. **Simple Concept Explanation**: Explains complex topics in beginner-friendly, student-ready terms using the local `MBZUAI/LaMini-Flan-T5-783M` model.
3. **Interactive Quiz Generation**: Creates structured 3-question multiple-choice quizzes with 4 options each, immediate feedback, and scoring.
4. **Text Summarization**: Distills dense textbook passages into concise, high-yield study takeaways.
5. **Personalized Learning Recommendations**: Crafts step-by-step learning roadmaps with beginner, intermediate, and advanced progressions.

---

## Architecture

```text
User
 ↓
HTML / CSS / JavaScript Frontend (Templates & Static)
 ↓
FastAPI Backend (main.py)
 ↓
Selected Module (qna, explanation_module, quiz_module, summary_module, learning_path)
 ↓
AI Engine (Google Gemini API / HuggingFace Transformers: MBZUAI/LaMini-Flan-T5-783M)
 ↓
FastAPI JSON Response
 ↓
Frontend Interactive Rendering
 ↓
User
```

---

## Project Structure

```text
EduGenie/
├── main.py                   # FastAPI application entrypoint & routing
├── gemini_client.py          # Unified Gemini client with fallback models & error handling
├── qna.py                    # Q&A module using Google Gemini
├── explanation_module.py     # Simple concept explanation using LaMini-Flan-T5
├── quiz_module.py            # 3-question quiz generator with strict schema validation
├── summary_module.py         # Text summarization module using Gemini
├── learning_path.py          # Structured learning roadmap module using Gemini
├── requirements.txt          # Python package dependencies
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules for virtual environments & secrets
├── README.md                 # Project documentation and setup guide
│
├── templates/
│   └── index.html            # Web interface with interactive tabs
│
└── static/
    ├── style.css             # Responsive, student-friendly CSS styling
    └── script.js             # Client-side API caller & interactive quiz logic
```

---

## Prerequisites

- **Python 3.10+** (Python 3.10, 3.11, 3.12, 3.13, or 3.14)
- **Google Gemini API Key**: Obtain a free API key from [Google AI Studio](https://aistudio.google.com/).

---

## Installation & Setup

### 1. Clone or Open the Repository

Open your terminal in the EduGenie root directory:

```bash
cd "c:\Users\RAJITHA\OneDrive\Desktop\new project"
```

### 2. Create and Activate a Virtual Environment

**On Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**On Windows (Command Prompt):**
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

**On macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Required Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create your `.env` file by copying the template:

**On Windows:**
```powershell
copy .env.example .env
```

**On macOS / Linux:**
```bash
cp .env.example .env
```

Open `.env` and set your Google Gemini API key:

```env
GEMINI_API_KEY=AIzaSy...YourActualKeyHere
GEMINI_MODEL=gemini-2.5-flash
PORT=8000
HOST=127.0.0.1
```

---

## Running the Application

Launch the application with Uvicorn:

```bash
uvicorn main:app --reload
```

Once started, open your web browser to:

- **Web Dashboard**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Check Endpoint**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## API Endpoints

| Method | Endpoint | Description | Request Parameters / Body |
|---|---|---|---|
| `GET` | `/` | Web Application Frontend | None |
| `GET` | `/health` | System Health Check | None |
| `GET` | `/qa` | Ask a Question | Query parameter: `?question=...` |
| `POST` | `/explain/` | Explain a Concept (LaMini-Flan-T5) | JSON body: `{"topic": "..."}` |
| `POST` | `/summarize/` | Summarize Passage (Gemini) | JSON body: `{"text": "..."}` |
| `POST` | `/quiz` | Generate 3-Question Quiz (Gemini) | JSON body: `{"topic": "..."}` |
| `GET` | `/learning-recommendations` | Learning Roadmap (Gemini) | Query parameter: `?topic=...` |

---

## Troubleshooting

### 1. `GEMINI_API_KEY is missing or invalid`
- Ensure you created a `.env` file in the project root directory.
- Verify that `GEMINI_API_KEY` is not empty and does not contain placeholder text like `your_gemini_api_key_here`.

### 2. First-Time Concept Explanation Delay
- The explanation module uses `MBZUAI/LaMini-Flan-T5-783M`.
- On the first request to `/explain/`, Hugging Face will download the model weights (~1.5GB to 3GB) and cache them in `~/.cache/huggingface/`.
- Subsequent requests will load the model directly from the cache instantly.
- Ensure your system has an active internet connection during the initial model download.

### 3. Model Compatibility & Rate Limits
- The Gemini client automatically falls back across `gemini-2.5-flash`, `gemini-1.5-flash`, and `gemini-2.0-flash` if a specific model tier is temporarily unavailable.
- If you encounter rate limit errors (HTTP 429), wait a few seconds before submitting another request or upgrade your Google AI Studio quota.

---

## License

EduGenie is developed for educational and academic use.
