import logging
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from services.ticket_service import ticket_service

logger = logging.getLogger('mysterymart.routes.support')
support_bp = Blueprint('support', __name__)


@support_bp.route('/support', methods=['GET', 'POST'])
def support_page():
    """Customer support ticket creation and tracking page."""
    ticket_created = None
    lookup_result = None
    lookup_error = None

    # Handle Ticket Creation Form
    if request.method == 'POST' and 'create_ticket' in request.form:
        name = request.form.get('customer_name', '').strip()
        email = request.form.get('customer_email', '').strip()
        subject = request.form.get('subject', '').strip()
        description = request.form.get('description', '').strip()

        session_id = session.get('chat_session_id')
        success, ticket_dict, error_msg = ticket_service.create_ticket(
            customer_name=name,
            customer_email=email,
            subject=subject,
            description=description,
            created_via='Web Support Form',
            session_id=session_id
        )

        if success:
            ticket_created = ticket_dict
            flash(f"Support ticket {ticket_dict['ticket_number']} generated successfully! Our concierge team will email you shortly.", 'success')
        else:
            flash(error_msg or "Failed to submit ticket. Please check your information.", 'danger')

    # Handle Ticket Status Verification & Lookup
    elif request.method == 'POST' and 'track_ticket' in request.form:
        ticket_num = request.form.get('ticket_number', '').strip()
        email = request.form.get('verify_email', '').strip()

        success, ticket_dict, err = ticket_service.get_ticket_status(ticket_num, email)
        if success:
            lookup_result = ticket_dict
            flash(f"Ticket {ticket_num} found. Status: {ticket_dict['status']}", 'info')
        else:
            lookup_error = err
            flash(err, 'warning')

    return render_template(
        'support.html',
        ticket_created=ticket_created,
        lookup_result=lookup_result,
        lookup_error=lookup_error,
        user_email=session.get('user_email', ''),
        user_name=session.get('username', '')
    )
