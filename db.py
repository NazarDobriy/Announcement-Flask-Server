import sqlite3

conn = sqlite3.connect("announcements.sqlite")

cursor = conn.cursor()
sql_query = """ CREATE TABLE announcement (
    id integer PRIMARY KEY,
    title text NOT NULL,
    description text NOT NULL,
    date datetime DEFAULT CURRENT_TIMESTAMP
) """
cursor.execute(sql_query)
