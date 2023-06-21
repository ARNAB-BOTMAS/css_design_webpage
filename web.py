from flask import Flask, render_template, request, redirect, session, g, jsonify
from github import Github
import psycopg2
import base64
from url import generate_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DATABASE_URL = 'postgres://srishti_database_sb6x_user:GesdgP3MvK6VJWc3IKusqx3WpgLvjk31@dpg-ci9dfudph6ekmcka4cvg-a.oregon-postgres.render.com/srishti_database_sb6x'

url = generate_hash()

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
    cursor.execute('''CREATE TABLE IF NOT EXISTS person_database_sri
                      (id TEXT PRIMARY KEY,
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

    return render_template('index.html', image_user_mapping=image_user_mapping, url=url)

@app.route('/download')
def download():
    return redirect(f"/{url}/download/Srishti")

@app.route('/register')
def register():
    return redirect(f"/{url}/register/developer")

@app.route('/login')
def login():
    return redirect(f"/{url}/login/developer")

@app.route('/about')
def about():
    return redirect(f"/{url}/about/Srishti")





# Registration page
@app.route(f'/{url}/register/developer', methods=['GET', 'POST'])
def register_page():
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
            return redirect(f'/{url}/login')
        except Exception as e:
            return f'Image upload not successfully {e}', 404

    return render_template('register.html', url=url)


# Login page
@app.route(f'/{url}/login/developer', methods=['GET', 'POST'])
def login_page():
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
            return redirect('/developer/profile')

        return 'Invalid username or password'

    return render_template('login.html', url=url)

# Profile page
@app.route('/developer/profile')
def profile():
    if 'username' in session:
        username = session['username']
        conn = get_db()
        cursor1 = conn.cursor()
        cursor2 = conn.cursor()
        cursor1.execute('SELECT email FROM devs WHERE username=%s', (username,))
        email = cursor1.fetchone()[0]
        cursor1.close()
        cursor2.execute('SELECT images FROM devs WHERE username=%s', (username,))
        rows = cursor2.fetchall()

        images = []
        for row in rows:
            image_data = base64.b64encode(row[0]).decode('utf-8')
            images.append(image_data)
        
        return render_template('profile.html', username=username, images=images, email=email)

    return redirect(f'/{url}/login')

# Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

@app.route(f'/{url}/download/Srishti')
def download_page():
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

    return render_template('download.html', image_user_mapping=image_user_mapping, url=url)
# Users data API
@app.route('/users_data', methods=['GET', 'POST'])
def handle_users():
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'GET':
        cursor.execute("SELECT * FROM person_database_sri")
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
        try:
            id = request.form['id']
            name = request.form['name']
            email = request.form['email']
            gender = request.form['gender']
            password = request.form['password']

            sql = """INSERT INTO person_database_sri (id, name, email, gender, password)
                     VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(sql, (id, name, email, gender, password))
            conn.commit()

            return "Database updated successfully", 201
        except Exception as e:
            return f"Failed to upload data: {str(e)}", 500

def delete_row(username):
    conn = get_db()
    cursor = conn.cursor()

    query = "DELETE FROM devs WHERE username = %s"
    cursor.execute(query, (username,))

    conn.commit()
    cursor.close()
    conn.close()

@app.route('/delete/<username>', methods=['GET'])
def delete_user(username):
    delete_row(username)
    return f"Deleted user with username: {username}"

if __name__ == '__main__':
    with app.app_context():
        create_table()
    app.run(debug=True, port=8000)
