# IT22301: Data Structures and Algorithms — Intelligent One-to-One Learning Support System

An intelligent, student-centered learning support platform engineered for undergraduate engineering students enrolled in **IT22301: Data Structures and Algorithms**.

The system models student skill acquisition through **Bayesian Knowledge Tracing (BKT)**, pinpoints cognitive misconceptions in Java implementations using deterministic rule diagnostics, delivers **4-tier progressive scaffolding**, adaptively selects pedagogical interventions, and interfaces with **Judge0 CE** for sandboxed code execution and **Google Gemini** for Socratic tutoring.

---

## Architectural Principles

1. **Separation of Concerns:**
   - **Learner Intelligence Engine (`backend/app/intelligence/`)** is domain-agnostic and mathematical (BKT, Scaffolding, Adaptive Intervention Selection).
   - **Curriculum Domain (`backend/app/content/`)** encapsulates IT22301 syllabus topics, Java code templates, test vectors, and language-specific misconceptions.
   - **External Integrations (`backend/app/services/`)** are strictly isolated through resilient service clients. No credentials leak to the browser or frontend.
   - **LLM vs. Deterministic Tutoring:** The platform operates reliably with structured pedagogical templates if external LLMs are unavailable, with zero simulated or fake connections.
2. **Database Portability:**
   - Starts out of the box with zero-configuration **SQLite**.
   - Built with database-agnostic SQLAlchemy 2.0 types and pooled connection parameters for drop-in migration to **PostgreSQL**.
3. **Restrained, Professional Academic UX:**
   - Built with **React 19**, **Vite**, **Tailwind CSS**, **Monaco Editor**, and **Recharts**.
   - No decorative animations or emojis. Clean, high-contrast, accessible typography tailored for engineering education.

---

## System Architecture

```text
                                  +---------------------------------------+
                                  |         React 19 + Vite Frontend      |
                                  |   (Monaco Editor, Recharts, Tailwind) |
                                  +-------------------+-------------------+
                                                      |
                                           REST API (Axios / JSON)
                                                      |
                                  +-------------------v-------------------+
                                  |         FastAPI Modular Backend       |
                                  +---------+-------------------+---------+
                                            |                   |
                        +-------------------+--+             +--+-------------------+
                        |   Domain Content     |             |  Cognitive Engine    |
                        |   (IT22301 Syllabus, |             |  (Bayesian Knowledge |
                        |    Java Tests, Bugs) |             |   Tracing, 4-Tier    |
                        +----------------------+             |   Scaffolding, Bandits|
                                                             +----------------------+
                                            |                   |
                        +-------------------+--+             +--+-------------------+
                        |   Service Clients    |             |  Persistence Layer   |
                        |   - Judge0 CE        |             |  - SQLite (Dev)      |
                        |   - Google Gemini    |             |  - PostgreSQL (Prod) |
                        +----------------------+             +----------------------+
```

---

## Directory Structure

