import uuid
from datetime import datetime
from models import db


def generate_ticket_number() -> str:
    """Generate a clean support ticket reference like MM-TKT-48921."""
    return f"MM-TKT-{uuid.uuid4().hex[:6].upper()}"


class SupportTicket(db.Model):
    """Customer support ticket stored in SQL database."""
    __tablename__ = 'support_tickets'

    id = db.Column(db.Integer, primary_key=True)
    ticket_number = db.Column(db.String(32), unique=True, nullable=False, index=True, default=generate_ticket_number)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(120), nullable=False, index=True)
    subject = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), default='Open', nullable=False)  # Open, In Progress, Resolved, Closed
    priority = db.Column(db.String(20), default='Normal', nullable=False)
    created_via = db.Column(db.String(30), default='Web Form', nullable=False)  # 'Web Form' or 'AI Assistant'
    resolution_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'ticket_number': self.ticket_number,
            'customer_name': self.customer_name,
            'customer_email': self.customer_email,
            'subject': self.subject,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'created_via': self.created_via,
            'resolution_notes': self.resolution_notes,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M UTC') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M UTC') if self.updated_at else None
        }

    def __repr__(self):
        return f'<SupportTicket {self.ticket_number} ({self.status})>'
