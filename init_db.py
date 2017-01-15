from app import db, models

db.create_all()

user_1 = models.User(name='Henrik')
user_2 = models.User(name='Mikaela')

db.session.add(user_1)
db.session.add(user_2)

db.session.commit()
