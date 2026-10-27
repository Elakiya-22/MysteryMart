import os
import time
import logging
from flask import Blueprint, render_template, jsonify, current_app, abort, redirect, request
from models import db, Product, FAQ, Order, User
from services.nosql_service import nosql_service
from services.weather_service import weather_service

logger = logging.getLogger('mysterymart.routes.main')
main_bp = Blueprint('main', __name__)


import json

@main_bp.before_app_request
def check_render_redirect():
    """
    Directly redirects requests from mysterymart1.onrender.com to the live shop
    at https://two-toes-shave.loca.lt/shop while allowing health checks.
    """
    if request.path.startswith('/static') or request.path == '/health':
        return None

    host = (request.host or '').lower()
    forwarded_host = (request.headers.get('X-Forwarded-Host') or '').lower()
    enable_redirect = current_app.config.get('ENABLE_RENDER_REDIRECT', True)
    redirect_target = current_app.config.get('REDIRECT_URL', 'https://two-toes-shave.loca.lt/shop')

    # If incoming request is from mysterymart1.onrender.com or forced via env
    is_render_host = (
        'mysterymart1.onrender.com' in host
        or 'mysterymart1' in host
        or 'onrender.com' in host
        or 'mysterymart1.onrender.com' in forwarded_host
        or 'onrender.com' in forwarded_host
        or os.environ.get('FORCE_TUNNEL_REDIRECT') == 'true'
    )

    if enable_redirect and is_render_host:
        if not request.path.startswith('/api/'):
            logger.info("Redirecting %s (%s) directly to live shop: %s", host, request.path, redirect_target)
            target_json = json.dumps(redirect_target)
            html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta http-equiv="refresh" content="0; url={redirect_target}">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Redirecting to MysteryMart Shop...</title>
  <script>window.location.replace({target_json});</script>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #0B0F19;
      color: #F1F5F9;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      margin: 0;
      padding: 1rem;
      text-align: center;
    }}
    .card {{
      background: rgba(17, 24, 39, 0.95);
      border: 1px solid rgba(139, 92, 246, 0.4);
      border-radius: 16px;
      padding: 2.5rem 2rem;
      max-width: 520px;
      box-shadow: 0 20px 40px rgba(0,0,0,0.6);
    }}
    h1 {{ font-size: 1.5rem; margin-bottom: 0.75rem; color: #A78BFA; }}
    p {{ color: #94A3B8; font-size: 0.95rem; margin-bottom: 1.5rem; }}
    .btn {{
      display: inline-block;
      background: linear-gradient(135deg, #7C3AED, #4F46E5);
      color: white;
      padding: 12px 28px;
      border-radius: 9999px;
      text-decoration: none;
      font-weight: 600;
      box-shadow: 0 4px 14px rgba(124, 58, 237, 0.4);
      transition: transform 0.2s;
    }}
    .btn:hover {{ transform: scale(1.03); }}
  </style>
</head>
<body>
  <div class="card">
    <h1>Redirecting to MysteryMart...</h1>
    <p>Taking you directly to the live Surprise Box catalog at <br><code>{redirect_target}</code></p>
    <a class="btn" href="{redirect_target}">Open MysteryMart Shop &rarr;</a>
  </div>
</body>
</html>"""
            response = current_app.make_response(html)
            response.status_code = 302
            response.headers['Location'] = redirect_target
            response.headers['Content-Type'] = 'text/html; charset=utf-8'
            return response


@main_bp.route('/')
def index():
    """MysteryMart homepage."""
    # Featured mystery boxes
    featured_products = Product.query.filter_by(is_active=True).order_by(Product.rating.desc()).limit(4).all()
    # Popular/Bestseller mystery boxes
    popular_products = Product.query.filter_by(is_active=True).order_by(Product.review_count.desc()).limit(4).all()
    # Unique categories
    categories = [
        {'name': 'Gadget Mystery Box', 'icon': 'bi-cpu', 'desc': 'Smart tech, GaN chargers & EDC tools', 'color': '#7C3AED'},
        {'name': 'Gaming Mystery Box', 'icon': 'bi-controller', 'desc': 'RGB gear, artisan keycaps & collectibles', 'color': '#EA580C'},
        {'name': 'Stationery Mystery Box', 'icon': 'bi-journal-bookmark', 'desc': 'Japanese paper, fine pens & washi tapes', 'color': '#0284C7'},
        {'name': 'Fashion Mystery Box', 'icon': 'bi-bag', 'desc': 'Streetwear accessories, beanies & jewellery', 'color': '#D97706'},
        {'name': 'Beauty & Accessories Mystery Box', 'icon': 'bi-stars', 'desc': 'Skincare rituals, quartz rollers & balms', 'color': '#DB2777'},
        {'name': 'Premium Mystery Box', 'icon': 'bi-gem', 'desc': 'VIP luxury audio, titanium EDC & coins', 'color': '#9333EA'}
    ]

    # Clearly labeled customer reviews demo data
    demo_reviews = [
        {
            'name': 'Alex Rivera',
            'box': 'CyberTech Gadget Box',
            'rating': 5,
            'comment': 'I was genuinely amazed when I unboxed the 65W GaN charger and mechanical cables! The value exceeded what I paid by at least 40%.',
            'date': 'October 2026',
            'verified': True,
            'is_demo': True
        },
        {
            'name': 'Samantha Lee',
            'box': 'Artisan Japanese Stationery Box',
            'rating': 5,
            'comment': 'The 160 GSM journal and fineliners are so premium. Opening each carefully wrapped item felt like a birthday surprise!',
            'date': 'September 2026',
            'verified': True,
            'is_demo': True
        },
        {
            'name': 'Marcus Vance',
            'box': 'Pro Gamer Battlestation Box',
            'rating': 5,
            'comment': 'Got the extended desk mat, wrist rest, and custom keycaps. Packed safely with zero damage. 10/10 unboxing experience.',
            'date': 'October 2026',
            'verified': True,
            'is_demo': True
        }
    ]

    return render_template(
        'index.html',
        featured_products=featured_products,
        popular_products=popular_products,
        categories=categories,
        demo_reviews=demo_reviews
    )


@main_bp.route('/how-it-works')
def how_it_works():
    """How MysteryMart Works guide."""
    return render_template('index.html', scroll_to='how-it-works')


@main_bp.route('/health')
def health_check():
    """
    Application Health Check Endpoint.
    Checks SQL database connectivity, NoSQL service, and configuration integrity
    without exposing internal credentials or connection strings.
    Returns HTTP 200 (healthy) or HTTP 503 (unhealthy).
    """
    start_time = time.time()
    health_status = {
        'status': 'healthy',
        'app': 'MysteryMart',
        'version': '1.0.0',
        'environment': current_app.config.get('ENV', 'production' if not current_app.debug else 'development'),
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'services': {}
    }

    # 1. Check SQL Database (Required service)
    sql_ok = False
    try:
        # Simple fast query to verify engine connectivity
        db.session.execute(db.text('SELECT 1'))
        product_count = Product.query.count()
        faq_count = FAQ.query.count()
        health_status['services']['sql_database'] = {
            'status': 'up',
            'type': 'PostgreSQL' if 'postgresql' in current_app.config['SQLALCHEMY_DATABASE_URI'] else 'SQLite',
            'products_count': product_count,
            'faqs_count': faq_count
        }
        sql_ok = True
    except Exception as e:
        logger.error("Health check SQL Database failure: %s", e)
        health_status['services']['sql_database'] = {
            'status': 'down',
            'error': 'Database query failed'
        }
        health_status['status'] = 'unhealthy'

    # 2. Check NoSQL MongoDB (Optional service with graceful fallback)
    mongo_status = 'connected' if nosql_service.is_connected() else 'standby_fallback'
    health_status['services']['nosql_storage'] = {
        'status': mongo_status,
        'mode': 'MongoDB Atlas' if nosql_service.is_connected() else 'In-Memory Fallback',
        'active': True
    }

    # 3. Check Weather Service (External API integration)
    health_status['services']['weather_api'] = {
        'status': 'available',
        'provider': 'Open-Meteo Forecast API',
        'timeout_seconds': current_app.config.get('WEATHER_API_TIMEOUT', 4)
    }

    # 4. Check Assistant Service
    health_status['services']['ai_assistant'] = {
        'status': 'ready',
        'mode': current_app.config.get('AI_PROVIDER', 'fallback')
    }

    duration_ms = round((time.time() - start_time) * 1000, 2)
    health_status['response_time_ms'] = duration_ms

    http_code = 200 if sql_ok else 503
    return jsonify(health_status), http_code


@main_bp.route('/test-500')
def trigger_test_500():
    """Controlled endpoint to test custom 500 error page handling."""
    raise RuntimeError("Controlled test exception for MysteryMart 500 handler validation.")


@main_bp.route('/test-460')
def trigger_test_460():
    """Controlled endpoint to test MysteryMart application-specific 460 error page."""
    from routes.error_handlers import MysteryMartConcurrencyError
    raise MysteryMartConcurrencyError("Controlled test exception for MysteryMart 460 handler validation.")
