import re
import logging
from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify, abort
from models import db, Product, Order, OrderItem, User
from routes.cart_routes import get_cart_session, calculate_cart_totals
from services.weather_service import weather_service
from routes.error_handlers import MysteryMartConcurrencyError

logger = logging.getLogger('mysterymart.routes.checkout')
checkout_bp = Blueprint('checkout', __name__)


@checkout_bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    """Checkout page with server-side validation, weather preview, and simulated payment."""
    cart_dict = get_cart_session()
    cart_data = calculate_cart_totals(cart_dict)

    if not cart_data['items']:
        flash('Your mystery cart is empty! Choose a surprise box before checkout.', 'warning')
        return redirect(url_for('shop.catalog'))

    # Pre-fill user data if authenticated
    user_id = session.get('user_id')
    user = User.query.get(user_id) if user_id else None

    if request.method == 'POST':
        # 1. Server-side Input Validation
        full_name = request.form.get('customer_name', '').strip()
        email = request.form.get('customer_email', '').strip().lower()
        phone = request.form.get('customer_phone', '').strip()
        address = request.form.get('shipping_address', '').strip()
        city = request.form.get('city', '').strip()
        state = request.form.get('state', '').strip()
        postal_code = request.form.get('postal_code', '').strip()
        delivery_notes = request.form.get('delivery_notes', '').strip()
        payment_method = request.form.get('payment_method', 'Simulated Card Payment').strip()

        errors = []
        if not full_name or len(full_name) < 2:
            errors.append("Please provide a valid recipient name (minimum 2 characters).")
        if not email or not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            errors.append("Please provide a valid delivery contact email address.")
        if not address or len(address) < 5:
            errors.append("Please provide a complete shipping street address.")
        if not city or len(city) < 2:
            errors.append("Please provide your delivery city.")
        if not postal_code or len(postal_code) < 3:
            errors.append("Please provide a valid postal or ZIP code.")

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template(
                'checkout.html',
                cart=cart_data,
                user=user,
                form_data=request.form
            )

        # 2. Re-verify Stock and Recalculate Totals in Database Transaction
        try:
            # Check for stock sufficiency
            for item in cart_data['items']:
                product = Product.query.with_for_update().get(item['product'].id)
                if not product or not product.is_active or product.stock < item['quantity']:
                    db.session.rollback()
                    # Trigger custom 460 if out of stock concurrency collision happens
                    logger.warning("Unboxing concurrency stock collision for product %s", product.name if product else item['product'].id)
                    raise MysteryMartConcurrencyError("Unboxing concurrency stock collision")

            # 3. Third-party Weather API Lookup for Delivery Destination
            weather_info = weather_service.get_weather_for_city(city)
            weather_note = weather_info.get('summary', f"Dispatched to {city}")

            # 4. Create Order Record
            new_order = Order(
                user_id=user.id if user else None,
                customer_name=full_name,
                customer_email=email,
                customer_phone=phone or None,
                shipping_address=address,
                city=city,
                state=state or None,
                postal_code=postal_code,
                delivery_notes=delivery_notes or None,
                subtotal=cart_data['subtotal'],
                delivery_fee=cart_data['delivery_fee'],
                total_amount=cart_data['total_amount'],
                payment_method=f"{payment_method} (Simulated Demo)",
                payment_status='Completed (Simulated)',
                status='Processing',
                weather_note=weather_note
            )
            db.session.add(new_order)
            db.session.flush()  # Generate order ID

            # 5. Create Order Items & Decrement Stock
            for item in cart_data['items']:
                product = Product.query.get(item['product'].id)
                product.stock -= item['quantity']
                
                order_item = OrderItem(
                    order_id=new_order.id,
                    product_id=product.id,
                    quantity=item['quantity'],
                    unit_price=product.price
                )
                db.session.add(order_item)

            # Commit Transaction
            db.session.commit()
            logger.info("Order %s successfully placed for %s ($%.2f)", new_order.order_number, email, new_order.total_amount)

            # 6. Clear session cart
            session['cart'] = {}
            session.modified = True

            # Save order reference in session for easy confirmation lookup
            session['last_order_number'] = new_order.order_number

            flash(f"Order #{new_order.order_number} confirmed! Your surprise is being packaged.", 'success')
            return redirect(url_for('checkout.order_confirmation', order_number=new_order.order_number))

        except Exception as e:
            db.session.rollback()
            if hasattr(e, 'code') and e.code == 460:
                raise e
            logger.error("Checkout transaction failure: %s", e)
            flash("A processing error occurred during checkout. Your card was not charged. Please try again.", 'danger')
            return render_template('checkout.html', cart=cart_data, user=user, form_data=request.form)

    # GET Request: check initial weather for default city or user's city
    default_city = 'New York'
    weather_preview = weather_service.get_weather_for_city(default_city)

    return render_template(
        'checkout.html',
        cart=cart_data,
        user=user,
        weather_preview=weather_preview
    )


@checkout_bp.route('/checkout/weather-check')
def weather_check():
    """AJAX endpoint for dynamically fetching weather when customer types their city."""
    city = request.args.get('city', '').strip()
    if not city:
        return jsonify({'available': False, 'message': 'No city provided'})
    weather = weather_service.get_weather_for_city(city)
    return jsonify(weather)


@checkout_bp.route('/order-confirmation/<order_number>')
def order_confirmation(order_number: str):
    """Order confirmation and tracking details page."""
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    return render_template('order_confirmation.html', order=order)
