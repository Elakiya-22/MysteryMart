from datetime import datetime
from models import db


class Product(db.Model):
    """Mystery Box product model."""
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(80), nullable=False, index=True)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    stock = db.Column(db.Integer, default=20, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Mystery Box Specific Attributes
    box_tier = db.Column(db.String(50), default='Standard Edition')
    guaranteed_inclusions = db.Column(db.Text, nullable=False)  # Semicolon separated list
    box_condition = db.Column(db.String(80), default='Brand New & Factory Sealed')
    delivery_info = db.Column(db.String(120), default='Standard Shipping: 3-5 Business Days')
    badge = db.Column(db.String(40), nullable=True)  # e.g., 'Bestseller', 'Hot', 'Premium'
    rating = db.Column(db.Float, default=4.8)
    review_count = db.Column(db.Integer, default=38)
    is_demo = db.Column(db.Boolean, default=True)  # Clearly labeled demo product
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_guaranteed_list(self):
        """Return guaranteed inclusions as a cleaned python list."""
        if not self.guaranteed_inclusions:
            return []
        return [item.strip() for item in self.guaranteed_inclusions.split(';') if item.strip()]

    def is_in_stock(self, quantity=1) -> bool:
        """Check if stock is sufficient for requested quantity."""
        return self.is_active and self.stock >= quantity and quantity > 0

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'price': round(float(self.price), 2),
            'image_url': self.image_url,
            'stock': self.stock,
            'is_active': self.is_active,
            'box_tier': self.box_tier,
            'guaranteed_inclusions': self.get_guaranteed_list(),
            'box_condition': self.box_condition,
            'delivery_info': self.delivery_info,
            'badge': self.badge,
            'rating': self.rating,
            'review_count': self.review_count,
            'is_demo': self.is_demo
        }

    def __repr__(self):
        return f'<Product #{self.id} {self.name} (${self.price:.2f})>'
