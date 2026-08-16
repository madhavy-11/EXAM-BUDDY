# app.py - Flask API Server with CORS Fix

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime

app = Flask(__name__)

# ===== FIX: Allow all origins and methods =====
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:8000", "http://127.0.0.1:8000", "http://localhost:5500", "http://127.0.0.1:5500", "*"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-User-ID"]
    }
})

# ============================================
# DATABASE FUNCTIONS
# ============================================

def get_db_connection():
    conn = sqlite3.connect('exams.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    
    # Create users table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create exams table with user_id foreign key
    conn.execute('''
        CREATE TABLE IF NOT EXISTS exams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            location TEXT,
            teacher TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

# ============================================
# AUTH ENDPOINTS
# ============================================

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        name = data.get('name', '')
        
        if not email or not password:
            return jsonify({'success': False, 'error': 'Email and password required!'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        existing = cursor.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        if existing:
            conn.close()
            return jsonify({'success': False, 'error': 'User already exists!'}), 400
        
        cursor.execute('''
            INSERT INTO users (email, password, name)
            VALUES (?, ?, ?)
        ''', (email, password, name))
        
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'User created successfully!',
            'user': {'id': user_id, 'email': email, 'name': name}
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'success': False, 'error': 'Email and password required!'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        user = cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password)).fetchone()
        conn.close()
        
        if not user:
            return jsonify({'success': False, 'error': 'Invalid credentials!'}), 401
        
        return jsonify({
            'success': True,
            'message': 'Login successful!',
            'user': {'id': user['id'], 'email': user['email'], 'name': user['name']}
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# HELPER FUNCTIONS
# ============================================

def get_user_id_from_request():
    user_id = request.headers.get('X-User-ID')
    if user_id:
        return int(user_id)
    return None

# ============================================
# EXAM API ENDPOINTS
# ============================================

@app.route('/api/exams', methods=['GET'])
def get_exams():
    try:
        user_id = get_user_id_from_request()
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated!'}), 401
        
        conn = get_db_connection()
        exams = conn.execute('''
            SELECT * FROM exams 
            WHERE user_id = ? 
            ORDER BY date ASC, time ASC
        ''', (user_id,)).fetchall()
        conn.close()
        
        result = []
        for exam in exams:
            result.append({
                'id': exam['id'],
                'subject': exam['subject'],
                'date': exam['date'],
                'time': exam['time'],
                'location': exam['location'] or 'Not specified',
                'teacher': exam['teacher'] or 'Not specified'
            })
        
        return jsonify({'success': True, 'exams': result, 'count': len(result)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/exams', methods=['POST'])
def add_exam():
    try:
        user_id = get_user_id_from_request()
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated!'}), 401
        
        data = request.json
        
        if not data.get('subject') or not data.get('date') or not data.get('time'):
            return jsonify({'success': False, 'error': 'Subject, date, and time are required!'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO exams (user_id, subject, date, time, location, teacher)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, data['subject'], data['date'], data['time'], 
              data.get('location'), data.get('teacher')))
        
        conn.commit()
        exam_id = cursor.lastrowid
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Exam added successfully!',
            'id': exam_id
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/exams/<int:exam_id>', methods=['PUT'])
def update_exam(exam_id):
    try:
        user_id = get_user_id_from_request()
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated!'}), 401
        
        data = request.json
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        exam = cursor.execute('SELECT * FROM exams WHERE id = ? AND user_id = ?', (exam_id, user_id)).fetchone()
        if not exam:
            conn.close()
            return jsonify({'success': False, 'error': 'Exam not found!'}), 404
        
        cursor.execute('''
            UPDATE exams 
            SET subject = ?, date = ?, time = ?, location = ?, teacher = ?
            WHERE id = ? AND user_id = ?
        ''', (data.get('subject'), data.get('date'), data.get('time'),
              data.get('location'), data.get('teacher'), exam_id, user_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Exam updated successfully!'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/exams/<int:exam_id>', methods=['DELETE'])
def delete_exam(exam_id):
    try:
        user_id = get_user_id_from_request()
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated!'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        exam = cursor.execute('SELECT * FROM exams WHERE id = ? AND user_id = ?', (exam_id, user_id)).fetchone()
        if not exam:
            conn.close()
            return jsonify({'success': False, 'error': 'Exam not found!'}), 404
        
        cursor.execute('DELETE FROM exams WHERE id = ? AND user_id = ?', (exam_id, user_id))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Exam deleted successfully!'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/exams/stats', methods=['GET'])
def get_stats():
    try:
        user_id = get_user_id_from_request()
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated!'}), 401
        
        today = datetime.now().strftime('%Y-%m-%d')
        conn = get_db_connection()
        
        total = conn.execute('SELECT COUNT(*) FROM exams WHERE user_id = ?', (user_id,)).fetchone()[0]
        upcoming = conn.execute('SELECT COUNT(*) FROM exams WHERE user_id = ? AND date >= ?', (user_id, today)).fetchone()[0]
        past = conn.execute('SELECT COUNT(*) FROM exams WHERE user_id = ? AND date < ?', (user_id, today)).fetchone()[0]
        today_count = conn.execute('SELECT COUNT(*) FROM exams WHERE user_id = ? AND date = ?', (user_id, today)).fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'stats': {
                'total': total,
                'upcoming': upcoming,
                'past': past,
                'today': today_count
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/')
def index():
    return jsonify({
        'message': 'Exam Buddy API Server',
        'endpoints': {
            'POST /api/auth/signup': 'Create account',
            'POST /api/auth/login': 'Login',
            'GET /api/exams': 'Get all exams',
            'POST /api/exams': 'Add exam',
            'PUT /api/exams/<id>': 'Update exam',
            'DELETE /api/exams/<id>': 'Delete exam',
            'GET /api/exams/stats': 'Get statistics'
        }
    })

# ============================================
# RUN THE SERVER
# ============================================

if __name__ == '__main__':
    print('=' * 60)
    print('   📚 EXAM BUDDY API SERVER')
    print('=' * 60)
    print('🔗 Server running at: http://localhost:5000')
    print('📋 API Endpoints:')
    print('   POST   /api/auth/signup     - Create account')
    print('   POST   /api/auth/login      - Login')
    print('   GET    /api/exams           - Get all exams')
    print('   POST   /api/exams           - Add exam')
    print('   PUT    /api/exams/<id>      - Update exam')
    print('   DELETE /api/exams/<id>      - Delete exam')
    print('   GET    /api/exams/stats     - Get statistics')
    print('=' * 60)
    print('✅ CORS allowed origins: http://localhost:8000, http://localhost:5500')
    print('=' * 60)
    
    app.run(debug=True, port=5000)