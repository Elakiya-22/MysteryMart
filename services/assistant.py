import os
import re
import logging
from typing import Dict, Any, Optional, List
from services.faq_service import faq_service
from services.ticket_service import ticket_service
from services.nosql_service import nosql_service
from models import Order, User

logger = logging.getLogger('mysterymart.assistant')

# HTTP Status Code Explanations supported by MysteryMart
HTTP_ERROR_KNOWLEDGE = {
    '400': {
        'title': '400 — Bad Request',
        'explanation': 'The server could not understand the request due to invalid syntax, missing parameters, or malformed data.',
        'troubleshooting': 'Check your cart parameters or form fields, clear your browser cache, and try submitting again.'
    },
    '401': {
        'title': '401 — Unauthorized',
        'explanation': 'Authentication is required to view this private page or order history.',
        'troubleshooting': 'Please log in with your MysteryMart account credentials or create a new account to continue.'
    },
    '403': {
        'title': '403 — Forbidden',
        'explanation': 'You do not have permission to access this administrative resource.',
        'troubleshooting': 'Ensure you are signed in with the correct authorized privileges.'
    },
    '404': {
        'title': '404 — Page Not Found',
        'explanation': 'The requested MysteryMart box page or link could not be located on our servers.',
        'troubleshooting': 'Check for typos in the URL, explore our Shop page, or search for your favorite mystery box category.'
    },
    '429': {
        'title': '429 — Too Many Requests',
        'explanation': 'Rate limit exceeded. Too many requests have been sent within a short window to protect our servers.',
        'troubleshooting': 'Please pause for 30-60 seconds before retrying your login or chat inquiry.'
    },
    '460': {
        'title': '460 — MysteryMart Unboxing Concurrency Exception (Application Custom Code)',
        'explanation': 'Notice: 460 is an application-specific custom status code, not a standard RFC HTTP status. It indicates a real-time inventory conflict where the final mystery box of a batch was reserved by another shopper during checkout.',
        'troubleshooting': 'Return to the Shop page and select another mystery box tier or category. Stock refreshes frequently!'
    },
    '500': {
        'title': '500 — Internal Server Error',
        'explanation': 'An unexpected server-side glitch occurred while processing your request.',
        'troubleshooting': 'Our engineering team has received the diagnostic trace. Please refresh in a moment or create a support ticket if urgent.'
    },
    '503': {
        'title': '503 — Service Unavailable',
        'explanation': 'The server or dependent upstream service is temporarily overwhelmed or under maintenance.',
        'troubleshooting': 'MysteryMart will resume normal operations momentarily. Deliveries and orders already placed remain secure.'
    }
}


