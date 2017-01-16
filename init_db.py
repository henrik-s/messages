import os

from app import db, models


def drop_and_create():
    try:
        os.remove('app.db')
    except OSError:
        pass

    db.create_all()

    user_1 = models.User(name='henrik')
    user_2 = models.User(name='mikaela')

    db.session.add(user_1)
    db.session.add(user_2)

    db.session.commit()


if __name__ == '__main__':
    drop_and_create()
    print 'New database created'
