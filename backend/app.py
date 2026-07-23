# app.py - Flask API Server for Exam Buddy
# Connects frontend to backend database

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Allow frontend to connect

# ============================================
# DATABASE FUNCTIONS
# ============================================

def get_db_connection():
    """Connect to SQLite database"""
    conn = sqlite3.connect('exams.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database if not exists"""
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS exams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            location TEXT,
            teacher TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# ============================================
# API ENDPOINTS
# ============================================

# ===== GET ALL EXAMS =====
@app.route('/api/exams', methods=['GET'])
def get_exams():
    """Get all exams"""
    try:
        conn = get_db_connection()
        exams = conn.execute('SELECT * FROM exams ORDER BY date ASC, time ASC').fetchall()
        conn.close()
        
        # Convert to list of dicts
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

# ===== ADD EXAM =====
@app.route('/api/exams', methods=['POST'])
def add_exam():
    """Add a new exam"""
    try:
        data = request.json
        
        # Validate required fields
        if not data.get('subject') or not data.get('date') or not data.get('time'):
            return jsonify({'success': False, 'error': 'Subject, date, and time are required!'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO exams (subject, date, time, location, teacher)
            VALUES (?, ?, ?, ?, ?)
        ''', (data['subject'], data['date'], data['time'], 
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

# ===== UPDATE EXAM =====
@app.route('/api/exams/<int:exam_id>', methods=['PUT'])
def update_exam(exam_id):
    """Update an existing exam"""
    try:
        data = request.json
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE exams 
            SET subject = ?, date = ?, time = ?, location = ?, teacher = ?
            WHERE id = ?
        ''', (data.get('subject'), data.get('date'), data.get('time'),
              data.get('location'), data.get('teacher'), exam_id))
        
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        
        if affected == 0:
            return jsonify({'success': False, 'error': 'Exam not found!'}), 404
        
        return jsonify({'success': True, 'message': 'Exam updated successfully!'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ===== DELETE EXAM =====
@app.route('/api/exams/<int:exam_id>', methods=['DELETE'])
def delete_exam(exam_id):
    """Delete an exam"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM exams WHERE id = ?', (exam_id,))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        
        if affected == 0:
            return jsonify({'success': False, 'error': 'Exam not found!'}), 404
        
        return jsonify({'success': True, 'message': 'Exam deleted successfully!'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ===== GET UPCOMING EXAMS =====
@app.route('/api/exams/upcoming', methods=['GET'])
def get_upcoming_exams():
    """Get upcoming exams"""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        conn = get_db_connection()
        exams = conn.execute('''
            SELECT * FROM exams 
            WHERE date >= ? 
            ORDER BY date ASC, time ASC
        ''', (today,)).fetchall()
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

# ===== GET TODAY'S EXAMS =====
@app.route('/api/exams/today', methods=['GET'])
def get_today_exams():
    """Get today's exams"""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        conn = get_db_connection()
        exams = conn.execute('''
            SELECT * FROM exams 
            WHERE date = ? 
            ORDER BY time ASC
        ''', (today,)).fetchall()
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

# ===== GET STATISTICS =====
@app.route('/api/exams/stats', methods=['GET'])
def get_stats():
    """Get exam statistics"""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        conn = get_db_connection()
        
        total = conn.execute('SELECT COUNT(*) FROM exams').fetchone()[0]
        upcoming = conn.execute('SELECT COUNT(*) FROM exams WHERE date >= ?', (today,)).fetchone()[0]
        past = conn.execute('SELECT COUNT(*) FROM exams WHERE date < ?', (today,)).fetchone()[0]
        today_count = conn.execute('SELECT COUNT(*) FROM exams WHERE date = ?', (today,)).fetchone()[0]
        
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

# ============================================
# RUN THE SERVER
# ============================================

if __name__ == '__main__':
    print('=' * 60)
    print('   📚 EXAM BUDDY API SERVER')
    print('=' * 60)
    print('🔗 Server running at: http://localhost:5000')
    print('📋 API Endpoints:')
    print('   GET    /api/exams           - Get all exams')
    print('   POST   /api/exams           - Add exam')
    print('   PUT    /api/exams/<id>      - Update exam')
    print('   DELETE /api/exams/<id>      - Delete exam')
    print('   GET    /api/exams/upcoming  - Get upcoming exams')
    print('   GET    /api/exams/today     - Get today\'s exams')
    print('   GET    /api/exams/stats     - Get statistics')
    print('=' * 60)
    
    app.run(debug=True, port=5000)