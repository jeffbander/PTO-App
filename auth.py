from flask import session, request, redirect, url_for, flash
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
from models import Manager, TeamMember

def roles_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if 'user_role' not in session:
                return redirect(url_for('login'))
            if session['user_role'] not in roles:
                flash('You do not have permission to access this page.', 'error')
                return redirect(url_for('not_authorized'))
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

def get_current_user():
    """Get the current logged-in user (TeamMember with role)"""
    if 'user_id' in session:
        # Check TeamMember first (Leadership)
        member = TeamMember.query.get(session['user_id'])
        if member and member.role:
            return member
        # Fallback to Manager for backwards compatibility
        return Manager.query.get(session['user_id'])
    return None

def is_logged_in():
    """Check if user is logged in"""
    return 'user_id' in session

def login_user(user):
    """Log in a user by setting session variables"""
    session['user_id'] = user.id
    session['user_name'] = user.name
    session['user_email'] = user.email
    session['user_role'] = user.role
    session['user_type'] = 'team_member' if isinstance(user, TeamMember) else 'manager'
    session.permanent = True

def logout_user():
    """Log out the current user"""
    session.clear()

def authenticate_user(email, password):
    """Authenticate a user with email and password - checks TeamMember (Leadership) first"""
    # First check TeamMember with role (Leadership members)
    member = TeamMember.query.filter_by(email=email).first()
    if member and member.role and member.password_hash and check_password_hash(member.password_hash, password):
        return member

    # Fallback to Manager table for backwards compatibility
    user = Manager.query.filter_by(email=email).first()
    if user and user.password_hash and check_password_hash(user.password_hash, password):
        return user

    return None

def create_default_passwords():
    """Create default passwords for existing managers"""
    from database import db

    # Manager passwords - updated in app.py initialization
    default_passwords = {
        'lauryn.padron@mountsinai.org': 'Carlostylermila5!',
        'ashley.stark@mountsinai.org': 'Heart123!',
        'samantha.zakow@mountsinai.org': 'Password123'
    }

    for email, password in default_passwords.items():
        manager = Manager.query.filter_by(email=email).first()
        if manager and not manager.password_hash:
            manager.password_hash = generate_password_hash(password)

    db.session.commit()