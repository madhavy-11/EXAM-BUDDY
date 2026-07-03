# exam_buddy_gui.py - Professional GUI for Exam Buddy
# Built with Tkinter - Desktop Application

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from tkcalendar import DateEntry
from datetime import datetime
import sqlite3
import os

# ============================================
# DATABASE CLASS (Reused from main app)
# ============================================
class ExamDatabase:
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
        except sqlite3.Error as e:
            print(f"Database error: {e}")
    
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
        except sqlite3.Error as e:
            print(f"Table creation error: {e}")
    
    def add_exam(self, subject, date, time, location=None, teacher=None):
        try:
            self.cursor.execute('''
                INSERT INTO exams (subject, date, time, location, teacher)
                VALUES (?, ?, ?, ?, ?)
            ''', (subject, date, time, location, teacher))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error adding exam: {e}")
            return None
    
    def get_all_exams(self):
        try:
            self.cursor.execute('SELECT * FROM exams ORDER BY date ASC, time ASC')
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
    
    def update_exam(self, exam_id, subject, date, time, location=None, teacher=None):
        try:
            self.cursor.execute('''
                UPDATE exams 
                SET subject = ?, date = ?, time = ?, location = ?, teacher = ?
                WHERE id = ?
            ''', (subject, date, time, location, teacher, exam_id))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error updating exam: {e}")
            return False
    
    def delete_exam(self, exam_id):
        try:
            self.cursor.execute('DELETE FROM exams WHERE id = ?', (exam_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error deleting exam: {e}")
            return False
    
    def get_upcoming_exams(self):
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            self.cursor.execute('''
                SELECT * FROM exams WHERE date >= date(?) ORDER BY date ASC, time ASC
            ''', (today,))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching upcoming exams: {e}")
            return []
    
    def get_todays_exams(self):
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            self.cursor.execute('''
                SELECT * FROM exams WHERE date = date(?) ORDER BY time ASC
            ''', (today,))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching today's exams: {e}")
            return []
    
    def get_stats(self):
        try:
            stats = {}
            self.cursor.execute('SELECT COUNT(*) FROM exams')
            stats['total'] = self.cursor.fetchone()[0]
            
            today = datetime.now().strftime("%Y-%m-%d")
            self.cursor.execute('SELECT COUNT(*) FROM exams WHERE date >= date(?)', (today,))
            stats['upcoming'] = self.cursor.fetchone()[0]
            
            self.cursor.execute('SELECT COUNT(*) FROM exams WHERE date < date(?)', (today,))
            stats['past'] = self.cursor.fetchone()[0]
            
            self.cursor.execute('SELECT COUNT(DISTINCT subject) FROM exams')
            stats['unique_subjects'] = self.cursor.fetchone()[0]
            
            return stats
        except sqlite3.Error as e:
            print(f"Error getting stats: {e}")
            return {}
    
    def close(self):
        if self.conn:
            self.conn.close()

# ============================================
# MAIN GUI CLASS
# ============================================
class ExamBuddyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("📚 Exam Buddy - Desktop")
        self.root.geometry("1100x650")
        self.root.resizable(True, True)
        self.root.configure(bg='#f0f0f0')
        
        # Database
        self.db = ExamDatabase()
        
        # Variables
        self.current_exam_id = None
        
        # Setup UI
        self.setup_menu()
        self.setup_main_frame()
        self.refresh_exam_list()
    
    def setup_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="📤 Export to JSON", command=self.export_data)
        file_menu.add_separator()
        file_menu.add_command(label="🚪 Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="📋 All Exams", command=lambda: self.filter_exams("all"))
        view_menu.add_command(label="🎯 Upcoming", command=lambda: self.filter_exams("upcoming"))
        view_menu.add_command(label="📅 Today", command=lambda: self.filter_exams("today"))
        menubar.add_cascade(label="View", menu=view_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="📖 About", command=self.show_about)
        help_menu.add_command(label="📊 Statistics", command=self.show_stats)
        menubar.add_cascade(label="Help", menu=help_menu)
    
    def setup_main_frame(self):
        """Create main interface"""
        # Left Panel - Add/Edit Exam
        left_frame = ttk.LabelFrame(self.root, text="📝 Add New Exam", padding=15)
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")
        
        # Subject
        ttk.Label(left_frame, text="Subject:", font=('Arial', 10)).grid(row=0, column=0, sticky="w", pady=5)
        self.subject_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.subject_var, width=30, font=('Arial', 10)).grid(row=0, column=1, pady=5)
        
        # Date
        ttk.Label(left_frame, text="Date:", font=('Arial', 10)).grid(row=1, column=0, sticky="w", pady=5)
        self.date_entry = DateEntry(left_frame, width=28, background='#667eea', 
                                    foreground='white', borderwidth=2, font=('Arial', 10))
        self.date_entry.grid(row=1, column=1, pady=5)
        
        # Time
        ttk.Label(left_frame, text="Time (HH:MM):", font=('Arial', 10)).grid(row=2, column=0, sticky="w", pady=5)
        self.time_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.time_var, width=30, font=('Arial', 10)).grid(row=2, column=1, pady=5)
        
        # Location
        ttk.Label(left_frame, text="Location:", font=('Arial', 10)).grid(row=3, column=0, sticky="w", pady=5)
        self.location_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.location_var, width=30, font=('Arial', 10)).grid(row=3, column=1, pady=5)
        
        # Teacher
        ttk.Label(left_frame, text="Teacher:", font=('Arial', 10)).grid(row=4, column=0, sticky="w", pady=5)
        self.teacher_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.teacher_var, width=30, font=('Arial', 10)).grid(row=4, column=1, pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(left_frame)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=15)
        
        self.add_btn = ttk.Button(btn_frame, text="➕ Add Exam", command=self.add_exam, width=12)
        self.add_btn.pack(side=tk.LEFT, padx=5)
        
        self.update_btn = ttk.Button(btn_frame, text="✏️ Update", command=self.update_exam, width=12, state=tk.DISABLED)
        self.update_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="🗑️ Clear", command=self.clear_form, width=12).pack(side=tk.LEFT, padx=5)
        
        # Right Panel - Exam List
        right_frame = ttk.LabelFrame(self.root, text="📋 Exam List", padding=10)
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Treeview
        columns = ('ID', 'Subject', 'Date', 'Time', 'Location', 'Teacher', 'Status')
        self.tree = ttk.Treeview(right_frame, columns=columns, show='headings', height=18)
        
        # Column headings
        self.tree.heading('ID', text='ID')
        self.tree.heading('Subject', text='Subject')
        self.tree.heading('Date', text='Date')
        self.tree.heading('Time', text='Time')
        self.tree.heading('Location', text='Location')
        self.tree.heading('Teacher', text='Teacher')
        self.tree.heading('Status', text='Status')
        
        # Column widths
        self.tree.column('ID', width=50, anchor='center')
        self.tree.column('Subject', width=180)
        self.tree.column('Date', width=100, anchor='center')
        self.tree.column('Time', width=80, anchor='center')
        self.tree.column('Location', width=120)
        self.tree.column('Teacher', width=120)
        self.tree.column('Status', width=100, anchor='center')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Selection bind
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        
        # Buttons below tree
        action_frame = ttk.Frame(right_frame)
        action_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        ttk.Button(action_frame, text="✏️ Edit Selected", command=self.edit_selected, width=14).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="🗑️ Delete Selected", command=self.delete_selected, width=14).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="🔄 Refresh", command=self.refresh_exam_list, width=14).pack(side=tk.LEFT, padx=5)
        
        # Search
        search_frame = ttk.Frame(right_frame)
        search_frame.grid(row=2, column=0, columnspan=2, pady=5)
        
        ttk.Label(search_frame, text="🔍 Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Search", command=self.search_exams).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Clear", command=lambda: (self.search_var.set(""), self.refresh_exam_list())).pack(side=tk.LEFT)
        
        # Bottom status bar
        status_frame = ttk.Frame(self.root)
        status_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        self.status_label = ttk.Label(status_frame, text="Ready", font=('Arial', 9))
        self.status_label.pack(side=tk.LEFT)
        
        self.count_label = ttk.Label(status_frame, text="Total: 0 exams", font=('Arial', 9))
        self.count_label.pack(side=tk.RIGHT)
    
    # ============================================
    # CRUD OPERATIONS
    # ============================================
    def add_exam(self):
        """Add new exam"""
        subject = self.subject_var.get().strip()
        date = self.date_entry.get()
        time = self.time_var.get().strip()
        location = self.location_var.get().strip()
        teacher = self.teacher_var.get().strip()
        
        if not subject or not time:
            messagebox.showerror("Error", "Subject and Time are required!")
            return
        
        # Validate time format
        try:
            datetime.strptime(time, "%H:%M")
        except:
            messagebox.showerror("Error", "Invalid time format! Use HH:MM")
            return
        
        exam_id = self.db.add_exam(subject, date, time, location or None, teacher or None)
        if exam_id:
            messagebox.showinfo("Success", f"✅ Exam added successfully!\nID: {exam_id}")
            self.clear_form()
            self.refresh_exam_list()
            self.update_status(f"Added: {subject}")
        else:
            messagebox.showerror("Error", "Failed to add exam!")
    
    def update_exam(self):
        """Update existing exam"""
        if not self.current_exam_id:
            return
        
        subject = self.subject_var.get().strip()
        date = self.date_entry.get()
        time = self.time_var.get().strip()
        location = self.location_var.get().strip()
        teacher = self.teacher_var.get().strip()
        
        if not subject or not time:
            messagebox.showerror("Error", "Subject and Time are required!")
            return
        
        try:
            datetime.strptime(time, "%H:%M")
        except:
            messagebox.showerror("Error", "Invalid time format! Use HH:MM")
            return
        
        if self.db.update_exam(self.current_exam_id, subject, date, time, location or None, teacher or None):
            messagebox.showinfo("Success", "✅ Exam updated successfully!")
            self.clear_form()
            self.current_exam_id = None
            self.add_btn.config(state=tk.NORMAL)
            self.update_btn.config(state=tk.DISABLED)
            self.refresh_exam_list()
            self.update_status(f"Updated: {subject}")
        else:
            messagebox.showerror("Error", "Failed to update exam!")
    
    def delete_exam(self, exam_id, subject):
        """Delete an exam"""
        if messagebox.askyesno("Delete Exam", f"Delete '{subject}'?"):
            if self.db.delete_exam(exam_id):
                messagebox.showinfo("Success", f"✅ Deleted: {subject}")
                if self.current_exam_id == exam_id:
                    self.clear_form()
                    self.current_exam_id = None
                    self.add_btn.config(state=tk.NORMAL)
                    self.update_btn.config(state=tk.DISABLED)
                self.refresh_exam_list()
                self.update_status(f"Deleted: {subject}")
            else:
                messagebox.showerror("Error", "Failed to delete exam!")
    
    def delete_selected(self):
        """Delete selected exam"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select an exam to delete!")
            return
        
        item = self.tree.item(selected[0])
        exam_id = item['values'][0]
        subject = item['values'][1]
        self.delete_exam(exam_id, subject)
    
    def edit_selected(self):
        """Load selected exam into form"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select an exam to edit!")
            return
        
        item = self.tree.item(selected[0])
        exam_id = item['values'][0]
        subject = item['values'][1]
        date = item['values'][2]
        time = item['values'][3]
        location = item['values'][4] or ""
        teacher = item['values'][5] or ""
        
        self.subject_var.set(subject)
        self.date_entry.set_date(date)
        self.time_var.set(time)
        self.location_var.set(location)
        self.teacher_var.set(teacher)
        
        self.current_exam_id = exam_id
        self.add_btn.config(state=tk.DISABLED)
        self.update_btn.config(state=tk.NORMAL)
    
    def clear_form(self):
        """Clear all form fields"""
        self.subject_var.set("")
        self.time_var.set("")
        self.location_var.set("")
        self.teacher_var.set("")
        self.current_exam_id = None
        self.add_btn.config(state=tk.NORMAL)
        self.update_btn.config(state=tk.DISABLED)
    
    def on_tree_select(self, event):
        """Handle tree selection"""
        selected = self.tree.selection()
        if selected:
            self.update_status(f"Selected exam ID: {self.tree.item(selected[0])['values'][0]}")
    
    # ============================================
    # DISPLAY FUNCTIONS
    # ============================================
    def refresh_exam_list(self):
        """Refresh the exam list"""
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get exams
        exams = self.db.get_all_exams()
        today = datetime.now().strftime("%Y-%m-%d")
        
        for exam in exams:
            # Get status
            if exam['date'] < today:
                status = "✅ Past"
            elif exam['date'] == today:
                status = "🎯 Today!"
            else:
                days = (datetime.strptime(exam['date'], "%Y-%m-%d") - datetime.now()).days
                status = f"📅 {days}d"
            
            self.tree.insert('', 'end', values=(
                exam['id'],
                exam['subject'],
                exam['date'],
                exam['time'],
                exam['location'] or "",
                exam['teacher'] or "",
                status
            ))
        
        # Update count
        self.count_label.config(text=f"Total: {len(exams)} exams")
        self.update_status(f"Loaded {len(exams)} exams")
    
    def filter_exams(self, filter_type):
        """Filter exams by type"""
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if filter_type == "all":
            exams = self.db.get_all_exams()
        elif filter_type == "upcoming":
            exams = self.db.get_upcoming_exams()
        elif filter_type == "today":
            exams = self.db.get_todays_exams()
        else:
            return
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        for exam in exams:
            if exam['date'] < today:
                status = "✅ Past"
            elif exam['date'] == today:
                status = "🎯 Today!"
            else:
                days = (datetime.strptime(exam['date'], "%Y-%m-%d") - datetime.now()).days
                status = f"📅 {days}d"
            
            self.tree.insert('', 'end', values=(
                exam['id'],
                exam['subject'],
                exam['date'],
                exam['time'],
                exam['location'] or "",
                exam['teacher'] or "",
                status
            ))
        
        self.count_label.config(text=f"Total: {len(exams)} exams")
        self.update_status(f"Filtered: {filter_type}")
    
    def search_exams(self):
        """Search exams by keyword"""
        keyword = self.search_var.get().strip()
        if not keyword:
            self.refresh_exam_list()
            return
        
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Search in database using manual filter
        exams = self.db.get_all_exams()
        filtered = []
        for exam in exams:
            if keyword.lower() in exam['subject'].lower() or keyword.lower() in (exam['teacher'] or "").lower():
                filtered.append(exam)
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        for exam in filtered:
            if exam['date'] < today:
                status = "✅ Past"
            elif exam['date'] == today:
                status = "🎯 Today!"
            else:
                days = (datetime.strptime(exam['date'], "%Y-%m-%d") - datetime.now()).days
                status = f"📅 {days}d"
            
            self.tree.insert('', 'end', values=(
                exam['id'],
                exam['subject'],
                exam['date'],
                exam['time'],
                exam['location'] or "",
                exam['teacher'] or "",
                status
            ))
        
        self.count_label.config(text=f"Found: {len(filtered)} exams")
        self.update_status(f"Search results for: '{keyword}'")
    
    # ============================================
    # ADDITIONAL FEATURES
    # ============================================
    def export_data(self):
        """Export exams to JSON"""
        exams = self.db.get_all_exams()
        if not exams:
            messagebox.showinfo("Info", "No exams to export!")
            return
        
        import json
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
        
        messagebox.showinfo("Success", f"✅ Exported {len(exam_list)} exams to:\n{filename}")
        self.update_status(f"Exported to {filename}")
    
    def show_stats(self):
        """Show statistics in a popup"""
        stats = self.db.get_stats()
        if not stats:
            messagebox.showinfo("Info", "No exams to analyze!")
            return
        
        stats_text = f"""
📊 Exam Statistics

Total Exams:        {stats['total']}
Upcoming Exams:     {stats['upcoming']}
Past Exams:         {stats['past']}
Unique Subjects:    {stats['unique_subjects']}
"""
        messagebox.showinfo("Statistics", stats_text)
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
📚 Exam Buddy - Desktop

Version: 2.0
Built with: Python + Tkinter + SQLite

Features:
• Add, edit, delete exams
• Smart date filtering
• Search functionality
• Export to JSON
• Automatic reminders

Created: July 2026
"""
        messagebox.showinfo("About Exam Buddy", about_text)
    
    def update_status(self, message):
        """Update status bar"""
        self.status_label.config(text=message)
    
    def on_closing(self):
        """Handle window close"""
        self.db.close()
        self.root.destroy()

# ============================================
# RUN APPLICATION
# ============================================
if __name__ == "__main__":
    root = tk.Tk()
    app = ExamBuddyGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()