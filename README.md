# Fiverr URL Shortener Service

A backend service for Fiverr sellers to create shareable short links. When users click on these links, sellers are rewarded with Fiverr credits (if the clicks pass fraud validation).

## Features

- **Short Link Generation**: Create unique short links for any Fiverr page
- **Click Tracking**: Track clicks on short links with fraud validation
- **Reward System**: Award 0.05 USD in Fiverr credits for valid clicks
- **Analytics**: View global and per-link statistics, including monthly breakdowns

## Setup

### Prerequisites

- Python 3.8+
- PostgreSQL 12+

### Environment Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd fiverr-backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   ```bash
   # Windows
   venv\Scripts\activate

   # macOS/Linux
   source venv/bin/activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Environment Variables:
   Set the following environment variables:

   ```bash
   # Windows
   set DATABASE_URL=postgresql://postgres:postgres@localhost:5432/fiverr_links
   set FLASK_ENV=development

   # macOS/Linux
   export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/fiverr_links
   export FLASK_ENV=development
   ```

   Or create a `.env` file in the project root:

   ```
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/fiverr_links
   FLASK_ENV=development
   ```

6. Database setup:
   - Make sure PostgreSQL is running
   - Create the database if it doesn't exist:
     ```bash
     psql -U postgres -c "CREATE DATABASE fiverr_links;"
     ```
   - Run the table creation script:
     ```bash
     python run_tables.py
     ```
   - Verify tables were created:
     ```bash
     python check_tables.py
     ```

### Running the Application

```
python app.py
```

The server will start on `http://localhost:5000`.

### Installation Checklist

Use this checklist to verify your setup:

- [ ] PostgreSQL is installed and running
- [ ] Python 3.8+ is installed
- [ ] Virtual environment is created and activated
- [ ] Dependencies are installed from requirements.txt
- [ ] Database is created in PostgreSQL
- [ ] Environment variables are set correctly
- [ ] Database tables are created successfully
- [ ] Tests are passing

### Troubleshooting Common Issues

#### Database Connection Issues

If you encounter database connection errors:

1. Verify PostgreSQL is running:
   ```bash
   # Windows
   sc query postgresql

   # macOS
   brew services list | grep postgres

   # Linux
   systemctl status postgresql
   ```

2. Check your connection parameters:
   ```bash
   python db_info.py
   ```

3. Make sure you can connect to the database manually:
   ```bash
   psql -U postgres -d fiverr_links
   ```

#### Missing Tables

If the application can't find the database tables:

1. Verify the tables exist:
   ```bash
   python check_tables.py
   ```

2. If tables are missing, create them:
   ```bash
   python run_tables.py
   ```

3. Check for any errors during table creation:
   ```bash
   python check_db.py
   ```

## Testing

### Running Automated Tests

```bash
pytest test_app.py -v
```

The test suite covers:
- URL shortening functionality
- Duplicate link detection
- Redirection and click tracking
- Fraud validation (using mocked validation function)
- Monthly and lifetime statistics
- Pagination
- Error handling for invalid inputs

### Manual Testing with Curl

1. Create a short link:
   ```bash
   curl -X POST http://localhost:5000/links \
     -H "Content-Type: application/json" \
     -d '{"target_url": "https://www.fiverr.com/start_selling", "seller_id": "test_seller"}'
   ```

2. Visit the short link in your browser:
   ```
   http://localhost:5000/<short_code>
   ```

3. View statistics:
   ```bash
   curl http://localhost:5000/stats
   ```

### Manual Testing with Postman

1. Set up a new request collection for Fiverr URL Shortener API
2. Create requests for each endpoint:
   - POST /links
   - GET /:short_code (use a short code from a previous response)
   - GET /stats

3. For POST /links, set the body to raw JSON:
   ```json
   {
     "target_url": "https://www.fiverr.com/categories/programming-tech",
     "seller_id": "seller123"
   }
   ```

4. Execute the requests in sequence to test the entire workflow

## API Documentation

### POST /links

Create a new short link.

**Request Body:**
```json
{
  "target_url": "https://fiverr.com/some_page",
  "seller_id": "seller123"
}
```

**Response:**
```json
{
  "original_url": "https://fiverr.com/some_page",
  "short_code": "abc123",
  "short_url": "http://localhost:5000/abc123",
  "created_at": "2026-02-17T10:15:30.123456+00:00"
}
```

### GET /:short_code

Redirect to the original URL and record the click.

**Process:**
1. Finds the original URL by short code
2. Records the click event
3. Performs fraud validation (500ms delay, 50% probability)
4. Awards credit for valid clicks (0.05 USD)
5. Updates monthly statistics
6. Redirects to the original URL

