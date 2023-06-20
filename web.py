from flask import Flask, render_template, request, redirect, session, g, jsonify
import requests
import psycopg2
import base64

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DATABASE_URL = 'postgres://srishti_database_user:Db6wKof7pq0kXcvTJt27Ko5AMhZoGV8a@dpg-ci7f8lenqql0ldbdt070-a.oregon-postgres.render.com/srishti_database'
GITHUB_ACCESS_TOKEN = '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'
GITHUB_REPO_NAME = 'upload_data_dev'
GITHUB_USERNAME = 'ARNAB-BOTMAS'

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
                       email TEXT)''')
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

        # Encode the profile picture as base64
        profile_picture_data = base64.b64encode(profile_picture.read()).decode('utf-8')

        # Create a JSON payload for uploading the profile picture to GitHub
        payload = {
            'message': 'Upload profile picture',
            'content': profile_picture_data,
            'branch': 'main'
        }

        # Upload the profile picture to GitHub repository
        headers = {
            'Authorization': f'Bearer {GITHUB_ACCESS_TOKEN}',
            'Content-Type': 'application/json',
        }
        file_path = f'/{username}.png'
        upload_url = f'https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO_NAME}/contents{file_path}'
        response = requests.put(upload_url, headers=headers, json=payload)

        # Check if the upload was successful
        if response.status_code == 201:
            # Insert user data into the database
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO devs (username, password, email) VALUES (%s, %s, %s)',
                           (username, password, email))
            conn.commit()

            return redirect('/login')
        else:
            return 'Failed to upload profile picture'

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
    cursor = conn.cursor()
    cursor.execute('SELECT username FROM devs')
    users = cursor.fetchall()
    return render_template('download.html', users=users)
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
    app.run(debug=True)
