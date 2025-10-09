# FIFA 2026 Ticket Management App

A simple, lightweight web application for managing FIFA 2026 ticket purchases. Users can login, add, edit, and delete their ticket information in a modern tabular interface.

## Features

- **User Authentication**: Simple username/password login system
- **Ticket Management**: Add, edit, delete, and view tickets
- **Modern UI**: Responsive design with clean, modern interface
- **Data Validation**: Match number format validation (M + digits)
- **User Isolation**: Each user only sees their own tickets
- **Search**: Search through tickets by various fields
- **Fast Package Management**: Uses `uv` for lightning-fast dependency management

## Ticket Fields

- **Name**: Ticket holder name
- **Match Number**: Format M + digits (e.g., M1, M23)
- **Date**: Match date
- **Venue**: Stadium/venue name
- **Category**: Ticket category (Category 1-4, VIP)
- **Quantity**: Number of tickets
- **Ticket Info**: Additional information (optional)
- **Ticket Price**: Price per ticket (optional)

## Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript
- **Authentication**: Session-based
- **Package Manager**: uv (10-100x faster than pip)

## Quick Start

### Prerequisites

- Python 3.8 or higher
- uv (modern Python package manager)

### Install uv

If you don't have uv installed:

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Or with pip:**
```bash
pip install uv
```

### Installation

1. **Clone or download the project**
   ```bash
   cd fifa_tickets_app
   ```

2. **Install dependencies with uv**
   ```bash
   uv sync
   ```

3. **Run the application**
   ```bash
   uv run python app.py
   ```

4. **Access the application**
   - Open your browser and go to `http://localhost:5001`
   - Default admin credentials:
     - Username: `admin`
     - Password: `admin123`

## Usage

### First Time Setup

1. **Login with default admin account**
2. **Create user accounts** for your friends using the registration form
3. **Each user can then login** and manage their own tickets

### Managing Tickets

1. **Login** with your credentials
2. **Add tickets** using the "Add New Ticket" button
3. **Edit tickets** by clicking the "Edit" button in the table
4. **Delete tickets** by clicking the "Delete" button
5. **Search tickets** using the search box

### Match Number Format

Match numbers must follow the format: **M** followed by digits
- ✅ Valid: M1, M23, M100
- ❌ Invalid: 1M, M, M1A, match1

## Deployment

### 🚀 Quick Deploy (Recommended)

**Railway** - Zero configuration deployment:
1. Go to [railway.app](https://railway.app)
2. Connect your GitHub repository
3. Set environment variables: `FLASK_ENV=production`, `SECRET_KEY=your-secret-key`
4. Deploy automatically!

**Render** - Free tier available:
1. Go to [render.com](https://render.com)
2. Create Web Service from GitHub
3. Build Command: `uv sync`
4. Start Command: `./start.sh`

### 📋 Full Deployment Guide

See [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive deployment instructions including:
- Railway, Render, Heroku, DigitalOcean
- Docker deployment
- VPS/server setup
- Security checklist
- Monitoring and maintenance


## Environment Variables

- `SECRET_KEY`: Secret key for session management (required for production)
- `DATABASE_URL`: Database URL (optional, defaults to SQLite)

## File Structure

```
fifa_tickets_app/
├── app.py                 # Main Flask application
├── models.py             # Database models
├── pyproject.toml        # Modern Python project configuration (uv)
├── uv.lock              # Lock file for reproducible installs
├── README.md            # This file
├── Procfile             # Heroku deployment
├── .gitignore           # Git ignore file
├── static/
│   ├── css/
│   │   └── style.css    # Modern styling
│   └── js/
│       └── main.js      # Frontend logic
└── templates/
    ├── login.html       # Login page
    └── dashboard.html   # Main ticket management page
```

## Benefits of Using uv

- **🚀 Lightning Fast**: 10-100x faster than pip for dependency resolution
- **🔒 Reproducible**: Lock file ensures identical installs across environments
- **📦 Modern**: Uses pyproject.toml standard instead of requirements.txt
- **🌍 Universal**: Works on all platforms with consistent behavior
- **⚡ Built-in Virtual Environment**: No need for separate venv management
- **🔄 Easy Updates**: Simple commands for adding/removing dependencies

## Security Notes

- **Change the default admin password** after first login
- **Use a strong SECRET_KEY** in production
- **Consider using HTTPS** in production
- **Regular backups** of the SQLite database

## Troubleshooting

### Common Issues

1. **Port already in use**
   - Change the port in `app.py`: `app.run(port=5001)`

2. **Database errors**
   - Delete `fifa_tickets.db` and restart the app

3. **Permission errors**
   - Make sure you have write permissions in the app directory

### Getting Help

- Check the console output for error messages
- Ensure all dependencies are installed
- Verify Python version compatibility

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to submit issues and enhancement requests!
