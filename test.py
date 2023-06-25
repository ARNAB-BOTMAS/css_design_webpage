from flask import Flask, render_template, request, redirect, session, g, jsonify, url_for, flash, get_flashed_messages
from github import Github
import psycopg2
import base64
from url import generate_hash, user_hash
from sende_mail_automation import send_mail, dev_mail, delete_mail
import json
from functools import wraps
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DATABASE_URL = 'postgres://srishti_database_ai_user:JaYaL1A92lAp0ikj0RxGjgKihQ3etVWj@dpg-cic47a95rnuk9qb0sbc0-a.oregon-postgres.render.com/srishti_database_ai'

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
    cursor.execute('''CREATE TABLE IF NOT EXISTS dev_datas
                        (id SERIAL PRIMARY KEY,
                        hash_id_code TEXT,
                        username TEXT,
                        password TEXT,
                        email TEXT,
                        bio TEXT,
                        images BYTEA)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS person_database_sri
                      (id TEXT PRIMARY KEY,
                       name TEXT,
                       gender TEXT,
                       password TEXT,
                       email TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS API_KEY
                      (id SERIAL PRIMARY KEY,
                       api_key TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS test_user
                    (id SERIAL PRIMARY KEY,
                    name TEXT,
                    encoding BYTEA)''')
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

    cursor1.execute('SELECT images FROM dev_datas')
    cursor2.execute('SELECT username FROM dev_datas')

    data = cursor1.fetchall()
    cursor1.close()
    users = cursor2.fetchall()
    cursor2.close()
    # print(users)
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


@app.route('/apis')
def apis_page():
    # Retrieve API keys from the API_KEY table
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT api_key FROM API_KEY')
        api_keys = [row[0] for row in cursor.fetchall()]
        cursor.close()
    except Exception as e:
        return f'Error retrieving API keys: {e}', 500

    # Create a dictionary containing the API keys
    api_keys_dict = {'api_keys': api_keys}

    # Convert the dictionary to JSON
    api_keys_json = json.dumps(api_keys_dict)

    # Set the response content type as JSON
    response = app.response_class(
        response=api_keys_json,
        status=200,
        mimetype='application/json'
    )

    return response



