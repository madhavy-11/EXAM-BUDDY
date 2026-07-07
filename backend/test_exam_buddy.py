# test_exam_buddy.py - Complete Unit Tests for Exam Buddy
# Run with: python test_exam_buddy.py

import unittest
import sqlite3
import os
import json
from datetime import datetime, timedelta
import tempfile

# Import your modules
import sys
sys.path.append('.')
from exam_buddy_final import ExamDatabase, fix_date_format, safe_days_until

# ============================================
# TEST DATABASE CLASS
# ============================================
class TestExamDatabase(unittest.TestCase):
    """Test the ExamDatabase class"""
    
    def setUp(self):
        """Create temporary database before each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.db = ExamDatabase(self.db_path)
    
    def tearDown(self):
        """Clean up after each test"""
        if hasattr(self, 'db') and self.db:
            self.db.close()
        
        if os.path.exists(self.db_path):
            try:
                os.unlink(self.db_path)
            except PermissionError:
                pass
        
        try:
            os.rmdir(self.temp_dir)
        except:
            pass
    
    def test_add_exam(self):
        """Test adding an exam to database"""
        exam_id = self.db.add_exam("Test Subject", "2026-07-15", "09:00", "Room 101", "Mr. Smith")
        
        self.assertIsNotNone(exam_id)
        exam = self.db.get_exam_by_id(exam_id)
        self.assertEqual(exam['subject'], "Test Subject")
        self.assertEqual(exam['date'], "2026-07-15")
        self.assertEqual(exam['time'], "09:00")
        self.assertEqual(exam['location'], "Room 101")
        self.assertEqual(exam['teacher'], "Mr. Smith")
    
    def test_get_all_exams(self):
        """Test retrieving all exams"""
        self.db.add_exam("Math", "2026-07-15", "09:00")
        self.db.add_exam("Physics", "2026-07-16", "14:00")
        self.db.add_exam("Chemistry", "2026-07-17", "10:00")
        
        exams = self.db.get_all_exams()
        self.assertEqual(len(exams), 3)
        
        subjects = [exam['subject'] for exam in exams]
        self.assertIn("Math", subjects)
        self.assertIn("Physics", subjects)
        self.assertIn("Chemistry", subjects)
    
    def test_update_exam(self):
        """Test updating an existing exam"""
        exam_id = self.db.add_exam("Old Subject", "2026-07-15", "09:00")
        
        result = self.db.update_exam(
            exam_id, 
            subject="New Subject",
            date="2026-07-16",
            time="10:00"
        )
        
        self.assertTrue(result)
        exam = self.db.get_exam_by_id(exam_id)
        self.assertEqual(exam['subject'], "New Subject")
        self.assertEqual(exam['date'], "2026-07-16")
        self.assertEqual(exam['time'], "10:00")
    
    def test_delete_exam(self):
        """Test deleting an exam"""
        exam_id = self.db.add_exam("To Delete", "2026-07-15", "09:00")
        
        result = self.db.delete_exam(exam_id)
        self.assertTrue(result)
        exam = self.db.get_exam_by_id(exam_id)
        self.assertIsNone(exam)
    
    def test_upcoming_exams(self):
        """Test getting upcoming exams"""
        today = datetime.now().strftime("%Y-%m-%d")
        future = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
        
        self.db.add_exam("Past", "2026-01-01", "09:00")
        self.db.add_exam("Today", today, "09:00")
        self.db.add_exam("Future", future, "09:00")
        
        upcoming = self.db.get_upcoming_exams()
        self.assertTrue(len(upcoming) >= 2)
        
        subjects = [exam['subject'] for exam in upcoming]
        self.assertNotIn("Past", subjects)
    
    def test_past_exams(self):
        """Test getting past exams"""
        today = datetime.now().strftime("%Y-%m-%d")
        future = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
        
        self.db.add_exam("Past", "2026-01-01", "09:00")
        self.db.add_exam("Today", today, "09:00")
        self.db.add_exam("Future", future, "09:00")
        
        past = self.db.get_past_exams()
        past_subjects = [exam['subject'] for exam in past]
        self.assertIn("Past", past_subjects)
        self.assertNotIn("Today", past_subjects)
        self.assertNotIn("Future", past_subjects)
    
    def test_search_exams(self):
        """Test searching exams"""
        self.db.add_exam("Mathematics", "2026-07-15", "09:00")
        self.db.add_exam("Physics", "2026-07-16", "14:00")
        self.db.add_exam("Biology", "2026-07-17", "10:00")
        
        results = self.db.search_exams("Math")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['subject'], "Mathematics")
        
        results = self.db.search_exams("Chemistry")
        self.assertEqual(len(results), 0)
    
    def test_statistics(self):
        """Test statistics"""
        self.db.add_exam("Math", "2026-07-15", "09:00")
        self.db.add_exam("Physics", "2026-07-16", "14:00")
        
        stats = self.db.get_statistics()
        self.assertEqual(stats['total'], 2)
        self.assertEqual(stats['unique_subjects'], 2)
    
    def test_export_to_json(self):
        """Test exporting to JSON"""
        self.db.add_exam("Math", "2026-07-15", "09:00")
        
        result = self.db.export_to_json()
        
        import glob
        files = glob.glob("exam_export_*.json")
        self.assertTrue(len(files) > 0)
        
        for f in files:
            try:
                os.remove(f)
            except:
                pass

# ============================================
# TEST DATE FUNCTIONS
# ============================================
class TestDateFunctions(unittest.TestCase):
    """Test date formatting functions"""
    
    def test_fix_date_format_yyyy_mm_dd(self):
        result = fix_date_format("2026-07-08")
        self.assertEqual(result, "2026-07-08")
    
    def test_fix_date_format_mm_dd_yy(self):
        result = fix_date_format("7/8/26")
        self.assertEqual(result, "2026-07-08")
    
    def test_fix_date_format_mm_dd_yyyy(self):
        result = fix_date_format("07/08/2026")
        self.assertEqual(result, "2026-07-08")
    
    def test_fix_date_format_invalid(self):
        result = fix_date_format("invalid-date")
        self.assertEqual(result, "invalid-date")
    
    def test_safe_days_until(self):
        future = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        days = safe_days_until(future)
        self.assertIn(days, [6, 7])

# ============================================
# TEST EDGE CASES (FIXED - All pass!)
# ============================================
class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.db = ExamDatabase(self.db_path)
    
    def tearDown(self):
        if hasattr(self, 'db') and self.db:
            self.db.close()
        
        if os.path.exists(self.db_path):
            try:
                os.unlink(self.db_path)
            except PermissionError:
                pass
        
        try:
            os.rmdir(self.temp_dir)
        except:
            pass
    
    def test_add_exam_missing_fields(self):
        """Test adding exam with missing fields - expects ValueError"""
        # Missing subject
        with self.assertRaises(ValueError):
            self.db.add_exam("", "2026-07-15", "09:00")
        
        # Missing date
        with self.assertRaises(ValueError):
            self.db.add_exam("Subject", "", "09:00")
        
        # Missing time
        with self.assertRaises(ValueError):
            self.db.add_exam("Subject", "2026-07-15", "")
    
    def test_delete_nonexistent_exam(self):
        result = self.db.delete_exam(999)
        self.assertFalse(result)
    
    def test_update_nonexistent_exam(self):
        result = self.db.update_exam(999, "New Subject")
        self.assertFalse(result)
    
    def test_get_nonexistent_exam(self):
        exam = self.db.get_exam_by_id(999)
        self.assertIsNone(exam)
    
    def test_empty_database(self):
        exams = self.db.get_all_exams()
        self.assertEqual(len(exams), 0)
        
        upcoming = self.db.get_upcoming_exams()
        self.assertEqual(len(upcoming), 0)
        
        past = self.db.get_past_exams()
        self.assertEqual(len(past), 0)
        
        stats = self.db.get_statistics()
        self.assertEqual(stats['total'], 0)

# ============================================
# RUN TESTS
# ============================================
if __name__ == "__main__":
    print("=" * 60)
    print("   🧪 EXAM BUDDY - TEST SUITE")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestExamDatabase)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDateFunctions))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestEdgeCases))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("   📊 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Tests Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Failures: {len(result.failures)}")
    print(f"❌ Errors: {len(result.errors)}")
    print(f"📊 Total: {result.testsRun}")
    
    if result.wasSuccessful():
        print("\n🎉 All tests passed! Your code is solid!")
    else:
        print("\n⚠️ Some tests failed. Check the output above.")