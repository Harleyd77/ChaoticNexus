#!/bin/bash
# Run ChaoticNexus in development mode with SQLite

cd "$(dirname "$0")"

# Create storage directory if it doesn't exist
mkdir -p storage

# Activate virtual environment
source .venv/bin/activate

# Load local development environment
export $(grep -v '^#' .env.local | xargs)

# Set Flask app
export FLASK_APP=app.wsgi:app

# Run database migrations if needed
echo "Running database migrations..."
flask db upgrade || echo "Note: Migrations may need initialization"

# Start the Flask development server
echo "Starting ChaoticNexus on http://localhost:5000"
python -m flask run --host=0.0.0.0 --port=5000 --debug
