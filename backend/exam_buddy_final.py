# exam_buddy_final.py - Complete Professional Version with Email Reminders
# All features working including SQLite database and email notifications

import sqlite3
import os
import json
import sys
import io
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ============================================
# COLOR CODES
# ============================================
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.CYAN}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}   {text}{Colors.END}")
    print(f"{Colors.CYAN}{'=' * 60}{Colors.END}")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

# ============================================
# EMAIL REMINDER CLASS
# ============================================
class EmailReminder:
    """Email reminder system for Exam Buddy"""
    
    def __init__(self, email=None, password=None):
        """Initialize email reminder system"""
        self.email = email
        self.password = password
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.config_file = "email_config.json"
        
        # Try to load saved config if not provided
        if not email or not password:
            self.load_config()
    
    def load_config(self):
        """Load email configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                self.email = config.get('email')
                self.password = config.get('password')
                print_success("Email configuration loaded!")
                return True
            except:
                print_error("Failed to load email config")
                return False
        return False
    
    def save_config(self):
        """Save email configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump({'email': self.email, 'password': self.password}, f, indent=2)
            print_success("Email configuration saved!")
            
            # Add to .gitignore if not already there
            if os.path.exists('.gitignore'):
                with open('.gitignore', 'r+') as f:
                    content = f.read()
                    if 'email_config.json' not in content:
                        f.write('\nemail_config.json\n')
            return True
        except Exception as e:
            print_error(f"Failed to save config: {e}")
            return False
    
    def is_configured(self):
        """Check if email is configured"""
        return self.email is not None and self.password is not None
    
    def send_reminder(self, to_email, exam_data):
        """Send a single exam reminder email"""
        if not self.is_configured():
            print_error("Email not configured! Please set up email first.")
            return False
        
        try:
            exam_date = datetime.strptime(exam_data['date'], "%Y-%m-%d")
            today = datetime.now()
            days_until = (exam_date - today).days
            
            subject = f"📚 Exam Reminder: {exam_data['subject']}"
            
            # Plain text version
            body = f"""
Hello Student! 👋

This is a reminder for your upcoming exam:

📖 Subject: {exam_data['subject']}
📅 Date: {exam_data['date']}
⏰ Time: {exam_data['time']}
📍 Location: {exam_data['location'] or 'Not specified'}
👨‍🏫 Teacher: {exam_data['teacher'] or 'Not specified'}

⏳ Days until exam: {days_until} day{'s' if days_until != 1 else ''}

📚 Study Tips:
- Start reviewing early
- Practice past papers
- Get enough sleep
- Stay hydrated

Good luck with your preparation! 💪

---
Exam Buddy - Your Study Assistant 📚
"""
            
            # HTML version
            html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f4f4f4; }}
        .container {{ background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 20px; border-radius: 10px 10px 0 0; margin: -30px -30px 20px -30px; text-align: center; }}
        .exam-details {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; }}
        .days-badge {{ display: inline-block; background-color: {'#ff6b6b' if days_until <= 3 else '#ffd93d' if days_until <= 7 else '#6bcb77'}; color: white; padding: 5px 15px; border-radius: 20px; font-weight: bold; }}
        .tips {{ background-color: #e3f2fd; padding: 15px; border-radius: 5px; margin: 10px 0; }}
        .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 20px; border-top: 1px solid #ddd; padding-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header"><h1>📚 Exam Reminder</h1><p>Don't forget your upcoming exam!</p></div>
        <h2>{exam_data['subject']}</h2>
        <div class="exam-details">
            <p><strong>📅 Date:</strong> {exam_data['date']}</p>
            <p><strong>⏰ Time:</strong> {exam_data['time']}</p>
            <p><strong>📍 Location:</strong> {exam_data['location'] or 'Not specified'}</p>
            <p><strong>👨‍🏫 Teacher:</strong> {exam_data['teacher'] or 'Not specified'}</p>
        </div>
        <div style="text-align: center; margin: 20px 0;">
            <span class="days-badge">{days_until} day{'s' if days_until != 1 else ''} to go</span>
        </div>
        <div class="tips">
            <h3>💡 Study Tips</h3>
            <ul><li>Start reviewing early</li><li>Practice past papers</li><li>Get enough sleep</li><li>Stay hydrated</li></ul>
        </div>
        <div class="footer"><p>Good luck with your preparation! 💪</p><p style="font-size: 10px;">Exam Buddy - Your Study Assistant</p></div>
    </div>
</body>
</html>
"""
            
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            part1 = MIMEText(body, 'plain')
            part2 = MIMEText(html_body, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email, self.password)
            server.send_message(msg)
            server.quit()
            
            print_success(f"Email sent to {to_email} for {exam_data['subject']}")
            return True
            
        except Exception as e:
            print_error(f"Error sending email: {e}")
            return False
    
    def send_daily_digest(self, to_email, exams):
        """Send a daily summary of all upcoming exams"""
        if not exams:
            print_info("No exams to include in digest")
            return False
        
        if not self.is_configured():
            print_error("Email not configured!")
            return False
        
        subject = f"📚 Daily Exam Digest - {datetime.now().strftime('%B %d, %Y')}"
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f4f4f4; }}
        .container {{ background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 20px; border-radius: 10px 10px 0 0; margin: -30px -30px 20px -30px; text-align: center; }}
        .exam-item {{ border-left: 4px solid #667eea; padding: 10px 15px; margin: 10px 0; background-color: #f8f9fa; border-radius: 5px; }}
        .urgent {{ border-left-color: #ff6b6b; background-color: #fff5f5; }}
        .soon {{ border-left-color: #ffd93d; background-color: #fffbf0; }}
        .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 20px; border-top: 1px solid #ddd; padding-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header"><h1>📚 Daily Exam Digest</h1><p>{datetime.now().strftime('%B %d, %Y')}</p></div>
        <h2>Your Upcoming Exams</h2>
        <p>You have {len(exams)} upcoming exam{'s' if len(exams) != 1 else ''}</p>
"""
        
        for exam in exams:
            exam_date = datetime.strptime(exam['date'], "%Y-%m-%d")
            days_until = (exam_date - datetime.now()).days
            urgency_class = "urgent" if days_until <= 3 else "soon" if days_until <= 7 else ""
            
            html_body += f"""
        <div class="exam-item {urgency_class}">
            <h3>{exam['subject']}</h3>
            <p>📅 {exam['date']} at {exam['time']}</p>
            <p>📍 {exam['location'] or 'Not specified'}</p>
            <p><strong>{days_until} day{'s' if days_until != 1 else ''} to go</strong></p>
        </div>
"""
        
        html_body += """
        <div class="footer">
            <p>Stay organized. Stay focused. You've got this! 💪</p>
            <p style="font-size: 10px;">Exam Buddy - Your Study Assistant</p>
        </div>
    </div>
</body>
</html>
"""
        
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            part = MIMEText(html_body, 'html')
            msg.attach(part)
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email, self.password)
            server.send_message(msg)
            server.quit()
            
            print_success(f"Daily digest sent to {to_email}")
            return True
            
        except Exception as e:
            print_error(f"Error sending digest: {e}")
            return False
    
    def check_and_send_reminders(self, to_email, exams, days_threshold=3):
        """Send reminders for exams within a certain number of days"""
        if not exams:
            print_info("No upcoming exams found")
            return False
        
        today = datetime.now().date()
        sent_count = 0
        
        for exam in exams:
            exam_date = datetime.strptime(exam['date'], "%Y-%m-%d").date()
            days_until = (exam_date - today).days
            
            if 0 <= days_until <= days_threshold:
                if self.send_reminder(to_email, exam):
                    sent_count += 1
        
        print_success(f"Sent {sent_count} reminder(s) for exams within {days_threshold} days")
        return sent_count > 0

# ============================================
# DATABASE CLASS
# ============================================
class ExamDatabase:
    """Professional SQLite database for Exam Buddy"""
    
    def __init__(self, db_name="exams.db"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            print_success(f"Connected to database: {self.db_name}")
        except sqlite3.Error as e:
            print_error(f"Database connection error: {e}")
    
    def create_tables(self):
        try:
            self.cursor.execute('''
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
            self.conn.commit()
            print_success("Tables created successfully")
        except sqlite3.Error as e:
            print_error(f"Table creation error: {e}")
    
    def get_today_str(self):
        return datetime.now().strftime("%Y-%m-%d")
    
    def add_exam(self, subject, date, time, location=None, teacher=None):
        try:
            if not subject or not date or not time:
                raise ValueError("Subject, date, and time are required!")
            
            self.cursor.execute('''
                INSERT INTO exams (subject, date, time, location, teacher)
                VALUES (?, ?, ?, ?, ?)
            ''', (subject, date, time, location, teacher))
            self.conn.commit()
            exam_id = self.cursor.lastrowid
            print_success(f"Exam added successfully (ID: {exam_id})")
            return exam_id
        except sqlite3.Error as e:
            print_error(f"Error adding exam: {e}")
            return None
    
    def get_all_exams(self):
        try:
            self.cursor.execute('SELECT * FROM exams ORDER BY date ASC, time ASC')
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print_error(f"Error fetching exams: {e}")
            return []
    
    def get_exam_by_id(self, exam_id):
        try:
            self.cursor.execute('SELECT * FROM exams WHERE id = ?', (exam_id,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print_error(f"Error fetching exam: {e}")
            return None
    
    def get_upcoming_exams(self):
        try:
            today = self.get_today_str()
            self.cursor.execute('''
                SELECT * FROM exams 
                WHERE date >= date(?)
                ORDER BY date ASC, time ASC
            ''', (today,))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print_error(f"Error fetching upcoming exams: {e}")
            return []
    
    def get_past_exams(self):
        try:
            today = self.get_today_str()
            self.cursor.execute('''
                SELECT * FROM exams 
                WHERE date < date(?)
                ORDER BY date DESC, time DESC
            ''', (today,))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print_error(f"Error fetching past exams: {e}")
            return []
    
    def get_todays_exams(self):
        try:
            today = self.get_today_str()
            self.cursor.execute('''
                SELECT * FROM exams 
                WHERE date = date(?)
                ORDER BY time ASC
            ''', (today,))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print_error(f"Error fetching today's exams: {e}")
            return []
    
    def search_exams(self, keyword):
        try:
            self.cursor.execute('''
                SELECT * FROM exams 
                WHERE subject LIKE ? OR teacher LIKE ?
                ORDER BY date ASC
            ''', (f'%{keyword}%', f'%{keyword}%'))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print_error(f"Error searching exams: {e}")
            return []
    
    def get_upcoming_week_exams(self):
        try:
            today = self.get_today_str()
            next_week = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
            self.cursor.execute('''
                SELECT * FROM exams 
                WHERE date >= date(?) AND date <= date(?)
                ORDER BY date ASC, time ASC
            ''', (today, next_week))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print_error(f"Error fetching week exams: {e}")
            return []
    
    def update_exam(self, exam_id, subject=None, date=None, time=None, 
                    location=None, teacher=None):
        try:
            current = self.get_exam_by_id(exam_id)
            if not current:
                print_error(f"Exam ID {exam_id} not found")
                return False
            
            subject = subject if subject else current['subject']
            date = date if date else current['date']
            time = time if time else current['time']
            location = location if location else current['location']
            teacher = teacher if teacher else current['teacher']
            
            self.cursor.execute('''
                UPDATE exams 
                SET subject = ?, date = ?, time = ?, 
                    location = ?, teacher = ?
                WHERE id = ?
            ''', (subject, date, time, location, teacher, exam_id))
            self.conn.commit()
            print_success(f"Exam ID {exam_id} updated successfully")
            return True
        except sqlite3.Error as e:
            print_error(f"Error updating exam: {e}")
            return False
    
    def delete_exam(self, exam_id):
        try:
            if not self.get_exam_by_id(exam_id):
                print_error(f"Exam ID {exam_id} not found")
                return False
            
            self.cursor.execute('DELETE FROM exams WHERE id = ?', (exam_id,))
            self.conn.commit()
            print_success(f"Exam ID {exam_id} deleted successfully")
            return True
        except sqlite3.Error as e:
            print_error(f"Error deleting exam: {e}")
            return False
    
    def delete_all_exams(self):
        try:
            count = self.cursor.execute('SELECT COUNT(*) FROM exams').fetchone()[0]
            if count == 0:
                print_warning("No exams to delete!")
                return False
            
            confirm = input(f"\nDelete ALL {count} exams? (yes/no): ").lower()
            if confirm in ['yes', 'y']:
                self.cursor.execute('DELETE FROM exams')
                self.conn.commit()
                print_success("All exams deleted successfully")
                return True
            else:
                print_info("Deletion cancelled")
                return False
        except sqlite3.Error as e:
            print_error(f"Error deleting all exams: {e}")
            return False
    
    def get_statistics(self):
        try:
            stats = {}
            self.cursor.execute('SELECT COUNT(*) FROM exams')
            stats['total'] = self.cursor.fetchone()[0]
            
            today = self.get_today_str()
            self.cursor.execute('SELECT COUNT(*) FROM exams WHERE date >= date(?)', (today,))
            stats['upcoming'] = self.cursor.fetchone()[0]
            
            self.cursor.execute('SELECT COUNT(*) FROM exams WHERE date < date(?)', (today,))
            stats['past'] = self.cursor.fetchone()[0]
            
            self.cursor.execute('SELECT COUNT(DISTINCT subject) FROM exams')
            stats['unique_subjects'] = self.cursor.fetchone()[0]
            
            return stats
        except sqlite3.Error as e:
            print_error(f"Error getting statistics: {e}")
            return {}
    
    def export_to_json(self):
        try:
            exams = self.get_all_exams()
            if not exams:
                print_warning("No exams to export!")
                return False
            
            exam_list = []
            for exam in exams:
                exam_list.append({
                    'id': exam['id'],
                    'subject': exam['subject'],
                    'date': exam['date'],
                    'time': exam['time'],
                    'location': exam['location'],
                    'teacher': exam['teacher']
                })
            
            filename = f"exam_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(exam_list, f, indent=2, ensure_ascii=False)
            
            print_success(f"Exported {len(exam_list)} exams to {filename}")
            return True
        except Exception as e:
            print_error(f"Export error: {e}")
            return False
    
    def migrate_from_json(self, json_file="exams.json"):
        if not os.path.exists(json_file):
            print_info(f"No JSON file found: {json_file}")
            return False
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                old_exams = json.load(f)
            
            if not old_exams:
                print_warning("JSON file is empty")
                return False
            
            count = 0
            for exam in old_exams:
                self.add_exam(
                    subject=exam.get('subject', 'Unknown'),
                    date=exam.get('date', datetime.now().strftime("%Y-%m-%d")),
                    time=exam.get('time', '12:00'),
                    location=exam.get('location', ''),
                    teacher=exam.get('teacher', '')
                )
                count += 1
            
            print_success(f"Migrated {count} exams from JSON to SQLite!")
            backup_name = f"{json_file}.backup"
            os.rename(json_file, backup_name)
            print_info(f"Old JSON backed up as {backup_name}")
            return True
        except Exception as e:
            print_error(f"Migration error: {e}")
            return False
    
    def close(self):
        if self.conn:
            self.conn.close()
            print_info("Database connection closed")

# ============================================
# DISPLAY FUNCTIONS
# ============================================
def get_status(exam):
    today = datetime.now().strftime("%Y-%m-%d")
    if exam['date'] < today:
        return "✅ Past"
    elif exam['date'] == today:
        return "🎯 Today!"
    else:
        days = (datetime.strptime(exam['date'], "%Y-%m-%d") - datetime.now()).days
        return f"📅 {days}d"

def display_exams(exams, title="EXAMS"):
    if not exams:
        print_warning("No exams found!")
        return
    
    print_header(title)
    print(f"{'ID':<5} {'Subject':<20} {'Date':<12} {'Time':<8} {'Status':<12}")
    print("-" * 65)
    
    for exam in exams:
        status = get_status(exam)
        print(f"{exam['id']:<5} {exam['subject']:<20} {exam['date']:<12} {exam['time']:<8} {status:<12}")
    
    print("-" * 65)
    print_info(f"Total: {len(exams)} exams")

def display_exam_details(exam):
    if not exam:
        return
    
    print_header("📖 EXAM DETAILS")
    print(f"ID:        {exam['id']}")
    print(f"Subject:   {exam['subject']}")
    print(f"Date:      {exam['date']}")
    print(f"Time:      {exam['time']}")
    print(f"Location:  {exam['location'] or 'Not specified'}")
    print(f"Teacher:   {exam['teacher'] or 'Not specified'}")
    
    days = (datetime.strptime(exam['date'], "%Y-%m-%d") - datetime.now()).days
    if days < 0:
        print(f"Status:    Past ({abs(days)} days ago)")
    elif days == 0:
        print(f"Status:    Today! 🎯")
    else:
        print(f"Status:    {days} days from now")

# ============================================
# MAIN APPLICATION
# ============================================
def main():
    """Main application with email reminders"""
    print_header("📚 EXAM BUDDY - PROFESSIONAL VERSION")
    print_info("SQLite Database Edition with Email Reminders")
    
    # Initialize database
    db = ExamDatabase()
    
    # Initialize email reminder
    email_reminder = EmailReminder()
    
    # Check for old JSON and offer migration
    if os.path.exists('exams.json'):
        print_warning("Found old exams.json file!")
        migrate = input("Would you like to migrate your old data? (yes/no): ").lower()
        if migrate in ['yes', 'y']:
            db.migrate_from_json()
    
    # Auto-check reminders
    print_header("🔔 AUTOMATIC REMINDERS")
    upcoming = db.get_upcoming_exams()
    if upcoming:
        print_info(f"You have {len(upcoming)} upcoming exams!")
        today_exams = db.get_todays_exams()
        if today_exams:
            print_warning(f"{len(today_exams)} exam(s) scheduled for TODAY!")
            for exam in today_exams:
                print(f"   • {exam['subject']} at {exam['time']}")
    else:
        print_success("No upcoming exams! Enjoy your break!")
    
    # Main menu
    while True:
        print("\n" + "=" * 60)
        print(f"📚 EXAM BUDDY - {len(db.get_all_exams())} exam(s)")
        print("=" * 60)
        print("1. 📝 Add Exam")
        print("2. 👀 View All Exams")
        print("3. 🎯 View Upcoming Exams")
        print("4. ⏰ View Past Exams")
        print("5. 📅 View Today's Exams")
        print("6. 📆 Next 7 Days")
        print("7. 🔍 Search Exams")
        print("8. ✏️  Edit Exam")
        print("9. 🗑️  Delete Exam")
        print("10. 🗑️  Delete All Exams")
        print("11. 📊 Statistics")
        print("12. 💾 Export to JSON")
        print("13. 🔄 Backup Database")
        print("14. 📧 Setup Email")
        print("15. 📧 Send Email Reminder")
        print("16. 📨 Send Daily Digest")
        print("17. 🚪 Exit")
        print("=" * 60)
        
        choice = input("Choose (1-17): ")
        
        if choice == "1":
            print_header("📝 ADD NEW EXAM")
            subject = input("Subject name: ").strip()
            date = input("Exam date (YYYY-MM-DD): ").strip()
            time = input("Exam time (HH:MM): ").strip()
            location = input("Location (optional): ").strip()
            teacher = input("Teacher (optional): ").strip()
            
            if subject and date and time:
                db.add_exam(subject, date, time, location or None, teacher or None)
            else:
                print_error("Subject, date, and time are required!")
        
        elif choice == "2":
            exams = db.get_all_exams()
            display_exams(exams, "📋 ALL EXAMS")
        
        elif choice == "3":
            exams = db.get_upcoming_exams()
            display_exams(exams, "🎯 UPCOMING EXAMS")
        
        elif choice == "4":
            exams = db.get_past_exams()
            display_exams(exams, "⏰ PAST EXAMS")
        
        elif choice == "5":
            exams = db.get_todays_exams()
            if exams:
                display_exams(exams, "📅 TODAY'S EXAMS")
            else:
                print_warning("No exams scheduled for today! 🎉")
        
        elif choice == "6":
            exams = db.get_upcoming_week_exams()
            if exams:
                display_exams(exams, "📆 NEXT 7 DAYS")
            else:
                print_warning("No exams in the next 7 days! 🎉")
        
        elif choice == "7":
            keyword = input("🔍 Enter search term: ").strip()
            if keyword:
                exams = db.search_exams(keyword)
                if exams:
                    display_exams(exams, f"🔍 SEARCH RESULTS: '{keyword}'")
                else:
                    print_warning(f"No exams found with '{keyword}'")
            else:
                print_error("Please enter a search term!")
        
        elif choice == "8":
            exam_id = input("📝 Enter exam ID to edit: ").strip()
            if exam_id.isdigit():
                exam = db.get_exam_by_id(int(exam_id))
                if exam:
                    display_exam_details(exam)
                    print_info("Press Enter to keep current value")
                    
                    subject = input(f"Subject [{exam['subject']}]: ").strip()
                    date = input(f"Date [{exam['date']}]: ").strip()
                    time = input(f"Time [{exam['time']}]: ").strip()
                    location = input(f"Location [{exam['location'] or ''}]: ").strip()
                    teacher = input(f"Teacher [{exam['teacher'] or ''}]: ").strip()
                    
                    db.update_exam(
                        int(exam_id),
                        subject or None,
                        date or None,
                        time or None,
                        location or None,
                        teacher or None
                    )
                else:
                    print_error("Exam not found!")
            else:
                print_error("Invalid ID!")
        
        elif choice == "9":
            exam_id = input("📝 Enter exam ID to delete: ").strip()
            if exam_id.isdigit():
                exam = db.get_exam_by_id(int(exam_id))
                if exam:
                    print_warning(f"Deleting: {exam['subject']}")
                    confirm = input("Are you sure? (yes/no): ").lower()
                    if confirm in ['yes', 'y']:
                        db.delete_exam(int(exam_id))
                else:
                    print_error("Exam not found!")
            else:
                print_error("Invalid ID!")
        
        elif choice == "10":
            db.delete_all_exams()
        
        elif choice == "11":
            stats = db.get_statistics()
            if stats:
                print_header("📊 EXAM STATISTICS")
                for key, value in stats.items():
                    print(f"{key.replace('_', ' ').title()}: {value}")
        
        elif choice == "12":
            db.export_to_json()
        
        elif choice == "13":
            backup_name = f"exams_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            try:
                import shutil
                shutil.copy2('exams.db', backup_name)
                print_success(f"Database backed up to {backup_name}")
            except Exception as e:
                print_error(f"Backup failed: {e}")
        
        elif choice == "14":
            # Setup Email
            print_header("📧 EMAIL SETUP")
            print_info("This will configure email reminders for your exams.")
            print_warning("You need to use an App Password (not your regular Gmail password).")
            
            email = input("Enter your Gmail address: ").strip()
            password = input("Enter your Gmail App Password: ").strip()
            
            if email and password:
                email_reminder.email = email
                email_reminder.password = password
                email_reminder.save_config()
                print_success("Email configured successfully!")
            else:
                print_error("Email and password are required!")
        
        elif choice == "15":
            # Send Email Reminder
            print_header("📧 SEND EMAIL REMINDER")
            
            if not email_reminder.is_configured():
                print_warning("Email not configured! Please set up email first (option 14).")
                continue
            
            to_email = input("Enter recipient email: ").strip()
            if not to_email:
                print_error("Recipient email is required!")
                continue
            
            days_input = input("Send reminders for exams within how many days? (default: 3): ").strip()
            days = int(days_input) if days_input else 3
            
            print_info(f"Sending reminders for exams within {days} days...")
            
            # Get upcoming exams and convert to dict
            exams = db.get_upcoming_exams()
            exam_list = []
            for exam in exams:
                exam_list.append({
                    'subject': exam['subject'],
                    'date': exam['date'],
                    'time': exam['time'],
                    'location': exam['location'],
                    'teacher': exam['teacher']
                })
            
            if exam_list:
                email_reminder.check_and_send_reminders(to_email, exam_list, days)
            else:
                print_info("No upcoming exams to send reminders for!")
        
        elif choice == "16":
            # Send Daily Digest
            print_header("📨 SEND DAILY DIGEST")
            
            if not email_reminder.is_configured():
                print_warning("Email not configured! Please set up email first (option 14).")
                continue
            
            to_email = input("Enter recipient email: ").strip()
            if not to_email:
                print_error("Recipient email is required!")
                continue
            
            # Get upcoming exams
            exams = db.get_upcoming_exams()
            exam_list = []
            for exam in exams:
                exam_list.append({
                    'subject': exam['subject'],
                    'date': exam['date'],
                    'time': exam['time'],
                    'location': exam['location'],
                    'teacher': exam['teacher']
                })
            
            if exam_list:
                email_reminder.send_daily_digest(to_email, exam_list)
            else:
                print_info("No upcoming exams to send digest for!")
        
        elif choice == "17":
            # Exit
            print("\n💾 Closing database...")
            db.close()
            print_header("👋 GOODBYE!")
            print_info("Your exams are safely stored in the database.")
            break
        
        else:
            print_error("Invalid choice!")

# ============================================
# RUN APPLICATION
# ============================================
if __name__ == "__main__":
    main()