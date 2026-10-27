from routes.main_routes import main_bp
from routes.shop_routes import shop_bp
from routes.cart_routes import cart_bp
from routes.checkout_routes import checkout_bp
from routes.auth_routes import auth_bp
from routes.faq_routes import faq_bp
from routes.support_routes import support_bp
from routes.assistant_routes import assistant_bp
from routes.error_handlers import register_error_handlers

__all__ = [
    'main_bp',
    'shop_bp',
    'cart_bp',
    'checkout_bp',
    'auth_bp',
    'faq_bp',
    'support_bp',
    'assistant_bp',
    'register_error_handlers'
]
