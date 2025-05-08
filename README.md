Flask REST API for Pins with MySQL
A Flask REST API for managing pins with CRUD operations, API token authentication, MySQL storage, and database migrations using Flask-Migrate. Database queries are handled in the model layer.
Setup

Install MySQL:Ensure MySQL is installed and running. Create a database and user:
CREATE DATABASE flask_api;
CREATE USER 'flask_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON flask_api.* TO 'flask_user'@'localhost';
FLUSH PRIVILEGES;


Create and activate a virtual environment:
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Install dependencies:
pip install -r requirements.txt


Set environment variables (optional):
export SECRET_KEY=your-secure-key
export API_TOKEN=your-secure-token
export DATABASE_URL=mysql+pymysql://flask_user:your_secure_password@localhost/flask_api
export FLASK_ENV=development


Initialize database migrations:
flask db init
flask db migrate -m "Initial migration with pins table"
flask db upgrade


Run the application:
python run.py



API Endpoints

GET /api/v1/pins: List all pins (supports author, order_by, order_dir query params)
GET /api/v1/pins/<id>: Get a pin by ID
POST /api/v1/pins: Create a new pin
PUT /api/v1/pins/<id>: Update a pin
DELETE /api/v1/pins/<id>: Delete a pin

All endpoints require the header X-API-Key: secret-token-123.
List Endpoint Query Parameters

author: Filter pins by author (e.g., ?author=alice)
order_by: Order by field (title, date_created, author) (e.g., ?order_by=title)
order_dir: Order direction (asc, desc) (e.g., ?order_dir=asc)

Database Migrations

Generate a new migration:
flask db migrate -m "Description of changes"


Apply migrations:
flask db upgrade


Revert migrations (if needed):
flask db downgrade



Example Requests

Get all pins:
curl -H "X-API-Key: secret-token-123" http://localhost:5000/api/v1/pins


Create a pin:
curl -H "X-API-Key: secret-token-123" -H "Content-Type: application/json" \
     -X POST -d '{"title":"New Pin","body":"Content","image_link":"https://example.com/new.jpg","author":"charlie"}' \
     http://localhost:5000/api/v1/pins



Testing
Run tests with:
python -m unittest discover tests

Environment Variables

SECRET_KEY: Flask secret key
API_TOKEN: API token for authentication
DATABASE_URL: MySQL connection string
FLASK_ENV: Set to development for debug mode

