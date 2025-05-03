from pathlib import Path
from models import ApiHostModel
import sentry_sdk
import os

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

BASE_DIR: Path = Path(__file__).resolve().parent
PROMPT_TEMPLATES_BASE_DIR: Path = BASE_DIR / 'prompt_templates'

api = ApiHostModel(os.getenv('API_URL'))
SENTRY_DSN = os.getenv('SENTRY_DSN')

sentry_sdk.init(
    dsn=SENTRY_DSN,
    send_default_pii = True,
)
