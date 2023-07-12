import psycopg2

DATABASE_URL = 'postgres://srishti_database_ai_user:JaYaL1A92lAp0ikj0RxGjgKihQ3etVWj@dpg-cic47a95rnuk9qb0sbc0-a.oregon-postgres.render.com/srishti_database_ai'

db = psycopg2.connect(DATABASE_URL)

conn = db
cursor = conn.cursor()

cursor.execute('SELECT username, email, password FROM dev_datas')
data = cursor.fetchall()

for dat in data:
    print(dat)
