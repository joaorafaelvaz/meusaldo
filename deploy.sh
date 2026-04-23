#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "🚀 Deploying Meusaldo MVP..."

echo "📥 Pulling latest code from git..."
# git pull origin main

echo "📦 Building Frontend (Next.js)..."
cd frontend
npm install
npm run build
cd ..

echo "🐍 Setting up Backend (FastAPI)..."
cd backend
if [ ! -d "venv" ]; then
    echo "Creating python virtual environment..."
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt
# Run alembic migrations here in the future
# alembic upgrade head
deactivate
cd ..

echo "🔄 Restarting services via PM2..."
# This requires PM2 to be installed globally on the VPS (npm install -g pm2)
pm2 startOrRestart ecosystem.config.js --env production

echo "🌐 Updating Nginx configuration..."
sudo cp meusaldo.nginx.conf /etc/nginx/sites-available/meusaldo
sudo ln -sf /etc/nginx/sites-available/meusaldo /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

echo "✅ Deploy complete!"
echo "➡️  Frontend running on http://127.0.0.1:3016"
echo "➡️  Backend running on http://127.0.0.1:8015"
