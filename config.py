from pathlib import Path
import os

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

BASE_DIR: Path = Path(__file__).resolve().parent
PROMPT_TEMPLATES_BASE_DIR: Path = BASE_DIR / 'prompt_templates'

OLLAMA_BASE_URL: str = 'http://localhost:11434'

