# Tech Stack

## Context

Project-specific tech stack for PowderApp1.3 - a Flask web application. These standards override the global defaults for this project.

## Application Stack

- **App Framework**: Flask 3.0+
- **Language**: Python 3.11+
- **Primary Database**: PostgreSQL 15+
- **ORM**: SQLAlchemy with psycopg binary driver
- **Web Server**: Gunicorn WSGI server
- **Development Server**: Flask built-in development server

## Frontend Stack

- **JavaScript Framework**: Vanilla JavaScript (no framework)
- **CSS Framework**: Custom CSS with Bootstrap components
- **Build Tool**: No build process - static files served directly
- **Package Manager**: pip for Python dependencies only

## Hosting & Infrastructure

- **Containerization**: Docker with docker-compose
- **Application Hosting**: Docker containers (development)
- **Database Hosting**: Docker PostgreSQL container
- **Database Backups**: Docker volume persistence
- **Asset Storage**: Local file system (development)
- **Environment Management**: python-dotenv for configuration

## Development Tools

- **IDE**: Cursor with Agent OS integration
- **Version Control**: Git
- **Container Runtime**: Docker Desktop
- **Python Environment**: Virtual environment (.venv)

## Production Considerations

- **WSGI Server**: Gunicorn for production deployment
- **Static Files**: Served by Flask/Nginx in production
- **Database**: PostgreSQL with proper connection pooling
- **Monitoring**: Basic logging with potential for structured logging
