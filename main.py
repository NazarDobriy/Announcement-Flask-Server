from flask import Flask, request, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///announcement.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Announcement(db.Model):

    def __init__(self, title=None, description=None):
        self.title = title
        self.description = description

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)


class AnnouncementController(object):

    def __init__(self, model_announcement=Announcement()):
        self.model_announcement = model_announcement

    def create(self, announcement_data=None):
        self.model_announcement.title = announcement_data.get('title')
        self.model_announcement.description = announcement_data.get('description')

        if not self.model_announcement.title:
            return make_response(jsonify({"message": "You miss title"}, 400))

        elif not self.model_announcement.description:
            return make_response(jsonify({"message": "You miss description"}, 400))

        else:
            announcement = Announcement(title=self.model_announcement.title, description=self.model_announcement.description)
            try:
                db.session.add(announcement)
                db.session.commit()
                return make_response(jsonify({"message": "An announcement was created"}, 200))
            except:
                return make_response(
                    jsonify({"message": "An error occurred while adding the announcement in the database"}, 400))

    def get_all_announcements(self):
        announcements = Announcement.query.order_by(Announcement.date.desc()).all()
        announcements_arr = []

        for announcement in announcements:
            announcements_arr.append({
                "id": announcement.id,
                "title": announcement.title,
                "description": announcement.description,
                "date": announcement.date.strftime('%d.%m.%Y')
            })

        return jsonify(announcements_arr)

    def get_announcement_by_id(self, current_id=None):
        if current_id:
            try:
                announcement = Announcement.query.get(current_id)

                if not announcement:
                    raise Exception("Don't exist announcement with this id")

                announcement_json = {
                    "title": announcement.title,
                    "description": announcement.description,
                    "date": announcement.date.strftime('%d.%m.%y')
                }

                return announcement_json
            except Exception as e:
                return make_response(jsonify({"message": str(e)}, 404))
        return make_response(jsonify({"message": "Announcement with this id is not found"}, 404))

    def update(self, current_id=None):
        if current_id:
            announcement = Announcement.query.get(current_id)
            new_announcement_data = request.get_json()

            if new_announcement_data.get('title'):
                announcement.title = new_announcement_data.get('title')

            if new_announcement_data.get('description'):
                announcement.title = new_announcement_data.get('description')

            db.session.commit()

            return make_response(jsonify({"message": "An announcement was updated"}, 200))
        return jsonify({"message": "Announcement with this id is not found"}, 404)

    def delete(self, current_id=None):
        if current_id:
            selected_announcement = Announcement.query.get(current_id)
            try:
                db.session.delete(selected_announcement)
                db.session.commit()
            except:
                return make_response(
                    jsonify({
                        "message": "An error occurred while deleting the announcement by id in the database"
                    }, 400)
                )
            return jsonify({"message": "Announcement was deleted"}, 200)
        return jsonify({"message": "Announcement with this id is not found"}, 404)


@app.route('/create-announcement', methods=['POST'])
def create_announcement():
    announcement_data = request.get_json()
    return AnnouncementController().create(announcement_data)


@app.route('/all-announcements', methods=['GET'])
def all_announcements():
    return AnnouncementController().get_all_announcements()


@app.route('/announcement/<int:id>', methods=['GET'])
def announcement(id):
    return AnnouncementController().get_announcement_by_id(id)


@app.route('/update-announcement/<int:id>', methods=['PUT'])
def update_announcement(id):
    return AnnouncementController().update(id)


@app.route('/delete-announcement/<int:id>', methods=['DELETE'])
def delete_announcement(id):
    return AnnouncementController().delete(id)


if __name__ == "__main__":
    app.run(debug=True)
