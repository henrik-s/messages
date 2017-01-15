from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    unread = db.Column(db.Boolean())
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)

    sender = db.relationship(User, foreign_keys=[sender_id], backref='sent')
    receiver = db.relationship(User, foreign_keys=[receiver_id], backref='received', lazy='dynamic', uselist=True)