```text
Adaptive AI learning platform/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI initialization, CORS & exception filters
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py            # Pydantic Settings & environment validation
│   │   │   ├── database.py          # SQLAlchemy engine, session maker & init_db
│   │   │   └── logging.py           # Structured application logger
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── learner.py           # Student entity
│   │   │   ├── concept.py           # IT22301 syllabus concepts
│   │   │   ├── problem.py           # DSA coding problems & test cases
│   │   │   ├── submission.py        # Code submissions & execution metrics
│   │   │   ├── knowledge_state.py   # BKT parameters: p(L0), p(T), p(G), p(S)
│   │   │   └── intervention_log.py  # Efficacy tracking of scaffolding hints
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── common.py            # Unified ApiResponse envelope
│   │   │   ├── learner.py           # Student request/response schemas
│   │   │   ├── concept.py           # Concept schemas with mastery overlays
│   │   │   ├── problem.py           # Problem details & test cases
│   │   │   ├── submission.py        # Code submission & test evaluation results
│   │   │   ├── intelligence.py      # BKT updates, scaffolding & diagnoses
│   │   │   └── health.py            # System & external service health statuses
│   │   ├── intelligence/
│   │   │   ├── __init__.py
│   │   │   ├── bkt_engine.py        # Pure Bayesian Knowledge Tracing mathematics
│   │   │   ├── scaffolding.py       # 4-tier progressive scaffolding engine
│   │   │   ├── misconception_engine.py # Rule-based diagnostic evaluator
│   │   │   └── intervention_selector.py# Adaptive pedagogical strategy selector
│   │   ├── content/
│   │   │   ├── __init__.py
│   │   │   ├── curriculum.py        # IT22301 Units 1-4 syllabus structure
│   │   │   ├── dsa_misconceptions.py# Java DSA cognitive bug catalog
│   │   │   └── seed_data.py         # Starter curriculum & benchmark problems
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── gemini_service.py    # Resilient Google Gemini HTTPX client
│   │   │   └── judge0_service.py    # Resilient Judge0 CE Java execution client
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── api.py               # Master API v1 router
│   │   │   ├── health_routes.py     # /api/v1/health probe
│   │   │   ├── concept_routes.py    # /api/v1/concepts
│   │   │   ├── problem_routes.py    # /api/v1/problems
│   │   │   ├── execution_routes.py  # /api/v1/execution/run
│   │   │   ├── tutoring_routes.py   # /api/v1/tutoring/scaffold & diagnose
│   │   │   └── learner_routes.py    # /api/v1/learners/:id/profile
│   │   └── utilities/
│   │       ├── __init__.py
│   │       ├── response.py          # Unified response helper functions
│   │       └── exceptions.py        # Domain-level application exceptions
│   ├── tests/
│   │   ├── conftest.py              # In-memory SQLite fixtures & TestClient
│   │   ├── test_health.py           # Health and discovery tests
│   │   ├── test_bkt_engine.py       # Unit tests for BKT probability math
│   │   └── test_misconceptions.py   # Diagnostic rule evaluation tests
│   ├── .env                         # Local backend environment variables
│   ├── .env.example                 # Template for backend settings
│   ├── pytest.ini                   # Pytest configuration
│   └── requirements.txt             # Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── layout/              # Navbar, Footer, AppLayout
│   │   │   ├── ui/                  # Button, Card, Badge, StatCard, ProgressBar
│   │   │   └── workspace/           # CodeEditor (Monaco), ScaffoldingPanel, TestResults
│   │   ├── pages/
│   │   │   ├── DashboardPage.jsx    # Curriculum overview & problem catalog
│   │   │   ├── WorkspacePage.jsx    # Java coding workspace & scaffolding tutor
│   │   │   ├── AnalyticsPage.jsx    # Recharts BKT cognitive visualizations
│   │   │   ├── SettingsPage.jsx     # Service status & architectural monitor
│   │   │   └── NotFoundPage.jsx     # 404 handler
│   │   ├── router/
│   │   │   └── AppRouter.jsx        # React Router route definitions
│   │   ├── services/
│   │   │   ├── apiClient.js         # Unified Axios HTTP client with interceptors
│   │   │   ├── curriculumService.js # Concepts & problems API calls
│   │   │   ├── executionService.js  # Code running & evaluation calls
│   │   │   ├── tutoringService.js   # Scaffolding hints & diagnoses
│   │   │   ├── learnerService.js    # Student mastery profiles
│   │   │   └── healthService.js     # Health probe calls
│   │   ├── App.jsx                  # Root React component
│   │   ├── main.jsx                 # React DOM mount point
│   │   └── index.css                # Tailwind CSS entry
│   ├── .env                         # Local frontend environment variables
│   ├── .env.example                 # Template for frontend settings
│   ├── index.html                   # HTML entry file
│   ├── package.json                 # Node dependencies & build scripts
│   └── vite.config.js               # Vite bundler & Tailwind configuration
│
├── .gitignore                       # Git exclusions (venv, node_modules, DBs, .env)
└── README.md                        # Master documentation
```

---

## Getting Started (Windows Guide)

### Prerequisites
Verify that the required runtimes are installed on your system:
- **Python 3.10+** (Tested on Python 3.12: `python --version`)
- **Node.js 18+** & npm (Tested on Node 24: `node -v` and `npm -v`)

---

### Step 1: Backend Setup (FastAPI & SQLite)