class AIAssistantService:
    """Core AI Customer Support Assistant orchestrator."""

    def __init__(self):
        self.provider = os.environ.get('AI_PROVIDER', 'fallback')
        self.gemini_key = os.environ.get('GEMINI_API_KEY')
        self.openai_key = os.environ.get('OPENAI_API_KEY')

    def get_mode_label(self) -> str:
        """Return the active assistant operational mode."""
        if self.gemini_key and self.provider == 'gemini':
            return "MysteryMart AI (Gemini Enhanced)"
        elif self.openai_key and self.provider == 'openai':
            return "MysteryMart AI (OpenAI Enhanced)"
        else:
            return "MysteryMart Assistant (Verified FAQ & Concierge Mode)"

    def process_message(
        self,
        session_id: str,
        user_message: str,
        user_id: Optional[int] = None,
        user_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process user message through multi-stage pipeline:
        1. Log user message to MongoDB
        2. Detect HTTP status code queries
        3. Detect Order tracking queries (with privacy verification)
        4. Detect Ambiguous queries (clarifying questions)
        5. Retrieve from SQL FAQ database
        6. AI augmentation or graceful ticket escalation
        7. Log bot response to MongoDB
        """
        raw_msg = (user_message or '').strip()
        if not raw_msg:
            return {
                'response': "Hello! I'm your MysteryMart Concierge. How can I help you unbox something amazing today?",
                'source': 'system',
                'actions': ['Browse Boxes', 'Track Order', 'FAQ', 'Contact Support']
            }

        # 1. Save user turn to MongoDB / NoSQL
        nosql_service.save_chat_log(session_id, 'user', raw_msg, {'user_id': user_id})

        # 2. Check for HTTP error code questions
        error_resp = self._check_http_error_query(raw_msg)
        if error_resp:
            self._save_assistant_reply(session_id, error_resp['response'], 'http_kb')
            return error_resp

        # 3. Check for Order tracking query
        order_resp = self._check_order_query(raw_msg, user_id, user_email)
        if order_resp:
            self._save_assistant_reply(session_id, order_resp['response'], 'order_tracking')
            return order_resp

        # 4. Check for Short / Ambiguous Queries
        clarify_resp = self._check_clarifying_questions(raw_msg)
        if clarify_resp:
            self._save_assistant_reply(session_id, clarify_resp['response'], 'clarification')
            return clarify_resp

        # 5. Retrieve from SQL FAQ database
        faq_matches = faq_service.search_faqs(raw_msg, limit=3)
        if faq_matches and faq_matches[0].get('score', 0) >= 20:
            top_faq = faq_matches[0]
            reply_text = f"**{top_faq['question']}**\n\n{top_faq['answer']}"
            
            related_titles = [f['question'] for f in faq_matches[1:3]]
            
            resp_payload = {
                'response': reply_text,
                'source': 'verified_faq',
                'faq_id': top_faq['id'],
                'category': top_faq['category'],
                'confidence': 'High (Verified SQL FAQ)',
                'suggested_questions': related_titles,
                'mode': self.get_mode_label(),
                'can_escalate': True
            }
            self._save_assistant_reply(session_id, reply_text, 'verified_faq')
            return resp_payload

        # 6. Fallback or AI Generation when no verified FAQ matches
        if self.gemini_key and self.provider == 'gemini':
            ai_reply = self._generate_gemini_response(raw_msg, faq_matches)
            if ai_reply:
                self._save_assistant_reply(session_id, ai_reply, 'gemini_ai')
                return {
                    'response': ai_reply,
                    'source': 'gemini_ai',
                    'confidence': 'AI Generated (FAQ Augmented)',
                    'mode': self.get_mode_label(),
                    'can_escalate': True
                }

        # Safe, honest FAQ-based fallback (Prompt rule: do not pretend an answer came from FAQ)
        fallback_msg = (
            "I searched our verified FAQ database but could not find a confirmed answer for your specific question.\n\n"
            "To ensure you receive completely accurate details, I can open a priority support ticket for our concierge team! "
            "Simply click below or let me know your details."
        )

        resp_payload = {
            'response': fallback_msg,
            'source': 'faq_fallback',
            'confidence': 'No Direct FAQ Match',
            'mode': self.get_mode_label(),
            'offer_ticket': True,
            'actions': ['Open Support Ticket', 'Search FAQs', 'View Return Policy']
        }
        self._save_assistant_reply(session_id, fallback_msg, 'faq_fallback')
        return resp_payload

    def _check_http_error_query(self, query: str) -> Optional[Dict[str, Any]]:
        """Identify if customer is asking about HTTP or custom 460 error codes."""
        code_match = re.search(r'\b(400|401|403|404|429|460|500|503)\b', query)
        if code_match or 'error code' in query.lower() or 'status code' in query.lower():
            code = code_match.group(1) if code_match else '404'
            info = HTTP_ERROR_KNOWLEDGE.get(code)
            if info:
                msg = (
                    f"### {info['title']}\n\n"
                    f"**Explanation:** {info['explanation']}\n\n"
                    f"**Suggested Troubleshooting:** {info['troubleshooting']}\n\n"
                    f"*Need further assistance? You can ask me to open a support ticket at any time.*"
                )
                return {
                    'response': msg,
                    'source': 'http_knowledge_base',
                    'error_code': code,
                    'mode': self.get_mode_label()
                }
        return None

    def _check_order_query(self, query: str, user_id: Optional[int], user_email: Optional[str]) -> Optional[Dict[str, Any]]:
        """Privacy-preserving order inquiry handler."""
        ord_match = re.search(r'\b(MM-ORD-[A-Za-z0-9]+)\b', query, re.IGNORECASE)
        if ord_match:
            order_num = ord_match.group(1).upper()
            order = Order.query.filter_by(order_number=order_num).first()
            if not order:
                return {
                    'response': f"No order found matching reference `{order_num}`. Please verify your order receipt.",
                    'source': 'order_lookup'
                }

            # Privacy rule: Require authentication or email verification
            email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', query)
            provided_email = email_match.group(0).lower() if email_match else (user_email or '').lower()

            if not provided_email or provided_email != order.customer_email.lower():
                return {
                    'response': (
                        f"I located reference `{order_num}`! To protect your privacy and order contents, "
                        f"please provide the registered email address used during purchase, or sign in to your account."
                    ),
                    'source': 'order_auth_required',
                    'requires_verification': True
                }

            # Verified customer
            item_names = ", ".join([item.product.name for item in order.items if item.product])
            return {
                'response': (
                    f"### Order Details: {order.order_number}\n\n"
                    f"- **Status:** {order.status}\n"
                    f"- **Mystery Boxes:** {item_names}\n"
                    f"- **Total Amount:** ${order.total_amount:.2f}\n"
                    f"- **Delivery Destination:** {order.city}, {order.postal_code}\n"
                    f"- **Dispatch Status:** {order.weather_note or 'On schedule'}\n"
                ),
                'source': 'order_verified',
                'order': order.to_dict()
            }

        return None

    def _check_clarifying_questions(self, query: str) -> Optional[Dict[str, Any]]:
        """Provide helpful clarifying questions for vague single-word inputs."""
        q_lower = query.lower().strip()
        single_words = {
            'shipping': "Are you asking about our **standard delivery times (3-5 business days)**, **delivery fees**, or **international shipping coverage**?",
            'refund': "Would you like information on our **Mystery Box Replacement Policy**, **cancellation before dispatch**, or **damaged parcel claims**?",
            'boxes': "Are you interested in our **Gadget Box**, **Gaming Box**, **Stationery Box**, **Fashion Box**, or **Premium Collector Tier**?",
            'price': "Our mystery boxes range from **$29.99 for Stationery** up to **$249.99 for Premium Collector Edition**. Free delivery applies on orders over $999! Which category fits your budget?",
            'mystery': "Every MysteryMart box includes guaranteed items of equal or greater value plus surprise items! Which category would you like to explore?"
        }

        if q_lower in single_words:
            return {
                'response': single_words[q_lower],
                'source': 'clarification_prompt',
                'mode': self.get_mode_label(),
                'actions': ['Explore Shop', 'View All FAQs', 'Contact Concierge']
            }
        return None

    def _generate_gemini_response(self, query: str, faqs: List[Dict[str, Any]]) -> Optional[str]:
        """Optional Gemini API integration when GEMINI_API_KEY is configured."""
        try:
            import requests
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_key}"
            context = "\n".join([f"Q: {f['question']} A: {f['answer']}" for f in faqs[:2]])
            prompt = (
                f"You are the MysteryMart Unboxing Concierge. Help the customer politely.\n"
                f"Context from Verified FAQs:\n{context}\n\n"
                f"Customer Query: {query}\n"
                f"Guidelines: Be concise, exciting, helpful. Never invent non-existent products or false prize claims."
            )
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            res = requests.post(url, json=payload, timeout=5)
            if res.status_code == 200:
                data = res.json()
                return data['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            logger.warning("Gemini AI request failed: %s. Using fallback.", e)
        return None

    def _save_assistant_reply(self, session_id: str, reply: str, source: str):
        """Record bot reply in MongoDB / NoSQL."""
        nosql_service.save_chat_log(session_id, 'assistant', reply, {'source': source})


assistant_service = AIAssistantService()
