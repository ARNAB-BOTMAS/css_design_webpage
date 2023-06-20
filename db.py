import sqlite3

conn = sqlite3.connect("dev.sqlite")

cursor = conn.cursor()
sql_query1 = """ 
CREATE TABLE devs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100),
    email VARCHAR(100),
    password VARCHAR(100),
    image_path VARCHAR(200)
);
"""
cursor.execute(sql_query1)