from flask import Flask, render_template, request, redirect, session, g, jsonify
import psycopg2
import os
from PIL import Image
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DATABASE_URL = 'postgres://srishti_database_user:Db6wKof7pq0kXcvTJt27Ko5AMhZoGV8a@dpg-ci7f8lenqql0ldbdt070-a.oregon-postgres.render.com/srishti_database'

# Connect to the PostgreSQL database
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = psycopg2.connect(DATABASE_URL)
    return db

# Create a table to store registered users if it doesn't exist
def create_table():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS devs
                      (username TEXT PRIMARY KEY,
                       password TEXT,
                       email TEXT,
                       profile_picture BYTEA)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_data_base
                      (id INTEGER PRIMARY KEY,
                       name TEXT,
                       gender TEXT,
                       password TEXT,
                       email TEXT,
                       profile_picture BYTEA)''')
    conn.commit()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT username FROM devs')
    users = cursor.fetchall()
    return render_template('index.html', users=users)

# Registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        profile_picture = request.files['profile_picture']

        try:
            # Read the image file
            image = profile_picture.read()
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO devs (username, password, email, profile_picture) VALUES (%s, %s, %s, %s)',
                           (username, password, email, psycopg2.Binary(image)))
            conn.commit()

            return redirect('/login')
        except Exception as e:
            return 'Failed to upload profile picture'

    return render_template('register.html')

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM devs WHERE username=%s AND password=%s',
                       (username, password))
        user = cursor.fetchone()

        if user:
            session['username'] = username
            return redirect('/profile')

        return 'Invalid username or password'

    return render_template('login.html')

# Profile page
@app.route('/profile')
def profile():
    if 'username' in session:
        username = session['username']
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT email, profile_picture FROM devs WHERE username=%s', (username,))
        user = cursor.fetchone()

        if user:
            email = user[0]
            profile_picture = user[1]

            # Create a PIL Image object from the binary data
            image = Image.open(BytesIO(profile_picture))
            image.show()  # Display the image

            return render_template('profile.html', username=username, email=email)

    return redirect('/login')

if __name__ == '__main__':
    with app.app_context():
        create_table()
    app.run(debug=True, port=8000)
