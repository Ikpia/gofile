'''
from flask import Flask, request, jsonify, session
from flask_mysqldb import MySQL
from werkzeug.security import check_password_hash, generate_password_hash
from flask_cors import CORS
import MySQLdb.cursors
import re
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'  # or your MySQL host
app.config['MYSQL_USER'] = 'emmy'
app.config['MYSQL_PASSWORD'] = 'emmy'
app.config['MYSQL_DB'] = 'userDB'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Secret key for sessions
app.secret_key = 'your_secret_key_here'  # Change this to a random secret key

# Initialize MySQL
mysql = MySQL(app)

# Create users table if it doesn't exist
def init_db():
    """Initialize database with users table"""
    cursor = mysql.connection.cursor()
    cursor.execute('''
        #CREATE TABLE IF NOT EXISTS users (
            #id INT AUTO_INCREMENT PRIMARY KEY,
            #email VARCHAR(255) UNIQUE NOT NULL,
            #password VARCHAR(255) NOT NULL,
            #created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            #last_login TIMESTAMP NULL,
            #is_active BOOLEAN DEFAULT TRUE
        #)
''')
    mysql.connection.commit()
    cursor.close()

@app.route('/api/signup', methods=['POST'])
def signin():
    """Handle user sign in"""
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # Validate input
        if not email or not password:
            return jsonify({'message': 'Email and password are required'}), 400
        
        # Validate email format
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            return jsonify({'message': 'Invalid email format'}), 400
        
        # Query database for user
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE email = %s AND is_active = TRUE', (email,))
        user = cursor.fetchone()
        
        if user and check_password_hash(user['password'], password):
            # Update last login
            cursor.execute('UPDATE users SET last_login = %s WHERE id = %s', 
                          (datetime.now(), user['id']))
            mysql.connection.commit()
            
            # Store user info in session
            session['user_id'] = user['id']
            session['email'] = user['email']
            session['logged_in'] = True
            
            cursor.close()
            
            return jsonify({
                'message': 'Login successful',
                'user': {
                    'id': user['id'],
                    'email': user['email'],
                    'last_login': user['last_login']
                },
                'redirect': '/dashboard'
            }), 200
        else:
            cursor.close()
            return jsonify({'message': 'Invalid email or password'}), 401
            
    except Exception as e:
        print(f"Error in signin: {str(e)}")
        return jsonify({'message': 'An error occurred during sign in'}), 500

@app.route('/api/signin', methods=['POST'])
def register():
    """Handle user signin"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # Validate input
        if not email or not password:
            return jsonify({'message': 'Email and password are required'}), 400
        
        # Validate email format
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            return jsonify({'message': 'Invalid email format'}), 400
        
        cursor = mysql.connection.cursor()
        
        # Check if user already exists
        cursor.execute('SELECT id FROM users WHERE email = %s', (email,))
        if cursor.fetchone():
            cursor.close()
            return jsonify({'message': 'Email already registered'}), 409
        
        # Hash password and insert user
        #hashed_password = generate_password_hash(password)
        cursor.execute('INSERT INTO users (email, password) VALUES (%s, %s)', 
                      (email, password))
        mysql.connection.commit()
        
        # Get the new user ID
        user_id = cursor.lastrowid
        cursor.close()
        
        return jsonify({
            'message': 'Registration successful',
            'user': {
                'id': user_id,
                'email': email
            }
        }), 201
        
    except Exception as e:
        print(f"Error in register: {str(e)}")
        return jsonify({'message': 'An error occurred during registration'}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    """Handle user logout"""
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/api/user', methods=['GET'])
def get_user():
    """Get current user info"""
    if 'logged_in' in session and session['logged_in']:
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT id, email, created_at, last_login FROM users WHERE id = %s', 
                      (session['user_id'],))
        user = cursor.fetchone()
        cursor.close()
        
        if user:
            return jsonify({
                'user': {
                    'id': user['id'],
                    'email': user['email'],
                    'created_at': user['created_at'],
                    'last_login': user['last_login']
                }
            }), 200
    
    return jsonify({'message': 'Not authenticated'}), 401

@app.route('/api/check-auth', methods=['GET'])
def check_auth():
    """Check if user is authenticated"""
    if 'logged_in' in session and session['logged_in']:
        return jsonify({'authenticated': True, 'user_id': session['user_id']}), 200
    return jsonify({'authenticated': False}), 401

# Dashboard route (example protected route)
@app.route('/dashboard')
def dashboard():
    """Protected dashboard route"""
    if 'logged_in' not in session or not session['logged_in']:
        return jsonify({'message': 'Please log in to access this page'}), 401
    
    return f"Welcome to dashboard, {session['email']}!"

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'message': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'message': 'Internal server error'}), 500

if __name__ == '__main__':
    # Initialize database on startup
    with app.app_context():
        init_db()
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)
'''


from flask import Flask, request, jsonify, session
import pymysql
from werkzeug.security import check_password_hash, generate_password_hash
from flask_cors import CORS
import re
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# MySQL Configuration using PyMySQL
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', '127.0.0.1')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', '')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'flask_auth')
app.config['MYSQL_PORT'] = int(os.getenv('MYSQL_PORT', 3300))

