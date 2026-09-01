from functools import wraps
from flask import abort
from flask_login import current_user

def roles_required(*roles):
    """
    Decorator to restrict route access to users with specified roles.
    Usage: @roles_required('Department Admin', 'Field Engineer')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)  # Unauthorized
            if not current_user.has_role(*roles):
                abort(403)  # Forbidden
            return f(*args, **kwargs)
        return decorated_function
    return decorator