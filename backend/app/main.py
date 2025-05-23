from fastapi import FastAPI
from pydantic import BaseModel
import subprocess
import json
import tempfile
import os
import logging
from logging.handlers import RotatingFileHandler
import sentry_sdk
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
from dotenv import load_dotenv


class LintRequest(BaseModel):
    language: str
    code: str


app = FastAPI()

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Logging configuration
log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'app.log')
handler = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=5)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[handler, logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Sentry configuration (replace with your DSN)
sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN", ""),
    traces_sample_rate=1.0,
    environment=os.getenv("SENTRY_ENV", "development")
)

# Prometheus metrics
lint_requests_total = Counter('lint_requests_total', 'Total number of lint requests', ['language'])


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/functions/run_linter")
def run_linter(req: LintRequest):
    logger.info(f"Lint request received for language: {req.language}")
    lint_requests_total.labels(language=req.language).inc()
    
    # Temporary save using tempfile
    suffix = ".py" if req.language == "python" else ".js"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        tmp_file.write(req.code.encode())
        filename = tmp_file.name

    # Linter choice
    if req.language == 'python':
        cmd = ["flake8", filename, "--format=json"]
    else:
        eslint_path = os.path.join(os.path.dirname(__file__), "..", "node_modules", ".bin", "eslint")
        if os.name == "nt":
            eslint_path += ".cmd"
        cmd = [eslint_path, filename, "-f", "json"]

    result = subprocess.run(cmd, capture_output=True, text=True)
    
    try:
        report = json.loads(result.stdout)
        logger.info(f"Linting completed for {filename}")
    except json.JSONDecodeError:
        logger.error(f"Linting error: {result.stderr}")
        sentry_sdk.capture_exception()
        report = {"error": result.stderr}
    return report
