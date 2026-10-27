import uuid
import logging
from flask import Blueprint, request, jsonify, session
from services.assistant import assistant_service
from services.ticket_service import ticket_service
from services.nosql_service import nosql_service
from services.rate_limiter import rate_limiter

logger = logging.getLogger('mysterymart.routes.assistant')
assistant_bp = Blueprint('assistant', __name__)


def get_or_create_chat_session() -> str:
    """Ensure a consistent session ID for the chat conversation."""
    if 'chat_session_id' not in session:
        session['chat_session_id'] = f"chat_{uuid.uuid4().hex[:12]}"
    return session['chat_session_id']


@assistant_bp.route('/api/chat', methods=['POST'])
def chat():
    """
    Floating AI Chat Assistant endpoint with rate limiting,
    FAQ retrieval, HTTP code explanation, and MongoDB logging.
    """
    # Rate limit chat queries (30 requests/minute per client IP)
    rate_limiter.limit('chat', max_requests=30, window_seconds=60)

    data = request.get_json() or {}
    user_message = data.get('message', '').strip()
    client_session_id = data.get('session_id') or get_or_create_chat_session()

    user_id = session.get('user_id')
    user_email = session.get('user_email')

    result = assistant_service.process_message(
        session_id=client_session_id,
        user_message=user_message,
        user_id=user_id,
        user_email=user_email
    )

    result['session_id'] = client_session_id
    return jsonify(result)


@assistant_bp.route('/api/chat/ticket', methods=['POST'])
def create_ticket_from_chat():
    """Create a support ticket directly through assistant workflow."""
    data = request.get_json() or {}
    name = data.get('customer_name', '').strip()
    email = data.get('customer_email', '').strip()
    subject = data.get('subject', 'Assistance Request via AI Concierge').strip()
    description = data.get('description', '').strip()
    chat_session_id = data.get('session_id') or session.get('chat_session_id')

    success, ticket_dict, error = ticket_service.create_ticket(
        customer_name=name,
        customer_email=email,
        subject=subject,
        description=description,
        created_via='AI Assistant Widget',
        session_id=chat_session_id
    )

    if success:
        return jsonify({
            'success': True,
            'ticket_number': ticket_dict['ticket_number'],
            'message': f"Ticket {ticket_dict['ticket_number']} confirmed! Our team will reach out to {email}."
        })
    else:
        return jsonify({
            'success': False,
            'message': error or 'Failed to generate support ticket.'
        }), 400


@assistant_bp.route('/api/chat/feedback', methods=['POST'])
def submit_feedback():
    """Save customer feedback and star ratings into MongoDB NoSQL storage."""
    data = request.get_json() or {}
    rating = data.get('rating', 5)
    comment = data.get('comment', '').strip()
    email = data.get('email', session.get('user_email', '')).strip()
    chat_session_id = data.get('session_id') or session.get('chat_session_id') or 'anon'

    nosql_service.save_feedback(
        session_id=chat_session_id,
        rating=int(rating),
        comment=comment,
        email=email
    )

    return jsonify({
        'success': True,
        'message': 'Thank you! Your feedback helps us curate even better mystery unboxings.'
    })


@assistant_bp.route('/api/chat/history', methods=['GET'])
def get_history():
    """Retrieve recent chat history for the active session."""
    chat_session_id = request.args.get('session_id') or session.get('chat_session_id')
    if not chat_session_id:
        return jsonify({'messages': []})

    history = nosql_service.get_recent_chat(chat_session_id, limit=12)
    return jsonify({'messages': history, 'session_id': chat_session_id})
