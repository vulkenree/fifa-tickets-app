# Gunicorn configuration file for FIFA 2026 Ticket App

import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', 8000)}"
backlog = 2048

# Worker processes
workers = int(os.environ.get('WEB_CONCURRENCY', 2))
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = 'fifa-tickets-app'

# Server mechanics
daemon = False
pidfile = '/tmp/gunicorn.pid'
user = None
group = None
tmp_upload_dir = None

# SSL (uncomment if using HTTPS)
# keyfile = '/path/to/keyfile'
# certfile = '/path/to/certfile'
