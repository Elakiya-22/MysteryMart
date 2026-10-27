import os
import time
import logging
from datetime import datetime
from flask import Flask, g, request, session
from config import config_by_name
from models import db
from routes import (
    main_bp,
    shop_bp,
    cart_bp,
    checkout_bp,
    auth_bp,
    faq_bp,
    support_bp,
    assistant_bp,
    register_error_handlers
)
from seed import seed_database

# Configure root MysteryMart application logger
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(name)s: %(message)s'
)
logger = logging.getLogger('mysterymart.access')


def create_app(config_name: str = None) -> Flask:
    """MysteryMart Flask Application Factory."""
    if not config_name:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app_config = config_by_name.get(config_name, config_by_name['default'])
    app.config.from_object(app_config)

    # Initialize SQLAlchemy database
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(shop_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(checkout_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(faq_bp)
    app.register_blueprint(support_bp)
    app.register_blueprint(assistant_bp)

    # Register custom error handlers (400, 401, 403, 404, 429, 460, 500, 503)
    register_error_handlers(app)

    # ---------------------------------------------------------
    # Request Logging Middleware (Requirement 10)
    # Records: Timestamp, HTTP method, Path, Status, Duration
    # Excludes passwords, auth tokens, session secrets, card details
    # ---------------------------------------------------------
    @app.before_request
    def record_start_time():
        g.start_time = time.time()

    @app.after_request
    def log_request_performance(response):
        # Calculate request execution duration
        start = getattr(g, 'start_time', None)
        duration_ms = round((time.time() - start) * 1000, 2) if start else 0.0

        # Sensitive paths to avoid logging query parameters
        path = request.path
        method = request.method
        status = response.status_code
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')

        # Filter out static assets from excessive logging
        if not path.startswith('/static/'):
            # Redact if query params contain sensitive keywords
            clean_query = ''
            if request.query_string:
                q_str = request.query_string.decode('utf-8', errors='ignore')
                if any(k in q_str.lower() for k in ['password', 'token', 'key', 'secret', 'card']):
                    clean_query = '?REDACTED'
                else:
                    clean_query = f"?{q_str}"

            logger.info(
                "[%s] %s %s%s -> HTTP %s (%sms)",
                timestamp,
                method,
                path,
                clean_query,
                status,
                duration_ms
            )

        # Append standard security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'

        return response

    # ---------------------------------------------------------
    # Context Processor for Global Template Variables
    # ---------------------------------------------------------
    @app.context_processor
    def inject_global_template_vars():
        """Provide cart item count, current year, and user session to all templates."""
        cart_dict = session.get('cart', {})
        total_items = sum(qty for qty in cart_dict.values() if isinstance(qty, int) and qty > 0)
        return {
            'cart_item_count': total_items,
            'current_year': datetime.utcnow().year,
            'current_user': {
                'id': session.get('user_id'),
                'username': session.get('username'),
                'email': session.get('user_email'),
                'role': session.get('user_role')
            } if session.get('user_id') else None,
            'app_tagline': 'Unbox the Unexpected!',
            'site_name': 'MysteryMart'
        }

    # Auto-initialize database tables and demo seed data on startup
    with app.app_context():
        try:
            db.create_all()
            seed_database()
        except Exception as e:
            logger.warning("Database auto-initialization skipped or failed: %s", e)

    return app


# Application instance for WSGI servers (Gunicorn / Waitress / Render)
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1')
    logger.info("Starting MysteryMart server on http://0.0.0.0:%d (debug=%s)", port, debug_mode)
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