# Secret key for sessions
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this')

def get_db_connection():
    """Create database connection"""
    try:
        connection = pymysql.connect(
            host=app.config['MYSQL_HOST'],
            port=app.config['MYSQL_PORT'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB'],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False
        )
        return connection
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def create_database_if_not_exists():
    """Create database if it doesn't exist"""
    try:
        connection = pymysql.connect(
            host=app.config['MYSQL_HOST'],
            port=app.config['MYSQL_PORT'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            charset='utf8mb4'
        )
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {app.config['MYSQL_DB']}")
        connection.commit()
        connection.close()
        print(f"✅ Database '{app.config['MYSQL_DB']}' created/verified successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

def init_db():
    """Initialize database with users table"""
    try:
        # First create database if it doesn't exist
        if not create_database_if_not_exists():
            return False
            
        # Then create table
        connection = get_db_connection()
        if not connection:
            print("❌ Could not connect to database")
            return False
            
        with connection.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP NULL,
                    is_active BOOLEAN DEFAULT TRUE
                )
            ''')
        connection.commit()
        connection.close()
        print("✅ Users table created/verified successfully!")
        return True
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False

@app.route('/api/register', methods=['POST'])
def signin():
    """Handle user sign in"""
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # Validate input
        if not email or not password:
            return jsonify({'message': 'Email and password are required'}), 400
        
        # Validate email format
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            return jsonify({'message': 'Invalid email format'}), 400
        
        # Query database for user
        connection = get_db_connection()
        if not connection:
            return jsonify({'message': 'Database connection error'}), 500
            
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM users WHERE email = %s AND is_active = TRUE', (email,))
            user = cursor.fetchone()
            
            if user and check_password_hash(user['password'], password):
                # Update last login
                cursor.execute('UPDATE users SET last_login = %s WHERE id = %s', 
                              (datetime.now(), user['id']))
                connection.commit()
                
                # Store user info in session
                session['user_id'] = user['id']
                session['email'] = user['email']
                session['logged_in'] = True
                
                connection.close()
                
                return jsonify({
                    'message': 'Login successful',
                    'user': {
                        'id': user['id'],
                        'email': user['email'],
                        'last_login': str(user['last_login']) if user['last_login'] else None
                    },
                    'redirect': '/dashboard'
                }), 200
            else:
                connection.close()
                return jsonify({'message': 'Invalid email or password'}), 401
                
    except Exception as e:
        print(f"Error in signin: {str(e)}")
        return jsonify({'message': 'An error occurred during sign in'}), 500

@app.route('/api/signin', methods=['POST'])
def register():
    """Handle user registration"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # Validate input
        if not email or not password:
            return jsonify({'message': 'Email and password are required'}), 400
        
        # Validate email format
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            return jsonify({'message': 'Invalid email format'}), 400
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'message': 'Database connection error'}), 500
            
        with connection.cursor() as cursor:
            # Check if user already exists
            
            # Hash password and insert user
            cursor.execute('INSERT INTO users (email, password) VALUES (%s, %s)', 
                          (email, password))
            connection.commit()
            
            # Get the new user ID
            user_id = cursor.lastrowid
            connection.close()
            
            return jsonify({
                'message': 'Registration successful',
                'user': {
                    'id': user_id,
                    'email': email
                }
            }), 201
            
    except Exception as e:
        print(f"Error in register: {str(e)}")
        return jsonify({'message': 'An error occurred during registration'}), 500

@app.route('/api/test-db', methods=['GET'])
def test_db():
    """Test database connection"""
    connection = get_db_connection()
    if connection:
        connection.close()
        return jsonify({'message': 'Database connection successful!'}), 200
    else:
        return jsonify({'message': 'Database connection failed!'}), 500

@app.route('/dashboard')
def dashboard():
    """Protected dashboard route"""
    if 'logged_in' not in session or not session['logged_in']:
        return jsonify({'message': 'Please log in to access this page'}), 401
    
    return f"Welcome to dashboard, {session['email']}!"

@app.route('/')
def home():
    """Home route"""
    return "Flask Authentication Server is running!"

if __name__ == '__main__':
    print("🚀 Starting Flask Authentication Server...")
    print(f"📊 Database Config: {app.config['MYSQL_USER']}@{app.config['MYSQL_HOST']}:{app.config['MYSQL_PORT']}")
    
    # Test database connection first
    print("🔍 Testing database connection...")
    if init_db():
        print("✅ Database setup complete!")
        print("🌐 Server starting on http://127.0.0.1:5000")
        app.run(debug=True, host='127.0.0.1', port=5000)
    else:
        print("❌ Failed to connect to database. Please check your MySQL server and configuration.")
        print(f"\n🔧 Current config:")
        print(f"   Host: {app.config['MYSQL_HOST']}")
        print(f"   Port: {app.config['MYSQL_PORT']}")
        print(f"   User: {app.config['MYSQL_USER']}")
        print(f"   Database: {app.config['MYSQL_DB']}")
        print("\n🔧 Troubleshooting steps:")
        print("1. Make sure MySQL server is running: net start mysql80")
        print("2. Check your .env file for correct credentials")
        print("3. Try using root user with correct password")
        print("4. Verify MySQL is running on the correct port")