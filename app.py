from flask import Flask, jsonify, request, redirect, url_for
from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker
from database import engine
from models import Link, Click, MonthlyStat
import string
import random
import time
from datetime import datetime, timezone

app = Flask(__name__)

# Create a session factory
Session = sessionmaker(bind=engine)

# Helper function to generate a random short code
def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

# Simulate fraud validation (takes 500ms, returns True/False with 50% probability)
def validate_click():
    time.sleep(0.5)  # 500ms delay
    return random.choice([True, False])  # 50% probability

# -----------------------------
# POST /links - Create a new short link
# -----------------------------
@app.post("/links")
def create_short_link():
    # Get JSON data from request
    data = request.json
    if not data or 'target_url' not in data:
        return jsonify({"error": "Missing target_url parameter"}), 400

    if 'seller_id' not in data:
        # In a real app, this might come from authentication
        return jsonify({"error": "Missing seller_id parameter"}), 400

    target_url = data['target_url']
    seller_id = data['seller_id']

    # Create a session
    session = Session()
    try:
        # Check if this URL already exists for this seller
        existing_link = session.query(Link).filter_by(
            original_url=target_url,
            seller_id=seller_id
        ).first()

        if existing_link:
            # Return the existing short link
            return jsonify({
                "original_url": existing_link.original_url,
                "short_code": existing_link.short_code,
                "short_url": request.host_url + existing_link.short_code,
                "created_at": existing_link.created_at.isoformat(),
                "message": "Existing link returned"
            })

        # Generate a unique short code
        while True:
            short_code = generate_short_code()
            if not session.query(Link).filter_by(short_code=short_code).first():
                break

        # Create a new link
        new_link = Link(
            original_url=target_url,
            short_code=short_code,
            seller_id=seller_id
        )

        session.add(new_link)
        session.commit()

        return jsonify({
            "original_url": new_link.original_url,
            "short_code": new_link.short_code,
            "short_url": request.host_url + new_link.short_code,
            "created_at": new_link.created_at.isoformat()
        }), 201

    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

# -----------------------------
# GET /:short_code - Redirect and track
# -----------------------------
@app.get("/<short_code>")
def redirect_short_link(short_code):
    # Create a session
    session = Session()
    try:
        # Find the link
        link = session.query(Link).filter_by(short_code=short_code).first()

        if not link:
            return jsonify({"error": "Link not found"}), 404

        # Record the click (before validation)
        current_time = datetime.now(timezone.utc)
        year_month = current_time.strftime('%Y-%m')

        # Create the click record
        click = Click(
            link_id=link.id,
            clicked_at=current_time
        )
        session.add(click)

        # Simulate fraud validation (async in a real app)
        is_valid = validate_click()
        click.is_valid = is_valid

        # If valid, award the credit (0.05 USD) and mark as rewarded
        if is_valid:
            click.rewarded = True

            # Update or create monthly stats
            monthly_stat = session.query(MonthlyStat).filter_by(
                link_id=link.id,
                year_month=year_month
            ).first()

            if not monthly_stat:
                monthly_stat = MonthlyStat(
                    link_id=link.id,
                    year_month=year_month,
                    clicks=1,
                    valid_clicks=1,
                    rewards_earned=0.05  # $0.05 USD
                )
                session.add(monthly_stat)
            else:
                monthly_stat.clicks += 1
                monthly_stat.valid_clicks += 1
                monthly_stat.rewards_earned += 0.05  # $0.05 USD
        else:
            # Still update click count even if not valid
            monthly_stat = session.query(MonthlyStat).filter_by(
                link_id=link.id,
                year_month=year_month
            ).first()

            if not monthly_stat:
                monthly_stat = MonthlyStat(
                    link_id=link.id,
                    year_month=year_month,
                    clicks=1,
                    valid_clicks=0,
                    rewards_earned=0.0
                )
                session.add(monthly_stat)
            else:
                monthly_stat.clicks += 1

        # Commit all the changes
        session.commit()

        # Redirect to the original URL
        return redirect(link.original_url)

    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

# -----------------------------
# GET /stats - Global analytics
# -----------------------------
@app.get("/stats")
def get_stats():
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Limit per_page to a reasonable value
    per_page = min(per_page, 100)

    # Calculate offset
    offset = (page - 1) * per_page

    # Create a session
    session = Session()
    try:
        # Get paginated links with their stats
        links = session.query(Link).order_by(Link.created_at.desc()).offset(offset).limit(per_page).all()

        links_data = []
        for link in links:
            # Get all monthly stats for this link
            monthly_stats = session.query(MonthlyStat).filter_by(link_id=link.id).all()

            # Calculate lifetime totals
            total_clicks = sum(stat.clicks for stat in monthly_stats)
            total_earnings = sum(stat.rewards_earned for stat in monthly_stats)

            # Format monthly stats according to the required format (MM/YYYY)
            monthly_breakdown = []
            for stat in monthly_stats:
                # Convert YYYY-MM to MM/YYYY
                year, month = stat.year_month.split('-')
                formatted_month = f"{month}/{year}"

                monthly_breakdown.append({
                    "month": formatted_month,
                    "earnings": stat.rewards_earned
                })

            links_data.append({
                "url": link.original_url,
                "total_clicks": total_clicks,
                "total_earnings": total_earnings,
                "monthly_breakdown": monthly_breakdown
            })

        # Return just the array as requested in the example
        return jsonify(links_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

# -----------------------------
# Root endpoint - API info
# -----------------------------
@app.get("/")
def index():
    return jsonify({
        "message": "Welcome to Fiverr URL Shortener API",
        "endpoints": {
            "POST /links": "Create a new short link",
            "GET /{short_code}": "Redirect to the original URL",
            "GET /stats": "Get link statistics with pagination",
            "GET /hello": "Health check endpoint"
        },
        "documentation": "See README.md for full documentation"
    })

# -----------------------------
# Sanity endpoint
# -----------------------------
@app.get("/hello")
def hello():
    with engine.begin() as conn:
        val = conn.execute(
            text("SELECT COUNT(*) FROM links")
        ).scalar_one_or_none() or 0

    return jsonify({
        "message": "Hello Fiverr",
        "db": "postgres",
        "links_count": val
    })

if __name__ == "__main__":
    app.run(port=5000, debug=True)