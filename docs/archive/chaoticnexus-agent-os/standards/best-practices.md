# Development Best Practices

## Context

Python/Flask specific development guidelines for PowderApp1.3. These standards override global defaults for this project.

<conditional-block context-check="core-principles">
IF this Core Principles section already read in current context:
  SKIP: Re-reading this section
  NOTE: "Using Core Principles already in context"
ELSE:
  READ: The following principles

## Core Principles

### Keep It Simple
- Implement code in the fewest lines possible
- Avoid over-engineering solutions
- Choose straightforward approaches over clever ones

### Optimize for Readability
- Prioritize code clarity over micro-optimizations
- Write self-documenting code with clear variable names
- Add comments for "why" not "what"

### DRY (Don't Repeat Yourself)
- Extract repeated business logic to utility functions
- Extract repeated database queries to repository classes
- Create reusable Flask blueprints for common functionality

### File Structure
- Keep files focused on a single responsibility
- Group related functionality together
- Use consistent naming conventions
</conditional-block>

## Python/Flask Specific Practices

### Application Structure
- Use Flask blueprints to organize routes by feature
- Keep route handlers thin - move business logic to service classes
- Use dependency injection for better testability
- Implement proper error handling with custom error pages

### Database Layer
- Use SQLAlchemy ORM with proper session management
- Create repository pattern for data access
- Use migrations for database schema changes
- Implement proper foreign key relationships

### Testing
- Write unit tests for all business logic functions
- Use pytest as the testing framework
- Mock external dependencies in tests
- Aim for high test coverage (>80%)

### Security
- Use Flask-WTF for form validation
- Implement CSRF protection
- Use secure password hashing (Werkzeug security)
- Validate and sanitize all user inputs

### Performance
- Use Flask-Caching for expensive operations
- Implement database query optimization
- Use connection pooling for PostgreSQL
- Minimize database queries with proper eager loading

<conditional-block context-check="dependencies" task-condition="choosing-external-library">
IF current task involves choosing an external library:
  IF Dependencies section already read in current context:
    SKIP: Re-reading this section
    NOTE: "Using Dependencies guidelines already in context"
  ELSE:
    READ: The following guidelines
ELSE:
  SKIP: Dependencies section not relevant to current task

## Dependencies

### Choose Libraries Wisely
When adding third-party dependencies:
- Select the most popular and actively maintained option
- Check the library's GitHub repository for:
  - Recent commits (within last 6 months)
  - Active issue resolution
  - Number of stars/downloads
  - Clear documentation
- For Flask extensions, prefer those with "Flask-" prefix
- Keep dependencies minimal to reduce security surface area
</conditional-block>

## Code Quality

### Static Analysis
- Use flake8 for PEP 8 compliance checking
- Use mypy for type checking
- Use black for code formatting
- Run these tools in CI/CD pipeline

### Documentation
- Write comprehensive docstrings for all modules, classes, and functions
- Use Sphinx for generating documentation
- Keep README.md updated with setup and development instructions
- Document API endpoints with examples
