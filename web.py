from flask import Flask, render_template, request, redirect, session, g, jsonify
from github import Github
import psycopg2
import os
import uploads_pro
import base64

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DATABASE_URL = 'postgres://srishti_database_sb6x_user:GesdgP3MvK6VJWc3IKusqx3WpgLvjk31@dpg-ci9dfudph6ekmcka4cvg-a.oregon-postgres.render.com/srishti_database_sb6x'


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
                       images BYTEA)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS person_database
                      (id INTEGER PRIMARY KEY,
                       name TEXT,
                       gender TEXT,
                       password TEXT,
                       email TEXT)''')
    conn.commit()


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    conn = get_db()
    cursor1 = conn.cursor()
    cursor2 = conn.cursor()
    cursor1.execute('SELECT images FROM devs')
    cursor2.execute('SELECT username FROM devs')
    data = cursor1.fetchall()
    cursor1.close()
    users = cursor2.fetchall()
    cursor2.close()
    print(users)
    image_user_mapping = {}  # Dictionary to store image-user mapping

    for i in range(len(users)):
        image_data = data[i][0]
        image_encoded = base64.b64encode(image_data).decode('utf-8')
        username = users[i][0]
        image_user_mapping[image_encoded] = username

    conn.close()

    return render_template('index.html', image_user_mapping=image_user_mapping)




# Registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        profile_picture = request.files['profile_picture']
        try:
            profile_picture_data = profile_picture.read()
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO devs (username, password, email, images) VALUES (%s, %s, %s, %s)',
                            (username, password, email, psycopg2.Binary(profile_picture_data)))
            conn.commit()
            return redirect('/login')
        except Exception as e:
            return f'Image upload not successfully {e}', 404

    return render_template('register.html')


# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username and password match in the database
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM devs WHERE username=%s AND password=%s',
                       (username, password))
        user = cursor.fetchone()
        print(user)
        if user:
            session['id'] = username
            return redirect('/')

        return 'Invalid username or password'

    return render_template('login.html')

# Profile page
@app.route('/profile')
def profile():
    if 'username' in session:
        username = session['username']
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT email FROM devs WHERE username=%s', (username,))
        email = cursor.fetchone()[0]
        
        return render_template('profile.html', username=username, email=email)

    return redirect('/login')

# Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

@app.route('/download')
def download():
    conn = get_db()
    cursor1 = conn.cursor()
    cursor2 = conn.cursor()
    cursor1.execute('SELECT images FROM devs')
    cursor2.execute('SELECT username FROM devs')
    data = cursor1.fetchall()
    cursor1.close()
    users = cursor2.fetchall()
    cursor2.close()

    image_user_mapping = {}  # Dictionary to store image-user mapping

    for i in range(len(users)):
        image_data = data[i][0]
        image_encoded = base64.b64encode(image_data).decode('utf-8')
        username = users[i][0]
        image_user_mapping[image_encoded] = username

    conn.close()

    return render_template('download.html', image_user_mapping=image_user_mapping)
# Users data API
@app.route('/users_data', methods=['GET', 'POST'])
def handle_users():
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'GET':
        cursor.execute("SELECT * FROM person_database")
        rows = cursor.fetchall()

        users = []
        for row in rows:
            user = {
                'id': row[0],
                'name': row[1],
                'gender': row[2],
                'password': row[3],
                'email': row[4]
            }
            users.append(user)

        if len(users) > 0:
            return jsonify(users)
        else:
            return 'No users found', 404
        
    if request.method == 'POST':
        id = request.form['id']
        name = request.form['name']
        email = request.form['email']
        gender = request.form['gender']
        password = request.form['password']

        sql = """INSERT INTO person_database (id, name, email, gender, password)
                 VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(sql, (id, name, email, gender, password))
        conn.commit()

        return f"Database updated successfully", 201

if __name__ == '__main__':
    with app.app_context():
        create_table()
    app.run(debug=True, port=8000)
