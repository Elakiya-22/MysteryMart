import logging
import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
from models import db, SupportTicket
from services.nosql_service import nosql_service

logger = logging.getLogger('mysterymart.tickets')


class TicketService:
    """Service to create, validate, deduplicate, and look up support tickets."""

    @staticmethod
    def validate_ticket_data(name: str, email: str, subject: str, description: str) -> Tuple[bool, Optional[str]]:
        """Validate ticket submission fields on server."""
        if not name or len(name.strip()) < 2:
            return False, "Please provide your full name (at least 2 characters)."
        
        email_clean = email.strip() if email else ''
        if not email_clean or not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email_clean):
            return False, "Please provide a valid email address for updates."
        
        if not subject or len(subject.strip()) < 4:
            return False, "Please provide a descriptive subject (at least 4 characters)."
        
        if not description or len(description.strip()) < 10:
            return False, "Please describe your query in detail (at least 10 characters)."
            
        return True, None

    @classmethod
    def create_ticket(
        cls,
        customer_name: str,
        customer_email: str,
        subject: str,
        description: str,
        created_via: str = 'Web Form',
        session_id: Optional[str] = None
    ) -> Tuple[bool, Dict[str, Any], Optional[str]]:
        """
        Create a new support ticket in the SQL database.
        Includes server-side validation and deduplication to prevent spam/double-clicks.
        """
        is_valid, error_msg = cls.validate_ticket_data(customer_name, customer_email, subject, description)
        if not is_valid:
            return False, {}, error_msg

        clean_name = customer_name.strip()
        clean_email = customer_email.strip().lower()
        clean_subject = subject.strip()
        clean_desc = description.strip()

        # Deduplication: Check if an identical ticket was submitted by this email in the last 5 minutes
        recent_cutoff = datetime.utcnow() - timedelta(minutes=5)
        existing = SupportTicket.query.filter(
            SupportTicket.customer_email == clean_email,
            SupportTicket.subject == clean_subject,
            SupportTicket.created_at >= recent_cutoff
        ).first()

        if existing:
            logger.info("Deduplicated repeated ticket submission for %s: %s", clean_email, existing.ticket_number)
            return True, existing.to_dict(), f"Existing ticket {existing.ticket_number} already recorded."

        try:
            ticket = SupportTicket(
                customer_name=clean_name,
                customer_email=clean_email,
                subject=clean_subject,
                description=clean_desc,
                created_via=created_via,
                status='Open',
                priority='Normal'
            )
            db.session.add(ticket)
            db.session.commit()

            # Record event in MongoDB / NoSQL service
            if session_id:
                nosql_service.save_chat_log(
                    session_id=session_id,
                    role='system',
                    message=f"Support ticket created: {ticket.ticket_number}",
                    meta={'ticket_number': ticket.ticket_number, 'subject': clean_subject}
                )

            logger.info("Successfully created support ticket: %s for %s", ticket.ticket_number, clean_email)
            return True, ticket.to_dict(), None

        except Exception as e:
            db.session.rollback()
            logger.error("Failed to create support ticket in SQL: %s", e)
            return False, {}, "An unexpected error occurred while creating your ticket. Please try again."

    @staticmethod
    def get_ticket_status(ticket_number: str, email: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Securely look up ticket status verifying the customer's email.
        Prevents revealing private ticket details to unauthorized parties.
        """
        if not ticket_number or not email:
            return False, None, "Ticket reference and registered email are required."

        clean_tkt = ticket_number.strip().upper()
        clean_email = email.strip().lower()

        ticket = SupportTicket.query.filter_by(ticket_number=clean_tkt).first()
        if not ticket:
            return False, None, f"No ticket found matching reference '{clean_tkt}'."

        if ticket.customer_email.lower() != clean_email:
            return False, None, "Email address does not match the ticket record. Please check your details."

        return True, ticket.to_dict(), None


ticket_service = TicketService()
