from flask_wtf.csrf import CSRFProtect
from flask import Flask, request
from functools import wraps

app = Flask(__name__)
csrf = CSRFProtect(app)
def disable_csrf_check(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        csrf.protect()
        return func(*args, **kwargs)
    return wrapper
