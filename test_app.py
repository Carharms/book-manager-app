# test_app.py
import os  # https://docs.python.org/3/library/os.html#module-os
import tempfile  # https://docs.python.org/3/library/tempfile.html
import unittest  # https://docs.python.org/3/library/unittest.html#module-unittest

from app import app, init_db


class BookManagerTestCase(unittest.TestCase):

    def setUp(self):
        # Create a temporary database file for testing
        self.db_fd, app.config["DATABASE"] = tempfile.mkstemp()
        # Enable testing mode for Flask app
        app.config["TESTING"] = True
        self.app = app.test_client()

        # Initialize the database within the application context
        with app.app_context():
            init_db()

    def tearDown(self):
        # Close and delete the temporary database file after each test
        os.close(self.db_fd)
        os.unlink(app.config["DATABASE"])

    # -- Test Cases: Adding Books --
    def test_add_book_success(self):
        """Test successful book addition and correct success message."""
        response = self.app.post(
            "/add",
            data={
                "title": "Test Book",
                "author": "Test Author",
                "pages": "400",
                "rating": "3",
                "date_completed": "2024-07-04",
            },
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Book added", response.data)

    def test_add_book_form_displays(self):
        """Test add book form displays correctly with expected elements."""
        response = self.app.get("/add")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Add New Book", response.data)
        self.assertIn(b"Title:", response.data)

    def test_add_book_required_fields(self):
        """Test add book form contains all required input fields."""
        response = self.app.get("/add")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'name="title"', response.data)
        self.assertIn(b'name="author"', response.data)
        self.assertIn(b'name="pages"', response.data)
        self.assertIn(b'name="rating"', response.data)
        self.assertIn(b'name="date_completed"', response.data)

    # -- Test Cases: Deleting Books --
    def test_delete_book_success(self):
        """Test successful book deletion and correct success message."""
        # Add a book to delete
        self.app.post(
            "/add",
            data={
                "title": "Book to Delete",
                "author": "Delete Author",
                "pages": "200",
                "rating": "5",
                "date_completed": "2025-07-01",
            },
        )

        # Delete the book (assuming ID 1 after first add)
        response = self.app.post("/delete/1", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Book deleted", response.data)

    def test_delete_book_redirect(self):
        """Test delete book redirects to the dashboard after deletion."""
        # Add a book first
        self.app.post(
            "/add",
            data={
                "title": "Another Book",
                "author": "Another Author",
                "pages": "2400",
                "rating": "4",
                "date_completed": "2025-03-01",
            },
        )

        # Delete and check for a 302 redirect status code
        response = self.app.post("/delete/1")
        self.assertEqual(response.status_code, 302)

    # -- Test Cases: Updating Books --
    def test_update_book_success(self):
        """Test successful book update and correct success message."""
        # Add a book to update
        self.app.post(
            "/add",
            data={
                "title": "Original Title",
                "author": "Original Author",
                "pages": "300",
                "rating": "4",
                "date_completed": "2025-02-28",
            },
        )

        # Update the book
        response = self.app.post(
            "/update/1",
            data={
                "title": "Updated Title",
                "author": "Updated Author",
                "pages": "300",
                "rating": "5",
                "date_completed": "2025-03-15",
            },
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Library updated", response.data)

    def test_update_book_redirect(self):
        """Test update book redirects to the dashboard after update."""
        # Add a book first
        self.app.post(
            "/add",
            data={
                "title": "Redirect Test Book",
                "author": "Redirect Author",
                "pages": "350",
                "rating": "1",
                "date_completed": "2025-04-01",
            },
        )

        # Update and check for a 302 redirect status code
        response = self.app.post(
            "/update/1",
            data={
                "title": "Redirected Title",
                "author": "Redirected Author",
                "pages": "350",
                "rating": "6",
                "date_completed": "2025-05-01",
            },
        )

        self.assertEqual(response.status_code, 302)

    # Additional basic tests
    def test_dashboard_loads(self):
        """Test dashboard loads correctly with the main heading."""
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"My Digital Library", response.data)


if __name__ == "__main__":
    unittest.main()
