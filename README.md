# Code Review Tool

This project is a code linting tool for Python and JavaScript, powered by a FastAPI backend. It allows you to send code via a REST API and receive a lint report in JSON format, using Flake8 for Python and ESLint for JavaScript.

This project is designed to be integrated with a custom GPT, providing it with access to advanced code linting capabilities through the API.

## Prerequisites

- Python 3.10+
- Node.js (for ESLint)
- pip (to install Python dependencies)
- npm (to install Node dependencies)

## Installation

1. **Clone the repository**

```bash
# Clone the project
git clone https://github.com/ClemNTTS/code-review-tool
cd code-review-tool
```

2. **Install Python dependencies**

```bash
cd backend
python -m venv ../env
source ../env/Scripts/activate
pip install -r requirements.txt
```

3. **Install Node dependencies (for ESLint)**

```bash
npm install
```

## Configuration

- The `.flake8` file configures Flake8 for Python.
- The `.eslintrc.json` file configures ESLint for JavaScript.

## Run the API server

```bash
uvicorn app.main:app --reload
```

The server will be available at http://127.0.0.1:8000

## API Usage

### Endpoint: `/functions/run_linter`

- **Method**: POST
- **Body (JSON)**:
  - `language`: "python" or "javascript"
  - `code`: the source code to analyze

#### Example with curl (Python)

```bash
curl -X POST "http://127.0.0.1:8000/functions/run_linter" \
  -H "Content-Type: application/json" \
  -d '{"language": "python", "code": "def add(a, b):\n    return a+b\n"}'
```

#### Example with curl (JavaScript)

```bash
curl -X POST "http://127.0.0.1:8000/functions/run_linter" \
  -H "Content-Type: application/json" \
  -d '{"language": "javascript", "code": "var unused; function add(a,b){return a+b;}"}'
```

## Monitoring & Logging

- **Logs**: All API requests and linting results are logged to `backend/logs/app.log` with automatic rotation.
- **Prometheus metrics**: The `/metrics` endpoint exposes Prometheus-compatible metrics, including the number of lint requests per language. Example: `curl http://localhost:8000/metrics`.
- **Sentry**: Error reporting is integrated with Sentry. Set your SENTRY_DSN and SENTRY_ENV in the `.env` file to enable error tracking. Errors are automatically sent to your Sentry dashboard.

## Environment Variables

- Use a `.env` file at the project root (see `.env.example`).
- Main variables:
  - `SENTRY_DSN`: Sentry Data Source Name (for error reporting)
  - `SENTRY_ENV`: Sentry environment (e.g. development, production)

## Docker & Docker Compose

- Build and run the backend with Docker Compose:

```bash
docker compose up --build
```

- The `.env` file is automatically loaded for environment variables.
- The backend is available on port 8000.

## Continuous Integration

- GitHub Actions workflow is set up in `.github/workflows/ci.yml`.
- On each push or pull request to `main`, the workflow:
  - Installs Python and Node dependencies
  - Runs all integration tests
  - Builds the Docker image to ensure Dockerfile validity

## Tests

- Integration tests are in `backend/tests/test_api.py`.
- Run all tests locally with:

```bash
pytest
```

## License

Read [LICENSE](LICENSE) file.
