import re
import logging
from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from models import db, User, Order
from services.rate_limiter import rate_limiter

logger = logging.getLogger('mysterymart.routes.auth')
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Customer registration with server-side validation and password hashing."""
    if session.get('user_id'):
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        errors = []
        if not username or len(username) < 3 or not re.match(r'^[a-zA-Z0-9_.-]+$', username):
            errors.append("Username must be at least 3 characters and contain only letters, numbers, and underscores.")

        if not email or not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            errors.append("Please provide a valid email address.")

        if not password or len(password) < 6:
            errors.append("Password must be at least 6 characters.")

        if password != confirm_password:
            errors.append("Passwords do not match.")

        # Check existing user
        if not errors:
            if User.query.filter_by(username=username).first():
                errors.append("This username is already registered.")
            elif User.query.filter_by(email=email).first():
                errors.append("An account with this email address already exists.")

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('register.html', username=username, email=email)

        # Create user
        try:
            new_user = User(
                username=username,
                email=email,
                role='customer'
            )
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()

            # Automatically log in the registered user
            session['user_id'] = new_user.id
            session['username'] = new_user.username
            session['user_role'] = new_user.role
            session['user_email'] = new_user.email
            session.permanent = True

            flash(f"Welcome to MysteryMart, {new_user.username}! Your mystery box journey begins.", 'success')
            return redirect(url_for('main.index'))

        except Exception as e:
            db.session.rollback()
            logger.error("User registration failed: %s", e)
            flash("Registration could not be completed. Please try again.", 'danger')
            return render_template('register.html', username=username, email=email)

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Customer login with rate limiting and secure password verification."""
    if session.get('user_id'):
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        # Apply rate limit to prevent brute-force attacks (5 attempts/min)
        rate_limiter.limit('login', max_requests=8, window_seconds=60)

        identity = request.form.get('identity', '').strip()  # email or username
        password = request.form.get('password', '')

        if not identity or not password:
            flash("Please enter both your email/username and password.", 'warning')
            return render_template('login.html', identity=identity)

        # Find by username or email
        user = User.query.filter(
            db.or_(User.username == identity, User.email == identity.lower())
        ).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['user_role'] = user.role
            session['user_email'] = user.email
            session.permanent = True

            logger.info("User logged in successfully: %s", user.username)
            flash(f"Welcome back, {user.username}!", 'success')
            
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('main.index'))
        else:
            logger.warning("Failed login attempt for identity: %s", identity)
            flash("Invalid username/email or password.", 'danger')
            return render_template('login.html', identity=identity)

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    """Clear user session and logout."""
    username = session.get('username')
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('user_role', None)
    session.pop('user_email', None)
    flash(f"You have been logged out. See you next time!", 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/my-orders')
def my_orders():
    """Customer order history page."""
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to view your order history.", 'info')
        return redirect(url_for('auth.login', next=url_for('auth.my_orders')))

    user = User.query.get(user_id)
    orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()
    return render_template('orders.html', user=user, orders=orders)
