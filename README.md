# Todo AI

A modern, full-stack Todo application with category support, built with FastAPI and React.

## Tech Stack

### Backend

- **Python 3.11+** with **FastAPI** — async REST API
- **SQLAlchemy 2.x** (async) — ORM with 3-layer architecture (Routes → Services → Repositories)
- **SQL Server** via aioodbc — database
- **Alembic** — schema migrations
- **Pydantic v2** — request/response validation

### Frontend

- **React 19** with **TypeScript** (strict mode)
- **Vite** — bundler and dev server
- **TanStack React Query** — server state management
- **Axios** — HTTP client

## Project Structure

```
Todo_AI/
├── api/                     # FastAPI backend
│   ├── app/
│   │   ├── main.py          # App factory, CORS, routes
│   │   ├── db/              # Async DB session & dependency injection
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── routes/          # API route handlers
│   │   ├── services/        # Business logic
│   │   ├── repositories/    # SQLAlchemy queries
│   │   └── schemas/         # Pydantic schemas
│   ├── alembic/             # Database migrations
│   ├── tests/               # pytest test suite
│   └── requirements.txt
├── web/                     # React TypeScript frontend
│   ├── src/
│   │   ├── pages/           # Page components
│   │   ├── components/      # Reusable UI components
│   │   ├── hooks/           # React Query hooks (one per domain)
│   │   ├── services/        # Axios API client layer
│   │   ├── types/           # TypeScript interfaces
│   │   └── utils/           # Utility functions
│   ├── public/              # Static assets
│   └── package.json
└── .github/                 # AI prompts, instructions, skills
```

## Prerequisites

- Python 3.11+
- Node.js (LTS)
- SQL Server instance (localhost:1433)
- [ODBC Driver 17 for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

## Getting Started

### Backend

```bash
cd api

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure database
cp .env.example .env
# Edit .env with your SQL Server credentials

# Run migrations
alembic upgrade head

# Start the API server
uvicorn app.main:app --reload --host localhost --port 8000
```

### Frontend

```bash
cd web

# Install dependencies
npm install

# (Optional) Configure API URL
cp .env.example .env

# Start dev server
npm run dev
```

The frontend runs at `http://localhost:5173` and proxies `/api` requests to the backend at `http://localhost:8000`.

## Development

### Backend Commands

| Command | Description |
|---|---|
| `uvicorn app.main:app --reload` | Start dev server with hot reload |
| `alembic revision --autogenerate -m "msg"` | Generate migration from model changes |
| `alembic upgrade head` | Apply all pending migrations |
| `pytest tests/` | Run test suite |

### Frontend Commands

| Command | Description |
|---|---|
| `npm run dev` | Start dev server with HMR |
| `npm run build` | Type-check and build for production |
| `npm run preview` | Preview production build |
| `npm run lint` | Run ESLint |

## Environment Variables

### Backend (`api/.env`)

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | SQL Server async connection string | — |

### Frontend (`web/.env`)

| Variable | Description | Default |
|---|---|---|
| `VITE_API_URL` | Backend API base URL | `http://localhost:8000` |

## License

This project is for personal use.
