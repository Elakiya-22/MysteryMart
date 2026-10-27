import logging
from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify, flash, has_request_context
from models import db, Product

logger = logging.getLogger('mysterymart.routes.cart')
cart_bp = Blueprint('cart', __name__)

STANDARD_DELIVERY_FEE = 9.99
FREE_DELIVERY_THRESHOLD = 99.00


def get_cart_session() -> dict:
    """Retrieve or initialize cart dictionary in user session: {product_id_str: quantity_int}."""
    if 'cart' not in session or not isinstance(session['cart'], dict):
        session['cart'] = {}
    return session['cart']


def calculate_cart_totals(cart_dict: dict):
    """
    Recalculates cart items, quantities, subtotal, delivery charges, and total strictly on the server.
    Ensures negative or zero quantities are removed and stock limits are respected.
    """
    items = []
    subtotal = 0.0
    total_quantity = 0

    clean_cart = {}

    for prod_id_str, qty in list(cart_dict.items()):
        try:
            prod_id = int(prod_id_str)
            quantity = int(qty)
        except (ValueError, TypeError):
            continue

        if quantity <= 0:
            continue

        product = db.session.get(Product, prod_id)
        if not product or not product.is_active:
            continue

        # Cap quantity to available stock
        adjusted_qty = min(quantity, product.stock)
        if adjusted_qty <= 0:
            continue

        clean_cart[str(prod_id)] = adjusted_qty
        line_total = product.price * adjusted_qty
        subtotal += line_total
        total_quantity += adjusted_qty

        items.append({
            'product': product,
            'quantity': adjusted_qty,
            'unit_price': product.price,
            'line_total': round(line_total, 2),
            'stock_available': product.stock
        })

    # Update session cart with cleaned valid items if in request context
    if has_request_context():
        session['cart'] = clean_cart
        session.modified = True

    # Calculate delivery fee
    delivery_fee = 0.0 if (subtotal >= FREE_DELIVERY_THRESHOLD or subtotal == 0) else STANDARD_DELIVERY_FEE
    total_amount = subtotal + delivery_fee

    return {
        'items': items,
        'cart_items': items,
        'item_count': total_quantity,
        'subtotal': round(subtotal, 2),
        'delivery_fee': round(delivery_fee, 2),
        'total_amount': round(total_amount, 2),
        'free_delivery_threshold': FREE_DELIVERY_THRESHOLD,
        'amount_needed_for_free_delivery': max(0.0, round(FREE_DELIVERY_THRESHOLD - subtotal, 2)) if subtotal > 0 else 0.0
    }


@cart_bp.route('/cart')
def view_cart():
    """Shopping cart page view."""
    cart_dict = get_cart_session()
    cart_data = calculate_cart_totals(cart_dict)
    return render_template('cart.html', cart=cart_data)


@cart_bp.route('/cart/add', methods=['POST'])
def add_to_cart():
    """Add a mystery box to cart with server-side stock validation."""
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json

    if request.is_json:
        data = request.get_json()
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
    else:
        product_id = request.form.get('product_id')
        quantity = request.form.get('quantity', 1)

    try:
        product_id = int(product_id)
        quantity = int(quantity)
    except (ValueError, TypeError):
        if is_ajax:
            return jsonify({'success': False, 'message': 'Invalid product or quantity'}), 400
        flash('Invalid product request.', 'danger')
        return redirect(url_for('shop.catalog'))

    if quantity <= 0:
        if is_ajax:
            return jsonify({'success': False, 'message': 'Quantity must be at least 1'}), 400
        flash('Quantity must be greater than zero.', 'warning')
        return redirect(url_for('shop.catalog'))

    product = db.session.get(Product, product_id)
    if not product or not product.is_active:
        if is_ajax:
            return jsonify({'success': False, 'message': 'Selected mystery box is unavailable.'}), 404
        flash('Mystery box not found.', 'danger')
        return redirect(url_for('shop.catalog'))

    cart = get_cart_session()
    current_qty = cart.get(str(product_id), 0)
    new_qty = current_qty + quantity

    if new_qty > product.stock:
        new_qty = product.stock
        message = f"Maximum available stock for {product.name} ({product.stock}) reached."
    else:
        message = f"Added {product.name} to your mystery cart!"

    cart[str(product_id)] = new_qty
    session['cart'] = cart
    session.modified = True

    cart_data = calculate_cart_totals(cart)

    if is_ajax:
        return jsonify({
            'success': True,
            'message': message,
            'item_count': cart_data['item_count'],
            'cart_subtotal': cart_data['subtotal'],
            'cart_total': cart_data['total_amount']
        })

    flash(message, 'success')
    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/cart/update', methods=['POST'])
def update_cart():
    """Update quantity for a cart line item."""
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json

    if request.is_json:
        data = request.get_json()
        product_id = data.get('product_id')
        quantity = data.get('quantity')
    else:
        product_id = request.form.get('product_id')
        quantity = request.form.get('quantity')

    try:
        product_id = int(product_id)
        quantity = int(quantity)
    except (ValueError, TypeError):
        if is_ajax:
            return jsonify({'success': False, 'message': 'Invalid parameters'}), 400
        return redirect(url_for('cart.view_cart'))

    cart = get_cart_session()
    prod_key = str(product_id)

    if quantity <= 0:
        cart.pop(prod_key, None)
    else:
        product = db.session.get(Product, product_id)
        if product:
            cart[prod_key] = min(quantity, product.stock)

    session['cart'] = cart
    session.modified = True
    cart_data = calculate_cart_totals(cart)

    if is_ajax:
        return jsonify({
            'success': True,
            'item_count': cart_data['item_count'],
            'subtotal': cart_data['subtotal'],
            'delivery_fee': cart_data['delivery_fee'],
            'total_amount': cart_data['total_amount']
        })

    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/cart/remove/<int:product_id>', methods=['POST', 'GET'])
def remove_from_cart(product_id: int):
    """Remove item from cart completely."""
    cart = get_cart_session()
    cart.pop(str(product_id), None)
    session['cart'] = cart
    session.modified = True
    flash('Item removed from cart.', 'info')
    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/cart/clear', methods=['POST'])
def clear_cart():
    """Empty cart."""
    session['cart'] = {}
    session.modified = True
    flash('Your mystery cart has been cleared.', 'info')
    return redirect(url_for('cart.view_cart'))
