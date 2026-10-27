from flask_sqlalchemy import SQLAlchemy

# Initialize shared SQLAlchemy instance
db = SQLAlchemy()

# Import models so they are registered with SQLAlchemy
from models.user import User
from models.product import Product
from models.order import Order, OrderItem
from models.faq import FAQ
from models.ticket import SupportTicket

__all__ = ['db', 'User', 'Product', 'Order', 'OrderItem', 'FAQ', 'SupportTicket']
