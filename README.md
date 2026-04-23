# Meusaldo

A WhatsApp-first personal and couple finance tracker for the Brazilian market.

## Architecture
- **Frontend:** Next.js (React) 
- **Backend:** Python (FastAPI) + LiteLLM + SQLAlchemy

## VPS Deployment Guide

This project uses **PM2** to manage the processes on your VPS.

### 1. Initial VPS Setup
Make sure your VPS has Node.js, Python 3, and PM2 installed:
```bash
sudo apt update
sudo apt install nodejs npm python3 python3-venv nginx -y
sudo npm install -g pm2
```

### 2. Deploying
Simply run the deploy script. It will pull the code, install dependencies, build the Next.js app, and restart the PM2 processes.
```bash
chmod +x deploy.sh
./deploy.sh
```

### 3. Ports
To avoid conflicts with your other services, the apps run on custom ports defined in `ecosystem.config.js`:
- **Frontend (Next.js):** `3016`
- **Backend (FastAPI):** `8015`

### 4. Nginx Reverse Proxy Setup
To route `meusaldo.linkwise.digital` to your app, create an Nginx configuration file (`/etc/nginx/sites-available/meusaldo`):

```nginx
server {
    listen 80;
    server_name meusaldo.linkwise.digital;

    # Route /api to the FastAPI Backend
    location /api/ {
        proxy_pass http://127.0.0.1:8015/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Route everything else to the Next.js Frontend
    location / {
        proxy_pass http://127.0.0.1:3016;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site and secure it with SSL:
```bash
sudo ln -s /etc/nginx/sites-available/meusaldo /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
sudo certbot --nginx -d meusaldo.linkwise.digital
```

## Running Locally
**Frontend:**
```bash
cd frontend
npm run dev
```

**Backend:**
```bash
cd backend
source venv/Scripts/activate  # Or venv/bin/activate on Linux
pip install -r requirements.txt
uvicorn main:app --reload
```