import json
from models import FAQ
from services.faq_service import faq_service


def test_at_least_10_faqs_exist_in_sql(app):
    """Verify requirement: At least 10 FAQs must exist in the SQL database."""
    with app.app_context():
        count = FAQ.query.count()
        assert count >= 10, f"Expected at least 10 FAQs in SQL, found {count}"


def test_faq_service_search_scoring(app):
    """Verify FAQ keyword retrieval and scoring."""
    with app.app_context():
        # Search for shipping/delivery
        results = faq_service.search_faqs('delivery take', limit=5)
        assert len(results) > 0
        top_match = results[0]
        assert 'delivery' in top_match['question'].lower() or 'delivery' in top_match['answer'].lower()
        assert top_match.get('score', 0) > 0


def test_faq_search_api_endpoint(client):
    """Verify /api/faqs/search returns structured results."""
    response = client.get('/api/faqs/search?q=unboxing')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'results' in data
    assert 'count' in data
    assert data['count'] > 0


def test_faq_category_filter(client):
    """Verify filtering by FAQ category."""
    response = client.get('/faq?category=Technical+%26+Error+Codes')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'error code 460' in html.lower() or '460' in html
