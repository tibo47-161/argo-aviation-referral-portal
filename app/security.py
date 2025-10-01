import os
import secrets
from functools import wraps
from flask import current_app, request, abort, flash, redirect, url_for
from flask_login import current_user
import bleach
import re
from datetime import datetime, timedelta

# Rate limiting storage (in production, use Redis)
rate_limit_storage = {}

def generate_secure_filename(filename):
    """Generate a secure filename for uploaded files."""
    if not filename:
        return None
    
    # Remove path components
    filename = os.path.basename(filename)
    
    # Generate random prefix
    random_prefix = secrets.token_hex(8)
    
    # Clean filename
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    
    return f"{random_prefix}_{filename}"

def sanitize_input(text):
    """Sanitize user input to prevent XSS attacks."""
    if not text:
        return text
    
    # Allow basic HTML tags for rich text
    allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li']
    allowed_attributes = {}
    
    return bleach.clean(text, tags=allowed_tags, attributes=allowed_attributes, strip=True)

def validate_file_upload(file):
    """Validate uploaded files for security."""
    if not file or not file.filename:
        return False, "Keine Datei ausgewählt"
    
    # Check file size (5MB limit)
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > 5 * 1024 * 1024:  # 5MB
        return False, "Datei zu groß (maximal 5MB)"
    
    # Check file extension
    allowed_extensions = {'.pdf', '.doc', '.docx'}
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        return False, "Dateityp nicht erlaubt"
    
    # Check MIME type
    allowed_mimes = {
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    }
    
    if hasattr(file, 'content_type') and file.content_type not in allowed_mimes:
        return False, "Ungültiger Dateityp"
    
    return True, "OK"

def rate_limit(max_requests=5, window_minutes=15):
    """Rate limiting decorator."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_app.config.get('TESTING'):
                return f(*args, **kwargs)
            
            # Get client identifier
            client_id = request.environ.get('REMOTE_ADDR', 'unknown')
            if current_user.is_authenticated:
                client_id = f"user_{current_user.user_id}"
            
            # Check rate limit
            now = datetime.utcnow()
            window_start = now - timedelta(minutes=window_minutes)
            
            if client_id not in rate_limit_storage:
                rate_limit_storage[client_id] = []
            
            # Clean old requests
            rate_limit_storage[client_id] = [
                req_time for req_time in rate_limit_storage[client_id]
                if req_time > window_start
            ]
            
            # Check if limit exceeded
            if len(rate_limit_storage[client_id]) >= max_requests:
                current_app.logger.warning(f'Rate limit exceeded for {client_id}')
                abort(429)  # Too Many Requests
            
            # Add current request
            rate_limit_storage[client_id].append(now)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """Decorator to require admin privileges."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Sie müssen angemeldet sein, um auf diese Seite zuzugreifen.', 'error')
            return redirect(url_for('auth.login'))
        
        if not current_user.is_admin and not current_user.is_superadmin:
            current_app.logger.warning(f'Unauthorized admin access attempt by user {current_user.email}')
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function

def superadmin_required(f):
    """Decorator to require superadmin privileges."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Sie müssen angemeldet sein, um auf diese Seite zuzugreifen.', 'error')
            return redirect(url_for('auth.login'))
        
        if not current_user.is_superadmin:
            current_app.logger.warning(f'Unauthorized superadmin access attempt by user {current_user.email}')
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function

def validate_email_format(email):
    """Validate email format with comprehensive regex."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password_strength(password):
    """Validate password strength."""
    if len(password) < 8:
        return False, "Passwort muss mindestens 8 Zeichen lang sein"
    
    if not re.search(r'[a-z]', password):
        return False, "Passwort muss mindestens einen Kleinbuchstaben enthalten"
    
    if not re.search(r'[A-Z]', password):
        return False, "Passwort muss mindestens einen Großbuchstaben enthalten"
    
    if not re.search(r'\d', password):
        return False, "Passwort muss mindestens eine Zahl enthalten"
    
    # Check for common weak passwords
    weak_passwords = [
        'password', '12345678', 'qwertz123', 'admin123',
        'password123', '123456789', 'qwerty123'
    ]
    
    if password.lower() in weak_passwords:
        return False, "Passwort ist zu schwach"
    
    return True, "OK"

def log_security_event(event_type, details, user_id=None):
    """Log security-related events."""
    if not user_id and current_user.is_authenticated:
        user_id = current_user.user_id
    
    current_app.logger.warning(
        f'SECURITY EVENT: {event_type} | User: {user_id} | IP: {request.environ.get("REMOTE_ADDR")} | Details: {details}'
    )

def check_sql_injection(input_string):
    """Basic SQL injection detection."""
    if not input_string:
        return False
    
    # Common SQL injection patterns
    sql_patterns = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
        r"(--|#|/\*|\*/)",
        r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
        r"(\'\s*(OR|AND)\s*\'\w*\'\s*=\s*\'\w*\')",
    ]
    
    for pattern in sql_patterns:
        if re.search(pattern, input_string, re.IGNORECASE):
            return True
    
    return False

def sanitize_search_query(query):
    """Sanitize search queries."""
    if not query:
        return query
    
    # Check for SQL injection
    if check_sql_injection(query):
        log_security_event('SQL_INJECTION_ATTEMPT', f'Query: {query}')
        return ""
    
    # Remove special characters except basic ones
    sanitized = re.sub(r'[^\w\s\-\.]', '', query)
    
    # Limit length
    return sanitized[:100]
