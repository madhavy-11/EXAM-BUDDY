# exam_buddy_final.py - Professional SQLite Version (COMPLETELY FIXED)
# All date features working with proper SQLite date functions!

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
# DATE HELPER FUNCTION
# ============================================
def fix_date_format(date_str):
    """Convert various date formats to YYYY-MM-DD"""
    if not date_str:
        return date_str
    
    # If it's already YYYY-MM-DD, return it
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError:
        pass
    
    # Try MM/DD/YY format
    try:
        dt = datetime.strptime(date_str, "%m/%d/%y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        pass
    
    # Try MM/DD/YYYY format
    try:
        dt = datetime.strptime(date_str, "%m/%d/%Y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        pass
    
    # If all fails, return as is
    return date_str

def safe_days_until(date_str):
    """Safely calculate days until a date"""
    try:
        # First, normalize the date format
        normalized_date = fix_date_format(date_str)
        exam_dt = datetime.strptime(normalized_date, "%Y-%m-%d")
        today = datetime.now()
        return (exam_dt - today).days
    except:
        return None

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
        self.email = email
        self.password = password
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.config_file = "email_config.json"
        
        if not email or not password:
            self.load_config()
    
    def load_config(self):
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
        try:
            with open(self.config_file, 'w') as f:
                json.dump({'email': self.email, 'password': self.password}, f, indent=2)
            print_success("Email configuration saved!")
            return True
        except Exception as e:
            print_error(f"Failed to save config: {e}")
            return False
    
    def is_configured(self):
        return self.email is not None and self.password is not None
    
    def send_reminder(self, to_email, exam_data):
        if not self.is_configured():
            print_error("Email not configured! Please set up email first.")
            return False
        
        try:
            # Fix date before calculating days
            fixed_date = fix_date_format(exam_data['date'])
            exam_date = datetime.strptime(fixed_date, "%Y-%m-%d")
            today = datetime.now()
            days_until = (exam_date - today).days
            
            subject = f"📚 Exam Reminder: {exam_data['subject']}"
            
            body = f"""
Hello Student! 👋

This is a reminder for your upcoming exam:

📖 Subject: {exam_data['subject']}
📅 Date: {exam_data['date']}
⏰ Time: {exam_data['time']}
📍 Location: {exam_data['location'] or 'Not specified'}
👨‍🏫 Teacher: {exam_data['teacher'] or 'Not specified'}

⏳ Days until exam: {days_until} day{'s' if days_until != 1 else ''}

Good luck with your preparation! 💪

---
Exam Buddy - Your Study Assistant 📚
"""
            
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            part = MIMEText(body, 'plain')
            msg.attach(part)
            
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
        if not exams:
            print_info("No exams to include in digest")
            return False
        
        if not self.is_configured():
            print_error("Email not configured!")
            return False
        
        subject = f"📚 Daily Exam Digest - {datetime.now().strftime('%B %d, %Y')}"
        
        body = f"""
📚 Daily Exam Digest - {datetime.now().strftime('%B %d, %Y')}

You have {len(exams)} upcoming exams:

"""
        for exam in exams:
            days = safe_days_until(exam['date'])
            days_text = f"{days} days" if days is not None else "Unknown"
            body += f"""
📖 {exam['subject']}
   📅 Date: {exam['date']}
   ⏰ Time: {exam['time']}
   📍 Location: {exam['location'] or 'Not specified'}
   ⏳ Days until: {days_text}
"""
        
        body += """
Stay organized. Stay focused. You've got this! 💪
---
Exam Buddy - Your Study Assistant
"""
        
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            part = MIMEText(body, 'plain')
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
        if not exams:
            print_info("No upcoming exams found")
            return False
        
        today = datetime.now().date()
        sent_count = 0
        
        for exam in exams:
            days = safe_days_until(exam['date'])
            if days is not None and 0 <= days <= days_threshold:
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
            
            # Normalize date format
            date = fix_date_format(date)
            
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
            
            # Normalize date format
            date = fix_date_format(date)
            
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
                # Fix date format before adding
                date = fix_date_format(exam.get('date', datetime.now().strftime("%Y-%m-%d")))
                
                self.add_exam(
                    subject=exam.get('subject', 'Unknown'),
                    date=date,
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
    """Get status of an exam - FIXED with safe date handling"""
    try:
        # Normalize date format first
        fixed_date = fix_date_format(exam['date'])
        exam_date = datetime.strptime(fixed_date, "%Y-%m-%d")
        today = datetime.now()
        days = (exam_date - today).days
        
        if days < 0:
            return "✅ Past"
        elif days == 0:
            return "🎯 Today!"
        else:
            return f"📅 {days}d"
    except:
        return "❓ Invalid Date"

def display_exams(exams, title="EXAMS"):
    """Display exams in a table - FIXED with safe date handling"""
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
    
    days = safe_days_until(exam['date'])
    if days is not None:
        if days < 0:
            print(f"Status:    Past ({abs(days)} days ago)")
        elif days == 0:
            print(f"Status:    Today! 🎯")
        else:
            print(f"Status:    {days} days from now")
    else:
        print(f"Status:    Invalid date")

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
            print_header("📨 SEND DAILY DIGEST")
            
            if not email_reminder.is_configured():
                print_warning("Email not configured! Please set up email first (option 14).")
                continue
            
            to_email = input("Enter recipient email: ").strip()
            if not to_email:
                print_error("Recipient email is required!")
                continue
            
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