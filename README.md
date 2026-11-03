# Empowering the Individual: An Intelligent One-to-One Learning Support System

A personalized learning platform for **Class 8 Mathematics**. The system diagnoses student misconceptions from their answers, provides targeted step-by-step explanations, tests whether the student learned independently with a transfer problem, and remembers which pedagogical interventions worked best using **Bayesian Knowledge Tracing (BKT)**.

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend** | React (Vite) + Tailwind CSS | Fast, responsive, student-centered UI |
| **Backend** | Python + FastAPI | High-performance asynchronous REST API |
| **Database** | SQLite + SQLAlchemy ORM | Lightweight, zero-config relational database |
| **Pedagogical ML** | Custom Bayesian Knowledge Tracing (BKT) | Tracks student concept mastery probability $p(L)$ |
| **Diagnostic AI** | Rule-Based Diagnoser + Optional LLM | Pinpoints misconceptions with fallback to static hints |

---

## 📁 Project Structure

```text
Adaptive AI learning platform/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI app entry point & CORS configuration
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes.py         # /health and diagnostic API routes
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py         # Pydantic environment settings
│   │   │   └── database.py       # SQLAlchemy engine, session maker & init_db()
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── models.py         # 6 Core SQLAlchemy database models
│   │   └── schemas/
│   │       ├── __init__.py
│   │       └── health.py         # Pydantic schemas for API health response
│   ├── .env                      # Local environment configuration
│   ├── .env.example              # Template environment variables
│   ├── requirements.txt          # Python dependencies
│   └── learning_platform.db      # SQLite database (auto-created on startup)
│
├── frontend/
│   ├── src/
│   │   ├── assets/               # Static images & icons
│   │   ├── services/
│   │   │   └── api.js            # Frontend-to-backend API communication client
│   │   ├── App.jsx               # Landing page with live backend health verification
│   │   ├── index.css             # Tailwind CSS entry point
│   │   └── main.jsx              # React DOM mounting
│   ├── .env                      # Frontend environment variables (VITE_API_BASE_URL)
│   ├── .env.example              # Template for frontend env variables
│   ├── index.html                # Web app HTML shell
│   ├── package.json              # Node dependencies & npm scripts
│   └── vite.config.js            # Vite bundler & Tailwind configuration
│
├── .gitignore                    # Git exclusions (venv, node_modules, .env, DBs)
└── README.md                     # Setup guide and documentation
```

---

## 🗄️ Initial Database Models

The database is built with **SQLAlchemy** and automatically generates the following tables in SQLite upon backend launch:

| Model | Table Name | Columns | Relationships / Notes |
| :--- | :--- | :--- | :--- |
| **Learner** | `learners` | `id`, `display_name` | One-to-many with attempts, masteries, and intervention history |
| **Concept** | `concepts` | `id`, `name`, `description` | e.g. "Linear Equations in One Variable" |
| **Question** | `questions` | `id`, `concept_id`, `prompt`, `correct_answer`, `misconception_rule` | Foreign key to `concepts.id`; stores bug-diagnosis rules |
| **Attempt** | `attempts` | `id`, `learner_id`, `question_id`, `answer`, `is_correct`, `timestamp` | Foreign keys to `learners.id` and `questions.id` |
| **Mastery** | `mastery` | `id`, `learner_id`, `concept_id`, `mastery_probability` | Estimated BKT probability $p(L) \in [0.0, 1.0]$ |
| **InterventionHistory** | `intervention_history` | `id`, `learner_id`, `concept_id`, `intervention_type`, `diagnosis`, `pre_score`, `post_score`, `independent_success`, `timestamp` | Tracks strategy efficacy (hints vs. worked examples vs. visual models) |

---

## 🚀 Getting Started (Windows Setup Guide)

### Prerequisites
Make sure you have installed on Windows:
- **Python 3.10+** (Verify via: `python --version`)
- **Node.js 18+** & npm (Verify via: `node -v` and `npm -v`)

---

### Step 1: Backend Setup (FastAPI & SQLite)

Open PowerShell or Command Prompt in the project root:

```powershell
# 1. Navigate to the backend directory
cd backend

# 2. Create a Python virtual environment named 'venv'
python -m venv venv

# 3. Activate the virtual environment:
# If using Windows PowerShell:
.\venv\Scripts\Activate.ps1
# (Note: If PowerShell says "running scripts is disabled", run:
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned)

# If using Windows Command Prompt (cmd.exe):
# .\venv\Scripts\activate.bat

# 4. Upgrade pip and install backend dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# 5. Check environment file
# .env is already pre-configured, or you can copy .env.example:
# Copy-Item .env.example .env

# 6. Start the FastAPI development server
uvicorn app.main:app --reload --port 8000
```

Once started, the backend is available at:
- **API Root:** [http://localhost:8000/](http://localhost:8000/)
- **Health Check:** [http://localhost:8000/api/health](http://localhost:8000/api/health)
- **Interactive Swagger Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

### Step 2: Frontend Setup (React, Vite & Tailwind CSS)

Open a **new second terminal window** in the project root:

```powershell
# 1. Navigate to the frontend directory
cd frontend

# 2. Install Node dependencies
npm install

# 3. Verify .env file exists
# .env contains: VITE_API_BASE_URL=http://localhost:8000
# Copy-Item .env.example .env

# 4. Start Vite development server
npm run dev
```

Open your browser at:
👉 **[http://localhost:5173/](http://localhost:5173/)**

You will see:
1. The landing page for **Empowering the Individual: Class 8 Math Learning Support**.
2. A **live status indicator** communicating with the FastAPI health endpoint.
3. The "Start Learning" call-to-action button.
4. Live JSON diagnostic output confirming the SQLite database connection.

---

## ⚙️ Environment Configuration

### Backend (`backend/.env`)
```ini
APP_NAME="Empowering the Individual - Learning Support API"
APP_ENV=development
DEBUG=True
PORT=8000
HOST=0.0.0.0
DATABASE_URL=sqlite:///./learning_platform.db
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
LLM_API_KEY=
LLM_PROVIDER=gemini
```

### Frontend (`frontend/.env`)
```ini
VITE_API_BASE_URL=http://localhost:8000
```

---

## 🔍 Health-Check Verification

You can verify the backend directly in PowerShell using:

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/health" -Method Get
```

**Expected JSON Response:**
```json
{
  "status": "ok",
  "app_name": "Empowering the Individual - Learning Support API",
  "environment": "development",
  "database_connected": true,
  "timestamp": "2026-11-03T14:29:55.685214Z",
  "details": {
    "database": "SQLite connected successfully"
  }
}
```

---

## 🧭 Incremental Next Steps for the Hackathon

Now that your boilerplate is running and verified, you can incrementally add:

1. **Seed Data:** Add initial Class 8 Math concepts (e.g. *Linear Equations in One Variable*, *Understanding Quadrilaterals*, *Exponents & Powers*) and diagnostic questions into `questions` and `concepts`.
2. **Bayesian Knowledge Tracing (BKT) Module:** Create `backend/app/ml/bkt.py` with standard parameters ($p(L_0), p(T), p(G), p(S)$) to update student mastery probabilities upon each attempt.
3. **Misconception Classifier:** Add a lightweight evaluation module in `backend/app/core/diagnosis.py` to match student answers against predictable arithmetic/algebraic slips.
4. **Learning Session View:** In the frontend, add the interactive question card, hint scaffold drawer, and independent transfer check screen.

