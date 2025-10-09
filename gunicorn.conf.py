import os

bind = f"0.0.0.0:{os.environ.get('PORT', 8000)}"
workers = 2
timeout = 30
accesslog = '-'
errorlog = '-'
loglevel = 'info'