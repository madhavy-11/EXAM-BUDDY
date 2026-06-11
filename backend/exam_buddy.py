# exam_buddy.py - Day 3: Add, View, Edit, Delete

from datetime import datetime

print("=" * 50)
print("   📚 EXAM BUDDY - DAY 3 📚")
print("=" * 50)

exams = []

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

def add_exam():
    print("\n--- Add New Exam ---")
    subject = input("Subject name: ")
    
    while True:
        date = input("Exam date (YYYY-MM-DD): ")
        if validate_date(date):
            break
        print("❌ Invalid date! Use YYYY-MM-DD")
    
    while True:
        time = input("Exam time (HH:MM): ")
        if validate_time(time):
            break
        print("❌ Invalid time! Use HH:MM")
    
    location = input("Exam location: ")
    teacher = input("Teacher's name (optional): ")
    
    exam = {
        "id": len(exams) + 1,
        "subject": subject,
        "date": date,
        "time": time,
        "location": location,
        "teacher": teacher if teacher else "Not specified"
    }
    
    exams.append(exam)
    print(f"\n✅ Added: {subject} on {date} at {time}")

def view_exams():
    if len(exams) == 0:
        print("\n📭 No exams yet!")
        return
    
    print("\n" + "=" * 65)
    print(f"{'ID':<5} {'Subject':<20} {'Date':<12} {'Time':<8} {'Location':<15}")
    print("=" * 65)
    
    for exam in exams:
        print(f"{exam['id']:<5} {exam['subject']:<20} {exam['date']:<12} {exam['time']:<8} {exam['location']:<15}")
    
    print("=" * 65)
    print(f"📊 TOTAL: {len(exams)} exams")

def edit_exam():
    if len(exams) == 0:
        print("\n📭 No exams to edit!")
        return
    
    view_exams()
    
    try:
        exam_id = int(input("\n📝 Enter Exam ID to edit: "))
        
        exam_to_edit = None
        for exam in exams:
            if exam['id'] == exam_id:
                exam_to_edit = exam
                break
        
        if not exam_to_edit:
            print("\n❌ Exam not found!")
            return
        
        print(f"\n✏️  Editing: {exam_to_edit['subject']}")
        print("(Press Enter to keep current value)")
        
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
            print("❌ Invalid date!")
        
        while True:
            new_time = input(f"Time [{exam_to_edit['time']}]: ").strip()
            if not new_time:
                break
            if validate_time(new_time):
                exam_to_edit['time'] = new_time
                break
            print("❌ Invalid time!")
        
        new_location = input(f"Location [{exam_to_edit['location']}]: ").strip()
        if new_location:
            exam_to_edit['location'] = new_location
        
        new_teacher = input(f"Teacher [{exam_to_edit['teacher']}]: ").strip()
        if new_teacher:
            exam_to_edit['teacher'] = new_teacher
        
        print("\n✅ Exam updated!")
        
    except ValueError:
        print("\n❌ Invalid ID!")

def delete_exam():
    if len(exams) == 0:
        print("\n📭 No exams to delete!")
        return
    
    view_exams()
    
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
                print(f"\n✅ Deleted!")
            else:
                print("\n❌ Cancelled.")
        else:
            print("\n❌ Exam not found!")
    except ValueError:
        print("\n❌ Invalid ID!")

# Main menu
while True:
    print("\n" + "=" * 40)
    print(f"📚 EXAM BUDDY - {len(exams)} exam(s)")
    print("=" * 40)
    print("1. 📝 Add Exam")
    print("2. 👀 View Exams")
    print("3. ✏️  Edit Exam")
    print("4. 🗑️  Delete Exam")
    print("5. 🚪 Exit")
    print("=" * 40)
    
    choice = input("Choose (1-5): ")
    
    if choice == "1":
        add_exam()
    elif choice == "2":
        view_exams()
    elif choice == "3":
        edit_exam()
    elif choice == "4":
        delete_exam()
    elif choice == "5":
        print("\n👋 Goodbye!")
        break
    else:
        print("❌ Invalid choice!")