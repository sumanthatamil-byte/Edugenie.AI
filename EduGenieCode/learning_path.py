"""
Learning Path Module for EduGenie
Generates structured learning recommendations and roadmaps using Google Gemini.
"""

import logging
from gemini_client import generate_text_with_gemini

logger = logging.getLogger("EduGenie.LearningPath")

LEARNING_PATH_SYSTEM_PROMPT = """You are EduGenie's curriculum designer and academic advisor.
Your task is to create a structured, step-by-step learning roadmap for a student on any topic they provide.

Guidelines for formatting the response:
1. Overview: A quick 1-2 sentence overview of why this subject matters.
2. Beginner Level (Foundations): Core concepts, fundamentals, and initial hands-on exercises in recommended learning order.
3. Intermediate Level (Core Proficiency): Practical applications, deeper theories, and mini-projects.
4. Advanced Level (Mastery): Specialized topics, optimization, and real-world project ideas.
5. Progression Guidance: Advice on how much time to spend, best learning practices, and how to test understanding.
6. Recommended Resources: High-quality learning resources (documentation, interactive platforms, books, or project concepts).

Format clearly with Markdown headings and bullet points for readability.
"""

def get_learning_recommendations(topic: str) -> str:
    """
    Generates structured learning recommendations and roadmap for a topic.
    
    Args:
        topic: The topic, subject, or skill (e.g. 'Python Programming', 'SQL', 'Quantum Physics').
        
    Returns:
        Structured markdown text containing the learning roadmap.
        
    Raises:
        ValueError: If topic is empty or invalid.
        Exception: If generation fails.
    """
    cleaned_topic = topic.strip() if topic else ""
    if not cleaned_topic:
        raise ValueError("Topic cannot be empty. Please specify a subject or skill to learn.")

    prompt = (
        f"Create a comprehensive and structured learning path for a student wanting to learn: '{cleaned_topic}'.\n"
        f"Include beginner, intermediate, and advanced levels with topics in logical order, progression tips, and suggested resources."
    )

    try:
        recommendations = generate_text_with_gemini(
            prompt=prompt,
            system_instruction=LEARNING_PATH_SYSTEM_PROMPT,
            temperature=0.5
        )
        return recommendations
    except Exception as e:
        logger.error(f"Error in get_learning_recommendations: {e}")
        raise
