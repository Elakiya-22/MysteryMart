import logging
from flask import Blueprint, render_template, request, jsonify
from services.faq_service import faq_service

logger = logging.getLogger('mysterymart.routes.faq')
faq_bp = Blueprint('faq', __name__)


@faq_bp.route('/faq')
def faq_page():
    """Frequently Asked Questions page backed by SQL database."""
    search_query = request.args.get('q', '').strip()
    selected_cat = request.args.get('category', '').strip()

    categories = faq_service.get_categories()

    if search_query:
        faqs = faq_service.search_faqs(search_query, limit=20)
    elif selected_cat and selected_cat != 'All':
        faqs = [faq.to_dict() for faq in faq_service.get_by_category(selected_cat)]
    else:
        faqs = [faq.to_dict() for faq in faq_service.get_all_faqs()]

    return render_template(
        'faq.html',
        faqs=faqs,
        categories=categories,
        selected_category=selected_cat or 'All',
        search_query=search_query,
        faq_count=len(faqs)
    )


@faq_bp.route('/api/faqs/search')
def api_search_faqs():
    """Live search API for client-side search autocomplete and instant filtering."""
    query = request.args.get('q', '').strip()
    results = faq_service.search_faqs(query, limit=8)
    return jsonify({
        'query': query,
        'count': len(results),
        'results': results
    })
