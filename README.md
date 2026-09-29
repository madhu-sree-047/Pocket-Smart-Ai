# PocketSmart AI

PocketSmart AI is a complete FastAPI + Jinja2 application for budget-aware recommendations across three planners: Home Interior, Party, and Jewelry. It follows the supplied project document's requested architecture, routes, authentication/session flow, history, optional image input, and fallback recommendation behavior.

## Important implementation note

The supplied document names Gemini 1.5 Flash Pro and also mixes Flask/FastAPI terminology. This implementation standardizes on **FastAPI** because the later architecture, milestones, routes, and frontend specification explicitly use FastAPI. The AI integration uses Google's current `google-genai` SDK and reads the model name from `GEMINI_MODEL`; this avoids hard-coding an obsolete model name. Google's current documentation shows `from google import genai` and `client.models.generate_content(...)`, and supports structured JSON output through a schema. See the official Gemini documentation for current model availability. 

## Features

- Responsive Jinja2 frontend
- Registration, login, logout, JWT token endpoint
- Session info and session data endpoints
- SQLite persistence with SQLAlchemy
- Home, Party, Jewelry planners
- Optional outfit image upload for Jewelry
- Gemini structured-output integration
- Deterministic fallback recommendations when Gemini is disabled/unavailable
- Recommendation history
- Platform links for Amazon, Flipkart, IKEA, Swiggy, Zomato and OYO
- Validation and upload size/type checks
- CORS configuration
- Automated API tests

## Project structure

```text
pocketsmart_ai/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── dependencies.py
│   ├── auth.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── db.py
│   │   └── schemas.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── planners.py
│   │   ├── pages.py
│   │   └── history.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── gemini.py
│   │   └── recommendations.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── dashboard.html
│   │   ├── planner.html
│   │   ├── history.html
│   │   └── results.html
│   └── static/
│       ├── css/style.css
│       └── js/app.js
├── tests/test_api.py
├── .env.example
├── requirements.txt
└── README.md
```

## VS Code setup

1. Install Python 3.11+ and VS Code.
2. Open the `pocketsmart_ai` folder in VS Code.
3. Create a virtual environment:

### Windows PowerShell

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

4. Copy `.env.example` to `.env`.
5. For real Gemini generation, put your Google AI API key in `GEMINI_API_KEY` and keep `GEMINI_ENABLED=true`.
6. If you want to run without an API key, set `GEMINI_ENABLED=false`. The app will use the built-in fallback engine, so all planners and UI still work.

## Run

```bash
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000

API docs: http://127.0.0.1:8000/docs

## Test

With the virtual environment active:

```bash
pytest -q
```

The tests disable Gemini and use the deterministic fallback, so they do not require an API key or internet access.

## API routes

- `POST /register`
- `POST /login`
- `POST /token`
- `POST /logout`
- `GET /session-info`
- `GET /session-data`
- `POST /generate-home`
- `POST /generate-party`
- `POST /generate-jewelry`
- `GET /recommendations-details/{recommendation_id}`
- `GET /history`
- `GET /health`

## Gemini integration

The service sends a planner-specific prompt and requests JSON conforming to the application's Pydantic recommendation schema. Jewelry can send text plus the uploaded image bytes. If Gemini fails, the service returns a clearly marked fallback result instead of crashing the request.

The app intentionally does **not** pretend that it has live Amazon/Flipkart/IKEA/Swiggy/Zomato/OYO inventory. The supplied project document calls for mock API calls/simulated sourcing, so this version uses curated search URLs and generated product concepts. Production live commerce integrations should be added through official partner/affiliate APIs and their terms.

## Production hardening checklist

- Replace the development `SECRET_KEY`.
- Use PostgreSQL or another managed database.
- Store uploads in object storage and virus-scan them.
- Put the app behind HTTPS and a reverse proxy.
- Add rate limiting and audit logging.
- Add real official commerce/restaurant APIs where permitted.
- Configure secure cookies/session strategy if browser-only JWT storage is introduced.
