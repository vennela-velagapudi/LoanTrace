# API Documentation

The FastAPI backend automatically generates OpenAPI documentation. Once the backend is running, visit:
*   Swagger UI: `http://localhost:8000/docs`
*   ReDoc: `http://localhost:8000/redoc`

## Phase 1 Endpoints (Foundation)
*   `GET /health`: Health check endpoint verifying DB connectivity.
*   `POST /api/auth/token`: JWT login endpoint for the three roles.

Future endpoints are stubbed and documented in `BLUEPRINT.md`.
