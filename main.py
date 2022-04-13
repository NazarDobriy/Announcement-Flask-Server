import sqlite3
from flask import Flask, request, jsonify, abort
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


def db_connection():
    conn = None
    try:
        conn = sqlite3.connect('announcements.sqlite')
    except sqlite3.error as e:
        print(e)
    return conn


@app.route('/create-announcement', methods=['POST'])
def create_announcement():
    conn = db_connection()
    announcement_data = request.get_json()

    new_title = announcement_data.get('title')
    new_description = announcement_data.get('description')

    sql = """ INSERT INTO announcement (title, description) VALUES (?, ?) """

    conn.execute(sql, (new_title, new_description))
    conn.commit()

    return jsonify({"message": "An announcement was created"}, 200)


@app.route('/all-announcements', methods=['GET'])
def all_announcements():
    announcements = None

    conn = db_connection()
    cursor = conn.execute("SELECT * FROM announcement ORDER BY date DESC")

    announcements = [
        dict(id=row[0], title=row[1], description=row[2], date=row[3])
        for row in cursor.fetchall()
    ]

    if announcements is not None:
        return jsonify(announcements)


@app.route('/announcement/<int:id>', methods=['GET'])
def announcement(id):
    announcement = {}

    conn = db_connection()
    cursor = conn.execute("SELECT * FROM announcement WHERE id == ?", (id,))

    rows = cursor.fetchall()

    if not len(rows):
        abort(404)

    for r in rows:
        announcement['title'] = r[1]
        announcement['description'] = r[2]
        announcement['date'] = r[3]

    if announcement is not None:
        return jsonify(announcement)


@app.route('/update-announcement/<int:id>', methods=['PUT'])
def update_announcement(id):
    conn = db_connection()

    sql = """ UPDATE announcement
        SET title = ?,
        description = ?
        WHERE id = ?
     """

    announcement = {}

    new_announcement_data = request.get_json()

    if new_announcement_data.get('title'):
        announcement["title"] = new_announcement_data.get('title')

    if new_announcement_data.get('description'):
        announcement["description"] = new_announcement_data.get('description')

    updated_announcement = {
        "id": id,
        "title": announcement["title"],
        "description": announcement["description"]
    }

    cursor = conn.execute("SELECT * FROM announcement ORDER BY date DESC")

    rows = cursor.fetchall()

    if not len(rows):
        abort(404)

    conn.execute(sql, (announcement["title"], announcement["description"], id))
    conn.commit()

    return jsonify(updated_announcement)


@app.route('/delete-announcement/<int:id>', methods=['DELETE'])
def delete_announcement(id):
    conn = db_connection()

    sql = """ DELETE FROM announcement WHERE id = ? """

    conn.execute(sql, (id,))
    conn.commit()

    return jsonify({"message": "Announcement was deleted"}, 200)


if __name__ == "__main__":
    app.run(debug=True)
