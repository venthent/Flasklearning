from functools import wraps
from flask import g
from .errors import forbiden


def permission_requied(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args,**kwargs):
            if not g.current_user.can(permission):
                return forbiden('Insufficient permissions')
            return f(*args,**kwargs)
        return decorated_function
    return decorator
