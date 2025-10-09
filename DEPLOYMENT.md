# FIFA 2026 Ticket App - Production Deployment Guide

This guide covers multiple deployment options for the FIFA 2026 Ticket Management App.

## 🚀 Quick Deploy Options

### Option 1: Railway (Recommended - Easiest)

Railway provides the simplest deployment with automatic builds and zero configuration.

1. **Create Railway Account**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub

2. **Deploy from GitHub**
   - Connect your GitHub repository
   - Railway will automatically detect the Python app
   - Set environment variables in Railway dashboard:
     ```
     FLASK_ENV=production
     SECRET_KEY=your-super-secret-key-here
     ```

3. **Access Your App**
   - Railway provides a public URL automatically
   - Your app will be live in minutes!

### Option 2: Render (Free Tier Available)

1. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub

2. **Create Web Service**
   - Connect your GitHub repository
   - Configure build settings:
     - **Build Command**: `uv sync`
     - **Start Command**: `./start.sh`
   - Set environment variables:
     ```
     FLASK_ENV=production
     SECRET_KEY=your-super-secret-key-here
     ```

3. **Deploy**
   - Click "Create Web Service"
   - Render will build and deploy automatically

### Option 3: Heroku (Classic Platform)

1. **Install Heroku CLI**
   ```bash
   # macOS
   brew install heroku/brew/heroku
   
   # Windows
   # Download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Create Heroku App**
   ```bash
   heroku create your-fifa-tickets-app
   ```

3. **Set Environment Variables**
   ```bash
   heroku config:set FLASK_ENV=production
   heroku config:set SECRET_KEY=your-super-secret-key-here
   ```

4. **Deploy**
   ```bash
   git push heroku main
   ```

### Option 4: DigitalOcean App Platform

1. **Create DigitalOcean Account**
   - Go to [digitalocean.com](https://digitalocean.com)

2. **Create App**
   - Connect your GitHub repository
   - Select "Web Service"
   - Configure:
     - **Build Command**: `uv sync`
     - **Run Command**: `./start.sh`
   - Set environment variables in the dashboard

3. **Deploy**
   - Click "Create Resources"
   - DigitalOcean handles the rest

## 🐳 Docker Deployment

### Local Docker Testing

1. **Build and Run**
   ```bash
   docker-compose up --build
   ```

2. **Access App**
   - Open http://localhost:8000
   - Login with admin/admin123

### Production Docker Deployment

1. **Build Image**
   ```bash
   docker build -t fifa-tickets-app .
   ```

2. **Run Container**
   ```bash
   docker run -d \
     -p 8000:8000 \
     -e FLASK_ENV=production \
     -e SECRET_KEY=your-secret-key \
     -v $(pwd)/data:/app/data \
     --name fifa-tickets \
     fifa-tickets-app
   ```

## 🖥️ VPS/Server Deployment

### Ubuntu/Debian Server

1. **Update System**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Install Dependencies**
   ```bash
   sudo apt install -y python3 python3-pip nginx curl
   ```

3. **Install uv**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   source ~/.bashrc
   ```

4. **Clone and Setup App**
   ```bash
   git clone https://github.com/yourusername/fifa_tickets_app.git
   cd fifa_tickets_app
   uv sync
   ```

5. **Configure Environment**
   ```bash
   cp env.example .env
   nano .env  # Edit with your values
   ```

6. **Start with Gunicorn**
   ```bash
   ./start.sh
   ```

7. **Setup Nginx (Optional)**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

## 🔒 Security Checklist

### Before Going Live

- [ ] **Change Default Admin Password**
  - Login with admin/admin123
  - Change password immediately

- [ ] **Set Strong Secret Key**
  ```bash
  # Generate a secure secret key
  python -c "import secrets; print(secrets.token_hex(32))"
  ```

- [ ] **Use HTTPS**
  - Most platforms provide SSL automatically
  - For custom servers, use Let's Encrypt

- [ ] **Environment Variables**
  - Never commit .env files
  - Use platform-specific secret management

- [ ] **Database Security**
  - Use strong database passwords
  - Consider PostgreSQL for production

## 📊 Monitoring & Maintenance

### Health Checks

The app includes built-in health checks:
- **URL**: `/login` (returns 200 when healthy)
- **Docker**: Automatic health checks every 30s

### Logs

- **Railway/Render**: View logs in dashboard
- **Heroku**: `heroku logs --tail`
- **Docker**: `docker logs fifa-tickets`
- **VPS**: Check gunicorn logs

### Database Backups

For SQLite (default):
```bash
# Backup
cp fifa_tickets.db fifa_tickets_backup_$(date +%Y%m%d).db

# Restore
cp fifa_tickets_backup_20240101.db fifa_tickets.db
```

## 🆘 Troubleshooting

### Common Issues

1. **App Won't Start**
   - Check environment variables
   - Verify all dependencies installed
   - Check logs for errors

2. **Database Issues**
   - Ensure write permissions
   - Check disk space
   - Verify DATABASE_URL format

3. **Static Files Not Loading**
   - Check file paths
   - Verify static directory structure
   - Clear browser cache

### Getting Help

- Check application logs
- Verify environment variables
- Test locally first
- Check platform-specific documentation

## 🎯 Performance Tips

### Optimization

1. **Database**
   - Use PostgreSQL for better performance
   - Add database indexes if needed

2. **Caching**
   - Consider Redis for session storage
   - Add CDN for static files

3. **Scaling**
   - Increase worker processes
   - Use load balancer for multiple instances

## 📝 Environment Variables Reference

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `FLASK_ENV` | Environment mode | `development` | Yes |
| `SECRET_KEY` | Flask secret key | - | Yes |
| `DATABASE_URL` | Database connection | `sqlite:///fifa_tickets.db` | No |
| `PORT` | Server port | `8000` | No |
| `WEB_CONCURRENCY` | Gunicorn workers | `2` | No |

## 🎉 Success!

Once deployed, your FIFA 2026 Ticket App will be live and ready for your friends to use!

**Default Login**: admin / admin123 (change immediately!)

**Features Available**:
- ✅ User registration and authentication
- ✅ Ticket management with FIFA 2026 venues
- ✅ Date restrictions (June 11 - July 19, 2026)
- ✅ Filtering and sorting
- ✅ Permission-based editing
- ✅ Modern responsive design
