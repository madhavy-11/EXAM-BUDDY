# -*- coding: utf-8 -*-

import sqlite3
from datetime import datetime

def fix_date_format(date_str):
    if not date_str:
        return date_str
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError:
        pass
    try:
        dt = datetime.strptime(date_str, "%m/%d/%y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        pass
    try:
        dt = datetime.strptime(date_str, "%m/%d/%Y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        pass
    return date_str

conn = sqlite3.connect('exams.db')
cursor = conn.cursor()

cursor.execute('SELECT id, date FROM exams')
exams = cursor.fetchall()

fixed = 0
for exam in exams:
    exam_id = exam[0]
    old_date = exam[1]
    new_date = fix_date_format(old_date)
    if old_date != new_date:
        cursor.execute('UPDATE exams SET date = ? WHERE id = ?', (new_date, exam_id))
        print(f"✅ Fixed exam {exam_id}: {old_date} → {new_date}")
        fixed += 1

conn.commit()
conn.close()

print(f"\n✅ Fixed {fixed} exam(s)")
