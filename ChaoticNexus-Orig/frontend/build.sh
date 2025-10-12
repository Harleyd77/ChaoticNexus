#!/bin/bash
# Build script for React frontend

echo "🚀 Building React frontend..."

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Build the React app
echo "🔨 Building React app..."
npm run build

echo "✅ Build complete! React app built to ../src/powder_app/static/dist/"
