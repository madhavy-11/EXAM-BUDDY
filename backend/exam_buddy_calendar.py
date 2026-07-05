# exam_buddy_calendar.py - Calendar Integration for Exam Buddy
# Export exams to Google Calendar, iCal, and more!

import sqlite3
import json
import os
from datetime import datetime, timedelta
from icalendar import Calendar, Event, vDatetime
import pytz

# ============================================
# DATABASE CLASS
# ============================================
class ExamDatabase:
    def __init__(self, db_name="exams.db"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.connect()
    
    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
    
    def get_all_exams(self):
        try:
            self.cursor.execute('SELECT * FROM exams ORDER BY date ASC, time ASC')
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching exams: {e}")
            return []
    
    def get_upcoming_exams(self):
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            self.cursor.execute('''
                SELECT * FROM exams WHERE date >= date(?) ORDER BY date ASC, time ASC
            ''', (today,))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching exams: {e}")
            return []
    
    def get_exam_by_id(self, exam_id):
        try:
            self.cursor.execute('SELECT * FROM exams WHERE id = ?', (exam_id,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Error fetching exam: {e}")
            return None
    
    def close(self):
        if self.conn:
            self.conn.close()

# ============================================
# CALENDAR EXPORTER CLASS
# ============================================
class CalendarExporter:
    """Export exams to calendar formats"""
    
    def __init__(self, db):
        self.db = db
        self.exams = db.get_all_exams()
        self.upcoming = db.get_upcoming_exams()
        self.timezone = pytz.timezone('Asia/Kolkata')  # Change to your timezone
    
    # ============================================
    # 1. CREATE iCal FILE
    # ============================================
    def create_ical_file(self, filename="exam_schedule.ics", exams=None):
        """Create iCal (.ics) file for all exams"""
        if exams is None:
            exams = self.exams
        
        if not exams:
            print("❌ No exams to export!")
            return None
        
        cal = Calendar()
        cal.add('prodid', '-//Exam Buddy//exam-schedule//EN')
        cal.add('version', '2.0')
        cal.add('calscale', 'GREGORIAN')
        cal.add('method', 'PUBLISH')
        
        for exam in exams:
            event = Event()
            
            # Subject
            event.add('summary', f"📚 Exam: {exam['subject']}")
            
            # Description
            description = f"""
            📚 Exam Details
            
            Subject: {exam['subject']}
            Date: {exam['date']}
            Time: {exam['time']}
            Location: {exam['location'] or 'Not specified'}
            Teacher: {exam['teacher'] or 'Not specified'}
            
            📝 Study Tips:
            - Review your notes
            - Practice previous papers
            - Get enough sleep
            - Arrive early
            
            Good luck! 💪
            """
            event.add('description', description)
            
            # Location
            if exam['location']:
                event.add('location', exam['location'])
            
            # Date and Time
            try:
                # Parse date and time
                exam_datetime = datetime.strptime(
                    f"{exam['date']} {exam['time']}", 
                    "%Y-%m-%d %H:%M"
                )
                
                # Set timezone
                start_time = self.timezone.localize(exam_datetime)
                end_time = start_time + timedelta(hours=2)  # Assume 2-hour exam
                
                event.add('dtstart', start_time)
                event.add('dtend', end_time)
                event.add('dtstamp', datetime.now())
                
                # Create unique ID
                event.add('uid', f"exam-{exam['id']}@exam-buddy")
                
                cal.add_component(event)
            except Exception as e:
                print(f"⚠️ Error adding exam {exam['id']}: {e}")
                continue
        
        # Save to file
        try:
            with open(filename, 'wb') as f:
                f.write(cal.to_ical())
            print(f"✅ iCal file created: {filename}")
            return filename
        except Exception as e:
            print(f"❌ Error saving iCal: {e}")
            return None
    
    # ============================================
    # 2. CREATE GOOGLE CALENDAR LINKS
    # ============================================
    def create_google_calendar_link(self, exam):
        """Create Google Calendar link for a single exam"""
        try:
            # Parse date and time
            exam_datetime = datetime.strptime(
                f"{exam['date']} {exam['time']}", 
                "%Y-%m-%d %H:%M"
            )
            end_datetime = exam_datetime + timedelta(hours=2)
            
            # Format for Google Calendar URL
            start_str = exam_datetime.strftime("%Y%m%dT%H%M%S")
            end_str = end_datetime.strftime("%Y%m%dT%H%M%S")
            
            # Build URL
            url = "https://calendar.google.com/calendar/render?action=TEMPLATE"
            url += f"&text=Exam: {exam['subject']}"
            url += f"&dates={start_str}/{end_str}"
            
            details = f"Subject: {exam['subject']}"
            if exam['location']:
                details += f"\nLocation: {exam['location']}"
            if exam['teacher']:
                details += f"\nTeacher: {exam['teacher']}"
            details += "\n\nGood luck with your exam! 💪"
            
            url += f"&details={details.replace(' ', '+')}"
            
            if exam['location']:
                url += f"&location={exam['location'].replace(' ', '+')}"
            
            return url
        except Exception as e:
            print(f"❌ Error creating Google Calendar link: {e}")
            return None
    
    def create_all_google_links(self):
        """Create Google Calendar links for all exams"""
        links = []
        for exam in self.upcoming:
            link = self.create_google_calendar_link(exam)
            if link:
                links.append({
                    'subject': exam['subject'],
                    'date': exam['date'],
                    'link': link
                })
        return links
    
    # ============================================
    # 3. CREATE HTML CALENDAR EXPORT
    # ============================================
    def create_html_calendar(self, filename="calendar_export.html"):
        """Create HTML page with calendar links"""
        if not self.exams:
            print("❌ No exams to export!")
            return None
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Exam Buddy - Calendar Export</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background-color: #f4f4f4;
        }}
        .container {{
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #667eea;
            text-align: center;
        }}
        .exam-item {{
            border-left: 4px solid #667eea;
            padding: 15px;
            margin: 15px 0;
            background-color: #f8f9fa;
            border-radius: 5px;
        }}
        .exam-item.upcoming {{
            border-left-color: #4CAF50;
        }}
        .exam-item.past {{
            border-left-color: #FF6B6B;
            opacity: 0.7;
        }}
        .btn {{
            display: inline-block;
            padding: 8px 16px;
            margin: 5px;
            background-color: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            border: none;
            cursor: pointer;
        }}
        .btn-google {{
            background-color: #4285F4;
        }}
        .btn-outlook {{
            background-color: #0078D4;
        }}
        .btn-apple {{
            background-color: #555555;
        }}
        .btn:hover {{
            opacity: 0.8;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            color: #666;
            font-size: 12px;
        }}
        .stats {{
            display: flex;
            justify-content: space-around;
            background-color: #f0f0f0;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📚 Exam Buddy - Calendar Export</h1>
        <p style="text-align: center; color: #666;">Export your exams to any calendar application</p>
        
        <div class="stats">
            <div><strong>Total Exams:</strong> {len(self.exams)}</div>
            <div><strong>Upcoming:</strong> {len(self.upcoming)}</div>
            <div><strong>Past:</strong> {len(self.exams) - len(self.upcoming)}</div>
        </div>
        
        <div style="text-align: center; margin: 20px 0;">
            <a href="exam_schedule.ics" class="btn">📅 Download iCal File</a>
        </div>
        
        <h2>📋 Upcoming Exams</h2>
"""
        
        # Add upcoming exams
        upcoming_exams = [e for e in self.exams if e['date'] >= datetime.now().strftime("%Y-%m-%d")]
        for exam in upcoming_exams:
            google_link = self.create_google_calendar_link(exam)
            
            html_content += f"""
        <div class="exam-item upcoming">
            <h3>{exam['subject']}</h3>
            <p><strong>📅 Date:</strong> {exam['date']}</p>
            <p><strong>⏰ Time:</strong> {exam['time']}</p>
            <p><strong>📍 Location:</strong> {exam['location'] or 'Not specified'}</p>
            <p><strong>👨‍🏫 Teacher:</strong> {exam['teacher'] or 'Not specified'}</p>
            <div style="margin-top: 10px;">
                <a href="{google_link}" target="_blank" class="btn btn-google">➕ Google Calendar</a>
            </div>
        </div>
"""
        
        # Add past exams
        past_exams = [e for e in self.exams if e['date'] < datetime.now().strftime("%Y-%m-%d")]
        if past_exams:
            html_content += f"""
        <h2>⏰ Past Exams</h2>
"""
            for exam in past_exams:
                html_content += f"""
        <div class="exam-item past">
            <h3>{exam['subject']}</h3>
            <p><strong>📅 Date:</strong> {exam['date']}</p>
            <p><strong>⏰ Time:</strong> {exam['time']}</p>
            <p><strong>📍 Location:</strong> {exam['location'] or 'Not specified'}</p>
            <p><strong>👨‍🏫 Teacher:</strong> {exam['teacher'] or 'Not specified'}</p>
            <p style="color: #666;">✅ Completed</p>
        </div>
"""
        
        html_content += """
        <div class="footer">
            <p>📚 Exam Buddy - Your Study Assistant</p>
            <p>Export generated on: """ + datetime.now().strftime("%B %d, %Y %H:%M") + """</p>
        </div>
    </div>
</body>
</html>
"""
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"✅ HTML calendar created: {filename}")
            return filename
        except Exception as e:
            print(f"❌ Error saving HTML: {e}")
            return None
    
    # ============================================
    # 4. BULK EXPORT TO GOOGLE CALENDAR
    # ============================================
    def export_to_google_calendar(self):
        """Generate Google Calendar links for all upcoming exams"""
        links = self.create_all_google_links()
        
        if not links:
            print("❌ No upcoming exams to export!")
            return
        
        print("\n" + "=" * 60)
        print("📅 GOOGLE CALENDAR LINKS")
        print("=" * 60)
        print("\n📋 Click the links below to add exams to Google Calendar:\n")
        
        for i, link_data in enumerate(links, 1):
            print(f"{i}. {link_data['subject']} ({link_data['date']})")
            print(f"   🔗 {link_data['link']}\n")
        
        print("=" * 60)
        return links
    
    # ============================================
    # 5. EXPORT TO OUTLOOK CALENDAR
    # ============================================
    def export_to_outlook(self):
        """Create iCal file for Outlook import"""
        filename = f"outlook_import_{datetime.now().strftime('%Y%m%d')}.ics"
        return self.create_ical_file(filename, self.exams)
    
    # ============================================
    # 6. EXPORT TO APPLE CALENDAR
    # ============================================
    def export_to_apple_calendar(self):
        """Create iCal file for Apple Calendar import"""
        filename = f"apple_import_{datetime.now().strftime('%Y%m%d')}.ics"
        return self.create_ical_file(filename, self.exams)
    
    # ============================================
    # 7. CREATE SHAREABLE CALENDAR SUMMARY
    # ============================================
    def create_calendar_summary(self):
        """Create a shareable calendar summary text"""
        if not self.exams:
            print("❌ No exams to summarize!")
            return
        
        summary = f"""
📚 EXAM CALENDAR SUMMARY
═══════════════════════════════════════════════════

Total Exams: {len(self.exams)}
Upcoming: {len(self.upcoming)}
Past: {len(self.exams) - len(self.upcoming)}

📋 UPCOMING EXAMS:
"""
        for exam in self.upcoming:
            summary += f"""
  📖 {exam['subject']}
     📅 Date: {exam['date']}
     ⏰ Time: {exam['time']}
     📍 Location: {exam['location'] or 'Not specified'}
     👨‍🏫 Teacher: {exam['teacher'] or 'Not specified'}
"""
        
        summary += """
═══════════════════════════════════════════════════
📅 Export Files Created:
  • exam_schedule.ics (iCal format)
  • calendar_export.html (HTML page)
  
💡 How to Import:
  1. Google Calendar: Use the links above
  2. Outlook: Download .ics and import
  3. Apple Calendar: Download .ics and import
  
Good luck with your exams! 💪
"""
        
        # Save summary
        filename = f"calendar_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"✅ Calendar summary saved: {filename}")
        print(summary)
        return filename

# ============================================
# HELPER FUNCTIONS
# ============================================
def print_header(text):
    print(f"\n{'=' * 60}")
    print(f"   {text}")
    print(f"{'=' * 60}")

def print_info(text):
    print(f"ℹ️  {text}")

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_warning(text):
    print(f"⚠️  {text}")

# ============================================
# MAIN APPLICATION
# ============================================
def main():
    """Main application for calendar integration"""
    print_header("📅 EXAM BUDDY - CALENDAR INTEGRATION")
    print_info("Export your exams to Google Calendar, iCal, and more!")
    
    # Connect to database
    db = ExamDatabase()
    
    # Check if there are exams
    exams = db.get_all_exams()
    if not exams:
        print_warning("No exams found! Add some exams first.")
        db.close()
        return
    
    print_success(f"Found {len(exams)} exams to export")
    
    # Initialize calendar exporter
    exporter = CalendarExporter(db)
    
    # Main menu
    while True:
        print("\n" + "=" * 60)
        print("📅 CALENDAR EXPORT")
        print("=" * 60)
        print("1. 📅 Create iCal File (.ics)")
        print("2. 🔗 Google Calendar Links")
        print("3. 🌐 Export to HTML Calendar")
        print("4. 📧 Export to Outlook Calendar")
        print("5. 🍎 Export to Apple Calendar")
        print("6. 📋 Create Calendar Summary")
        print("7. 🎬 Export All Formats")
        print("8. 🚪 Exit")
        print("=" * 60)
        
        choice = input("Choose (1-8): ")
        
        if choice == "1":
            # Create iCal
            print_header("📅 CREATE iCAL FILE")
            filename = input("Enter filename (default: exam_schedule.ics): ").strip()
            if not filename:
                filename = "exam_schedule.ics"
            
            exporter.create_ical_file(filename)
        
        elif choice == "2":
            # Google Calendar Links
            print_header("🔗 GOOGLE CALENDAR LINKS")
            exporter.export_to_google_calendar()
        
        elif choice == "3":
            # HTML Calendar
            print_header("🌐 HTML CALENDAR")
            exporter.create_html_calendar()
            print_info("Open calendar_export.html in your browser")
        
        elif choice == "4":
            # Outlook Calendar
            print_header("📧 OUTLOOK CALENDAR")
            exporter.export_to_outlook()
            print_info("Import the .ics file into Outlook")
        
        elif choice == "5":
            # Apple Calendar
            print_header("🍎 APPLE CALENDAR")
            exporter.export_to_apple_calendar()
            print_info("Double-click the .ics file to import to Apple Calendar")
        
        elif choice == "6":
            # Calendar Summary
            print_header("📋 CALENDAR SUMMARY")
            exporter.create_calendar_summary()
        
        elif choice == "7":
            # Export All Formats
            print_header("🎬 EXPORT ALL FORMATS")
            print_info("Creating all calendar exports...")
            
            # iCal
            exporter.create_ical_file("exam_schedule.ics")
            
            # Google Calendar Links
            exporter.export_to_google_calendar()
            
            # HTML Calendar
            exporter.create_html_calendar()
            
            # Outlook
            exporter.export_to_outlook()
            
            # Apple
            exporter.export_to_apple_calendar()
            
            # Summary
            exporter.create_calendar_summary()
            
            print_success("All exports created successfully!")
            print_info("Check your folder for the exported files.")
        
        elif choice == "8":
            # Exit
            print("\n💾 Closing...")
            db.close()
            print_header("👋 GOODBYE!")
            print_info("Calendar integration complete!")
            break
        
        else:
            print_error("Invalid choice!")

# ============================================
# RUN APPLICATION
# ============================================
if __name__ == "__main__":
    main()