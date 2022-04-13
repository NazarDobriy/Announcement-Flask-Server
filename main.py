from flask import Flask, request, make_response, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://iaulxgamotslnv:995d75631de839c0f838765e4bc286f42daca7f77a5f3c8d1e64e66a2accdf15@ec2-99-80-170-190.eu-west-1.compute.amazonaws.com:5432/da3iqde2em552k"
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
            abort(400, "You miss title")

        elif not self.model_announcement.description:
            abort(400, "You miss description")

        else:
            announcement = Announcement(title=self.model_announcement.title, description=self.model_announcement.description)
            db.session.add(announcement)
            db.session.commit()
            return make_response(jsonify({"message": "An announcement was created"}, 200))

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
            announcement = Announcement.query.get(current_id)

            if not announcement:
                abort(404, "Announcement with this id isn't found")

            announcement_json = {
                "title": announcement.title,
                "description": announcement.description,
                "date": announcement.date.strftime('%d.%m.%y')
            }
            return announcement_json
        abort(404)

    def update(self, current_id=None):
        if current_id:
            announcement = Announcement.query.get(current_id)
            new_announcement_data = request.get_json()

            if new_announcement_data.get('title'):
                announcement.title = new_announcement_data.get('title')

            if new_announcement_data.get('description'):
                announcement.description = new_announcement_data.get('description')

            db.session.commit()

            return make_response(jsonify({"message": "An announcement was updated"}, 200))
        abort(404, "Announcement with this id is not found")

    def delete(self, current_id=None):
        if current_id:
            selected_announcement = Announcement.query.get(current_id)
            db.session.delete(selected_announcement)
            db.session.commit()
            return jsonify({"message": "Announcement was deleted"}, 200)
        abort(404, "Announcement with this id is not found")


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
