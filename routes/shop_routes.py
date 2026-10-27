import logging
from flask import Blueprint, render_template, request, abort
from models import Product, db

logger = logging.getLogger('mysterymart.routes.shop')
shop_bp = Blueprint('shop', __name__)


@shop_bp.route('/shop')
def catalog():
    """Shop page with category filters, price range, search, and sorting."""
    # Query parameters
    search_query = request.args.get('q', '').strip()
    selected_category = request.args.get('category', '').strip()
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    sort_by = request.args.get('sort', 'popular').strip()

    query = Product.query.filter_by(is_active=True)

    # 1. Search Filter
    if search_query:
        search_term = f"%{search_query}%"
        query = query.filter(
            db.or_(
                Product.name.ilike(search_term),
                Product.description.ilike(search_term),
                Product.category.ilike(search_term),
                Product.guaranteed_inclusions.ilike(search_term)
            )
        )

    # 2. Category Filter
    if selected_category and selected_category != 'All':
        query = query.filter_by(category=selected_category)

    # 3. Price Range Filter
    if min_price is not None and min_price >= 0:
        query = query.filter(Product.price >= min_price)
    if max_price is not None and max_price > 0:
        query = query.filter(Product.price <= max_price)

    # 4. Sorting
    if sort_by == 'price_low':
        query = query.order_by(Product.price.asc())
    elif sort_by == 'price_high':
        query = query.order_by(Product.price.desc())
    elif sort_by == 'rating':
        query = query.order_by(Product.rating.desc())
    elif sort_by == 'newest':
        query = query.order_by(Product.id.desc())
    else:  # 'popular'
        query = query.order_by(Product.review_count.desc(), Product.rating.desc())

    products = query.all()

    # Get distinct categories for filter buttons
    categories = [
        'All',
        'Gadget Mystery Box',
        'Gaming Mystery Box',
        'Stationery Mystery Box',
        'Fashion Mystery Box',
        'Beauty & Accessories Mystery Box',
        'Premium Mystery Box'
    ]

    return render_template(
        'shop.html',
        products=products,
        categories=categories,
        selected_category=selected_category or 'All',
        search_query=search_query,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by,
        total_count=len(products)
    )


@shop_bp.route('/product/<int:product_id>')
def product_details(product_id: int):
    """Product details page with guaranteed inclusions, related boxes, and disclosure."""
    product = db.session.get(Product, product_id)
    if not product or not product.is_active:
        abort(404)

    # Fetch related products from the same category or overall popular
    related_products = Product.query.filter(
        Product.id != product.id,
        Product.is_active == True,
        Product.category == product.category
    ).limit(3).all()

    if len(related_products) < 3:
        additional = Product.query.filter(
            Product.id != product.id,
            Product.is_active == True,
            Product.category != product.category
        ).limit(3 - len(related_products)).all()
        related_products.extend(additional)

    return render_template(
        'product.html',
        product=product,
        related_products=related_products
    )
