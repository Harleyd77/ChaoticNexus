# Code Style Guide

## Context

Python/Flask specific code style rules for PowderApp1.3. These standards override global defaults for this project.

<conditional-block context-check="general-formatting">
IF this General Formatting section already read in current context:
  SKIP: Re-reading this section
  NOTE: "Using General Formatting rules already in context"
ELSE:
  READ: The following formatting rules

## General Formatting

### Indentation
- Use 4 spaces for indentation (never tabs) - following PEP 8
- Maintain consistent indentation throughout files
- Align nested structures for readability

### Naming Conventions
- **Variables and Functions**: Use snake_case (e.g., `user_profile`, `calculate_total`)
- **Classes**: Use PascalCase (e.g., `UserProfile`, `PaymentProcessor`)
- **Constants**: Use UPPER_SNAKE_CASE (e.g., `MAX_RETRY_COUNT`)
- **Modules**: Use snake_case (e.g., `user_authentication.py`)

### String Formatting
- Use f-strings for string interpolation: `f"Hello {name}"`
- Use `.format()` method for complex formatting
- Use single quotes for strings unless the string contains single quotes
- Use triple quotes for docstrings and multi-line strings

### Code Comments
- Add docstrings to all modules, classes, and functions
- Use triple quotes for docstrings following Google style
- Add brief comments above non-obvious business logic
- Document complex algorithms or calculations
- Explain the "why" behind implementation choices
- Never remove existing comments unless removing the associated code
- Update comments when modifying code to maintain accuracy
- Keep comments concise and relevant
</conditional-block>

<conditional-block task-condition="python" context-check="python-style">
IF current task involves writing or updating Python code:
  NOTE: "Following Python PEP 8 standards with Flask-specific conventions"
  - Use type hints for function parameters and return values
  - Import statements: standard library, third-party, then local imports
  - Maximum line length: 88 characters (Black formatter default)
  - Use descriptive variable names over short ones
  - Functions should do one thing and do it well (single responsibility)
  - Use list/dict comprehensions where appropriate for readability
ELSE:
  SKIP: Python style guide not relevant to current task
</conditional-block>

<conditional-block task-condition="html-css" context-check="html-css-style">
IF current task involves writing or updating HTML or CSS:
  IF html-style.md AND css-style.md already in context:
    SKIP: Re-reading these files
    NOTE: "Using HTML/CSS style guides already in context"
  ELSE:
    <context_fetcher_strategy>
      IF current agent is Claude Code AND context-fetcher agent exists:
        USE: @agent:context-fetcher
        REQUEST: "Get HTML formatting rules from code-style/html-style.md"
        REQUEST: "Get CSS rules from code-style/css-style.md"
        PROCESS: Returned style rules
      ELSE:
        READ the following style guides (only if not in context):
        - @.agent-os/standards/code-style/html-style.md (if not in context)
        - @.agent-os/standards/code-style/css-style.md (if not in context)
    </context_fetcher_strategy>
ELSE:
  SKIP: HTML/CSS style guides not relevant to current task
</conditional-block>

<conditional-block task-condition="javascript" context-check="javascript-style">
IF current task involves writing or updating JavaScript:
  IF javascript-style.md already in context:
    SKIP: Re-reading this file
    NOTE: "Using JavaScript style guide already in context"
  ELSE:
    <context_fetcher_strategy>
      IF current agent is Claude Code AND context-fetcher agent exists:
        USE: @agent:context-fetcher
        REQUEST: "Get JavaScript style rules from code-style/javascript-style.md"
        PROCESS: Returned style rules
      ELSE:
        READ: @.agent-os/standards/code-style/javascript-style.md
    </context_fetcher_strategy>
ELSE:
  SKIP: JavaScript style guide not relevant to current task
</conditional-block>

## Flask-Specific Conventions

- Use Blueprint pattern for organizing routes
- Route functions should be concise and focused
- Use `current_app` for configuration access within blueprint routes
- Error handlers should return appropriate HTTP status codes
- Use `url_for()` for generating URLs instead of hardcoding paths
- Database models should inherit from a common base class
- Use SQLAlchemy session management properly with context managers