**Response:**
- 302 Redirect to the original URL

### GET /stats

Get statistics for all links.

**Query Parameters:**
- `page` (default: 1): Page number for pagination
- `per_page` (default: 10, max: 100): Number of items per page

**Response:**
```json
[
  {
    "url": "fiverr.com/signup",
    "total_clicks": 16,
    "total_earnings": 1.05,
    "monthly_breakdown": [
      { "month": "12/2025", "earnings": 1.00 },
      { "month": "01/2026", "earnings": 0.05 }
    ]
  },
  {
    "url": "fiverr.com/homepage",
    "total_clicks": 20,
    "total_earnings": 1.05,
    "monthly_breakdown": [
      { "month": "11/2025", "earnings": 1.00 },
      { "month": "02/2026", "earnings": 0.05 }
    ]
  }
]
```

## Architecture

### Project Structure

```
fiverr-backend/
│
├── app.py               # Main Flask application with API endpoints
├── models.py            # SQLAlchemy models defining the database schema
├── database.py          # Database connection and configuration
├── run_tables.py        # Script to create database tables
├── check_db.py          # Utility to check database status and display sample data
├── db_info.py           # Script to display database information
├── check_tables.py      # Script to verify table creation
├── test_app.py          # Automated tests for the application
└── README.md            # Project documentation
```

### Component Interaction

1. **API Layer (`app.py`)**:
   - Handles HTTP requests and responses
   - Routes requests to appropriate handlers
   - Implements business logic for link shortening, click tracking, and statistics

2. **Data Access Layer (`models.py`)**:
   - Defines SQLAlchemy ORM models that map to database tables
   - Encapsulates data structure and relationships
   - Includes data validation rules

3. **Database Configuration (`database.py`)**:
   - Sets up the database connection
   - Configures SQLAlchemy engine and session management

4. **Utility Scripts**:
   - Tools for database management and debugging
   - Scripts for checking database state and schema

### Database Schema

#### `links` Table
- `id`: Primary key
- `original_url`: The target URL
- `short_code`: Unique code for the short URL
- `seller_id`: ID of the Fiverr seller
- `created_at`: Timestamp of creation

#### `clicks` Table
- `id`: Primary key
- `link_id`: Foreign key referencing the links table
- `clicked_at`: Timestamp of click
- `is_valid`: Boolean indicating if the click passed validation
- `rewarded`: Boolean indicating if a reward was issued

#### `monthly_stats` Table
- `id`: Primary key
- `link_id`: Foreign key referencing the links table
- `year_month`: String in format 'YYYY-MM'
- `clicks`: Total clicks in this month
- `valid_clicks`: Valid clicks in this month
- `rewards_earned`: Total rewards earned in this month

### Core Components and Technologies

- **Flask**: Web framework for handling HTTP requests
- **SQLAlchemy**: ORM for database interactions
- **PostgreSQL**: Relational database for data storage
- **pytest**: Testing framework

## Custom Improvements and Optimizations

### Performance Enhancements

1. **Database Indexing**
   - Added indexes on frequently queried columns like `short_code` in the links table
   - Optimized query patterns for statistics aggregation

2. **Fraud Validation**
   - Implemented with configurable parameters for delay and probability
   - In a production environment, this could be replaced with a real fraud detection system

### Scalability Considerations

For a production environment, consider these enhancements:

1. **Asynchronous Processing**
   - Move fraud validation to an asynchronous task queue (e.g., Celery)
   - Process rewards in the background to improve response times

2. **Caching Layer**
   - Implement Redis caching for frequently accessed links
   - Cache statistics data to reduce database load

3. **Rate Limiting**
   - Add rate limiting to prevent abuse of the API
   - Implement per-seller quotas for link creation

4. **Monitoring and Logging**
   - Add structured logging for better debugging
   - Implement monitoring for API performance and error rates

### Future Enhancements

1. **Analytics Dashboard**
   - Create a frontend dashboard for sellers to view their link performance
   - Add charts and visualizations for click data

2. **Custom Short Codes**
   - Allow sellers to specify custom short codes for brand recognition
   - Implement vanity URLs for premium sellers

3. **Advanced Fraud Detection**
   - Implement IP-based fraud detection
   - Add user agent and referrer analysis
   - Incorporate machine learning models for click validation

4. **Webhook Notifications**
   - Send notifications to sellers when their links receive valid clicks
   - Integrate with Fiverr's notification system

## Conclusion

This Fiverr URL Shortener Service provides a robust solution for Fiverr sellers to create and share short links while earning rewards for valid clicks. The implementation follows best practices for API design, database management, and testing, making it easy to extend and maintain for future requirements.