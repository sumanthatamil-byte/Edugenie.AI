"""
Q&A Module for EduGenie
Handles answering educational questions using Google Gemini.
"""

import logging
from gemini_client import generate_text_with_gemini

logger = logging.getLogger("EduGenie.QnA")

SYSTEM_PROMPT = """You are EduGenie, an encouraging, highly knowledgeable, and friendly AI tutor for students.
Your goal is to answer the student's question accurately, clearly, and concisely in an engaging, educational tone.
Guidelines:
1. Provide a direct, well-structured explanation.
2. Break down complex ideas using simple analogies or step-by-step points where appropriate.
3. Keep the language accessible and age-appropriate for learners.
4. Avoid overly academic jargon unless defined clearly.
"""

def answer_question_with_gemini(question: str) -> str:
    """
    Answers an educational question using Google Gemini.
    
    Args:
        question: The user's/student's question text.
        
    Returns:
        The educational answer string.
        
    Raises:
        ValueError: If input is empty or validation fails.
        Exception: If the AI generation fails.
    """
    cleaned_question = question.strip() if question else ""
    if not cleaned_question:
        raise ValueError("Question cannot be empty. Please ask a valid question.")

    prompt = f"Student Question: {cleaned_question}\n\nPlease provide a clear, educational, and helpful explanation."

    try:
        answer = generate_text_with_gemini(
            prompt=prompt,
            system_instruction=SYSTEM_PROMPT,
            temperature=0.4
        )
        return answer
    except Exception as e:
        logger.error(f"Error answering question with Gemini: {e}")
        raise
