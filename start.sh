#!/bin/bash

echo "🚀 Starting Credit Risk Assessment System..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9+ first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "📦 Installing backend dependencies..."
cd backend
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt

echo "📦 Installing frontend dependencies..."
cd ../frontend
npm install

echo "🔧 Setting up environment..."
cd ../backend
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit backend/.env and add your OpenAI API key"
fi

echo "🌐 Starting backend server..."
cd ../backend
source venv/bin/activate
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo "🌐 Starting frontend server..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo "✅ Credit Risk Assessment System is starting up!"
echo "📊 Backend API: http://localhost:8000"
echo "🌐 Frontend: http://localhost:5173"
echo "📚 API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for user to stop
trap "echo '🛑 Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
