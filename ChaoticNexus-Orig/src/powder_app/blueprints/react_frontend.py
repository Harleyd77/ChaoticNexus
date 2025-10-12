from flask import Blueprint, render_template, send_from_directory, current_app, request, jsonify, session, url_for
import os
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from ..core.security import public_endpoint
from ..core.db import db_execute, db_query_one, INTEGRITY_ERRORS
from ..core.customer_auth import (
    authenticate_customer_credentials,
    end_customer_session,
    start_customer_session,
)

react_bp = Blueprint('react', __name__, url_prefix='/react')

_ADMIN_SESSION_KEYS = ("user_id", "username", "is_admin")

def _set_admin_session(user: dict) -> None:
    """Set admin session variables"""
    for key in _ADMIN_SESSION_KEYS:
        session.pop(key, None)
    session["user_id"] = user["id"]
    session["username"] = user["username"]
    session["is_admin"] = bool(user["is_admin"])

@react_bp.route('/')
@react_bp.route('/<path:path>')
@public_endpoint
def index(path=None):
    """Serve the React frontend for all React routes"""
    # Special handling for demo page (Flask-rendered template)
    if path == 'demo':
        return render_template('react_demo.html')
    
    # Serve the built React app for all other routes
    static_dir = os.path.join(current_app.root_path, 'static', 'dist')
    return send_from_directory(static_dir, 'index.html')

@react_bp.route('/assets/<path:filename>')
@public_endpoint
def serve_assets(filename):
    """Serve React app assets"""
    static_dir = os.path.join(current_app.root_path, 'static', 'dist', 'assets')
    return send_from_directory(static_dir, filename)

@react_bp.route('/api/login', methods=['POST'])
@public_endpoint
def api_login():
    """API endpoint for React login"""
    try:
        data = request.get_json() if request.is_json else {}
        
        # Support both JSON and form data
        if not data:
            identifier = request.form.get('identifier', '').strip()
            password = request.form.get('password', '')
        else:
            identifier = data.get('identifier', '').strip()
            password = data.get('password', '')

        if not identifier or not password:
            return jsonify({
                'success': False,
                'error': 'Email or username and password are required'
            }), 400

        # Try admin user first
        user = db_query_one(
            "SELECT * FROM users WHERE lower(trim(username)) = lower(trim(?))",
            (identifier,),
        )

        if user and check_password_hash(user["password_hash"], password):
            end_customer_session()
            _set_admin_session(user)
            return jsonify({
                'success': True,
                'redirect': url_for('base.nav'),
                'user_type': 'admin'
            })

        # Try customer login
        customer_record, customer_error = authenticate_customer_credentials(
            identifier.lower(), password
        )
        
        if customer_record:
            for key in _ADMIN_SESSION_KEYS:
                session.pop(key, None)
            start_customer_session(customer_record)
            return jsonify({
                'success': True,
                'redirect': url_for('customer_portal.dashboard'),
                'user_type': 'customer',
                'message': f"Welcome back, {customer_record['first_name']}!"
            })

        # Invalid credentials
        return jsonify({
            'success': False,
            'error': 'Invalid login credentials'
        }), 401

    except Exception as e:
        current_app.logger.error(f"Login API error: {e}")
        return jsonify({
            'success': False,
            'error': 'An error occurred during login'
        }), 500
