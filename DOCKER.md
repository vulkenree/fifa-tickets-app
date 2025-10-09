# Docker Deployment Guide

This guide explains how to deploy the FIFA 2026 Ticket Management App using Docker containers for production environments.

## Table of Contents

- [Quick Start](#quick-start)
- [Building the Docker Image](#building-the-docker-image)
- [Running with Docker Compose](#running-with-docker-compose)
- [Running with Docker](#running-with-docker)
- [Environment Variables](#environment-variables)
- [Data Persistence](#data-persistence)
- [Platform Deployment](#platform-deployment)
- [Health Checks](#health-checks)
- [Security Best Practices](#security-best-practices)

## Quick Start

The fastest way to run the app in Docker:

```bash
# Build and run with docker-compose
docker-compose up -d

# Access the app at http://localhost:8000
```

## Building the Docker Image

### Basic Build

```bash
docker build -t fifa-tickets-app:latest .
```

### Multi-platform Build (for deployment)

```bash
docker buildx build --platform linux/amd64,linux/arm64 -t fifa-tickets-app:latest .
```

## Running with Docker Compose

Docker Compose is the easiest way to run the app locally for testing.

### Start the Application

```bash
docker-compose up -d
```

### View Logs

```bash
docker-compose logs -f
```

### Stop the Application

```bash
docker-compose down
```

### Stop and Remove Data

```bash
docker-compose down -v
```

## Running with Docker

### Run the Container

```bash
docker run -d \
  --name fifa-tickets-app \
  -p 8000:8000 \
  -e FLASK_ENV=production \
  -e SECRET_KEY=your-secret-key-here \
  -v $(pwd)/data:/app/data \
  fifa-tickets-app:latest
```

### View Container Logs

```bash
docker logs -f fifa-tickets-app
```

### Stop and Remove Container

```bash
docker stop fifa-tickets-app
docker rm fifa-tickets-app
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `FLASK_ENV` | No | `production` | Flask environment (production/development) |
| `SECRET_KEY` | **Yes** | - | Secret key for session management and security |
| `PORT` | No | `8000` | Port the application listens on |
| `DATABASE_URL` | No | `sqlite:////app/data/fifa_tickets.db` | Database connection string |

### Setting Environment Variables

**With docker-compose:**
```yaml
environment:
  - FLASK_ENV=production
  - SECRET_KEY=your-secret-key
```

**With docker run:**
```bash
docker run -e FLASK_ENV=production -e SECRET_KEY=your-secret-key fifa-tickets-app
```

**With .env file:**
```bash
# Create .env file
echo "SECRET_KEY=your-secret-key-here" > .env

# Use with docker-compose
docker-compose --env-file .env up
```

## Data Persistence

The application uses SQLite for data storage. To persist data between container restarts, mount a volume:

### With Docker Compose

```yaml
volumes:
  - ./data:/app/data
```

### With Docker Run

```bash
docker run -v $(pwd)/data:/app/data fifa-tickets-app
```

### Backup Database

```bash
# Copy database from container
docker cp fifa-tickets-app:/app/data/fifa_tickets.db ./backup-$(date +%Y%m%d).db
```

### Restore Database

```bash
# Copy database to container
docker cp ./backup-20251009.db fifa-tickets-app:/app/data/fifa_tickets.db

# Restart container
docker restart fifa-tickets-app
```

## Platform Deployment

### Railway

1. **Push your code to GitHub**

2. **Connect to Railway:**
   - Go to [railway.app](https://railway.app)
   - Click "Deploy from GitHub repo"
   - Select your repository

3. **Configure environment variables:**
   ```
   FLASK_ENV=production
   SECRET_KEY=your-generated-secret-key
   ```

4. **Railway will automatically:**
   - Detect the Dockerfile
   - Build the image
   - Deploy the container
   - Provide a public URL

5. **Health check path:** `/health`

### Render

1. **Create a new Web Service:**
   - Go to [render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure the service:**
   - **Environment:** Docker
   - **Build Command:** (auto-detected)
   - **Start Command:** (auto-detected from Dockerfile)

3. **Set environment variables:**
   ```
   FLASK_ENV=production
   SECRET_KEY=your-generated-secret-key
   ```

4. **Deploy!**

### Heroku

1. **Install Heroku CLI and login:**
   ```bash
   heroku login
   ```

2. **Create a new app:**
   ```bash
   heroku create your-app-name
   ```

3. **Set environment variables:**
   ```bash
   heroku config:set FLASK_ENV=production
   heroku config:set SECRET_KEY=your-secret-key
   ```

4. **Deploy with Docker:**
   ```bash
   heroku container:push web
   heroku container:release web
   ```

5. **Open the app:**
   ```bash
   heroku open
   ```

### DigitalOcean App Platform

1. **Create a new app:**
   - Go to [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
   - Click "Create App"
   - Connect your GitHub repository

2. **Configure:**
   - **Type:** Docker
   - **Dockerfile Path:** `Dockerfile`
   - **HTTP Port:** `8000`

3. **Add environment variables:**
   ```
   FLASK_ENV=production
   SECRET_KEY=your-secret-key
   ```

4. **Launch!**

### Google Cloud Run

1. **Build and push to Google Container Registry:**
   ```bash
   gcloud builds submit --tag gcr.io/your-project-id/fifa-tickets-app
   ```

2. **Deploy to Cloud Run:**
   ```bash
   gcloud run deploy fifa-tickets-app \
     --image gcr.io/your-project-id/fifa-tickets-app \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars FLASK_ENV=production,SECRET_KEY=your-secret-key
   ```

### AWS ECS/Fargate

1. **Build and push to ECR:**
   ```bash
   aws ecr create-repository --repository-name fifa-tickets-app
   docker tag fifa-tickets-app:latest your-account.dkr.ecr.region.amazonaws.com/fifa-tickets-app:latest
   docker push your-account.dkr.ecr.region.amazonaws.com/fifa-tickets-app:latest
   ```

2. **Create ECS task definition and service** (via AWS Console or CLI)

3. **Set environment variables in task definition**

## Health Checks

The application provides health check endpoints for monitoring:

### Basic Health Check
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-09T16:00:00",
  "service": "FIFA 2026 Ticket App",
  "version": "1.0.0",
  "database": "connected"
}
```

### Simple Ping
```bash
curl http://localhost:8000/ping
```

### Docker Health Check

The Dockerfile includes a health check that runs automatically:
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1
```

## Security Best Practices

### 1. Generate a Strong SECRET_KEY

```python
python -c "import secrets; print(secrets.token_hex(32))"
```

### 2. Change Default Admin Password

After first login, change the default admin password (`admin`/`admin123`).

### 3. Use HTTPS

Always deploy behind HTTPS in production. Most platforms (Railway, Render, etc.) provide this automatically.

### 4. Regular Updates

Keep your dependencies updated:
```bash
# Update local dependencies
uv sync --upgrade

# Rebuild Docker image
docker build -t fifa-tickets-app:latest .
```

### 5. Environment Variables

Never commit `.env` files or hardcode secrets in code. Use platform-specific secret management.

### 6. Database Backups

Regularly backup your database:
```bash
# Automated backup script
#!/bin/bash
docker cp fifa-tickets-app:/app/data/fifa_tickets.db ./backups/fifa_tickets-$(date +%Y%m%d-%H%M%S).db
```

### 7. Resource Limits

Set resource limits in docker-compose:
```yaml
deploy:
  resources:
    limits:
      cpus: '1'
      memory: 512M
```

## Troubleshooting

### Container Won't Start

Check logs:
```bash
docker logs fifa-tickets-app
```

### Database Permission Errors

Ensure the data directory is writable:
```bash
mkdir -p ./data
chmod 755 ./data
```

### Health Check Failing

Test the health endpoint:
```bash
curl -v http://localhost:8000/health
```

### Port Already in Use

Change the port mapping:
```bash
docker run -p 8080:8000 fifa-tickets-app
```

## Development vs Production

| Feature | Development (uv) | Production (Docker) |
|---------|------------------|---------------------|
| Command | `uv run python app.py` | `docker-compose up` |
| Server | Flask dev server | Gunicorn |
| Hot Reload | ✅ Yes | ❌ No |
| Debug Mode | ✅ On | ❌ Off |
| Dependencies | Auto-managed by uv | Baked into image |
| Setup Time | Very fast | Slower (build once) |
| Use Case | Local development | Production deployment |

## Need Help?

- Check [README.md](README.md) for local development setup
- Review [app.py](app.py) for application configuration
- Open an issue on GitHub for support

---

**Ready to deploy?** Choose your platform above and follow the step-by-step instructions!
