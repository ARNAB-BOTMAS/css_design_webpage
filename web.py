from flask import Flask, render_template, request, redirect, session, g
import psycopg2

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

        # Save the profile picture with the user id as the file name
        profile_picture.save(f'static/{username}.png')

        # Insert user data into the database
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO devs (username, password, email) VALUES (%s, %s, %s)',
                       (username, password, email))
        conn.commit()

        return redirect('/login')
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

if __name__ == '__main__':
    with app.app_context():
        create_table()
    app.run(debug=True)
