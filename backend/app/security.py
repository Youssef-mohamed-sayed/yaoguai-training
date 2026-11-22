from functools import wraps

from flask import jsonify
from flask_login import current_user


def authenticated_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        from flask import request
        if not current_user.is_authenticated:
            return jsonify(error={"code": "authentication_required", "message": "Sign in to continue"}), 401
        if not current_user.is_active:
            return jsonify(error={"code": "account_disabled", "message": "This account is disabled"}), 403
        if current_user.must_change_password and request.path != "/api/auth/password":
            return jsonify(error={"code": "password_change_required", "message": "Change your initial password to continue"}), 403
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify(error={"code": "authentication_required", "message": "Sign in to continue"}), 401
        if not current_user.is_active or not current_user.is_admin:
            return jsonify(error={"code": "forbidden", "message": "Administrator access is required"}), 403
        if current_user.must_change_password:
            return jsonify(error={"code": "password_change_required", "message": "Change your initial password to continue"}), 403
        return view(*args, **kwargs)
    return wrapped


def json_object():
    from flask import request
    value = request.get_json(silent=True)
    return value if isinstance(value, dict) else None


def error(code, message, status):
    return jsonify(error={"code": code, "message": message}), status

