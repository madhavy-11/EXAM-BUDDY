# email_reminder.py - Email Reminder System for Exam Buddy

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import json

class EmailReminder:
    """Email reminder system for Exam Buddy"""
    
    def __init__(self, email, password):
        """
        Initialize email reminder system
        
        Args:
            email (str): Your Gmail address
            password (str): Gmail App Password (not your regular password!)
        """
        self.email = email
        self.password = password
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
    
    def send_reminder(self, to_email, exam_data):
        """
        Send a single exam reminder email
        
        Args:
            to_email (str): Recipient's email address
            exam_data (dict): Exam information
        """
        try:
            # Calculate days until exam
            exam_date = datetime.strptime(exam_data['date'], "%Y-%m-%d")
            today = datetime.now()
            days_until = (exam_date - today).days
            
            # Create email content
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
            
            # HTML version (for better formatting)
            html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f4f4f4;
        }}
        .container {{
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 20px;
            border-radius: 10px 10px 0 0;
            margin: -30px -30px 20px -30px;
            text-align: center;
        }}
        .exam-details {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
        }}
        .days-badge {{
            display: inline-block;
            background-color: {'#ff6b6b' if days_until <= 3 else '#ffd93d' if days_until <= 7 else '#6bcb77'};
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
        }}
        .tips {{
            background-color: #e3f2fd;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
        }}
        .footer {{
            text-align: center;
            color: #666;
            font-size: 12px;
            margin-top: 20px;
            border-top: 1px solid #ddd;
            padding-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 Exam Reminder</h1>
            <p>Don't forget your upcoming exam!</p>
        </div>
        
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
            <ul>
                <li>Start reviewing early</li>
                <li>Practice past papers</li>
                <li>Get enough sleep</li>
                <li>Stay hydrated</li>
            </ul>
        </div>
        
        <div class="footer">
            <p>Good luck with your preparation! 💪</p>
            <p style="font-size: 10px;">This email was sent by Exam Buddy</p>
        </div>
    </div>
</body>
</html>
"""
            
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Attach both plain text and HTML versions
            part1 = MIMEText(body, 'plain')
            part2 = MIMEText(html_body, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email, self.password)
            server.send_message(msg)
            server.quit()
            
            print(f"📧 Email sent to {to_email} for {exam_data['subject']}")
            return True
            
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            return False
    
    def send_daily_digest(self, to_email, exams):
        """
        Send a daily summary of all upcoming exams
        
        Args:
            to_email (str): Recipient's email
            exams (list): List of exam dictionaries
        """
        if not exams:
            print("📭 No exams to include in digest")
            return False
        
        subject = f"📚 Daily Exam Digest - {datetime.now().strftime('%B %d, %Y')}"
        
        # Build HTML body
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f4f4f4;
        }}
        .container {{
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 20px;
            border-radius: 10px 10px 0 0;
            margin: -30px -30px 20px -30px;
            text-align: center;
        }}
        .exam-item {{
            border-left: 4px solid #667eea;
            padding: 10px 15px;
            margin: 10px 0;
            background-color: #f8f9fa;
            border-radius: 5px;
        }}
        .urgent {{
            border-left-color: #ff6b6b;
            background-color: #fff5f5;
        }}
        .soon {{
            border-left-color: #ffd93d;
            background-color: #fffbf0;
        }}
        .footer {{
            text-align: center;
            color: #666;
            font-size: 12px;
            margin-top: 20px;
            border-top: 1px solid #ddd;
            padding-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 Daily Exam Digest</h1>
            <p>{datetime.now().strftime('%B %d, %Y')}</p>
        </div>
        
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
        
        html_body += f"""
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
            
            print(f"📧 Daily digest sent to {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Error sending digest: {e}")
            return False
    
    def send_reminder_for_exams(self, to_email, exams, days_threshold=3):
        """
        Send reminders for exams within a certain number of days
        
        Args:
            to_email (str): Recipient's email
            exams (list): List of exam dictionaries
            days_threshold (int): Send reminders for exams within this many days
        """
        today = datetime.now().date()
        sent_count = 0
        
        for exam in exams:
            exam_date = datetime.strptime(exam['date'], "%Y-%m-%d").date()
            days_until = (exam_date - today).days
            
            if 0 <= days_until <= days_threshold:
                if self.send_reminder(to_email, exam):
                    sent_count += 1
        
        print(f"📧 Sent {sent_count} reminder(s) for exams within {days_threshold} days")
        return sent_count
    
    def check_and_send_reminders(self, to_email, db, days_threshold=3):
        """
        Check database and send reminders automatically
        
        Args:
            to_email (str): Recipient's email
            db: Database connection object
            days_threshold (int): Remind for exams within this many days
        """
        # Get upcoming exams from database
        from exam_buddy_final import ExamDatabase
        
        if not isinstance(db, ExamDatabase):
            print("❌ Invalid database object")
            return False
        
        exams = db.get_upcoming_exams()
        
        if not exams:
            print("📭 No upcoming exams found")
            return False
        
        # Convert to dictionaries
        exam_list = []
        for exam in exams:
            exam_list.append({
                'subject': exam['subject'],
                'date': exam['date'],
                'time': exam['time'],
                'location': exam['location'],
                'teacher': exam['teacher']
            })
        
        # Send reminders
        return self.send_reminder_for_exams(to_email, exam_list, days_threshold)