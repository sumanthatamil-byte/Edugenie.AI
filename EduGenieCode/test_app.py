"""
Comprehensive Test Suite for EduGenie
Tests routes, input validation, error handling, quiz parsing/validation,
and end-to-end pipeline responses with both real and mocked AI backends.
"""

import os
import json
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

# Import app and modules
from main import app
from quiz_module import clean_json_text, validate_quiz_structure

client = TestClient(app)

# ==========================================
# 1. Health and UI Route Tests
# ==========================================

def test_health_endpoint():
    """Verify GET /health returns 200 and status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data == {"status": "ok"}

def test_docs_endpoint():
    """Verify Swagger UI is accessible at /docs."""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "swagger" in response.text.lower() or "openapi" in response.text.lower()

def test_frontend_home():
    """Verify GET / renders EduGenie dashboard with all 5 capabilities."""
    response = client.get("/")
    assert response.status_code == 200
    html = response.text
    assert "EduGenie" in html
    assert "Your personal AI tutor for learning support" in html
    assert "Ask a Question" in html
    assert "Explain a Topic" in html
    assert "Summarize Text" in html
    assert "Generate a Quiz" in html
    assert "Learning Recommendations" in html


# ==========================================
# 2. Input Validation (Empty Inputs -> 400 Bad Request)
# ==========================================

def test_qa_empty_input():
    """Verify /qa rejects empty question with 400."""
    response = client.get("/qa?question=   ")
    assert response.status_code == 400
    assert "error" in response.json()

def test_explain_empty_input():
    """Verify /explain/ rejects empty topic with 400."""
    response = client.post("/explain/", json={"topic": ""})
    assert response.status_code == 400
    assert "error" in response.json()

def test_summarize_empty_input():
    """Verify /summarize/ rejects empty text with 400."""
    response = client.post("/summarize/", json={"text": "   "})
    assert response.status_code == 400
    assert "error" in response.json()

def test_quiz_empty_input():
    """Verify /quiz rejects empty topic/text with 400."""
    response = client.post("/quiz", json={"topic": ""})
    assert response.status_code == 400
    assert "error" in response.json()

def test_learning_empty_input():
    """Verify /learning-recommendations rejects empty topic with 400."""
    response = client.get("/learning-recommendations?topic=  ")
    assert response.status_code == 400
    assert "error" in response.json()


# ==========================================
# 3. Missing API Key Error Handling
# ==========================================

def test_missing_api_key_graceful_handling():
    """Verify missing API key produces informative 400/500 JSON without server crash."""
    with patch.dict(os.environ, {"GEMINI_API_KEY": ""}, clear=True):
        response = client.get("/qa?question=What+is+photosynthesis?")
        assert response.status_code in [400, 500]
        data = response.json()
        assert "error" in data
        assert "GEMINI_API_KEY" in data["error"] or "missing" in data["error"].lower()


# ==========================================
# 4. Quiz Parser and Validator Unit Tests
# ==========================================

def test_clean_json_text_with_markdown_fences():
    """Ensure clean_json_text strips ```json ... ``` correctly."""
    raw = '```json\n[{"question": "Q1", "options": ["A","B","C","D"], "answer": "A"}]\n```'
    cleaned = clean_json_text(raw)
    assert cleaned == '[{"question": "Q1", "options": ["A","B","C","D"], "answer": "A"}]'

def test_clean_json_text_with_surrounding_prose():
    """Ensure clean_json_text extracts only the JSON array."""
    raw = 'Here is your quiz:\n[{"question": "Q", "options": ["1","2","3","4"], "answer": "1"}]\nHope this helps!'
    cleaned = clean_json_text(raw)
    assert cleaned == '[{"question": "Q", "options": ["1","2","3","4"], "answer": "1"}]'

def test_validate_quiz_structure_valid():
    """Verify validation passes for valid 3-question quiz with 4 options and matching answer."""
    valid_data = [
        {"question": "Q1?", "options": ["Opt 1", "Opt 2", "Opt 3", "Opt 4"], "answer": "Opt 1"},
        {"question": "Q2?", "options": ["A", "B", "C", "D"], "answer": "C"},
        {"question": "Q3?", "options": ["W", "X", "Y", "Z"], "answer": "Z"}
    ]
    result = validate_quiz_structure(valid_data)
    assert len(result) == 3
    assert result[0]["answer"] == "Opt 1"

def test_validate_quiz_structure_rejects_wrong_question_count():
    """Verify validation fails if quiz does not have exactly 3 questions."""
    invalid_data = [
        {"question": "Q1?", "options": ["A", "B", "C", "D"], "answer": "A"}
    ]
    with pytest.raises(ValueError, match="must contain exactly 3 questions"):
        validate_quiz_structure(invalid_data)

def test_validate_quiz_structure_rejects_wrong_options_count():
    """Verify validation fails if a question doesn't have exactly 4 options."""
    invalid_data = [
        {"question": "Q1?", "options": ["A", "B", "C"], "answer": "A"},
        {"question": "Q2?", "options": ["A", "B", "C", "D"], "answer": "B"},
        {"question": "Q3?", "options": ["A", "B", "C", "D"], "answer": "C"}
    ]
    with pytest.raises(ValueError, match="exactly 4 options"):
        validate_quiz_structure(invalid_data)

