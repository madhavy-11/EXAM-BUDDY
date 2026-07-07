# exam_buddy_sms.py - SMS Alerts for Exam Buddy
# Send SMS reminders using Twilio

import sqlite3
import os
import json
from datetime import datetime, timedelta
from twilio.rest import Client

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
    
    def get_exams_within_days(self, days=3):
        """Get exams within specified number of days"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            future = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
            self.cursor.execute('''
                SELECT * FROM exams 
                WHERE date >= date(?) AND date <= date(?)
                ORDER BY date ASC, time ASC
            ''', (today, future))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching exams: {e}")
            return []
    
    def close(self):
        if self.conn:
            self.conn.close()

# ============================================
# SMS MANAGER CLASS
# ============================================
class SMSManager:
    """Send SMS alerts using Twilio"""
    
    def __init__(self):
        self.config_file = "twilio_config.json"
        self.account_sid = None
        self.auth_token = None
        self.twilio_phone = None
        self.client = None
        self.load_config()
    
    def load_config(self):
        """Load Twilio configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                self.account_sid = config.get('account_sid')
                self.auth_token = config.get('auth_token')
                self.twilio_phone = config.get('twilio_phone')
                self.client = Client(self.account_sid, self.auth_token)
                print("✅ Twilio configuration loaded!")
                return True
            except Exception as e:
                print(f"❌ Error loading config: {e}")
                return False
        return False
    
    def save_config(self, account_sid, auth_token, twilio_phone):
        """Save Twilio configuration to file"""
        try:
            config = {
                'account_sid': account_sid,
                'auth_token': auth_token,
                'twilio_phone': twilio_phone
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            print("✅ Twilio configuration saved!")
            return True
        except Exception as e:
            print(f"❌ Error saving config: {e}")
            return False
    
    def is_configured(self):
        """Check if Twilio is configured"""
        return self.client is not None and self.twilio_phone is not None
    
    def send_sms(self, to_phone, message):
        """
        Send a single SMS
        
        Args:
            to_phone (str): Recipient's phone number (e.g., +1234567890)
            message (str): SMS message content
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_configured():
            print("❌ Twilio not configured! Please set up first.")
            return False
        
        try:
            # Format phone number (remove spaces, ensure +)
            to_phone = to_phone.strip()
            if not to_phone.startswith('+'):
                print("⚠️ Phone number should include country code (e.g., +1...")
                to_phone = '+' + to_phone
            
            message = message.strip()
            if len(message) > 1600:
                print("⚠️ Message is too long (max 1600 characters)")
                message = message[:1597] + "..."
            
            # Send SMS
            sms = self.client.messages.create(
                body=message,
                from_=self.twilio_phone,
                to=to_phone
            )
            
            print(f"✅ SMS sent to {to_phone}")
            print(f"   Message SID: {sms.sid}")
            print(f"   Status: {sms.status}")
            return True
            
        except Exception as e:
            print(f"❌ Error sending SMS: {e}")
            return False
    
    def send_exam_reminder(self, to_phone, exam):
        """
        Send an exam reminder SMS
        
        Args:
            to_phone (str): Recipient's phone number
            exam (dict): Exam information
        """
        # Calculate days until exam
        try:
            exam_date = datetime.strptime(exam['date'], "%Y-%m-%d")
            today = datetime.now()
            days_until = (exam_date - today).days
        except:
            days_until = "unknown"
        
        # Build message
        if days_until == 0:
            days_text = "TODAY! 🎯"
        elif days_until == 1:
            days_text = "Tomorrow"
        elif days_until < 0:
            days_text = f"{abs(days_until)} days ago"
        else:
            days_text = f"in {days_until} days"
        
        message = f"""
📚 Exam Reminder!

Subject: {exam['subject']}
Date: {exam['date']}
Time: {exam['time']}
Location: {exam['location'] or 'Not specified'}
Teacher: {exam['teacher'] or 'Not specified'}

⏳ {days_text}

Good luck! 💪
"""
        
        return self.send_sms(to_phone, message)
    
    def send_daily_digest(self, to_phone, exams):
        """
        Send a daily digest SMS of all upcoming exams
        
        Args:
            to_phone (str): Recipient's phone number
            exams (list): List of exam dictionaries
        """
        if not exams:
            print("📭 No exams to send!")
            return
        
        # Build digest message
        message = f"📚 Daily Exam Digest\n\n"
        message += f"📊 {len(exams)} upcoming exam(s)\n"
        message += "-" * 20 + "\n\n"
        
        for exam in exams[:5]:  # Max 5 exams per SMS
            try:
                exam_date = datetime.strptime(exam['date'], "%Y-%m-%d")
                days_until = (exam_date - datetime.now()).days
                days_text = "Today!" if days_until == 0 else f"{days_until}d"
            except:
                days_text = "Unknown"
            
            message += f"📖 {exam['subject']}\n"
            message += f"   📅 {exam['date']} ({days_text})\n"
            message += f"   ⏰ {exam['time']}\n\n"
        
        if len(exams) > 5:
            message += f"... and {len(exams) - 5} more exams"
        
        message += "\n💪 Stay focused and study hard!"
        
        return self.send_sms(to_phone, message)
    
    def send_emergency_alert(self, to_phone, exams):
        """
        Send urgent SMS for exams within 24 hours
        
        Args:
            to_phone (str): Recipient's phone number
            exams (list): List of exam dictionaries
        """
        if not exams:
            print("📭 No urgent exams to alert!")
            return
        
        message = "🚨 URGENT: Exams within 24 hours!\n\n"
        
        for exam in exams:
            try:
                exam_date = datetime.strptime(exam['date'], "%Y-%m-%d")
                if (exam_date - datetime.now()).days == 0:
                    message += f"🔴 {exam['subject']} - TODAY at {exam['time']}\n"
                else:
                    message += f"🟠 {exam['subject']} - Tomorrow at {exam['time']}\n"
            except:
                message += f"📖 {exam['subject']} - {exam['date']}\n"
        
        message += "\n⚡ Good luck! Study hard!"
        
        return self.send_sms(to_phone, message)
    
    def send_bulk_reminders(self, phone_list, exams, days_threshold=3):
        """
        Send reminders to multiple phone numbers
        
        Args:
            phone_list (list): List of phone numbers
            exams (list): List of exam dictionaries
            days_threshold (int): Exams within this many days
        """
        if not phone_list:
            print("❌ No phone numbers provided!")
            return
        
        # Filter exams within threshold
        today = datetime.now().date()
        filtered_exams = []
        for exam in exams:
            try:
                exam_date = datetime.strptime(exam['date'], "%Y-%m-%d").date()
                days_until = (exam_date - today).days
                if 0 <= days_until <= days_threshold:
                    filtered_exams.append(exam)
            except:
                pass
        
        if not filtered_exams:
            print(f"📭 No exams within {days_threshold} days")
            return
        
        success_count = 0
        for phone in phone_list:
            for exam in filtered_exams:
                if self.send_exam_reminder(phone, exam):
                    success_count += 1
        
        print(f"✅ Sent {success_count} reminders to {len(phone_list)} numbers")
        return success_count

# ============================================
# HELPER FUNCTIONS
# ============================================
def print_header(text):
    print(f"\n{'=' * 60}")
    print(f"   {text}")
    print(f"{'=' * 60}")

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_info(text):
    print(f"ℹ️  {text}")

def print_warning(text):
    print(f"⚠️  {text}")

# ============================================
# MAIN APPLICATION
# ============================================
def main():
    """Main application for SMS alerts"""
    print_header("📱 EXAM BUDDY - SMS ALERTS")
    print_info("Send SMS reminders for your exams using Twilio")
    
    # Connect to database
    db = ExamDatabase()
    sms = SMSManager()
    
    # Check if there are exams
    exams = db.get_all_exams()
    if not exams:
        print_warning("No exams found! Add some exams first.")
        db.close()
        return
    
    print_success(f"Found {len(exams)} exams")
    
    # Main menu
    while True:
        print("\n" + "=" * 60)
        print("📱 SMS ALERTS")
        print("=" * 60)
        print("1. 📧 Setup Twilio")
        print("2. 📱 Send Exam Reminder")
        print("3. 📨 Send Daily Digest")
        print("4. 🚨 Send Emergency Alert (24h)")
        print("5. 📊 Send Bulk Reminders")
        print("6. 📋 Show Upcoming Exams")
        print("7. 🚪 Exit")
        print("=" * 60)
        
        choice = input("Choose (1-7): ")
        
        if choice == "1":
            # Setup Twilio
            print_header("📧 TWILIO SETUP")
            print_info("You need these from Twilio Console:")
            print("   • Account SID")
            print("   • Auth Token")
            print("   • Twilio Phone Number\n")
            
            account_sid = input("Account SID: ").strip()
            auth_token = input("Auth Token: ").strip()
            twilio_phone = input("Twilio Phone Number (e.g., +1234567890): ").strip()
            
            if account_sid and auth_token and twilio_phone:
                sms.save_config(account_sid, auth_token, twilio_phone)
                # Reload config
                sms.load_config()
                if sms.is_configured():
                    print_success("Twilio setup complete!")
                else:
                    print_error("Setup failed. Please check your credentials.")
            else:
                print_error("All fields are required!")
        
        elif choice == "2":
            # Send Exam Reminder
            print_header("📱 SEND EXAM REMINDER")
            
            if not sms.is_configured():
                print_warning("Twilio not configured! Set up first (option 1).")
                continue
            
            to_phone = input("Recipient phone number (e.g., +1234567890): ").strip()
            if not to_phone:
                print_error("Phone number required!")
                continue
            
            # Show upcoming exams
            exams = db.get_upcoming_exams()
            if not exams:
                print_warning("No upcoming exams!")
                continue
            
            print("\n📋 Upcoming exams:")
            for i, exam in enumerate(exams, 1):
                print(f"   {i}. {exam['subject']} - {exam['date']} at {exam['time']}")
            
            exam_choice = input("\nEnter exam number (or 'all' for all): ").strip()
            
            if exam_choice.lower() == 'all':
                for exam in exams:
                    sms.send_exam_reminder(to_phone, exam)
            elif exam_choice.isdigit():
                idx = int(exam_choice) - 1
                if 0 <= idx < len(exams):
                    sms.send_exam_reminder(to_phone, exams[idx])
                else:
                    print_error("Invalid exam number!")
            else:
                print_error("Invalid choice!")
        
        elif choice == "3":
            # Send Daily Digest
            print_header("📨 SEND DAILY DIGEST")
            
            if not sms.is_configured():
                print_warning("Twilio not configured! Set up first (option 1).")
                continue
            
            to_phone = input("Recipient phone number (e.g., +1234567890): ").strip()
            if not to_phone:
                print_error("Phone number required!")
                continue
            
            exams = db.get_upcoming_exams()
            if exams:
                sms.send_daily_digest(to_phone, [dict(e) for e in exams])
            else:
                print_warning("No upcoming exams to send!")
        
        elif choice == "4":
            # Send Emergency Alert
            print_header("🚨 SEND EMERGENCY ALERT")
            
            if not sms.is_configured():
                print_warning("Twilio not configured! Set up first (option 1).")
                continue
            
            to_phone = input("Recipient phone number (e.g., +1234567890): ").strip()
            if not to_phone:
                print_error("Phone number required!")
                continue
            
            # Get exams within 24 hours
            exams = db.get_exams_within_days(1)
            if exams:
                sms.send_emergency_alert(to_phone, [dict(e) for e in exams])
            else:
                print_warning("No exams within 24 hours!")
        
        elif choice == "5":
            # Send Bulk Reminders
            print_header("📊 SEND BULK REMINDERS")
            
            if not sms.is_configured():
                print_warning("Twilio not configured! Set up first (option 1).")
                continue
            
            phones_input = input("Enter phone numbers (comma separated): ").strip()
            if not phones_input:
                print_error("Phone numbers required!")
                continue
            
            phone_list = [p.strip() for p in phones_input.split(',')]
            
            days_input = input("Send reminders for exams within how many days? (default: 3): ").strip()
            days = int(days_input) if days_input else 3
            
            exams = db.get_exams_within_days(days)
            if exams:
                sms.send_bulk_reminders(phone_list, [dict(e) for e in exams], days)
            else:
                print_warning(f"No exams within {days} days!")
        
        elif choice == "6":
            # Show Upcoming Exams
            print_header("📋 UPCOMING EXAMS")
            exams = db.get_upcoming_exams()
            if exams:
                for exam in exams:
                    try:
                        days = (datetime.strptime(exam['date'], "%Y-%m-%d") - datetime.now()).days
                        days_text = "Today!" if days == 0 else f"{days} days"
                    except:
                        days_text = "Unknown"
                    print(f"📖 {exam['subject']} - {exam['date']} at {exam['time']} ({days_text})")
            else:
                print_warning("No upcoming exams!")
        
        elif choice == "7":
            # Exit
            print("\n💾 Closing...")
            db.close()
            print_header("👋 GOODBYE!")
            print_info("SMS alerts complete!")
            break
        
        else:
            print_error("Invalid choice!")

# ============================================
# RUN APPLICATION
# ============================================
if __name__ == "__main__":
    main()