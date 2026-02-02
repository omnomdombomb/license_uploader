"""
Gunicorn configuration for production deployment
"""
import multiprocessing
import os

# Server Socket
bind = '127.0.0.1:8000'  # Bind to localhost, use nginx/apache as reverse proxy
backlog = 2048

# Worker Processes
workers = multiprocessing.cpu_count() * 2 + 1  # Recommended: (2 x $num_cores) + 1
worker_class = 'sync'  # Can use 'gevent' or 'eventlet' for async
worker_connections = 1000
max_requests = 1000  # Restart workers after this many requests (prevents memory leaks)
max_requests_jitter = 50  # Add randomness to prevent all workers restarting simultaneously
timeout = 300  # 5 minutes (for LLM API calls which can be slow)
graceful_timeout = 30
keepalive = 2

# Logging
accesslog = 'logs/gunicorn_access.log'
errorlog = 'logs/gunicorn_error.log'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process Naming
proc_name = 'license_uploader'

# Server Mechanics
daemon = False  # Don't daemonize (use systemd or supervisor instead)
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (if not using reverse proxy for SSL termination)
# keyfile = None
# certfile = None

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

def post_fork(server, worker):
    """Called after a worker has been forked"""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def pre_fork(server, worker):
    """Called before a worker is forked"""
    pass

def pre_exec(server):
    """Called before master process is forked"""
    server.log.info("Forked child, re-executing.")

def when_ready(server):
    """Called when the server is started"""
    server.log.info("Server is ready. Spawning workers")

def worker_int(worker):
    """Called when a worker receives INT or QUIT signal"""
    worker.log.info("Worker received INT or QUIT signal")

def worker_abort(worker):
    """Called when a worker receives SIGABRT signal"""
    worker.log.info("Worker received SIGABRT signal")

def worker_exit(server, worker):
    """Called when a worker exits (cleanup resources)"""
    worker.log.info("Worker exiting (pid: %s)", worker.pid)
    # Force garbage collection to ensure __del__ methods are called
    import gc
    gc.collect()

def on_exit(server):
    """Called when the server is shutting down"""
    server.log.info("Server shutting down - cleaning up resources")
    # Force garbage collection to clean up any remaining resources
    import gc
    gc.collect()
