from flask import flash, redirect, url_for, g
from functools import wraps
from flask_login import current_user



def check_confirmed(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        try:
            if current_user.confirmed is False:
                flash('Please confirm your account!')
                return redirect(url_for('auth.unconfirmed'))
            return func(*args, **kwargs)
        except:
            pass

    return decorated_function