def test_validate_quiz_structure_rejects_unmatched_answer():
    """Verify validation fails if answer does not match any option."""
    invalid_data = [
        {"question": "Q1?", "options": ["A", "B", "C", "D"], "answer": "Option E"},
        {"question": "Q2?", "options": ["A", "B", "C", "D"], "answer": "B"},
        {"question": "Q3?", "options": ["A", "B", "C", "D"], "answer": "C"}
    ]
    with pytest.raises(ValueError, match="does not match any of its 4 options"):
        validate_quiz_structure(invalid_data)


# ==========================================
# 5. End-to-End Mocked Gemini Flow Tests
# ==========================================

@patch("qna.generate_text_with_gemini")
def test_qa_endpoint_success(mock_gemini):
    mock_gemini.return_value = "The Pacific Ocean is the largest and deepest ocean on Earth."
    response = client.get("/qa?question=Which+is+the+largest+ocean%3F")
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "Pacific Ocean" in data["answer"]

@patch("summary_module.generate_text_with_gemini")
def test_summarize_endpoint_success(mock_gemini):
    mock_gemini.return_value = "Key takeaway: Photosynthesis converts light into chemical energy (glucose)."
    response = client.post("/summarize/", json={"text": "Long passage about botany..."})
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "Photosynthesis" in data["summary"]

@patch("quiz_module.generate_text_with_gemini")
def test_quiz_endpoint_success(mock_gemini):
    mock_gemini.return_value = json.dumps([
        {"question": "What is 2+2?", "options": ["3", "4", "5", "6"], "answer": "4"},
        {"question": "What is the capital of France?", "options": ["Rome", "Berlin", "Paris", "Madrid"], "answer": "Paris"},
        {"question": "Which gas do plants absorb?", "options": ["Oxygen", "Carbon Dioxide", "Nitrogen", "Helium"], "answer": "Carbon Dioxide"}
    ])
    response = client.post("/quiz", json={"topic": "General Science"})
    assert response.status_code == 200
    data = response.json()
    assert "quiz" in data
    assert len(data["quiz"]) == 3
    assert data["quiz"][0]["answer"] == "4"

@patch("learning_path.generate_text_with_gemini")
def test_learning_recommendations_endpoint_success(mock_gemini):
    mock_gemini.return_value = "## Python Roadmap\n1. Beginner: Variables, Loops\n2. Intermediate: OOP, Modules\n3. Advanced: Concurrency, Metaclasses"
    response = client.get("/learning-recommendations?topic=Python+Programming")
    assert response.status_code == 200
    data = response.json()
    assert data["topic"] == "Python Programming"
    assert "recommendation" in data
    assert "Python Roadmap" in data["recommendation"]
