#!/bin/bash

echo "🚀 Starting Bitcoin Trading Signals deployment..."

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

echo "✅ Dependencies installed successfully!"
echo "🌟 Ready to start the application!"
