from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os
import base64
from datetime import datetime
import json
import numpy as np

# Face recognition disabled for deployment compatibility
FACE_RECOGNITION_AVAILABLE = False
print("Face recognition disabled for deployment. Using simplified mode.")

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Database setup
def init_db():
    conn = sqlite3.connect('voting.db')
    cursor = conn.cursor()
    
    # Create Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            face_encoding BLOB,
            has_voted BOOLEAN DEFAULT FALSE
        )
    ''')
    
    # Create Admins table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    
    # Create Candidates table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            photo_path TEXT
        )
    ''')
    
    # Create Votes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            voter_id INTEGER,
            candidate_id INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (voter_id) REFERENCES users (id),
            FOREIGN KEY (candidate_id) REFERENCES candidates (id)
        )
    ''')
    
    # Insert default admin if not exists
    cursor.execute('SELECT * FROM admins WHERE username = ?', ('admin',))
    if not cursor.fetchone():
        admin_password = generate_password_hash('admin123')
        cursor.execute('INSERT INTO admins (username, password_hash) VALUES (?, ?)', 
                      ('admin', admin_password))
    
    # Insert sample candidates if not exists
    cursor.execute('SELECT * FROM candidates')
    if not cursor.fetchall():
        candidates = [
            ('John Doe', 'static/candidates/john_doe.jpg'),
            ('Jane Smith', 'static/candidates/jane_smith.jpg'),
            ('Mike Johnson', 'static/candidates/mike_johnson.jpg')
        ]
        for name, photo in candidates:
            cursor.execute('INSERT INTO candidates (name, photo_path) VALUES (?, ?)', 
                          (name, photo))
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

def is_blurry(image_array):
    """Check if image is blurry using OpenCV"""
    return False  # Skip blur check for deployment

def get_db_connection():
    conn = sqlite3.connect('voting.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if username already exists
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            flash('Username already exists. Please choose another.', 'error')
            conn.close()
            return render_template('register.html')
        
        # Save user without face encoding (simplified for deployment)
        password_hash = generate_password_hash(password)
        cursor.execute('''
            INSERT INTO users (name, username, password_hash, face_encoding)
            VALUES (?, ?, ?, ?)
        ''', (name, username, password_hash, None))
        
        conn.commit()
        conn.close()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['name'] = user['name']
            conn.close()
            return redirect(url_for('facial_verification'))
        else:
            flash('Invalid username or password.', 'error')
            conn.close()
    
    return render_template('login.html')

@app.route('/facial-verification', methods=['GET', 'POST'])
def facial_verification():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Skip face verification for deployment (simplified mode)
    return redirect(url_for('vote'))

@app.route('/vote')
def vote():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if user has already voted
    cursor.execute('SELECT has_voted FROM users WHERE id = ?', (session['user_id'],))
    user = cursor.fetchone()
    
    if user['has_voted']:
        flash('You have already voted.', 'info')
        return redirect(url_for('results'))
    
    # Get candidates
    cursor.execute('SELECT * FROM candidates')
    candidates = cursor.fetchall()
    conn.close()
    
    return render_template('vote.html', candidates=candidates)

@app.route('/submit-vote', methods=['POST'])
def submit_vote():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    candidate_id = request.form.get('candidate_id')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if user has already voted
    cursor.execute('SELECT has_voted FROM users WHERE id = ?', (session['user_id'],))
    user = cursor.fetchone()
    
    if user['has_voted']:
        conn.close()
        return jsonify({'success': False, 'message': 'You have already voted'})
    
    # Record vote
    cursor.execute('INSERT INTO votes (voter_id, candidate_id) VALUES (?, ?)', 
                  (session['user_id'], candidate_id))
    
    # Mark user as voted
    cursor.execute('UPDATE users SET has_voted = TRUE WHERE id = ?', (session['user_id'],))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Vote submitted successfully!'})

@app.route('/results')
def results():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get vote counts
    cursor.execute('''
        SELECT c.name, COUNT(v.id) as vote_count
        FROM candidates c
        LEFT JOIN votes v ON c.id = v.candidate_id
        GROUP BY c.id, c.name
        ORDER BY vote_count DESC
    ''')
    results = cursor.fetchall()
    
    # Get total votes
    cursor.execute('SELECT COUNT(*) FROM votes')
    total_votes = cursor.fetchone()[0]
    
    conn.close()
    
    return render_template('results.html', results=results, total_votes=total_votes)

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM admins WHERE username = ?', (username,))
        admin = cursor.fetchone()
        
        if admin and check_password_hash(admin['password_hash'], password):
            session['admin_id'] = admin['id']
            session['admin_username'] = admin['username']
            conn.close()
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials.', 'error')
            conn.close()
    
    return render_template('admin_login.html')

@app.route('/admin')
def admin_dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get candidates with vote counts
    cursor.execute('''
        SELECT c.*, COUNT(v.id) as vote_count
        FROM candidates c
        LEFT JOIN votes v ON c.id = v.candidate_id
        GROUP BY c.id, c.name, c.photo_path
        ORDER BY vote_count DESC
    ''')
    candidates = cursor.fetchall()
    
    # Get total votes
    cursor.execute('SELECT COUNT(*) FROM votes')
    total_votes = cursor.fetchone()[0]
    
    # Get total users
    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]
    
    conn.close()
    
    return render_template('admin_dashboard.html', 
                         candidates=candidates, 
                         total_votes=total_votes,
                         total_users=total_users)

@app.route('/add-candidate', methods=['POST'])
def add_candidate():
    if 'admin_id' not in session:
        return jsonify({'success': False, 'message': 'Not authorized'})
    
    name = request.form['name']
    photo = request.files['photo']
    
    if photo:
        filename = secure_filename(photo.filename)
        photo_path = f'static/candidates/{filename}'
        
        # Create directory if it doesn't exist
        os.makedirs('static/candidates', exist_ok=True)
        
        photo.save(photo_path)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO candidates (name, photo_path) VALUES (?, ?)', 
                      (name, photo_path))
        conn.commit()
        conn.close()
        
        flash('Candidate added successfully!', 'success')
    else:
        flash('Please select a photo.', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/delete-candidate/<int:candidate_id>')
def delete_candidate(candidate_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM candidates WHERE id = ?', (candidate_id,))
    conn.commit()
    conn.close()
    
    flash('Candidate deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/clear_votes', methods=['POST'])
def clear_votes():
    if 'admin_id' not in session:
        return jsonify({'success': False, 'message': 'Not authorized'})
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Clear all votes
    cursor.execute('DELETE FROM votes')
    
    # Reset all users' has_voted status
    cursor.execute('UPDATE users SET has_voted = FALSE')
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'All votes cleared successfully!'})

@app.route('/vote-success')
def vote_success():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('vote_success.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port) 
