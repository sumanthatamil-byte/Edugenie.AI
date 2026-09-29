"""
Quiz Generation Module for EduGenie
Generates structured 3-question multiple choice quizzes using Google Gemini.
Validates output structure strictly according to specifications.
"""

import json
import re
import logging
from typing import List, Dict, Any
from gemini_client import generate_text_with_gemini

logger = logging.getLogger("EduGenie.Quiz")

QUIZ_SYSTEM_PROMPT = """You are EduGenie's assessment expert.
Generate an educational multiple-choice quiz based on the user's provided topic or passage.

Strict Requirements:
1. Generate EXACTLY 3 multiple-choice questions.
2. For each question, provide EXACTLY 4 distinct answer options.
3. Provide the EXACT correct answer string, which MUST match one of the 4 options character-for-character.
4. Output ONLY valid JSON in the exact structure below, with NO extra conversational text, markdown formatting, or explanations outside the JSON:

[
  {
    "question": "Clear question text?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "answer": "Option A"
  },
  {
    "question": "Second question text?",
    "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
    "answer": "Option 2"
  },
  {
    "question": "Third question text?",
    "options": ["Choice A", "Choice B", "Choice C", "Choice D"],
    "answer": "Choice D"
  }
]
"""

def clean_json_text(raw_text: str) -> str:
    """Strips Markdown code fences and extracts JSON array content."""
    text = raw_text.strip()
    # Strip markdown fences if present e.g. ```json ... ``` or ``` ... ```
    if text.startswith("```"):
        # Match ```json or ```
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        # Strip trailing ```
        text = re.sub(r"\s*```$", "", text)
        text = text.strip()

    # If there's any text before the first '[' or after the last ']', slice it out
    start_idx = text.find('[')
    end_idx = text.rfind(']')
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        text = text[start_idx:end_idx + 1]

    return text

def validate_quiz_structure(quiz_data: Any) -> List[Dict[str, Any]]:
    """
    Validates that the parsed data conforms to the EduGenie quiz specification:
    - Must be a list
    - Must contain exactly 3 questions
    - Each question must have 'question' (non-empty str)
    - Each question must have exactly 4 options (list of non-empty strings)
    - Each question must have 'answer' (str)
    - 'answer' must exactly match one of the options
    """
    if not isinstance(quiz_data, list):
        raise ValueError("Quiz output is not a JSON list.")

    if len(quiz_data) != 3:
        raise ValueError(f"Quiz must contain exactly 3 questions, got {len(quiz_data)}.")

    validated_questions = []
    for idx, item in enumerate(quiz_data, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Question {idx} must be a dictionary.")

        q_text = item.get("question")
        if not q_text or not isinstance(q_text, str) or not q_text.strip():
            raise ValueError(f"Question {idx} is missing a valid 'question' text.")

        options = item.get("options")
        if not isinstance(options, list) or len(options) != 4:
            raise ValueError(f"Question {idx} must have exactly 4 options.")

        cleaned_options = [str(opt).strip() for opt in options]
        if any(not opt for opt in cleaned_options):
            raise ValueError(f"Question {idx} has one or more empty options.")

        answer = item.get("answer")
        if not answer or not isinstance(answer, str) or not answer.strip():
            raise ValueError(f"Question {idx} is missing a valid 'answer'.")

        cleaned_answer = answer.strip()
        if cleaned_answer not in cleaned_options:
            # Check if answer is like 'A', 'Option A', or case-insensitive match
            matched = False
            for opt in cleaned_options:
                if cleaned_answer.lower() == opt.lower():
                    cleaned_answer = opt
                    matched = True
                    break
            if not matched:
                raise ValueError(
                    f"Question {idx} answer '{cleaned_answer}' does not match any of its 4 options: {cleaned_options}."
                )

        validated_questions.append({
            "question": q_text.strip(),
            "options": cleaned_options,
            "answer": cleaned_answer
        })

    return validated_questions

def generate_quiz(topic_or_passage: str) -> List[Dict[str, Any]]:
    """
    Generates a 3-question educational quiz with 4 options per question.
    
    Args:
        topic_or_passage: Topic or passage for quiz generation.
        
    Returns:
        List of 3 question dictionaries.
    """
    cleaned_input = topic_or_passage.strip() if topic_or_passage else ""
    if not cleaned_input:
        raise ValueError("Quiz topic or passage cannot be empty.")

    prompt = (
        f"Generate a 3-question multiple-choice quiz based on the following topic or passage:\n\n"
        f"\"{cleaned_input}\"\n\n"
        f"Remember: Respond ONLY with a valid JSON array of exactly 3 questions with 4 options and the exact matching answer."
    )

    last_error = None
    # Allow up to 2 attempts in case the model returns malformed JSON on the first try
    for attempt in range(2):
        try:
            raw_response = generate_text_with_gemini(
                prompt=prompt,
                system_instruction=QUIZ_SYSTEM_PROMPT,
                temperature=0.2
            )
            cleaned_json = clean_json_text(raw_response)
            parsed_data = json.loads(cleaned_json)
            validated = validate_quiz_structure(parsed_data)
            return validated
        except Exception as e:
            logger.warning(f"Quiz generation attempt {attempt + 1} failed: {e}")
            last_error = e

    raise ValueError(f"Unable to generate a valid quiz: {last_error}")
