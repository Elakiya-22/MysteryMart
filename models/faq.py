from models import db


class FAQ(db.Model):
    """Frequently Asked Questions model stored in SQL database."""
    __tablename__ = 'faqs'

    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False, index=True)
    answer = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(80), nullable=False, default='General', index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'category': self.category
        }

    def __repr__(self):
        return f'<FAQ #{self.id}: {self.question[:40]}...>'
