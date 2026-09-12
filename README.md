# Flood Emergency Response System

Transform emergency flood response from reactive data interpretation to proactive decision intelligence, enabling coordinators to protect vulnerable populations through rapid, justified actions.

## Product Vision

This system empowers emergency coordinators, hospital administrators, and city emergency managers to make rapid, data-driven flood response decisions that protect vulnerable populations.

## Target Audience

- Emergency coordinators
- Hospital administrators  
- City emergency managers
- First responders responsible for flood response

## Core Features

- **Location Management**: Track hospitals, shelters, and critical infrastructure
- **Alert System**: Create and manage flood alerts with severity levels
- **Decision Intelligence**: Document recommended actions with justifications
- **Real-time Monitoring**: Track water levels and affected populations

## Technology Stack

- **Backend**: FastAPI (Python)
- **Database**: SQLite (SQLAlchemy ORM)
- **API**: RESTful API with automatic OpenAPI documentation
- **Architecture**: Modular Monolith

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
cd /app/user_workspace/team_048/0a6dc5d9-ed09-499c-8c8d-0fe143c72027
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r backend/requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Running the Application

### Development Mode

Start the FastAPI development server:

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive API docs (Swagger): http://localhost:8000/docs
- Alternative API docs (ReDoc): http://localhost:8000/redoc

### Production Mode

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Locations

- `POST /api/v1/locations` - Create a new location
- `GET /api/v1/locations` - List all locations (with filtering)
- `GET /api/v1/locations/{id}` - Get a specific location
- `PUT /api/v1/locations/{id}` - Update a location
- `DELETE /api/v1/locations/{id}` - Delete a location

### Alerts

- `POST /api/v1/alerts` - Create a new alert
- `GET /api/v1/alerts` - List all alerts (with filtering)
- `GET /api/v1/alerts/{id}` - Get a specific alert
- `PUT /api/v1/alerts/{id}` - Update an alert
- `DELETE /api/v1/alerts/{id}` - Delete an alert

### Health Check

- `GET /health` - Check API health status

## Database Schema

### Location Model
- Tracks vulnerable locations (hospitals, shelters, critical infrastructure)
- Stores capacity, occupancy, and contact information
- Includes geolocation data (latitude/longitude)

### Alert Model
- Manages flood alerts and evacuation orders
- Links to specific locations
- Tracks severity levels, water levels, and affected populations
- Documents recommended actions with justifications

## Environment Variables

See `.env.example` for all available configuration options:

- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: Secret key for security (change in production)
- `ALLOWED_ORIGINS`: CORS allowed origins
- `DEBUG`: Enable/disable debug mode

## Project Structure

```
.
├── backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── database.py          # Database connection and session
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas for validation
│   └── routers/
│       ├── __init__.py
│       ├── alerts.py        # Alert endpoints
│       └── locations.py     # Location endpoints
├── .env.example             # Environment variables template
├── README.md                # This file
└── requirements.txt         # Python dependencies
```

## Development Guidelines

### Adding New Features

1. Define models in `backend/models.py`
2. Create Pydantic schemas in `backend/schemas.py`
3. Implement routes in `backend/routers/`
4. Register routes in `backend/main.py`

### Code Quality

- Follow PEP 8 style guidelines
- Add logging for important operations
- Include error handling for all database operations
- Validate input using Pydantic schemas
- Document API endpoints with docstrings

## Security Considerations

- Change `SECRET_KEY` in production
- Use environment variables for sensitive data
- Enable HTTPS in production
- Implement rate limiting for production use
- Add authentication/authorization as needed

## Support

For issues or questions, please refer to the API documentation at `/docs` when the server is running.
