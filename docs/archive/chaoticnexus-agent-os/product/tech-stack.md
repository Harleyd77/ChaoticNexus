# Project-Specific Tech Stack

## Context

This document overrides and extends the global tech stack standards specifically for PowderApp1.3. It defines the exact versions and configurations used in this project.

## Application Stack

### Core Framework
- **Flask**: 3.0.3 (specified in requirements.txt)
- **Python**: 3.11+ (development environment)
- **PostgreSQL**: 15+ (production database)

### Database & ORM
- **SQLAlchemy**: Latest compatible with Flask 3.0
- **psycopg[binary]**: 3.2.1 (PostgreSQL adapter)
- **Alembic**: For database migrations (if implemented)

### Web Server & Deployment
- **Gunicorn**: 21.2.0 (WSGI server for production)
- **Docker**: For containerized deployment
- **python-dotenv**: 1.0.1 (environment management)

## Development Environment

### Local Development
- **Virtual Environment**: .venv directory
- **IDE**: Cursor with Agent OS integration
- **Debug Mode**: Flask built-in development server
- **Hot Reload**: Enabled for templates and static files

### Database Development
- **Docker Compose**: PostgreSQL container for local development
- **Database Tools**: pgAdmin or command-line tools for inspection
- **Migration Tools**: Custom scripts in tools/ directory

## Production Configuration

### Deployment Strategy
- **Container Registry**: Local or cloud-based registry
- **Orchestration**: Docker Compose for multi-container setup
- **Volumes**: Persistent storage for uploads and database data
- **Networking**: Internal networking between services

### Environment Variables
- **SECRET_KEY**: Flask application secret (must be changed for production)
- **ADMIN_PIN**: Administrative access PIN
- **DATABASE_URL**: PostgreSQL connection string
- **FLASK_ENV**: Set to 'production' in production
- **GUNICORN_WORKERS**: Number of Gunicorn workers

### Security Considerations
- **HTTPS**: Required in production (reverse proxy setup)
- **CORS**: Configured for cross-origin requests if needed
- **CSRF Protection**: Enabled for form submissions
- **Session Security**: Secure session cookie configuration

## File Structure Specifics

### Application Organization
- **Blueprints**: Feature-based organization in src/powder_app/blueprints/
- **Core Utilities**: Shared functionality in src/powder_app/core/
- **Templates**: Jinja2 templates in src/powder_app/templates/
- **Static Assets**: CSS, JS, images in src/powder_app/static/
- **Storage**: User uploads and exports in storage/data/

### Configuration Files
- **requirements.txt**: Python dependencies
- **Dockerfile**: Application container definition
- **docker-compose.postgres.yml**: Database service definition
- **.env**: Environment variables (not committed to version control)

## Performance Optimizations

### Database Performance
- **Connection Pooling**: Configured for multiple concurrent users
- **Query Optimization**: Indexes on frequently queried columns
- **Eager Loading**: Configured for related data to reduce N+1 queries
- **Caching**: Flask-Caching for expensive operations (future enhancement)

### Application Performance
- **Static File Serving**: Efficient serving of CSS/JS/images
- **Template Caching**: Jinja2 template caching in production
- **Compression**: Gzip compression for responses
- **Minification**: CSS/JS minification (future enhancement)

## Monitoring & Logging

### Application Monitoring
- **Error Tracking**: Flask error handlers with logging
- **Performance Metrics**: Basic timing and request logging
- **Health Checks**: Database connectivity and application status endpoints

### Logging Configuration
- **Levels**: DEBUG for development, INFO/WARNING for production
- **Format**: Structured logging with timestamps and context
- **Output**: Console for development, file for production
- **Rotation**: Log rotation for production environments

## Future Technology Considerations

### Potential Upgrades
- **Flask**: Monitor for Flask 3.1+ features and security updates
- **Python**: Plan migration to Python 3.12+ when stable
- **PostgreSQL**: Upgrade to PostgreSQL 16+ for performance improvements
- **Docker**: Keep Docker and Docker Compose updated

### Scalability Technologies
- **Redis**: For caching and session storage (if needed)
- **Celery**: For background task processing (if needed)
- **Nginx**: As reverse proxy for better static file serving
- **Load Balancer**: For multi-instance deployment (future)

### Development Tooling
- **Testing**: pytest for unit and integration tests
- **Linting**: flake8, black for code quality
- **Type Checking**: mypy for static type analysis
- **Documentation**: Sphinx for API documentation

## Maintenance & Updates

### Dependency Management
- **Security Updates**: Regular updates for security vulnerabilities
- **Compatibility Testing**: Test updates in staging environment
- **Version Pinning**: Pin major versions to prevent breaking changes
- **Update Schedule**: Monthly review of dependency updates

### Backup Strategy
- **Database Backups**: Automated daily backups with retention policy
- **Application Backups**: Configuration and code backups
- **Disaster Recovery**: Tested restore procedures
- **Monitoring**: Backup success/failure monitoring

This tech stack configuration ensures PowderApp1.3 remains maintainable, secure, and performant while providing a solid foundation for future enhancements.
