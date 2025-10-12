#!/bin/bash
# Build script for React frontend

echo "🚀 Building React frontend..."

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Build the React app and Tailwind stylesheet
echo "🔨 Building React app..."
npm run build:all

echo "✅ Build complete! Assets available under ./static/"
