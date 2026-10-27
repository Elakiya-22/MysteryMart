from models import SupportTicket
from services.ticket_service import ticket_service


def test_ticket_creation_and_unique_reference(app):
    """Verify ticket creation in SQL with MM-TKT-XXXXXX format."""
    with app.app_context():
        success, ticket, err = ticket_service.create_ticket(
            customer_name="John Mystery",
            customer_email="john@mysterymart.test",
            subject="Question regarding box unboxing",
            description="I would like to verify the delivery date of my mystery package."
        )

        assert success is True
        assert err is None
        assert ticket['ticket_number'].startswith("MM-TKT-")
        assert len(ticket['ticket_number']) >= 10

        # Verify persisted in SQL
        db_ticket = SupportTicket.query.filter_by(ticket_number=ticket['ticket_number']).first()
        assert db_ticket is not None
        assert db_ticket.customer_email == "john@mysterymart.test"


def test_ticket_deduplication(app):
    """Verify repeated identical submissions are deduplicated to prevent duplicate tickets."""
    with app.app_context():
        # First submission
        s1, t1, e1 = ticket_service.create_ticket(
            customer_name="Sarah Connor",
            customer_email="sarah@resistance.test",
            subject="Repeat Submission Test",
            description="Testing automated deduplication filter in ticket service."
        )
        assert s1 is True

        # Second immediate submission with identical email & subject
        s2, t2, e2 = ticket_service.create_ticket(
            customer_name="Sarah Connor",
            customer_email="sarah@resistance.test",
            subject="Repeat Submission Test",
            description="Testing automated deduplication filter in ticket service."
        )
        assert s2 is True
        # Must return the existing ticket reference, not create a new one!
        assert t1['ticket_number'] == t2['ticket_number']


def test_ticket_status_verification_lookup(app):
    """Verify ticket lookup requires email verification for privacy."""
    with app.app_context():
        success, t, _ = ticket_service.create_ticket(
            customer_name="Bruce Wayne",
            customer_email="bruce@wayne.test",
            subject="VIP Sovereign delivery",
            description="Checking status of titanium EDC package."
        )
        tkt_num = t['ticket_number']

        # Lookup with correct email -> Success
        ok, res, err = ticket_service.get_ticket_status(tkt_num, "bruce@wayne.test")
        assert ok is True
        assert res['ticket_number'] == tkt_num

        # Lookup with mismatched email -> Rejected for privacy
        bad_ok, bad_res, bad_err = ticket_service.get_ticket_status(tkt_num, "wrong@email.test")
        assert bad_ok is False
        assert "does not match" in bad_err.lower()
