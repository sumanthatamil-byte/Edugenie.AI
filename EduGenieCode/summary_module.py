"""
Summarization Module for EduGenie
Handles summarizing educational passages using Google Gemini.
"""

import logging
from gemini_client import generate_text_with_gemini

logger = logging.getLogger("EduGenie.Summary")

SUMMARY_SYSTEM_PROMPT = """You are EduGenie's educational summarizer.
Your goal is to summarize educational passages clearly, concisely, and accurately for students.
Guidelines:
1. Retain the core ideas, key terms, definitions, and conclusions.
2. Eliminate redundant fluff and conversational filler.
3. Organize the summary logically with bullet points or brief paragraphs if it helps comprehension.
4. Keep the vocabulary student-friendly and easy to review before an exam.
"""

def summarize_text(text: str) -> str:
    """
    Summarizes an educational text using Google Gemini.
    
    Args:
        text: The educational text or passage to summarize.
        
    Returns:
        A concise, understandable summary.
        
    Raises:
        ValueError: If the text is empty or blank.
        Exception: If summarization fails.
    """
    cleaned_text = text.strip() if text else ""
    if not cleaned_text:
        raise ValueError("Text to summarize cannot be empty.")

    prompt = (
        f"Please summarize the following educational passage clearly and concisely:\n\n"
        f"--- PASSAGE START ---\n"
        f"{cleaned_text}\n"
        f"--- PASSAGE END ---\n\n"
        f"Summary:"
    )

    try:
        summary = generate_text_with_gemini(
            prompt=prompt,
            system_instruction=SUMMARY_SYSTEM_PROMPT,
            temperature=0.3
        )
        return summary
    except Exception as e:
        logger.error(f"Error in summarize_text: {e}")
        raise
