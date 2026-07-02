# exam_buddy.py - Day 7: Complete with Fixed Export

import json
import os
import sys
import io
from datetime import datetime, timedelta

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Constants
DATA_FILE = "exams.json"
BACKUP_FILE = "exams_backup.json"

# ===== COLOR CODES =====
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def print_colored(text, color=Colors.END):
    print(f"{color}{text}{Colors.END}")

def print_success(text):
    print_colored(f"✅ {text}", Colors.GREEN)

def print_error(text):
    print_colored(f"❌ {text}", Colors.RED)

def print_warning(text):
    print_colored(f"⚠️  {text}", Colors.YELLOW)

def print_info(text):
    print_colored(f"ℹ️  {text}", Colors.BLUE)

def print_header(text):
    print_colored(f"\n{'=' * 60}", Colors.CYAN)
    print_colored(f"   {text}", Colors.BOLD + Colors.CYAN)
    print_colored(f"{'=' * 60}", Colors.CYAN)

# ===== HELPER FUNCTIONS =====
def validate_date(date_string):
    try:
        datetime.strptime(date_string, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def validate_time(time_string):
    try:
        datetime.strptime(time_string, "%H:%M")
        return True
    except ValueError:
        return False

def days_until(exam_date):
    try:
        exam_dt = datetime.strptime(exam_date, "%Y-%m-%d").date()
        today = datetime.now().date()
        delta = exam_dt - today
        return delta.days
    except:
        return None

def validate_not_empty(value, field_name):
    if value.strip() == "":
        print_error(f"{field_name} cannot be empty!")
        return False
    return True

# ===== FILE OPERATIONS =====
def save_exams():
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(exams, f, indent=2, ensure_ascii=False)
        return True
    except:
        return False

def load_exams():
    if not os.path.exists(DATA_FILE):
        print_info("No saved data found. Starting fresh!")
        return []
    
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print_success(f"Loaded {len(data)} exams from {DATA_FILE}")
        return data
    except:
        print_error("Error loading data. Starting fresh!")
        return []

def create_backup():
    try:
        with open(BACKUP_FILE, 'w', encoding='utf-8') as f:
            json.dump(exams, f, indent=2, ensure_ascii=False)
        return True
    except:
        return False

# ===== SORTING FUNCTIONS =====
def sort_exams_by_date(exams_list):
    return sorted(exams_list, key=lambda x: x['date'])

def sort_exams_by_subject(exams_list):
    return sorted(exams_list, key=lambda x: x['subject'].lower())

def get_upcoming_exams(exams_list):
    today = datetime.now().date()
    upcoming = []
    for exam in exams_list:
        exam_date = datetime.strptime(exam['date'], "%Y-%m-%d").date()
        if exam_date >= today:
            upcoming.append(exam)
    return sorted(upcoming, key=lambda x: x['date'])

def get_past_exams(exams_list):
    today = datetime.now().date()
    past = []
    for exam in exams_list:
        exam_date = datetime.strptime(exam['date'], "%Y-%m-%d").date()
        if exam_date < today:
            past.append(exam)
    return sorted(past, key=lambda x: x['date'], reverse=True)

# ===== REMINDER FUNCTIONS =====
def check_reminders():
    if len(exams) == 0:
        print_error("No exams to remind you about!")
        return
    
    today = datetime.now().date()
    reminders = []
    
    print_header("🔔 REMINDER CHECK")
    
    for exam in exams:
        exam_date = datetime.strptime(exam['date'], "%Y-%m-%d").date()
        days_until_exam = (exam_date - today).days
        
        if days_until_exam < 0:
            status = "✅ PAST"
            emoji = "📌"
        elif days_until_exam == 0:
            status = "🎯 TODAY!"
            emoji = "🔴"
        elif days_until_exam <= 3:
            status = f"⚠️ SOON ({days_until_exam} days)"
            emoji = "🟠"
        elif days_until_exam <= 7:
            status = f"📅 In {days_until_exam} days"
            emoji = "🟡"
        else:
            status = f"📆 In {days_until_exam} days"
            emoji = "🟢"
        
        reminders.append({
            'exam': exam,
            'days': days_until_exam,
            'status': status,
            'emoji': emoji
        })
    
    reminders.sort(key=lambda x: x['days'])
    
    for r in reminders:
        print(f"{r['emoji']} {r['exam']['subject']:<20} | {r['exam']['date']} | {r['status']}")
    
    urgent = [r for r in reminders if 0 <= r['days'] <= 3]
    
    if urgent:
        print_header("⚠️ URGENT REMINDERS (Within 3 days)")
        for r in urgent:
            print(f"🔴 {r['exam']['subject']} - {r['exam']['date']} ({r['days']} days from now)")
    else:
        if len(reminders) > 0:
            print_success("No urgent exams! Keep studying at your own pace.")

def show_countdown_timer():
    if len(exams) == 0:
        print_error("No exams to countdown to!")
        return
    
    today = datetime.now().date()
    upcoming = []
    
    for exam in exams:
        exam_date = datetime.strptime(exam['date'], "%Y-%m-%d").date()
        days_until_exam = (exam_date - today).days
        if days_until_exam >= 0:
            upcoming.append({
                'exam': exam,
                'days': days_until_exam,
                'date': exam_date
            })
    
    if not upcoming:
        print_warning("No upcoming exams! You're all done!")
        return
    
    nearest = min(upcoming, key=lambda x: x['days'])
    
    print_header("⏰ COUNTDOWN TO NEXT EXAM")
    
    exam = nearest['exam']
    days = nearest['days']
    
    if days == 0:
        print(f"🎯 {exam['subject']} is TODAY!")
        print(f"   Time: {exam['time']}")
        print(f"   Location: {exam['location']}")
        print(f"   Teacher: {exam['teacher']}")
    elif days == 1:
        print(f"📅 {exam['subject']} is TOMORROW!")
        print(f"   Time: {exam['time']}")
        print(f"   Location: {exam['location']}")
        print(f"   Teacher: {exam['teacher']}")
    else:
        print(f"📅 {exam['subject']} in {days} days")
        print(f"   Date: {exam['date']} at {exam['time']}")
        print(f"   Location: {exam['location']}")
        print(f"   Teacher: {exam['teacher']}")
    
    print("\n📋 Next 3 exams:")
    for i, u in enumerate(sorted(upcoming, key=lambda x: x['days'])[:3], 1):
        exam = u['exam']
        days = u['days']
        if days == 0:
            days_text = "TODAY!"
        elif days == 1:
            days_text = "Tomorrow"
        else:
            days_text = f"{days} days"
        print(f"   {i}. {exam['subject']} - {exam['date']} ({days_text})")

def show_today_exams():
    today_str = datetime.now().strftime("%Y-%m-%d")
    today_date = datetime.now().date()
    
    print_header(f"📅 TODAY'S DATE: {today_str}")
    
    if len(exams) == 0:
        print_error("No exams added yet!")
        return
    
    today_exams = []
    
    for exam in exams:
        if exam['date'] == today_str:
            today_exams.append(exam)
    
    if len(today_exams) == 0:
        for exam in exams:
            try:
                exam_date = datetime.strptime(exam['date'], "%Y-%m-%d").date()
                if exam_date == today_date:
                    if exam not in today_exams:
                        today_exams.append(exam)
            except:
                pass
    
    if len(today_exams) == 0:
        print_warning("No exams scheduled for today! 🎉")
        
        upcoming = get_upcoming_exams(exams)
        if len(upcoming) > 0:
            print("\n📋 Your next exams:")
            for i, exam in enumerate(upcoming[:3], 1):
                days = days_until(exam['date'])
                if days is not None:
                    print(f"   {i}. {exam['subject']} - {exam['date']} ({days} days from now)")
        return
    
    print(f"\n🎯 EXAMS TODAY ({len(today_exams)} found):")
    print("-" * 50)
    
    for exam in sorted(today_exams, key=lambda x: x['time']):
        print(f"📖 {exam['subject']}")
        print(f"   ⏰ Time: {exam['time']}")
        print(f"   📍 Location: {exam['location']}")
        print(f"   👨‍🏫 Teacher: {exam['teacher']}")
        print()
    
    print_info("Good luck on your exams today! You've got this! 💪")

# ===== EXPORT FUNCTION (FIXED) =====
def export_exams():
    """Export exams to a text file (Fixed for Windows)"""
    if len(exams) == 0:
        print_error("No exams to export!")
        return
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"exam_schedule_{timestamp}.txt"
    
    try:
        # Use UTF-8 encoding to handle emojis
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("   EXAM BUDDY - EXAM SCHEDULE\n")
            f.write(f"   Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 70 + "\n\n")
            
            # Get upcoming and past exams
            upcoming = get_upcoming_exams(exams)
            past = get_past_exams(exams)
            
            # Upcoming exams
            if len(upcoming) > 0:
                f.write("UPCOMING EXAMS:\n")
                f.write("-" * 50 + "\n")
                
                for exam in upcoming:
                    days = days_until(exam['date'])
                    if days == 0:
                        days_text = "TODAY!"
                    elif days == 1:
                        days_text = "Tomorrow"
                    else:
                        days_text = f"{days} days"
                    
                    f.write(f"\nSubject: {exam['subject']}\n")
                    f.write(f"Date: {exam['date']}\n")
                    f.write(f"Time: {exam['time']}\n")
                    f.write(f"Location: {exam['location']}\n")
                    f.write(f"Teacher: {exam['teacher']}\n")
                    f.write(f"Days until: {days_text}\n")
                    f.write("-" * 30 + "\n")
                f.write("\n")
            
            # Past exams
            if len(past) > 0:
                f.write("PAST EXAMS:\n")
                f.write("-" * 50 + "\n")
                
                for exam in past:
                    days = days_until(exam['date'])
                    f.write(f"\nSubject: {exam['subject']}")
                    if days is not None:
                        f.write(f" ({abs(days)} days ago)")
                    f.write(f"\nDate: {exam['date']}\n")
                    f.write(f"Time: {exam['time']}\n")
                    f.write(f"Location: {exam['location']}\n")
                    f.write(f"Teacher: {exam['teacher']}\n")
                    f.write("-" * 30 + "\n")
                f.write("\n")
            
            # Statistics
            f.write("\n" + "=" * 70 + "\n")
            f.write("STATISTICS\n")
            f.write("=" * 70 + "\n")
            f.write(f"Total exams: {len(exams)}\n")
            f.write(f"Upcoming: {len(upcoming)}\n")
            f.write(f"Past: {len(past)}\n")
            
            # Unique subjects
            unique_subjects = set()
            for exam in exams:
                unique_subjects.add(exam['subject'])
            f.write(f"Unique subjects: {len(unique_subjects)}\n")
            
            if len(unique_subjects) > 0:
                f.write("\nSubjects:\n")
                for subject in sorted(unique_subjects):
                    f.write(f"  - {subject}\n")
            
            f.write("\n" + "=" * 70 + "\n")
            f.write("Thank you for using Exam Buddy!\n")
            f.write("Good luck with your exams!\n")
            f.write("=" * 70 + "\n")
        
        print_success(f"Exams exported successfully!")
        print_info(f"File: {filename}")
        print_info(f"Location: {os.getcwd()}")
        
        # Ask if user wants to open the file
        try:
            open_file = input("\nOpen the exported file? (yes/no): ").lower()
            if open_file in ['yes', 'y']:
                if os.name == 'nt':  # Windows
                    os.startfile(filename)
                else:  # Mac/Linux
                    import subprocess
                    subprocess.call(['open', filename])
                print_info("File opened!")
        except:
            pass
        
    except PermissionError:
        print_error(f"Permission denied! Can't write to {os.getcwd()}")
        print_info("Try saving to a different location.")
    except Exception as e:
        print_error(f"Failed to export: {e}")
        print_info("Make sure you have write permissions in this folder.")

# ===== OTHER FUNCTIONS =====
def clear_all_exams():
    if len(exams) == 0:
        print_error("No exams to clear!")
        return
    
    print_header("⚠️ CLEAR ALL EXAMS")
    print_warning(f"You are about to delete ALL {len(exams)} exams!")
    print_warning("This action CANNOT be undone!")
    
    confirm = input("\nType 'DELETE ALL' to confirm: ").strip()
    
    if confirm == "DELETE ALL":
        create_backup()
        print_info("Backup created before clearing")
        
        exams.clear()
        save_exams()
        
        print_success("All exams have been cleared!")
        print_info(f"Backup saved to {BACKUP_FILE}")
    else:
        print_info("Clear operation cancelled.")

def restore_from_backup():
    if not os.path.exists(BACKUP_FILE):
        print_error("No backup file found!")
        return
    
    try:
        with open(BACKUP_FILE, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        print_header("💾 RESTORE FROM BACKUP")
        print_info(f"Found backup with {len(backup_data)} exams")
        print_info(f"Current exams: {len(exams)}")
        
        confirm = input("\nRestore from backup? (yes/no): ").lower()
        
        if confirm in ['yes', 'y']:
            exams.clear()
            for exam in backup_data:
                exams.append(exam)
            for i, exam in enumerate(exams, start=1):
                exam['id'] = i
            
            save_exams()
            print_success(f"Restored {len(exams)} exams from backup!")
        else:
            print_info("Restore cancelled.")
            
    except Exception as e:
        print_error(f"Failed to restore: {e}")

def show_schedule_summary():
    if len(exams) == 0:
        print_error("No exams to summarize!")
        return
    
    print_header("📅 SCHEDULE SUMMARY")
    
    upcoming = get_upcoming_exams(exams)
    past = get_past_exams(exams)
    
    print(f"📊 Total: {len(exams)} exams")
    print(f"🎯 Upcoming: {len(upcoming)}")
    print(f"⏰ Past: {len(past)}")
    
    if len(upcoming) > 0:
        print("\n📋 Next 5 upcoming exams:")
        for i, exam in enumerate(upcoming[:5], 1):
            days = days_until(exam['date'])
            days_text = "TODAY! 🎯" if days == 0 else f"in {days} days"
            print(f"   {i}. {exam['subject']} - {exam['date']} ({days_text})")
    
    if len(past) > 0:
        print(f"\n📌 Recent past exams:")
        for exam in past[:3]:
            days = days_until(exam['date'])
            print(f"   • {exam['subject']} ({abs(days)} days ago)")

# ===== IMPROVED ADD EXAM =====
def add_exam_improved():
    print_header("📝 ADD NEW EXAM")
    
    while True:
        subject = input("Subject name: ").strip()
        if validate_not_empty(subject, "Subject"):
            break
    
    while True:
        date = input("Exam date (YYYY-MM-DD): ").strip()
        if validate_not_empty(date, "Date") and validate_date(date):
            break
        print_error("Invalid date! Use YYYY-MM-DD")
    
    while True:
        time = input("Exam time (HH:MM): ").strip()
        if validate_not_empty(time, "Time") and validate_time(time):
            break
        print_error("Invalid time! Use HH:MM")
    
    location = input("Exam location (optional): ").strip()
    if location == "":
        location = "Not specified"
    
    teacher = input("Teacher's name (optional): ").strip()
    if teacher == "":
        teacher = "Not specified"
    
    exam = {
        "id": len(exams) + 1,
        "subject": subject,
        "date": date,
        "time": time,
        "location": location,
        "teacher": teacher
    }
    
    exams.append(exam)
    save_exams()
    create_backup()
    
    days = days_until(date)
    if days is not None:
        if days < 0:
            print_success(f"Added: {subject} on {date} at {time} (PAST - {abs(days)} days ago)")
        elif days == 0:
            print_success(f"Added: {subject} on {date} at {time} (TODAY! 🎯)")
        else:
            print_success(f"Added: {subject} on {date} at {time} ({days} days from now)")
    print(f"📊 Total exams: {len(exams)}")

# ===== VIEW FUNCTIONS =====
def view_sorted_by_date():
    sorted_exams = sort_exams_by_date(exams)
    print_header("📅 EXAMS (By Date)")
    for exam in sorted_exams:
        days = days_until(exam['date'])
        if days is not None and days < 0:
            status = f"({abs(days)} days ago)"
        elif days == 0:
            status = "🎯 TODAY!"
        elif days is not None:
            status = f"({days} days)"
        else:
            status = ""
        print(f"📖 {exam['subject']} - {exam['date']} at {exam['time']} {status}")

def view_exams_with_countdown():
    if len(exams) == 0:
        print_error("No exams yet!")
        return
    
    sorted_exams = sort_exams_by_date(exams)
    
    print_header("📊 EXAMS WITH COUNTDOWN")
    print(f"{'ID':<5} {'Subject':<20} {'Date':<12} {'Days Until':<12} {'Status':<10}")
    print("-" * 70)
    
    for exam in sorted_exams:
        days = days_until(exam['date'])
        
        if days is None:
            status = "⚠️ Invalid"
        elif days < 0:
            status = "✅ Past"
        elif days == 0:
            status = "🎯 TODAY!"
        elif days <= 7:
            status = "🔴 Soon!"
        elif days <= 30:
            status = "🟡 Coming"
        else:
            status = "🟢 Later"
        
        days_display = f"{days} days" if days is not None else "Invalid"
        print(f"{exam['id']:<5} {exam['subject']:<20} {exam['date']:<12} {days_display:<12} {status:<10}")

def view_exams():
    if len(exams) == 0:
        print_error("No exams yet!")
        return
    
    while True:
        print_header("VIEW EXAMS - Choose how to view")
        print("1. 📅 By Date (Upcoming first)")
        print("2. 📖 By Subject (A-Z)")
        print("3. 🎯 Upcoming Only")
        print("4. ⏰ Past Exams")
        print("5. 🔥 With Countdown")
        print("6. ◀️  Back to Main Menu")
        print("=" * 60)
        
        choice = input("Choose (1-6): ")
        
        if choice == "1":
            view_sorted_by_date()
        elif choice == "2":
            sorted_exams = sort_exams_by_subject(exams)
            print_header("📖 EXAMS (By Subject)")
            for exam in sorted_exams:
                print(f"📖 {exam['subject']} - {exam['date']} at {exam['time']}")
        elif choice == "3":
            upcoming = get_upcoming_exams(exams)
            if len(upcoming) == 0:
                print_warning("No upcoming exams! Enjoy your break!")
            else:
                print_header("🎯 UPCOMING EXAMS")
                for exam in upcoming:
                    days = days_until(exam['date'])
                    days_text = "TODAY! 🎯" if days == 0 else f"({days} days)"
                    print(f"📖 {exam['subject']} - {exam['date']} {days_text}")
        elif choice == "4":
            past = get_past_exams(exams)
            if len(past) == 0:
                print_warning("No past exams yet!")
            else:
                print_header("⏰ PAST EXAMS")
                for exam in past:
                    days = days_until(exam['date'])
                    print(f"📖 {exam['subject']} - {exam['date']} at {exam['time']} ({abs(days)} days ago)")
        elif choice == "5":
            view_exams_with_countdown()
        elif choice == "6":
            break
        else:
            print_error("Invalid choice!")

# ===== CRUD FUNCTIONS =====
def edit_exam():
    if len(exams) == 0:
        print_error("No exams to edit!")
        return
    
    view_sorted_by_date()
    
    try:
        exam_id = int(input("\n📝 Enter Exam ID to edit: "))
        
        exam_to_edit = None
        for exam in exams:
            if exam['id'] == exam_id:
                exam_to_edit = exam
                break
        
        if not exam_to_edit:
            print_error("Exam not found!")
            return
        
        print_header(f"✏️ Editing: {exam_to_edit['subject']}")
        print_info("Press Enter to keep current value")
        
        new_subject = input(f"Subject [{exam_to_edit['subject']}]: ").strip()
        if new_subject:
            exam_to_edit['subject'] = new_subject
        
        while True:
            new_date = input(f"Date [{exam_to_edit['date']}]: ").strip()
            if not new_date:
                break
            if validate_date(new_date):
                exam_to_edit['date'] = new_date
                break
            print_error("Invalid date!")
        
        while True:
            new_time = input(f"Time [{exam_to_edit['time']}]: ").strip()
            if not new_time:
                break
            if validate_time(new_time):
                exam_to_edit['time'] = new_time
                break
            print_error("Invalid time!")
        
        new_location = input(f"Location [{exam_to_edit['location']}]: ").strip()
        if new_location:
            exam_to_edit['location'] = new_location
        
        new_teacher = input(f"Teacher [{exam_to_edit['teacher']}]: ").strip()
        if new_teacher:
            exam_to_edit['teacher'] = new_teacher
        
        save_exams()
        create_backup()
        print_success("Exam updated and saved!")
        
    except ValueError:
        print_error("Invalid ID!")

def delete_exam():
    if len(exams) == 0:
        print_error("No exams to delete!")
        return
    
    view_sorted_by_date()
    
    try:
        exam_id = int(input("\n📝 Enter Exam ID to delete: "))
        
        exam_to_delete = None
        for exam in exams:
            if exam['id'] == exam_id:
                exam_to_delete = exam
                break
        
        if exam_to_delete:
            confirm = input(f"\nDelete '{exam_to_delete['subject']}'? (yes/no): ").lower()
            if confirm in ['yes', 'y']:
                exams.remove(exam_to_delete)
                for i, exam in enumerate(exams, start=1):
                    exam['id'] = i
                save_exams()
                create_backup()
                print_success("Deleted and saved!")
            else:
                print_info("Cancelled.")
        else:
            print_error("Exam not found!")
    except ValueError:
        print_error("Invalid ID!")

def search_exams():
    if len(exams) == 0:
        print_error("No exams to search!")
        return
    
    search_term = input("\n🔍 Enter subject to search: ").strip().lower()
    
    if not search_term:
        print_error("Please enter a search term!")
        return
    
    found = []
    for exam in exams:
        if search_term in exam['subject'].lower():
            found.append(exam)
    
    if len(found) == 0:
        print_error(f"No exams found with '{search_term}'")
        return
    
    print_success(f"Found {len(found)} exam(s) matching '{search_term}':")
    print("-" * 50)
    for exam in found:
        print(f"📖 {exam['subject']} - {exam['date']} at {exam['time']} (ID: {exam['id']})")

def show_stats():
    if len(exams) == 0:
        print_error("No exams to analyze!")
        return
    
    print_header("📊 EXAM STATISTICS")
    print(f"Total exams: {len(exams)}")
    print(f"Unique subjects: {len(set([e['subject'] for e in exams]))}")
    
    upcoming = get_upcoming_exams(exams)
    past = get_past_exams(exams)
    print(f"Upcoming: {len(upcoming)}")
    print(f"Past: {len(past)}")
    
    sorted_exams = sort_exams_by_date(exams)
    if len(sorted_exams) > 0:
        print(f"Earliest exam: {sorted_exams[0]['subject']} on {sorted_exams[0]['date']}")
        print(f"Latest exam: {sorted_exams[-1]['subject']} on {sorted_exams[-1]['date']}")

# ===== MAIN PROGRAM =====
# Load existing exams
exams = load_exams()

# Show welcome message
print_header("📚 EXAM BUDDY - FINAL VERSION")
print_info("Your personal exam schedule manager")

# Auto-check reminders on startup
check_reminders()
show_countdown_timer()

# Main menu
while True:
    print("\n" + "=" * 60)
    print(f"📚 EXAM BUDDY - {len(exams)} exam(s)")
    print("=" * 60)
    print("1. 📝 Add Exam")
    print("2. 👀 View Exams")
    print("3. 🔍 Search Exam")
    print("4. ✏️ Edit Exam")
    print("5. 🗑️ Delete Exam")
    print("6. 📊 Statistics")
    print("7. 🔔 Check Reminders")
    print("8. ⏰ Countdown Timer")
    print("9. 🎯 Today's Exams")
    print("10. 📅 Schedule Summary")
    print("11. 💾 Export Exams")
    print("12. 🔄 Restore from Backup")
    print("13. 🗑️ Clear All Exams")
    print("14. 💾 Manual Save")
    print("15. 🚪 Exit")
    print("=" * 60)
    
    choice = input("Choose (1-15): ")
    
    if choice == "1":
        add_exam_improved()
    elif choice == "2":
        view_exams()
    elif choice == "3":
        search_exams()
    elif choice == "4":
        edit_exam()
    elif choice == "5":
        delete_exam()
    elif choice == "6":
        show_stats()
    elif choice == "7":
        check_reminders()
    elif choice == "8":
        show_countdown_timer()
    elif choice == "9":
        show_today_exams()
    elif choice == "10":
        show_schedule_summary()
    elif choice == "11":
        export_exams()
    elif choice == "12":
        restore_from_backup()
    elif choice == "13":
        clear_all_exams()
    elif choice == "14":
        if save_exams():
            create_backup()
            print_success("Data saved manually!")
        else:
            print_error("Failed to save!")
    elif choice == "15":
        print("\n💾 Saving data...")
        save_exams()
        create_backup()
        print_header("👋 GOODBYE!")
        print_info("Your exams are saved. Good luck with your studies!")
        break
    else:
        print_error("Invalid choice!")