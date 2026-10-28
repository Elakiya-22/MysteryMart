import json
from models import Product


def test_home_page_returns_200(client):
    """Test that homepage loads successfully with branding and sections."""
    response = client.get('/')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'MysteryMart' in html
    assert 'Unbox the' in html
    assert 'Discover Mystery Boxes' in html
    assert 'How MysteryMart Works' in html


def test_shop_page_returns_200(client):
    """Test catalog loading and product listings."""
    response = client.get('/shop')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'Mystery Box Collection' in html
    assert 'Gadget Mystery Box' in html


def test_product_details_page(client):
    """Test product details page for valid and invalid product IDs."""
    product = Product.query.first()
    assert product is not None

    response = client.get(f'/product/{product.id}')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert product.name in html
    assert 'Guaranteed Box Inclusions' in html
    assert 'Surprise Contents Disclosure' in html

    # Invalid product ID returns 404
    bad_resp = client.get('/product/999999')
    assert bad_resp.status_code == 404


def test_cart_page(client):
    """Test cart page loads."""
    response = client.get('/cart')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'Mystery Cart' in html


def test_faq_page(client):
    """Test FAQ page loads."""
    response = client.get('/faq')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'Frequently Asked Questions' in html
    assert 'mysteryFaqAccordion' in html


def test_support_page(client):
    """Test support page loads."""
    response = client.get('/support')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'Create Support Ticket' in html
    assert 'Track Ticket Status' in html


def test_auth_pages(client):
    """Test login and register pages load."""
    login_resp = client.get('/login')
    assert login_resp.status_code == 200
    assert 'Sign In to MysteryMart' in login_resp.get_data(as_text=True)

    reg_resp = client.get('/register')
    assert reg_resp.status_code == 200
    assert 'Join MysteryMart' in reg_resp.get_data(as_text=True)


def test_health_check_endpoint(client):
    """Test structured /health endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert data['app'] == 'MysteryMart'
    assert 'sql_database' in data['services']
    assert data['services']['sql_database']['status'] == 'up'
    assert data['services']['sql_database']['products_count'] > 0
    assert data['services']['sql_database']['faqs_count'] >= 10


def test_render_direct_serves_homepage(client):
    """Test that requests to mysterymart1.onrender.com directly serve the homepage."""
    response = client.get('/', headers={'Host': 'mysterymart1.onrender.com'})
    assert response.status_code == 200
    assert b'MysteryMart' in response.data
