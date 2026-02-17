import pytest
import json
from app import app, generate_short_code, validate_click
from models import Base, Link, Click, MonthlyStat
from database import engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch

# Setup test database
TEST_DB_URL = "postgresql://postgres:postgres@localhost:5432/fiverr_test"

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        # Create all tables in the test database
        Base.metadata.create_all(engine)
        yield client
        # Drop all tables after tests
        Base.metadata.drop_all(engine)

def test_hello_endpoint(client):
    """Test the hello endpoint works"""
    response = client.get('/hello')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'message' in data
    assert data['message'] == 'Hello Fiverr'

def test_generate_short_code():
    """Test short code generation"""
    code = generate_short_code()
    assert len(code) == 6
    assert all(c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789' for c in code)

    # Test different length
    code = generate_short_code(length=8)
    assert len(code) == 8

def test_validate_click():
    """Test click validation returns boolean"""
    with patch('time.sleep'):  # Mock sleep to speed up tests
        result = validate_click()
        assert isinstance(result, bool)

def test_create_short_link(client):
    """Test creating a new short link"""
    # Test missing target_url
    response = client.post('/links', json={})
    assert response.status_code == 400

    # Test missing seller_id
    response = client.post('/links', json={'target_url': 'https://fiverr.com'})
    assert response.status_code == 400

    # Test successful creation
    response = client.post('/links', json={
        'target_url': 'https://fiverr.com',
        'seller_id': 'test_seller'
    })
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'short_code' in data
    assert 'short_url' in data
    assert data['original_url'] == 'https://fiverr.com'

    # Test duplicate URL returns same short code
    response2 = client.post('/links', json={
        'target_url': 'https://fiverr.com',
        'seller_id': 'test_seller'
    })
    assert response2.status_code == 200  # Not 201 because it's a duplicate
    data2 = json.loads(response2.data)
    assert data2['short_code'] == data['short_code']  # Same short code

def test_redirect_short_link(client):
    """Test redirection from short link"""
    # First create a short link
    response = client.post('/links', json={
        'target_url': 'https://fiverr.com',
        'seller_id': 'test_seller'
    })
    data = json.loads(response.data)
    short_code = data['short_code']

    # Test redirection
    with patch('app.validate_click', return_value=True):  # Force validation to be true
        response = client.get(f'/{short_code}')
        assert response.status_code == 302  # Redirect status
        assert response.headers['Location'] == 'https://fiverr.com'

    # Test nonexistent short code
    response = client.get('/nonexistent')
    assert response.status_code == 404

def test_stats_endpoint(client):
    """Test the stats endpoint"""
    # First create some links
    client.post('/links', json={'target_url': 'https://fiverr.com/1', 'seller_id': 'seller1'})
    client.post('/links', json={'target_url': 'https://fiverr.com/2', 'seller_id': 'seller2'})

    # Test stats endpoint
    response = client.get('/stats')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)  # Should be a list not an object
    assert len(data) >= 2

    # Check if the response structure matches the expected format
    for item in data:
        assert 'url' in item
        assert 'total_clicks' in item
        assert 'total_earnings' in item
        assert 'monthly_breakdown' in item

        # Check monthly breakdown format
        assert isinstance(item['monthly_breakdown'], list)
        for month_data in item['monthly_breakdown']:
            if month_data:  # If there's any data
                assert 'month' in month_data
                assert 'earnings' in month_data

                # Ensure month format is MM/YYYY
                if 'month' in month_data:
                    month_parts = month_data['month'].split('/')
                    assert len(month_parts) == 2, f"Month format should be MM/YYYY, got {month_data['month']}"

    # Test pagination
    response = client.get('/stats?page=1&per_page=1')
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) == 1