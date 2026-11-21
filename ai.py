import os
import json
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

api_key = os.getenv("groq_API_KEY") or os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("Missing groq_API_KEY in .env file.")

client = Groq(api_key=api_key)

def get_candidate_models() -> list[str]:
    """Lists active text chat models on your Groq account, excluding audio/TTS/guard models."""
    models = client.models.list().data
    blocked_keywords = ("whisper", "guard", "orpheus", "tts", "playai", "distil-whisper", "safeguard")
    
    available = [
        m.id for m in models
        if not any(bad in m.id.lower() for bad in blocked_keywords)
    ]

    # Put strong general-purpose instruct/versatile models first if present
    priority_terms = ("llama-3.3", "llama-3.1", "llama-4", "qwen", "gpt-oss", "gemma", "mistral", "deepseek")
    prioritized = [m for m in available if any(t in m.id.lower() for t in priority_terms)]
    others = [m for m in available if m not in prioritized]

    return prioritized + others

def analyze_resume(resume_text: str, user_goal: str) -> dict:
    prompt = f"""
    Analyze the following resume for the target job role: "{user_goal}".
    Return ONLY valid JSON with these exact keys and non-empty lists of strings:
    {{
        "missing_skills": [
            "<missing skill 1>",
            "<missing skill 2>",
            "<missing skill 3>"
        ],
        "roadmap": [
            "<step 1 to learn missing skills and build projects>",
            "<step 2>",
            "<step 3>",
            "<step 4>"
        ],
        "interview_questions": [
            "<technical or role-specific interview question 1>",
            "<interview question 2>",
            "<interview question 3>",
            "<interview question 4>"
        ]
    }}

    Resume:
    {resume_text}
    """

    last_error = "No suitable chat models available."
    for model_id in get_candidate_models():
        try:
            response = client.chat.completions.create(
                model=model_id,
                messages=[
                    {"role": "system", "content": "You are an expert technical recruiter and career coach. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            last_error = str(e)
            continue

    return {"error": f"AI analysis failed: {last_error}"}

def get_candidate_models() -> list[str]:
    """Lists active text chat models on your Groq account safely."""
    raw_models = client.models.list().data
    blocked_keywords = ("whisper", "guard", "orpheus", "tts", "playai", "distil-whisper", "safeguard")

    available = []
    for m in raw_models:
        model_id = m if isinstance(m, str) else getattr(m, "id", str(m))
        if not any(bad in model_id.lower() for bad in blocked_keywords):
            available.append(model_id)

    priority_terms = ("llama-3.3", "llama-3.1", "llama-4", "qwen", "gpt-oss", "gemma", "mistral", "deepseek")
    prioritized = [m for m in available if any(t in m.lower() for t in priority_terms)]
    others = [m for m in available if m not in prioritized]

    return prioritized + others