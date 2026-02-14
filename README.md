# Pitwall

An F1 Manager game built with Electron (Frontend) and Python (Backend).

## Project Structure

- **frontend/**: Electron + Vanilla JS frontend.
- **backend/**: Python + SQLite backend, using Pydantic for data models.

## Setup

### Prerequisites
- Node.js
- Python 3.12+
- `uv` (Python package manager)

### Installation

1.  **Frontend**:
    ```bash
    cd frontend
    npm install
    ```

2.  **Backend**:
    ```bash
    cd backend
    uv sync
    ```

## Running the Game

```bash
cd frontend
npm start
```

## Running Tests

### Backend (pytest)
Contains unit and integration tests for game logic.

```bash
cd backend
uv run pytest
```

### Frontend (vitest)
Contains component tests for UI logic.

```bash
cd frontend
npm test
```
