import uuid
from datetime import datetime
from models import db


def generate_order_number() -> str:
    """Generate a clean, professional order reference code like MM-ORD-7A9B3E."""
    return f"MM-ORD-{uuid.uuid4().hex[:8].upper()}"


class Order(db.Model):
    """Customer order model."""
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    order_number = db.Column(db.String(32), unique=True, nullable=False, index=True, default=generate_order_number)
    
    # Customer Details
    customer_name = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(120), nullable=False, index=True)
    customer_phone = db.Column(db.String(25), nullable=True)
    
    # Shipping Address Details
    shipping_address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(80), nullable=False)
    state = db.Column(db.String(80), nullable=True)
    postal_code = db.Column(db.String(20), nullable=False)
    delivery_notes = db.Column(db.Text, nullable=True)
    
    # Financial Breakdown (recalculated on server)
    subtotal = db.Column(db.Float, nullable=False)
    delivery_fee = db.Column(db.Float, default=0.0, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    
    # Payment & Dispatch
    payment_method = db.Column(db.String(50), default='Simulated Card Payment', nullable=False)
    payment_status = db.Column(db.String(30), default='Completed (Simulated)', nullable=False)
    status = db.Column(db.String(30), default='Processing', nullable=False)  # Processing, Dispatched, Delivered, Cancelled
    
    # Delivery City Weather Snapshot (Third-Party API Integration)
    weather_note = db.Column(db.String(255), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    items = db.relationship('OrderItem', backref='order', cascade='all, delete-orphan', lazy='joined')

    def to_dict(self):
        return {
            'id': self.id,
            'order_number': self.order_number,
            'user_id': self.user_id,
            'customer_name': self.customer_name,
            'customer_email': self.customer_email,
            'shipping_address': self.shipping_address,
            'city': self.city,
            'postal_code': self.postal_code,
            'subtotal': round(float(self.subtotal), 2),
            'delivery_fee': round(float(self.delivery_fee), 2),
            'total_amount': round(float(self.total_amount), 2),
            'payment_method': self.payment_method,
            'status': self.status,
            'weather_note': self.weather_note,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M UTC') if self.created_at else None,
            'items': [item.to_dict() for item in self.items]
        }

    def __repr__(self):
        return f'<Order {self.order_number} (${self.total_amount:.2f})>'


class OrderItem(db.Model):
    """Line item in an order."""
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='RESTRICT'), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Float, nullable=False)

    # Relationship to product
    product = db.relationship('Product', lazy='joined')

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else 'Mystery Box',
            'product_category': self.product.category if self.product else 'Unboxed',
            'product_image': self.product.image_url if self.product else '/static/images/mystery-box.svg',
            'quantity': self.quantity,
            'unit_price': round(float(self.unit_price), 2),
            'line_total': round(float(self.unit_price * self.quantity), 2)
        }

    def __repr__(self):
        return f'<OrderItem #{self.id} Product {self.product_id} x{self.quantity}>'
