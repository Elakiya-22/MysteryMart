import json
from models import Product
from routes.cart_routes import calculate_cart_totals


def test_server_side_cart_totals_calculation(app):
    """Verify server recalculates subtotal, delivery fee, and grand total."""
    with app.app_context():
        p1 = Product.query.first()
        assert p1 is not None

        # Simulate cart session dict
        cart_dict = {str(p1.id): 2}
        result = calculate_cart_totals(cart_dict)

        expected_subtotal = round(p1.price * 2, 2)
        assert result['subtotal'] == expected_subtotal
        assert result['item_count'] == 2

        # Check delivery calculation
        if expected_subtotal >= 99.00:
            assert result['delivery_fee'] == 0.0
            assert result['total_amount'] == expected_subtotal
        else:
            assert result['delivery_fee'] == 9.99
            assert result['total_amount'] == round(expected_subtotal + 9.99, 2)


def test_cart_prevents_negative_and_zero_quantities(app):
    """Verify negative or 0 quantities are excluded by server calculation."""
    with app.app_context():
        p1 = Product.query.first()
        cart_dict = {
            str(p1.id): -5,
            '99999': 2  # Non-existent product
        }
        result = calculate_cart_totals(cart_dict)
        assert result['item_count'] == 0
        assert result['subtotal'] == 0.0


def test_cart_caps_at_maximum_stock(app):
    """Verify quantity cannot exceed product's available stock."""
    with app.app_context():
        p = Product.query.first()
        stock = p.stock

        cart_dict = {str(p.id): stock + 50}
        result = calculate_cart_totals(cart_dict)
        assert result['item_count'] == stock


def test_ajax_add_to_cart_flow(client):
    """Verify AJAX add-to-cart endpoint."""
    product = Product.query.first()
    response = client.post(
        '/cart/add',
        data=json.dumps({'product_id': product.id, 'quantity': 1}),
        content_type='application/json',
        headers={'X-Requested-With': 'XMLHttpRequest'}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert data['item_count'] >= 1
