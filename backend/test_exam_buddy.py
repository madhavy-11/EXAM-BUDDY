# test_exam_buddy.py - Unit Tests for Exam Buddy
# Run with: pytest test_exam_buddy.py -v

import unittest
import sqlite3
import os
import json
from datetime import datetime, timedelta
import tempfile
import shutil

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
        self.test_db = tempfile.NamedTemporaryFile(delete=False)
        self.db_path = self.test_db.name
        self.db = ExamDatabase(self.db_path)
    
    def tearDown(self):
        """Clean up after each test"""
        self.db.close()
        os.unlink(self.db_path)
    
    # ===== TEST 1: Add Exam =====
    def test_add_exam(self):
        """Test adding an exam to database"""
        # Add exam
        exam_id = self.db.add_exam("Test Subject", "2026-07-15", "09:00", "Room 101", "Mr. Smith")
        
        # Check it was added
        self.assertIsNotNone(exam_id)
        
        # Retrieve and verify
        exam = self.db.get_exam_by_id(exam_id)
        self.assertEqual(exam['subject'], "Test Subject")
        self.assertEqual(exam['date'], "2026-07-15")
        self.assertEqual(exam['time'], "09:00")
        self.assertEqual(exam['location'], "Room 101")
        self.assertEqual(exam['teacher'], "Mr. Smith")
    
    # ===== TEST 2: Get All Exams =====
    def test_get_all_exams(self):
        """Test retrieving all exams"""
        # Add multiple exams
        self.db.add_exam("Math", "2026-07-15", "09:00")
        self.db.add_exam("Physics", "2026-07-16", "14:00")
        self.db.add_exam("Chemistry", "2026-07-17", "10:00")
        
        # Get all exams
        exams = self.db.get_all_exams()
        
        # Verify
        self.assertEqual(len(exams), 3)
        
        # Check sorting (should be by date)
        self.assertEqual(exams[0]['subject'], "Math")
        self.assertEqual(exams[1]['subject'], "Physics")
        self.assertEqual(exams[2]['subject'], "Chemistry")
    
    # ===== TEST 3: Update Exam =====
    def test_update_exam(self):
        """Test updating an existing exam"""
        # Add exam
        exam_id = self.db.add_exam("Old Subject", "2026-07-15", "09:00")
        
        # Update exam
        result = self.db.update_exam(
            exam_id, 
            subject="New Subject",
            date="2026-07-16",
            time="10:00"
        )
        
        # Verify update
        self.assertTrue(result)
        exam = self.db.get_exam_by_id(exam_id)
        self.assertEqual(exam['subject'], "New Subject")
        self.assertEqual(exam['date'], "2026-07-16")
        self.assertEqual(exam['time'], "10:00")
    
    # ===== TEST 4: Delete Exam =====
    def test_delete_exam(self):
        """Test deleting an exam"""
        # Add exam
        exam_id = self.db.add_exam("To Delete", "2026-07-15", "09:00")
        
        # Delete exam
        result = self.db.delete_exam(exam_id)
        
        # Verify deletion
        self.assertTrue(result)
        exam = self.db.get_exam_by_id(exam_id)
        self.assertIsNone(exam)
    
    # ===== TEST 5: Upcoming Exams =====
    def test_upcoming_exams(self):
        """Test getting upcoming exams"""
        today = datetime.now().strftime("%Y-%m-%d")
        future = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
        
        # Add exams
        self.db.add_exam("Past", "2026-01-01", "09:00")
        self.db.add_exam("Today", today, "09:00")
        self.db.add_exam("Future", future, "09:00")
        
        # Get upcoming
        upcoming = self.db.get_upcoming_exams()
        
        # Verify
        self.assertTrue(len(upcoming) >= 2)  # Today and Future
        
        # Check that past is not included
        subjects = [exam['subject'] for exam in upcoming]
        self.assertNotIn("Past", subjects)
    
    # ===== TEST 6: Past Exams =====
    def test_past_exams(self):
        """Test getting past exams"""
        today = datetime.now().strftime("%Y-%m-%d")
        future = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
        
        # Add exams
        self.db.add_exam("Past", "2026-01-01", "09:00")
        self.db.add_exam("Today", today, "09:00")
        self.db.add_exam("Future", future, "09:00")
        
        # Get past
        past = self.db.get_past_exams()
        
        # Verify
        past_subjects = [exam['subject'] for exam in past]
        self.assertIn("Past", past_subjects)
        self.assertNotIn("Today", past_subjects)
        self.assertNotIn("Future", past_subjects)
    
    # ===== TEST 7: Search =====
    def test_search_exams(self):
        """Test searching exams"""
        self.db.add_exam("Mathematics", "2026-07-15", "09:00")
        self.db.add_exam("Physics", "2026-07-16", "14:00")
        self.db.add_exam("Biology", "2026-07-17", "10:00")
        
        # Search for Math
        results = self.db.search_exams("Math")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['subject'], "Mathematics")
        
        # Search for no results
        results = self.db.search_exams("Chemistry")
        self.assertEqual(len(results), 0)
    
    # ===== TEST 8: Statistics =====
    def test_statistics(self):
        """Test statistics"""
        # Add exams
        self.db.add_exam("Math", "2026-07-15", "09:00")
        self.db.add_exam("Physics", "2026-07-16", "14:00")
        
        # Get stats
        stats = self.db.get_statistics()
        
        # Verify
        self.assertEqual(stats['total'], 2)
        self.assertEqual(stats['unique_subjects'], 2)
    
    # ===== TEST 9: Export =====
    def test_export_to_json(self):
        """Test exporting to JSON"""
        # Add exams
        self.db.add_exam("Math", "2026-07-15", "09:00")
        
        # Export
        result = self.db.export_to_json()
        
        # Verify file was created
        import glob
        files = glob.glob("exam_export_*.json")
        self.assertTrue(len(files) > 0)
        
        # Clean up
        for f in files:
            os.remove(f)

