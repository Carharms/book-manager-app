# test_app.py
import unittest # https://docs.python.org/3/library/unittest.html#module-unittest
import tempfile # https://docs.python.org/3/library/tempfile.html
import os # https://docs.python.org/3/library/os.html#module-os
from app import app, init_db

class BookManagerTestCase(unittest.TestCase):
    
    def setUp(self):
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        self.app = app.test_client()
        
        with app.app_context():
            init_db()
    
    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])
    
    # -- Test Cases: Adding Books --
    def test_add_book_success(self):
        """Test successful book addition"""
        response = self.app.post('/add', data={
            'title': 'Test Book',
            'author': 'Test Author',
            'pages': '400',
            'rating': '3',
            'date_completed': '2024-07-04'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Book added - test successful', response.data)
    
    def test_add_book_form_displays(self):
        """Test add book form displays correctly"""
        response = self.app.get('/add')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Add New Book', response.data)
        self.assertIn(b'Title:', response.data)
    
    def test_add_book_required_fields(self):
        """Test add book form has required fields"""
        response = self.app.get('/add')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'name="title"', response.data)
        self.assertIn(b'name="author"', response.data)
        self.assertIn(b'name="pages"', response.data)
        self.assertIn(b'name="rating"', response.data)
        self.assertIn(b'name="date_completed"', response.data)
    
    # -- Test Cases: Deleting Books --
    def test_delete_book_success(self):
        """Test successful book deletion"""
        # First add a book
        self.app.post('/add', data={
            'title': 'Test Book',
            'author': 'Test Author',
            'pages': '200',
            'rating': '5',
            'date_completed': '2025-07-01'
        })
        
        # Restore database
        response = self.app.post('/delete/1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Book deleted - test successful', response.data)
    
    def test_delete_book_redirect(self):
        """Test delete book redirects to dashboard"""
        # Add a book first
        self.app.post('/add', data={
            'title': 'Test Book',
            'author': 'Test Author',
            'pages': '2400',
            'rating': '4',
            'date_completed': '2025-03-01'
        })
        
        # Delete and check redirect
        response = self.app.post('/delete/1')
        self.assertEqual(response.status_code, 302)
    
    # -- Test Cases: Updating Books --
    def test_update_book_success(self):
        """Test successful book update"""
        self.app.post('/add', data={
            'title': 'Original Title',
            'author': 'Original Author',
            'pages': '300',
            'rating': '4',
            'date_completed': '2025-02-28'
        })
        
        # Update the book
        response = self.app.post('/update/1', data={
            'title': 'Updated Title',
            'author': 'Updated Author',
            'pages': '300',
            'rating': '5',
            'date_completed': '2025-03-15'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Book updated - test successful', response.data)
    
    def test_update_book_form_displays(self):
        """Test update book form displays with existing data"""
        # Add a book first
        self.app.post('/add', data={
            'title': 'Test Book',
            'author': 'Test Author',
            'pages': '200',
            'rating': '5',
            'date_completed': '2025-05-15'
        })
        
        # Get update form
        response = self.app.get('/update/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Update Book', response.data)
        self.assertIn(b'Test Book', response.data)
    
    def test_update_book_redirect(self):
        """Test update book redirects to dashboard"""
        # Add a book first
        self.app.post('/add', data={
            'title': 'Test Book',
            'author': 'Test Author',
            'pages': '350',
            'rating': '1',
            'date_completed': '2025-04-01'
        })
        
        # Update and check redirect
        response = self.app.post('/update/1', data={
            'title': 'Updated Title',
            'author': 'Updated Author',
            'pages': '350',
            'rating': '6',
            'date_completed': '2025-05-01'
        })
        
        self.assertEqual(response.status_code, 302)
    
    # Additional basic tests
    def test_dashboard_loads(self):
        """Test dashboard loads correctly"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Reading Dashboard', response.data)

if __name__ == '__main__':
    unittest.main()