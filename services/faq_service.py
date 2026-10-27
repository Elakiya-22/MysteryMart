import re
from typing import List, Dict, Any, Optional
from models import db, FAQ


COMMON_STOP_WORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'he',
    'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 'to', 'was', 'were',
    'will', 'with', 'can', 'could', 'should', 'would', 'have', 'had', 'what',
    'who', 'where', 'when', 'why', 'how', 'which', 'this', 'these', 'those', 'i', 'me'
}


class FAQService:
    """Service to search, retrieve, and categorize FAQs from SQL database."""

    @staticmethod
    def get_all_faqs() -> List[FAQ]:
        """Fetch all FAQs from the database sorted by category."""
        return FAQ.query.order_by(FAQ.category.asc(), FAQ.id.asc()).all()

    @staticmethod
    def get_by_category(category: str) -> List[FAQ]:
        """Fetch FAQs for a specific category."""
        return FAQ.query.filter_by(category=category).all()

    @staticmethod
    def get_categories() -> List[str]:
        """Get unique FAQ categories."""
        results = db.session.query(FAQ.category).distinct().order_by(FAQ.category.asc()).all()
        return [r[0] for r in results if r[0]]

    @staticmethod
    def get_faq_by_id(faq_id: int) -> Optional[FAQ]:
        """Fetch a single FAQ by primary key."""
        return db.session.get(FAQ, faq_id)

    @classmethod
    def search_faqs(cls, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search FAQs in SQL database using token scoring over question and answer fields.
        Returns matching FAQ items with relevance score.
        """
        if not query or not query.strip():
            return [faq.to_dict() for faq in cls.get_all_faqs()[:limit]]

        cleaned_query = query.lower().strip()
        tokens = [
            t for t in re.findall(r'\b\w+\b', cleaned_query)
            if len(t) > 2 and t not in COMMON_STOP_WORDS
        ]
        
        all_faqs = FAQ.query.all()
        scored_results = []

        for faq in all_faqs:
            q_text = faq.question.lower()
            a_text = faq.answer.lower()
            cat_text = faq.category.lower()

            score = 0
            # Exact phrase match in question gets massive boost
            if len(cleaned_query) > 5 and cleaned_query in q_text:
                score += 50
            # Exact phrase in answer
            if len(cleaned_query) > 5 and cleaned_query in a_text:
                score += 25
            
            # Meaningful token match scoring
            for token in tokens:
                if token in q_text:
                    score += 20
                if token in a_text:
                    score += 8
                if token in cat_text:
                    score += 10

            if score >= 15:
                faq_dict = faq.to_dict()
                faq_dict['score'] = score
                scored_results.append(faq_dict)

        # Sort descending by score
        scored_results.sort(key=lambda x: x['score'], reverse=True)
        return scored_results[:limit]


faq_service = FAQService()
