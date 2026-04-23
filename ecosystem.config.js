module.exports = {
  apps: [
    {
      name: 'meusaldo-frontend',
      script: 'npm',
      args: 'start -- -p 3016',
      cwd: './frontend',
      env: {
        NODE_ENV: 'production',
        NEXT_PUBLIC_API_URL: 'https://meusaldo.linkwise.digital/api'
      }
    },
    {
      name: 'meusaldo-backend',
      script: './backend/venv/bin/uvicorn',
      args: 'backend.main:app --host 127.0.0.1 --port 8015',
      cwd: './',
      interpreter: 'none',
      env: {
        NODE_ENV: 'production',
        DATABASE_URL: 'sqlite:///./backend/meusaldo.db'
      }
    }
  ]
};
