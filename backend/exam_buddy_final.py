# exam_buddy_final.py - Professional SQLite Version (FIXED)
# All date features working correctly!

import sqlite3
import os
import json
import sys
import io
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
# DATABASE CLASS
# ============================================
class ExamDatabase:
    """Professional SQLite database for Exam Buddy"""
    
    def __init__(self, db_name="exams.db"):
        """Initialize database connection"""
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Connect to SQLite database"""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            print_success(f"Connected to database: {self.db_name}")
        except sqlite3.Error as e:
            print_error(f"Database connection error: {e}")
    
    def create_tables(self):
        """Create exams table if it doesn't exist"""
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
    
    # ===== HELPER: Get today's date =====
    def get_today_str(self):
        """Get today's date as string in YYYY-MM-DD format"""
        return datetime.now().strftime("%Y-%m-%d")
    
    # ===== CREATE =====
    def add_exam(self, subject, date, time, location=None, teacher=None):
        """Add a new exam"""
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
    
    # ===== READ =====
    def get_all_exams(self):
        """Get all exams sorted by date"""
        try:
            self.cursor.execute('''
                SELECT * FROM exams 
                ORDER BY date ASC, time ASC
            ''')
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print_error(f"Error fetching exams: {e}")
            return []
    
    def get_exam_by_id(self, exam_id):
        """Get a single exam by ID"""
        try:
            self.cursor.execute('SELECT * FROM exams WHERE id = ?', (exam_id,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print_error(f"Error fetching exam: {e}")
            return None
    
    def get_upcoming_exams(self):
        """Get upcoming exams (including today) - FIXED"""
        try:
            today = self.get_today_str()
            # Use string comparison with YYYY-MM-DD format (works correctly)
            self.cursor.execute('''
                SELECT * FROM exams 
                WHERE date >= ?
                ORDER BY date ASC, time ASC
            ''', (today,))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print_error(f"Error fetching upcoming exams: {e}")
            return []
    
    def get_past_exams(self):
        """Get past exams - FIXED"""
        try:
            today = self.get_today_str()
            self.cursor.execute('''
                SELECT * FROM exams 
                WHERE date < ?
                ORDER BY date DESC, time DESC
            ''', (today,))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print_error(f"Error fetching past exams: {e}")
            return []
    
    def get_todays_exams(self):
        """Get today's exams - FIXED"""
        try:
            today = self.get_today_str()
            self.cursor.execute('''
                SELECT * FROM exams 
                WHERE date = ?
                ORDER BY time ASC
            ''', (today,))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print_error(f"Error fetching today's exams: {e}")
            return []
    
    def search_exams(self, keyword):
        """Search exams by subject or teacher"""
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
        """Get exams in the next 7 days - FIXED"""
        try:
            today = self.get_today_str()
            next_week = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
            self.cursor.execute('''
                SELECT * FROM exams 
                WHERE date >= ? AND date <= ?
                ORDER BY date ASC, time ASC
            ''', (today, next_week))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print_error(f"Error fetching week exams: {e}")
            return []
    
    def get_exams_by_date_range(self, start_date, end_date):
        """Get exams within a date range"""
        try:
            self.cursor.execute('''
                SELECT * FROM exams 
                WHERE date >= ? AND date <= ?
                ORDER BY date ASC, time ASC
            ''', (start_date, end_date))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print_error(f"Error fetching date range: {e}")
            return []
    
    # ===== UPDATE =====
    def update_exam(self, exam_id, subject=None, date=None, time=None, 
                    location=None, teacher=None):
        """Update an existing exam"""
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
    
    # ===== DELETE =====
    def delete_exam(self, exam_id):
        """Delete an exam by ID"""
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
        """Delete all exams"""
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
    
    # ===== STATISTICS =====
    def get_statistics(self):
        """Get exam statistics"""
        try:
            stats = {}
            self.cursor.execute('SELECT COUNT(*) FROM exams')
            stats['total'] = self.cursor.fetchone()[0]
            
            today = self.get_today_str()
            self.cursor.execute('SELECT COUNT(*) FROM exams WHERE date >= ?', (today,))
            stats['upcoming'] = self.cursor.fetchone()[0]
            
            self.cursor.execute('SELECT COUNT(*) FROM exams WHERE date < ?', (today,))
            stats['past'] = self.cursor.fetchone()[0]
            
            self.cursor.execute('SELECT COUNT(DISTINCT subject) FROM exams')
            stats['unique_subjects'] = self.cursor.fetchone()[0]
            
            return stats
        except sqlite3.Error as e:
            print_error(f"Error getting statistics: {e}")
            return {}
    
    def days_until(self, exam_date):
        """Calculate days until an exam"""
        try:
            exam_dt = datetime.strptime(exam_date, "%Y-%m-%d")
            today = datetime.now()
            return (exam_dt - today).days
        except:
            return None
    
    # ===== EXPORT =====
    def export_to_json(self):
        """Export exams to JSON file"""
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
            with open(filename, 'w') as f:
                json.dump(exam_list, f, indent=2)
            
            print_success(f"Exported {len(exam_list)} exams to {filename}")
            return True
        except Exception as e:
            print_error(f"Export error: {e}")
            return False
    
    # ===== MIGRATION =====
    def migrate_from_json(self, json_file="exams.json"):
        """Migrate old JSON data to SQLite"""
        if not os.path.exists(json_file):
            print_info(f"No JSON file found: {json_file}")
            return False
        
        try:
            with open(json_file, 'r') as f:
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
            
            # Backup old JSON
            backup_name = f"{json_file}.backup"
            os.rename(json_file, backup_name)
            print_info(f"Old JSON backed up as {backup_name}")
            
            return True
        except Exception as e:
            print_error(f"Migration error: {e}")
            return False
    
    # ===== CLOSE =====
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print_info("Database connection closed")

# ============================================
# DISPLAY FUNCTIONS
# ============================================
def get_status(exam):
    """Get status of an exam - FIXED"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    if exam['date'] < today:
        return "✅ Past"
    elif exam['date'] == today:
        return "🎯 Today!"
    else:
        days = (datetime.strptime(exam['date'], "%Y-%m-%d") - datetime.now()).days
        return f"📅 {days}d"

def display_exams(exams, title="EXAMS"):
    """Display exams in a table"""
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
    """Display single exam details"""
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
    """Main application"""
    print_header("📚 EXAM BUDDY - PROFESSIONAL VERSION")
    print_info("SQLite Database Edition")
    
    # Initialize database
    db = ExamDatabase()
    
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
        print("14. 🚪 Exit")
        print("=" * 60)
        
        choice = input("Choose (1-14): ")
        
        if choice == "1":
            # Add Exam
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
            # View All Exams
            exams = db.get_all_exams()
            display_exams(exams, "📋 ALL EXAMS")
        
        elif choice == "3":
            # View Upcoming Exams
            exams = db.get_upcoming_exams()
            display_exams(exams, "🎯 UPCOMING EXAMS")
        
        elif choice == "4":
            # View Past Exams
            exams = db.get_past_exams()
            display_exams(exams, "⏰ PAST EXAMS")
        
        elif choice == "5":
            # View Today's Exams
            exams = db.get_todays_exams()
            if exams:
                display_exams(exams, "📅 TODAY'S EXAMS")
            else:
                print_warning("No exams scheduled for today! 🎉")
        
        elif choice == "6":
            # Next 7 Days
            exams = db.get_upcoming_week_exams()
            if exams:
                display_exams(exams, "📆 NEXT 7 DAYS")
            else:
                print_warning("No exams in the next 7 days! 🎉")
        
        elif choice == "7":
            # Search Exams
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
            # Edit Exam
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
            # Delete Exam
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
            # Delete All Exams
            db.delete_all_exams()
        
        elif choice == "11":
            # Statistics
            stats = db.get_statistics()
            if stats:
                print_header("📊 EXAM STATISTICS")
                for key, value in stats.items():
                    print(f"{key.replace('_', ' ').title()}: {value}")
        
        elif choice == "12":
            # Export to JSON
            db.export_to_json()
        
        elif choice == "13":
            # Backup Database
            backup_name = f"exams_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            try:
                import shutil
                shutil.copy2('exams.db', backup_name)
                print_success(f"Database backed up to {backup_name}")
            except Exception as e:
                print_error(f"Backup failed: {e}")
        
        elif choice == "14":
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