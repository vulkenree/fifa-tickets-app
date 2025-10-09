# FIFA 2026 Ticket Management App

A simple, lightweight web application for managing FIFA 2026 ticket purchases. Users can login, add, edit, and delete their ticket information in a modern tabular interface.

## Features

- **User Authentication**: Simple username/password login system
- **Ticket Management**: Add, edit, delete, and view tickets
- **Modern UI**: Responsive design with clean, modern interface
- **Data Validation**: Match number format validation (M + digits)
- **User Isolation**: Each user only sees their own tickets
- **Search**: Search through tickets by various fields
- **Simple Deployment**: Easy to deploy with Docker and pip

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
- **Package Manager**: pip (standard Python package manager)

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone or download the project**
   ```bash
   cd fifa_tickets_app
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
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

## Railway Deployment

### Quick Deploy to Railway

1. **Push code to GitHub**
   - Ensure your code is in a GitHub repository

2. **Connect repository to Railway**
   - Go to [railway.app](https://railway.app)
   - Sign in with GitHub
   - Click "Deploy from GitHub repo"
   - Select your repository

3. **Set environment variables**
   - In Railway dashboard, go to Variables tab
   - Add these variables:
     - `FLASK_ENV=production`
     - `SECRET_KEY=your-secret-key-here` (generate a secure key)

4. **Deploy**
   - Railway will automatically detect the Dockerfile
   - No additional configuration needed
   - Your app will be live in minutes!

5. **Health check endpoint**: `/health`

### Railway Configuration

In Railway dashboard:
- **Build**: Automatically detected (Dockerfile)
- **Start Command**: (leave empty, uses CMD from Dockerfile)
- **Health Check Path**: `/health`
- **Environment Variables**:
  - `FLASK_ENV=production`
  - `SECRET_KEY=(generate secure key)`


## Environment Variables

- `SECRET_KEY`: Secret key for session management (required for production)
- `DATABASE_URL`: Database URL (optional, defaults to SQLite)

## File Structure

```
fifa_tickets_app/
├── app.py                 # Main Flask application
├── models.py             # Database models
├── start.sh              # Startup script for Railway
├── Dockerfile            # Docker configuration for Railway
├── gunicorn.conf.py      # Gunicorn configuration
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── .gitignore           # Git ignore file
├── static/
│   ├── css/
│   │   └── style.css    # Modern styling
│   ├── js/
│   │   └── main.js      # Frontend logic
│   └── images/
│       └── logo.jpg     # App logo
└── templates/
    ├── login.html       # Login page
    └── dashboard.html   # Main ticket management page
```

## Benefits of This Setup

- **🚀 Simple**: Easy to understand and deploy
- **🔒 Reliable**: Uses standard Python tools (pip, gunicorn)
- **📦 Lightweight**: Minimal dependencies for fast deployment
- **🌍 Universal**: Works on all platforms with standard Python
- **⚡ Fast Deployment**: Quick setup on Railway and other platforms
- **🔄 Easy Maintenance**: Standard Python project structure

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
