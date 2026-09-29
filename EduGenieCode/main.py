"""
EduGenie: Google Gemini Powered Learning Assistant
Main FastAPI Application Entrypoint
"""

import os
import logging
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment configuration
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("EduGenie.Main")

# Import EduGenie AI Modules
from qna import answer_question_with_gemini
from explanation_module import explain_topic
from quiz_module import generate_quiz
from summary_module import summarize_text
from learning_path import get_learning_recommendations

# Initialize FastAPI App with metadata for Swagger/OpenAPI docs
app = FastAPI(
    title="EduGenie API",
    description="Google Gemini and LaMini-Flan-T5 powered learning assistant providing Q&A, concept explanation, quizzes, summarization, and learning recommendations.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Paths setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Ensure static & template directories exist
os.makedirs(TEMPLATES_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

# Mount static files and Jinja2 templates
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


# ==========================================
# Pydantic Request Models
# ==========================================

class ExplainRequest(BaseModel):
    topic: str = Field(..., min_length=1, description="The topic or concept to explain in simple terms.")

class SummarizeRequest(BaseModel):
    text: str = Field(..., min_length=1, description="The educational passage or text to summarize.")

class QuizRequest(BaseModel):
    topic: Optional[str] = Field(None, description="Topic for quiz generation.")
    text: Optional[str] = Field(None, description="Passage or text for quiz generation.")
    passage: Optional[str] = Field(None, description="Alternative key for passage.")


# ==========================================
# Global Exception Handlers
# ==========================================

from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Translates Pydantic validation errors to clean 400 Bad Request responses."""
    msg = exc.errors()[0]["msg"] if exc.errors() else "Invalid request data"
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": f"Invalid input: {msg}", "detail": str(exc.errors())}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Ensures consistent JSON error format with both 'error' and 'detail' fields."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "detail": exc.detail}
    )

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handles input validation and bad request errors cleanly."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": str(exc), "detail": str(exc)}
    )

@app.exception_handler(RuntimeError)
async def runtime_error_handler(request: Request, exc: RuntimeError):
    """Handles runtime and model execution errors cleanly."""
    logger.error(f"Runtime error handling request {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": str(exc), "detail": str(exc)}
    )


# ==========================================
# Frontend and Health Endpoints
# ==========================================

@app.get("/", response_class=HTMLResponse, summary="EduGenie Web Dashboard")
async def serve_frontend(request: Request):
    """Renders the EduGenie interactive student web dashboard."""
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/health", summary="Health Check")
async def health_check():
    """Returns application health status."""
    return {"status": "ok"}


# ==========================================
# 1. Question & Answer Endpoint
# ==========================================

@app.get(
    "/qa",
    summary="Ask a Question",
    description="Answers educational questions clearly and concisely using Google Gemini."
)
async def qa_endpoint(
    question: str = Query(..., min_length=1, description="Student's educational question")
):
    cleaned_question = question.strip() if question else ""
    if not cleaned_question:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty. Please provide a valid question."
        )

    try:
        answer = answer_question_with_gemini(cleaned_question)
        return {"answer": answer}
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"Error in /qa: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to answer question: {str(e)}"
        )


# ==========================================
# 2. Simple Concept Explanation Endpoint
# ==========================================

@app.post(
    "/explain/",
    summary="Explain a Topic",
    description="Explains concepts in simple, student-friendly terms using MBZUAI/LaMini-Flan-T5-783M."
)
async def explain_endpoint(payload: ExplainRequest):
    cleaned_topic = payload.topic.strip() if payload.topic else ""
    if not cleaned_topic:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Topic cannot be empty. Please provide a concept to explain."
        )

    try:
        explanation = explain_topic(cleaned_topic)
        return {
            "topic": cleaned_topic,
            "explanation": explanation
        }
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"Error in /explain/: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to explain concept: {str(e)}"
        )


# ==========================================
# 3. Text Summarization Endpoint
# ==========================================

@app.post(
    "/summarize/",
    summary="Summarize Educational Text",
    description="Generates concise, high-yield educational summaries using Google Gemini."
)
async def summarize_endpoint(payload: SummarizeRequest):
    cleaned_text = payload.text.strip() if payload.text else ""
    if not cleaned_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text to summarize cannot be empty."
        )

    try:
        summary = summarize_text(cleaned_text)
        return {"summary": summary}
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"Error in /summarize/: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to summarize text: {str(e)}"
        )


# ==========================================
# 4. Quiz Generation Endpoint
# ==========================================

@app.post(
    "/quiz",
    summary="Generate Educational Quiz",
    description="Generates exactly 3 multiple-choice questions with 4 options each using Google Gemini."
)
async def quiz_endpoint(payload: QuizRequest):
    # Accept input from topic, text, or passage field
    target_input = payload.topic or payload.text or payload.passage or ""
    cleaned_input = target_input.strip()

    if not cleaned_input:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quiz topic or passage cannot be empty. Please provide content to generate quiz."
        )

    try:
        quiz_data = generate_quiz(cleaned_input)
        return {"quiz": quiz_data}
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"Error in /quiz: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to generate quiz: {str(e)}"
        )


# ==========================================
# 5. Personalized Learning Recommendations Endpoint
# ==========================================

@app.get(
    "/learning-recommendations",
    summary="Get Learning Recommendations",
    description="Generates structured roadmaps and topic progression using Google Gemini."
)
async def learning_recommendations_endpoint(
    topic: str = Query(..., min_length=1, description="Topic or skill to learn")
):
    cleaned_topic = topic.strip() if topic else ""
    if not cleaned_topic:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Topic cannot be empty. Please provide a subject or skill to learn."
        )

    try:
        recommendations = get_learning_recommendations(cleaned_topic)
        return {
            "topic": cleaned_topic,
            "recommendation": recommendations
        }
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"Error in /learning-recommendations: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to generate learning recommendations: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "127.0.0.1")
    uvicorn.run("main:app", host=host, port=port, reload=True)
