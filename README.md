# FIFA 2026 Ticket Management App

A simple, lightweight web application for managing FIFA 2026 ticket purchases. Users can login, add, edit, and delete their ticket information in a modern tabular interface.

## Features

- **User Authentication**: Simple username/password login system
- **Ticket Management**: Add, edit, delete, and view tickets
- **Modern UI**: Responsive design with clean, modern interface
- **Data Validation**: Match number format validation (M + digits)
- **View All Tickets**: All users can view each other's tickets
- **Filtering & Sorting**: Search and sort tickets by various fields
- **Simple Setup**: Easy to run locally for development and testing

## Ticket Fields

- **Name**: Ticket holder name
- **Match Number**: Format M + digits (e.g., M1, M23)
- **Date**: Match date (June 11, 2026 - July 19, 2026)
- **Venue**: FIFA 2026 World Cup venue (dropdown selection)
- **Category**: Ticket category (Category 1-4, VIP)
- **Quantity**: Number of tickets
- **Ticket Info**: Additional information (optional)
- **Ticket Price**: Price per ticket (optional)

## Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript
- **Authentication**: Session-based
- **Package Manager**: uv (ultra-fast Python package manager)

## Quick Start

### Prerequisites

- Python 3.9 or higher
- uv (ultra-fast Python package manager)

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
   This will automatically:
   - Create a virtual environment in `.venv/`
   - Install all dependencies
   - Create a lock file for reproducible installs

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
5. **Filter tickets** using the filter controls at the top
6. **Sort tickets** by clicking column headers

### Match Number Format

Match numbers must follow the format: **M** followed by digits
- ✅ Valid: M1, M23, M100
- ❌ Invalid: 1M, M, M1A, match1

### Date Range

Tickets can only be added for the FIFA 2026 World Cup period:
- **Start Date**: June 11, 2026
- **End Date**: July 19, 2026

### Venues

The app includes all 16 FIFA 2026 World Cup venues across the US, Mexico, and Canada.

## File Structure

```
fifa_tickets_app/
├── app.py                 # Main Flask application
├── models.py             # Database models
├── pyproject.toml        # Project configuration with dependencies
├── uv.lock               # Lock file for reproducible installs
├── requirements.txt      # Legacy pip format (generated from pyproject.toml)
├── README.md            # This file
├── .gitignore           # Git ignore file
├── .venv/                # Virtual environment (created by uv)
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

## Benefits of Using uv

- **🚀 Lightning Fast**: 10-100x faster than pip for dependency resolution
- **🔒 Reproducible**: Lock file ensures identical installs across environments
- **📦 Modern**: Uses pyproject.toml standard
- **🌍 Universal**: Works on all platforms with consistent behavior
- **⚡ Built-in Virtual Environment**: No need for separate venv management
- **🔄 Easy Updates**: Simple commands for adding/removing dependencies

## Security Notes

- **Change the default admin password** after first login
- **Use a strong SECRET_KEY** if deploying (set as environment variable)
- **Consider using HTTPS** if deploying to production
- **Regular backups** of the SQLite database

## Troubleshooting

### Common Issues

1. **Port already in use**
   - Change the port in `app.py`: `app.run(port=5001)`

2. **Database errors**
   - Delete `fifa_tickets.db` and restart the app

3. **Permission errors**
   - Make sure you have write permissions in the app directory

4. **Module not found errors**
   - Ensure all dependencies are installed: `uv sync`
   - Always run the app with: `uv run python app.py`

### Getting Help

- Check the console output for error messages
- Ensure all dependencies are installed
- Verify Python version compatibility (3.8+)

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to submit issues and enhancement requests!