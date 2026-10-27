import json
from services.assistant import assistant_service


def test_assistant_retrieves_verified_faq(app):
    """Verify assistant performs SQL FAQ retrieval first and includes verified badge."""
    with app.app_context():
        res = assistant_service.process_message(
            session_id="test_sess_1",
            user_message="How does MysteryMart work?"
        )
        assert res['source'] == 'verified_faq'
        assert 'MysteryMart lets you select a themed category' in res['response']
        assert res['confidence'] == 'High (Verified SQL FAQ)'


def test_assistant_explains_http_codes(app):
    """Verify assistant explains supported HTTP status codes and custom 460."""
    with app.app_context():
        # Test 404 explanation
        res_404 = assistant_service.process_message(
            session_id="test_sess_2",
            user_message="What is error 404?"
        )
        assert res_404['source'] == 'http_knowledge_base'
        assert '404 — Page Not Found' in res_404['response']

        # Test custom 460 code
        res_460 = assistant_service.process_message(
            session_id="test_sess_3",
            user_message="What does status code 460 mean?"
        )
        assert res_460['source'] == 'http_knowledge_base'
        assert '460' in res_460['response']
        assert 'Unboxing Concurrency' in res_460['response']


def test_assistant_clarifying_questions(app):
    """Verify assistant asks clarifying questions on vague inputs."""
    with app.app_context():
        res = assistant_service.process_message(
            session_id="test_sess_4",
            user_message="shipping"
        )
        assert res['source'] == 'clarification_prompt'
        assert 'Are you asking about' in res['response']


def test_assistant_fallback_offers_ticket_when_no_match(app):
    """Verify assistant does not invent answers and offers a support ticket when no FAQ matches."""
    with app.app_context():
        res = assistant_service.process_message(
            session_id="test_sess_5",
            user_message="Can I feed chocolate to an astronaut on Mars?"
        )
        assert res['source'] == 'faq_fallback'
        assert res.get('offer_ticket') is True
        assert 'could not find a confirmed answer' in res['response']


def test_assistant_chat_api_endpoint(client):
    """Verify /api/chat endpoint."""
    response = client.post(
        '/api/chat',
        data=json.dumps({'message': 'How does MysteryMart work?', 'session_id': 'test_api_sess'}),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'response' in data
    assert 'session_id' in data


def test_assistant_feedback_submission(client):
    """Verify customer feedback and star ratings endpoint."""
    response = client.post(
        '/api/chat/feedback',
        data=json.dumps({
            'rating': 5,
            'comment': 'Awesome concierge assistance!',
            'email': 'shopper@test.com',
            'session_id': 'test_api_sess'
        }),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
