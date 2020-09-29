from datetime import datetime

from app import db
from app.models.searchable_mixin import SearchableMixin


class Post(SearchableMixin,  db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    __searchable__ = ['body']

    def __repr__(self):
        return '<Post {}>'.format(self.body)
