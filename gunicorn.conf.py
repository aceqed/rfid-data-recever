# Gunicorn configuration file
# Number of worker processes
workers = 3

# Number of threads per worker
threads = 2

# Socket to bind
bind = '0.0.0.0:5000'

# Maximum number of pending connections
backlog = 2048

# Timeout for worker processes
timeout = 60

# Automatically restart workers if they crash
max_requests = 1000
max_requests_jitter = 50

# Access log settings
accesslog = 'logs/access.log'
errorlog = 'logs/error.log'
loglevel = 'info'

# Process name
proc_name = 'rfid-api'

# Preload application for better performance
preload_app = True