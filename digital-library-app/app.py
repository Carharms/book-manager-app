from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'personal-library'

DATABASE = 'books.db'

def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection

def init_db():
    with get_db() as connection:
        connection.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                pages INTEGER NOT NULL,
                rating INTEGER NOT NULL,
                date_completed TEXT NOT NULL
            )
        ''')
        connection.commit()

# -- General Dashboard Endpoint --
    def dashboard():
        with get_db() as connection:
            books = connection.execute('SELECT * FROM books ORDER BY id DESC').fetchall()
            highest_rated = connection.execute('SELECT * FROM books ORDER BY rating DESC LIMIT 10').fetchall()
        
        total_books = len(books)
        reading_goal = 24
        
        return render_template('dashboard.html', 
                            books=books,
                            highest_rated=highest_rated,
                            total_books=total_books,
                            reading_goal=reading_goal)

# -- Add Book Endpoint --
@app.route('/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        pages = int(request.form['pages'])
        rating = int(request.form['rating'])
        date_completed = request.form['date_completed']
        
        with get_db() as connection:
            connection.execute('''
                INSERT INTO books (title, author, pages, rating, date_completed)
                VALUES (?, ?, ?, ?, ?)
            ''', (title, author, pages, rating, date_completed))
            connection.commit()
        
        flash('Book added')
        return redirect(url_for('dashboard')) 
    return render_template('add_book.html')

# -- Delete Book Selection Endpoint --
@app.route('/delete')
def delete_book_selection():
    with get_db() as connection:
        books = connection.execute('SELECT * FROM books ORDER BY title').fetchall()
    return render_template('delete_book.html', books=books)

# -- Delete Book Endpoint --
@app.route('/delete/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    with get_db() as connection:
        connection.execute('DELETE FROM books WHERE id = ?', (book_id,))
        connection.commit()
    
    flash('Book deleted')
    return redirect(url_for('dashboard'))

# -- Update Book Selection Endpoint --
@app.route('/update')
def update_book_selection():
    with get_db() as connection:
        books = connection.execute('SELECT * FROM books ORDER BY title').fetchall()
    return render_template('update_book_selection.html', books=books)

# -- Update Book Endpoint --
@app.route('/update/<int:book_id>', methods=['GET', 'POST'])
def update_book(book_id):
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        pages = int(request.form['pages'])
        rating = int(request.form['rating'])
        date_completed = request.form['date_completed']
        
        with get_db() as connection:
            connection.execute('''
                UPDATE books 
                SET title = ?, author = ?, pages = ?, rating = ?, date_completed = ?
                WHERE id = ?
            ''', (title, author, pages, rating, date_completed, book_id))
            connection.commit()
        
        flash('Library updated')
        return redirect(url_for('dashboard'))
    
    with get_db() as connection:
        book = connection.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
    
    return render_template('update_book.html', book=book)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)