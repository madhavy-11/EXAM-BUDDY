# exam_buddy_visualizer.py - Data Visualization for Exam Buddy
# Creates professional charts and graphs from your exam data

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime, timedelta
import sqlite3
import os
import json

# ============================================
# DATABASE CLASS (Reused)
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
    
    def get_past_exams(self):
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            self.cursor.execute('''
                SELECT * FROM exams WHERE date < date(?) ORDER BY date DESC, time DESC
            ''', (today,))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching exams: {e}")
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
# VISUALIZER CLASS
# ============================================
class ExamVisualizer:
    """Create charts and graphs from exam data"""
    
    def __init__(self, db):
        self.db = db
        self.exams = db.get_all_exams()
        self.upcoming = db.get_upcoming_exams()
        self.past = db.get_past_exams()
        self.stats = db.get_stats()
        
        # Set style for professional look
        plt.style.use('seaborn-v0_8-darkgrid')
    
    # ============================================
    # CHART 1: Subject Distribution (Bar Chart)
    # ============================================
    def show_subject_distribution(self):
        """Show bar chart of exams by subject"""
        if not self.exams:
            print("No exams to visualize!")
            return
        
        # Count subjects
        subjects = {}
        for exam in self.exams:
            subject = exam['subject']
            subjects[subject] = subjects.get(subject, 0) + 1
        
        # Create chart
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Sort by count (descending)
        sorted_subjects = dict(sorted(subjects.items(), key=lambda x: x[1], reverse=True))
        
        bars = ax.bar(sorted_subjects.keys(), sorted_subjects.values(), 
                     color='#667eea', edgecolor='white', linewidth=2)
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}', ha='center', va='bottom', fontweight='bold')
        
        ax.set_xlabel('Subjects', fontsize=12)
        ax.set_ylabel('Number of Exams', fontsize=12)
        ax.set_title('📊 Exam Distribution by Subject', fontsize=16, fontweight='bold')
        ax.tick_params(axis='x', rotation=45)
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    # ============================================
    # CHART 2: Upcoming vs Past (Pie Chart)
    # ============================================
    def show_upcoming_vs_past(self):
        """Show pie chart of upcoming vs past exams"""
        if not self.exams:
            print("No exams to visualize!")
            return
        
        upcoming_count = len(self.upcoming)
        past_count = len(self.past)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Pie chart
        colors = ['#4CAF50', '#FF6B6B']
        labels = [f'Upcoming\n({upcoming_count})', f'Past\n({past_count})']
        
        if upcoming_count + past_count > 0:
            ax1.pie([upcoming_count, past_count], labels=labels, colors=colors,
                    autopct='%1.1f%%', startangle=90, explode=(0.05, 0),
                    textprops={'fontsize': 12, 'fontweight': 'bold'})
            ax1.set_title('📈 Upcoming vs Past Exams', fontsize=14, fontweight='bold')
        
        # Donut chart (optional - shows same data)
        if upcoming_count + past_count > 0:
            wedgeprops = {'width': 0.7}
            ax2.pie([upcoming_count, past_count], labels=labels, colors=colors,
                    autopct='%1.1f%%', startangle=90, wedgeprops=wedgeprops,
                    textprops={'fontsize': 12, 'fontweight': 'bold'})
            ax2.set_title('🍩 Exam Status Distribution', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        plt.show()
    
    # ============================================
    # CHART 3: Timeline View
    # ============================================
    def show_timeline(self):
        """Show timeline of exams"""
        if not self.exams:
            print("No exams to visualize!")
            return
        
        # Convert dates and sort
        exam_data = []
        for exam in self.exams:
            try:
                date_obj = datetime.strptime(exam['date'], "%Y-%m-%d")
                exam_data.append({
                    'date': date_obj,
                    'subject': exam['subject'],
                    'time': exam['time']
                })
            except:
                pass
        
        if not exam_data:
            print("No valid dates found!")
            return
        
        exam_data.sort(key=lambda x: x['date'])
        
        dates = [d['date'] for d in exam_data]
        subjects = [d['subject'] for d in exam_data]
        y_positions = list(range(len(dates)))
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Create scatter plot
        scatter = ax.scatter(dates, y_positions, color='#667eea', s=200, 
                            edgecolor='white', linewidth=2, zorder=3)
        
        # Add labels for each point
        for i, (date, subject) in enumerate(zip(dates, subjects)):
            ax.annotate(subject, (date, i), xytext=(10, 5),
                       textcoords='offset points', fontsize=10)
        
        # Add vertical lines
        ax.vlines(dates, -0.5, [i+0.5 for i in y_positions], 
                 color='#667eea', alpha=0.3, linewidth=1)
        
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Exams', fontsize=12)
        ax.set_title('📅 Exam Timeline', fontsize=16, fontweight='bold')
        
        # Format x-axis dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates)//7)))
        plt.xticks(rotation=45)
        
        # Remove y-axis ticks
        ax.set_yticks([])
        ax.spines['left'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.grid(axis='x', alpha=0.2)
        
        plt.tight_layout()
        plt.show()
    
    # ============================================
    # CHART 4: Monthly Heatmap
    # ============================================
    def show_monthly_heatmap(self):
        """Show heatmap of exams by month"""
        if not self.exams:
            print("No exams to visualize!")
            return
        
        # Count exams by month
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        month_counts = [0] * 12
        
        for exam in self.exams:
            try:
                date_obj = datetime.strptime(exam['date'], "%Y-%m-%d")
                month_counts[date_obj.month - 1] += 1
            except:
                pass
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Create bar chart
        colors = ['#e8f5e9' if c == 0 else '#c8e6c9' if c <= 1 else 
                 '#a5d6a7' if c <= 2 else '#81c784' if c <= 3 else 
                 '#66bb6a' if c <= 4 else '#4caf50' if c <= 5 else 
                 '#43a047' if c <= 6 else '#388e3c' if c <= 7 else '#2e7d32']
        
        bars = ax.bar(months, month_counts, color=colors, edgecolor='white', linewidth=2)
        
        # Add value labels
        for bar, count in zip(bars, month_counts):
            if count > 0:
                ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.1,
                       f'{count}', ha='center', va='bottom', fontweight='bold')
        
        ax.set_xlabel('Month', fontsize=12)
        ax.set_ylabel('Number of Exams', fontsize=12)
        ax.set_title('📆 Monthly Exam Distribution', fontsize=16, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    # ============================================
    # CHART 5: Status Dashboard (Combined)
    # ============================================
    def show_dashboard(self):
        """Show a complete dashboard with all charts"""
        if not self.exams:
            print("No exams to visualize!")
            return
        
        # Create figure with subplots
        fig = plt.figure(figsize=(15, 12))
        fig.suptitle('📊 EXAM BUDDY - STATISTICS DASHBOARD', 
                    fontsize=20, fontweight='bold', y=0.98)
        
        # 1. Subject Distribution (Top Left)
        ax1 = plt.subplot(2, 2, 1)
        subjects = {}
        for exam in self.exams:
            subject = exam['subject']
            subjects[subject] = subjects.get(subject, 0) + 1
        
        sorted_subjects = dict(sorted(subjects.items(), key=lambda x: x[1], reverse=True))
        bars = ax1.bar(sorted_subjects.keys(), sorted_subjects.values(), 
                      color='#667eea', edgecolor='white', linewidth=2)
        
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}', ha='center', va='bottom', fontweight='bold')
        
        ax1.set_xlabel('Subjects')
        ax1.set_ylabel('Count')
        ax1.set_title('Subject Distribution', fontweight='bold')
        ax1.tick_params(axis='x', rotation=45)
        ax1.grid(axis='y', alpha=0.3)
        
        # 2. Upcoming vs Past (Top Right)
        ax2 = plt.subplot(2, 2, 2)
        upcoming_count = len(self.upcoming)
        past_count = len(self.past)
        
        colors = ['#4CAF50', '#FF6B6B']
        labels = [f'Upcoming\n({upcoming_count})', f'Past\n({past_count})']
        
        if upcoming_count + past_count > 0:
            ax2.pie([upcoming_count, past_count], labels=labels, colors=colors,
                   autopct='%1.1f%%', startangle=90, explode=(0.05, 0),
                   textprops={'fontsize': 11, 'fontweight': 'bold'})
            ax2.set_title('Exam Status', fontweight='bold')
        
        # 3. Monthly Distribution (Bottom Left)
        ax3 = plt.subplot(2, 2, 3)
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        month_counts = [0] * 12
        
        for exam in self.exams:
            try:
                date_obj = datetime.strptime(exam['date'], "%Y-%m-%d")
                month_counts[date_obj.month - 1] += 1
            except:
                pass
        
        bars = ax3.bar(months, month_counts, color='#a29bfe', edgecolor='white', linewidth=2)
        for bar, count in zip(bars, month_counts):
            if count > 0:
                ax3.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.1,
                        f'{count}', ha='center', va='bottom', fontweight='bold')
        
        ax3.set_xlabel('Month')
        ax3.set_ylabel('Count')
        ax3.set_title('Monthly Distribution', fontweight='bold')
        ax3.grid(axis='y', alpha=0.3)
        
        # 4. Statistics Summary (Bottom Right)
        ax4 = plt.subplot(2, 2, 4)
        ax4.axis('off')
        
        stats_text = f"""
        📊 EXAM STATISTICS SUMMARY
        
        ┌─────────────────────────────────────┐
        │  Total Exams:        {len(self.exams):>4}        │
        │  Upcoming Exams:     {len(self.upcoming):>4}        │
        │  Past Exams:         {len(self.past):>4}        │
        │  Unique Subjects:    {len(subjects):>4}        │
        │  Most Common:        {max(subjects, key=subjects.get) if subjects else 'None'} │
        │  Total Subjects:     {sum(subjects.values()):>4}        │
        └─────────────────────────────────────┘
        """
        
        ax4.text(0.1, 0.5, stats_text, transform=ax4.transAxes,
                fontsize=14, verticalalignment='center',
                fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='#f0f0f0', edgecolor='#667eea'))
        
        plt.tight_layout()
        plt.show()
    
    # ============================================
    # CHART 6: Save Chart to File
    # ============================================
    def save_chart(self, chart_type="dashboard"):
        """Save chart as image file"""
        chart_types = {
            "subject": self.show_subject_distribution,
            "status": self.show_upcoming_vs_past,
            "timeline": self.show_timeline,
            "monthly": self.show_monthly_heatmap,
            "dashboard": self.show_dashboard
        }
        
        if chart_type not in chart_types:
            print(f"Invalid chart type: {chart_type}")
            return
        
        filename = f"exam_chart_{chart_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        # Show the chart first
        chart_types[chart_type]()
        
        # Wait for user to close the chart
        print(f"\n💾 Chart displayed. To save:")
        print(f"   In the chart window, click the save icon (💾) or press Ctrl+S")
        print(f"   Or take a screenshot of the chart.")
        print(f"   Chart type: {chart_type}")
    
    # ============================================
    # CHART 7: Show All Charts (Demo)
    # ============================================
    def show_all_charts(self):
        """Display all charts one by one"""
        print_header("📊 EXAM BUDDY - VISUALIZATIONS")
        print_info("Displaying all charts...")
        print_info("Close each chart window to see the next one.\n")
        
        charts = [
            ("Subject Distribution", self.show_subject_distribution),
            ("Upcoming vs Past", self.show_upcoming_vs_past),
            ("Timeline", self.show_timeline),
            ("Monthly Heatmap", self.show_monthly_heatmap),
            ("Dashboard", self.show_dashboard)
        ]
        
        for i, (name, func) in enumerate(charts, 1):
            print(f"\n📊 Chart {i}/{len(charts)}: {name}")
            print("   Close the window to continue...")
            func()
        
        print_success("All charts displayed!")

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
    """Main application for data visualization"""
    print_header("📊 EXAM BUDDY - DATA VISUALIZATION")
    print_info("Visualizing your exam data with matplotlib")
    
    # Connect to database
    db = ExamDatabase()
    
    # Check if there are exams
    exams = db.get_all_exams()
    if not exams:
        print_warning("No exams found! Add some exams first.")
        db.close()
        return
    
    print_success(f"Found {len(exams)} exams to visualize")
    
    # Initialize visualizer
    visualizer = ExamVisualizer(db)
    
    # Main menu
    while True:
        print("\n" + "=" * 60)
        print("📊 EXAM VISUALIZER")
        print("=" * 60)
        print("1. 📊 Subject Distribution (Bar Chart)")
        print("2. 🥧 Upcoming vs Past (Pie Chart)")
        print("3. 📅 Timeline View")
        print("4. 📆 Monthly Heatmap")
        print("5. 📈 Full Dashboard")
        print("6. 🎬 Show All Charts")
        print("7. 💾 Save Chart as Image")
        print("8. 🚪 Exit")
        print("=" * 60)
        
        choice = input("Choose (1-8): ")
        
        if choice == "1":
            visualizer.show_subject_distribution()
        elif choice == "2":
            visualizer.show_upcoming_vs_past()
        elif choice == "3":
            visualizer.show_timeline()
        elif choice == "4":
            visualizer.show_monthly_heatmap()
        elif choice == "5":
            visualizer.show_dashboard()
        elif choice == "6":
            visualizer.show_all_charts()
        elif choice == "7":
            print("\n📊 Chart Types:")
            print("1. Subject Distribution")
            print("2. Upcoming vs Past")
            print("3. Timeline")
            print("4. Monthly Heatmap")
            print("5. Dashboard")
            
            chart_choice = input("Choose chart type (1-5): ")
            
            chart_map = {
                "1": "subject",
                "2": "status",
                "3": "timeline",
                "4": "monthly",
                "5": "dashboard"
            }
            
            if chart_choice in chart_map:
                visualizer.save_chart(chart_map[chart_choice])
            else:
                print_error("Invalid choice!")
        elif choice == "8":
            print("\n💾 Closing...")
            db.close()
            print_header("👋 GOODBYE!")
            print_info("Data visualization complete!")
            break
        else:
            print_error("Invalid choice!")

# ============================================
# RUN APPLICATION
# ============================================
if __name__ == "__main__":
    main()