Open **Terminal 1** (PowerShell or Command Prompt):

```powershell
# 1. Navigate to the backend directory
cd "c:\Projects\AI-ML Projects\Adaptive AI learning platform\backend"

# 2. Create Python virtual environment
python -m venv venv

# 3. Activate the virtual environment
# In Windows PowerShell:
.\venv\Scripts\Activate.ps1
# (If script execution is disabled in PowerShell, execute:
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned)

# In Windows Command Prompt (cmd.exe):
# .\venv\Scripts\activate.bat

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run backend unit tests to verify BKT math and endpoints
pytest -v

# 6. Start the FastAPI development server
uvicorn app.main:app --reload --port 8000
```

The backend server is now running at:
- **API Root:** [http://localhost:8000/](http://localhost:8000/)
- **Swagger Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Endpoint:** [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

---

### Step 2: Frontend Setup (React, Vite, Monaco & Tailwind)

Open **Terminal 2**:

```powershell
# 1. Navigate to the frontend directory
cd "c:\Projects\AI-ML Projects\Adaptive AI learning platform\frontend"

# 2. Install Node dependencies
npm install

# 3. Start the Vite development server
npm run dev
```

Open your browser to:
**[http://localhost:5173/](http://localhost:5173/)**

---

## Cognitive Model Specification

### 1. Bayesian Knowledge Tracing (BKT)
Latent knowledge probability $P(L_t)$ is updated after every problem execution:

$$\text{Posterior: } P(L_t \mid \text{Obs}) = \begin{cases} \frac{P(L_t) \cdot (1 - P(S))}{P(L_t) \cdot (1 - P(S)) + (1 - P(L_t)) \cdot P(G)}, & \text{if Correct} \\ \frac{P(L_t) \cdot P(S)}{P(L_t) \cdot P(S) + (1 - P(L_t)) \cdot (1 - P(G))}, & \text{if Incorrect} \end{cases}$$

$$\text{Next Prior: } P(L_{t+1}) = P(L_t \mid \text{Obs}) + (1 - P(L_t \mid \text{Obs})) \cdot P(T)$$

- **Default Parameters:** $P(L_0) = 0.20$, $P(T) = 0.15$, $P(G) = 0.15$, $P(S) = 0.10$.
- **Mastery Threshold:** $P(L_t) \ge 0.85$.

### 2. 4-Tier Progressive Scaffolding
- **Tier 1 (Conceptual Orientation):** Reflective prompts highlighting invariants and boundary conditions.
- **Tier 2 (Algorithmic Blueprint):** High-level pseudocode mapping state transformations.
- **Tier 3 (Concrete State Trace):** Step-by-step variable/pointer transitions on failing test vectors.
- **Tier 4 (Code Skeleton):** Scaffolded Java code with targeted blanks for student completion.

---

## Database Migration Path (SQLite -> PostgreSQL)

To migrate from local SQLite to PostgreSQL:

1. Install `psycopg2-binary` in the backend virtual environment:
   ```powershell
   pip install psycopg2-binary
   ```
2. Update `DATABASE_URL` in `backend/.env`:
   ```ini
   DATABASE_URL=postgresql+psycopg2://<user>:<password>@<host>:5432/<database_name>
   ```
3. Restart the FastAPI server. `init_db()` will automatically initialize tables with PostgreSQL-compatible schema types.

---

## Primary API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/health` | Comprehensive system health check and service latency probe |
| `GET` | `/api/v1/concepts` | List all IT22301 curriculum concepts with current student mastery |
| `GET` | `/api/v1/problems` | List active DSA practice problems |
| `GET` | `/api/v1/problems/{id}` | Retrieve problem workspace details, Java starter code, and test cases |
| `POST` | `/api/v1/execution/run` | Execute Java code via Judge0 CE, diagnose bugs, and update BKT state |
| `POST` | `/api/v1/tutoring/scaffold` | Generate progressive scaffolding hints (Tiers 1 to 4) |
| `POST` | `/api/v1/tutoring/diagnose` | Evaluate student code against IT22301 misconception rule catalog |
| `GET` | `/api/v1/learners/{id}/profile`| Student profile and multidimensional BKT mastery statistics |