# Registration page
@app.route(f'/{url}/register/developer', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        profile_picture = request.files['profile_picture']
        bio = request.form['bio']
        hash_id_code = user_hash(username, password)
        # print(hash_id_code)
        # print(profile_picture)  # Check if the object exists and contains data
        # print(profile_picture.filename)  # Check the filename to ensure it's not empty
        if profile_picture.filename != '':
            try:
                profile_picture_data = profile_picture.read()
                # print(profile_picture_data)
                conn = get_db()
                cursor1 = conn.cursor()
                cursor2 = conn.cursor()
                
                cursor1.execute('INSERT INTO dev_datas (hash_id_code, username, password, email, bio, images) VALUES (%s, %s, %s, %s, %s, %s)',
                    (hash_id_code, username, password, email, bio, psycopg2.Binary(profile_picture_data),))
                
                cursor1.close()
                
                cursor2.execute('INSERT INTO API_KEY (api_key) VALUES (%s)', (hash_id_code,))
                cursor2.close()
                dev_mail(username, hash_id_code, email)
                conn.commit()
                return redirect('/login')
            except Exception as e:
                return "Unable to try", 404
        else:
            return 'Image upload not successful', 404

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
        cursor.execute('SELECT hash_id_code FROM dev_datas WHERE username=%s AND password=%s',
                       (username, password))
        user = cursor.fetchone()
        hash_url = user[0]
        # print(user)
        if user:
            session['username'] = username
            return redirect(url_for('profile', hash_url=hash_url))

        return 'Invalid username or password'

    return render_template('login.html', url=url)

# Profile page
@app.route('/profile/<hash_url>')
def profile(hash_url):
    if 'username' in session:
        username = session['username']
        conn = get_db()
        cursor = conn.cursor()
        cursor1 = conn.cursor()
        cursor2 = conn.cursor()
        cursor3 = conn.cursor()
        cursor1.execute('SELECT email FROM dev_datas WHERE username=%s', (username,))
        email = cursor1.fetchone()[0]
        cursor1.close()
        cursor2.execute('SELECT images FROM dev_datas WHERE username=%s', (username,))
        rows = cursor2.fetchall()
        valid_api_key = hash_url
        images = []
        for row in rows:
            image_data = base64.b64encode(row[0]).decode('utf-8')
            images.append(image_data)

        cursor.execute("SELECT * FROM person_database_sri")
        data = cursor.fetchall()
        user_database = []
        for row in data:
            user = {
                'id': row[0],
                'name': row[1],
                'gender': row[2],
                'password': row[3],
                'email': row[4]
            }
            user_database.append(user)
        cursor.close()
        cursor3.execute('SELECT * FROM test_user')
        face_data = cursor3.fetchall()
        face_id = []
        for row1 in face_data:
            face = {
                'id': row1[0],
                'face_id': row1[1],
            }
            face_id.append(face)
        cursor3.close()
    else:
        return redirect('/login')
    
    return render_template('profile.html', username=username, images=images, email=email, user_database=user_database, valid_api_key=valid_api_key, face_id=face_id)    
    

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
    cursor1.execute('SELECT images FROM dev_datas')
    cursor2.execute('SELECT username FROM dev_datas')
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

def authenticate_api_key(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')  # Assuming the API key is passed in the request header

        # Retrieve API keys from the database or any other secure storage
        valid_api_keys = get_valid_api_keys()

        if api_key in valid_api_keys:
            return func(*args, **kwargs)  # Proceed with the API request
        else:
            return jsonify({'error': 'Invalid API key'}), 401  # Return error response for unauthorized access

    return wrapper

@app.route('/users_data', methods=['GET', 'POST'])
@authenticate_api_key
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
        elif len(users) == 0:
            return 'empty', 200
        else:
            return 'No users found', 404

    if request.method == 'POST':
        try:
            id = request.form['id']
            name = request.form['name']
            email = request.form['email']
            gender = request.form['gender']
            password = request.form['password']

            send = send_mail(id, name, gender, password, email)

            if send == True:
                sql = """INSERT INTO person_database_sri (id, name, email, gender, password)
                        VALUES (%s, %s, %s, %s, %s)"""
                cursor.execute(sql, (id, name, email, gender, password))
                conn.commit()
                return "Database updated successfully", 200
            else:
                return "Fail to send mail"
        except Exception as e:
            return f"Failed to upload data: {str(e)}", 500
        
def get_valid_api_keys():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT api_key FROM API_KEY')
        api_keys = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return api_keys
    except Exception as e:
        return []

def delete_row(username):
    conn = get_db()
    cursor = conn.cursor()

    query = "DELETE FROM dev_datas WHERE username = %s"
    cursor.execute(query, (username,))

    conn.commit()
    cursor.close()
    conn.close()

@app.route('/data', methods=['GET'])
def get_data():
    try:
        with open('intents/intents.json') as file:
            data = json.load(file)
            return jsonify(data['intents'])
    except FileNotFoundError:
        return jsonify({'error': 'File not found'})

@app.route('/data', methods=['POST'])
def save_data():
    data = request.get_json()
    try:
        with open('your_file.json', 'w') as file:
            json.dump(data, file)
            return jsonify({'message': 'Data saved successfully'})
    except:
        return jsonify({'error': 'Failed to save data'})

@app.route('/delete', methods=['POST'])
def delete_user():
    if request.method == 'POST':
        user_id = request.form['user_id']
        hash_url = request.form['url']
        conn = get_db()
        cursor1 = conn.cursor()
        cursor2 = conn.cursor()
        cursor3 = conn.cursor()
        cursor3.execute("SELECT * FROM person_database_sri WHERE id = %s", (user_id,))
        rows = cursor3.fetchall()
        users = []
        for row in rows:
            user = {
                'name': row[1],
                'email': row[4]
            }
            users.append(user)
        cursor3.close()
        if len(users) > 0:
            name = users[0]['name']
            mail = users[0]['email']
            cursor1.execute('DELETE FROM person_database_sri WHERE id = %s', (user_id,))
            cursor1.close()
            cursor2.execute('DELETE FROM test_user WHERE name = %s', (user_id,))
            cursor2.close()
            delete_mail(name, mail)
            flash('Data deleted successfully', 'success')
            session['keep_flashed_messages'] = True
        else:
            flash('User not found', 'error')

        conn.commit()
        conn.close()

    return redirect(url_for('profile', hash_url=hash_url))



@app.context_processor
def inject_flashed_messages():
    # Retrieve the flashed messages and decide whether to keep them or not
    messages = get_flashed_messages()
    if session.get('keep_flashed_messages'):
        session.pop('keep_flashed_messages')
    else:
        messages = None
    return dict(messages=messages)

@app.route(f"/{url}/about/Srishti")
def about_page():
    conn = get_db()

    cursor1 = conn.cursor()
    cursor2 = conn.cursor()

    cursor1.execute('SELECT images FROM dev_datas')
    cursor2.execute('SELECT username, bio FROM dev_datas')  # Modify the query to include the bio field

    data = cursor1.fetchall()
    cursor1.close()
    users = cursor2.fetchall()
    cursor2.close()
    
    image_user_mapping = {}  # Dictionary to store image-user mapping

    for i in range(len(users)):
        image_data = data[i][0]
        image_encoded = base64.b64encode(image_data).decode('utf-8')
        username = users[i][0]
        bio = users[i][1]  # Get the bio from the fetched data
        image_user_mapping[image_encoded] = {'username': username, 'bio': bio}  # Store both username and bio in the dictionary

    conn.close()

    return render_template('about.html', image_user_mapping=image_user_mapping, url=url)



if __name__ == '__main__':
    with app.app_context():
        create_table()
    app.run(debug=True)