# ============================================
# TEST DATE FUNCTIONS
# ============================================
class TestDateFunctions(unittest.TestCase):
    """Test date formatting functions"""
    
    def test_fix_date_format_yyyy_mm_dd(self):
        """Test fixing YYYY-MM-DD format"""
        result = fix_date_format("2026-07-08")
        self.assertEqual(result, "2026-07-08")
    
    def test_fix_date_format_mm_dd_yy(self):
        """Test fixing MM/DD/YY format"""
        result = fix_date_format("7/8/26")
        self.assertEqual(result, "2026-07-08")
    
    def test_fix_date_format_mm_dd_yyyy(self):
        """Test fixing MM/DD/YYYY format"""
        result = fix_date_format("07/08/2026")
        self.assertEqual(result, "2026-07-08")
    
    def test_fix_date_format_invalid(self):
        """Test invalid date returns as-is"""
        result = fix_date_format("invalid-date")
        self.assertEqual(result, "invalid-date")
    
    def test_safe_days_until(self):
        """Test days until calculation"""
        today = datetime.now().strftime("%Y-%m-%d")
        future = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        
        days = safe_days_until(future)
        self.assertEqual(days, 7)

# ============================================
# TEST EDGE CASES
# ============================================
class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""
    
    def setUp(self):
        """Create temporary database before each test"""
        self.test_db = tempfile.NamedTemporaryFile(delete=False)
        self.db_path = self.test_db.name
        self.db = ExamDatabase(self.db_path)
    
    def tearDown(self):
        """Clean up after each test"""
        self.db.close()
        os.unlink(self.db_path)
    
    def test_add_exam_missing_fields(self):
        """Test adding exam with missing fields"""
        # Missing subject
        exam_id = self.db.add_exam("", "2026-07-15", "09:00")
        self.assertIsNone(exam_id)
        
        # Missing date
        exam_id = self.db.add_exam("Subject", "", "09:00")
        self.assertIsNone(exam_id)
        
        # Missing time
        exam_id = self.db.add_exam("Subject", "2026-07-15", "")
        self.assertIsNone(exam_id)
    
    def test_delete_nonexistent_exam(self):
        """Test deleting non-existent exam"""
        result = self.db.delete_exam(999)
        self.assertFalse(result)
    
    def test_update_nonexistent_exam(self):
        """Test updating non-existent exam"""
        result = self.db.update_exam(999, "New Subject")
        self.assertFalse(result)
    
    def test_get_nonexistent_exam(self):
        """Test getting non-existent exam"""
        exam = self.db.get_exam_by_id(999)
        self.assertIsNone(exam)
    
    def test_empty_database(self):
        """Test operations on empty database"""
        # Get all
        exams = self.db.get_all_exams()
        self.assertEqual(len(exams), 0)
        
        # Get upcoming
        upcoming = self.db.get_upcoming_exams()
        self.assertEqual(len(upcoming), 0)
        
        # Get past
        past = self.db.get_past_exams()
        self.assertEqual(len(past), 0)
        
        # Statistics
        stats = self.db.get_statistics()
        self.assertEqual(stats['total'], 0)

# ============================================
# RUN TESTS
# ============================================
def run_all_tests():
    """Run all tests with verbose output"""
    print("=" * 60)
    print("   🧪 EXAM BUDDY - TEST SUITE")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add tests
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestExamDatabase))
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
    
    return result

if __name__ == "__main__":
    run_all_tests()