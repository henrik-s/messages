import datetime
import json

from app import app, db, util
from flask import jsonify, request, abort
from sqlalchemy import desc
from app.models import User, Message
from functools import wraps


def user_must_exist(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not util.user_exists(kwargs['username']):
            abort(404, 'User does not exists')
        return func(*args, **kwargs)
    return decorated_function


@app.route('/user/<string:username>', methods=['PUT'])
def create_user(username):
    if util.user_exists(username):
        return ""

    new_user = User(name=username)
    db.session.add(new_user)
    db.session.commit()

    return '', 201


@app.route('/user/<string:username>/messages', methods=['POST'])
@user_must_exist
def send_message(username):
    json_data = request.get_json()
    required_data = ['sender', 'message']

    if json_data is None:
        return json.dumps(required_data), 400

    missing_params = [x for x in required_data if x not in json_data]
    print json_data
    if missing_params:
        return json.dumps(missing_params), 400

    sender_name = json_data['sender']
    if sender_name is None or not util.user_exists(sender_name):
        abort(404, 'Could not find sender')

    message = json_data['message']

    newMessage = Message(sender_id=util.get_user_id(sender_name),
                         receiver_id=util.get_user_id(username),
                         message=message,
                         unread=True,
                         timestamp=datetime.datetime.utcnow())

    db.session.add(newMessage)
    db.session.commit()
    return '', 200


@app.route('/user/<string:username>/messages/unread', methods=['GET'])
@user_must_exist
def get_unread_messages(username):
    user = util.get_user_by_username(username)
    unread_messages = []

    for message in user.received:
        if not message.unread:
            continue

        message.unread = False
        unread_messages.append(util.get_message_repr_as_dict(message))

    db.session.commit()

    return jsonify(unread_messages)


@app.route('/user/<string:username>/messages', methods=['DELETE'])
@user_must_exist
def delete_messages(username):
    ids = request.args.getlist('id')
    if not ids:
        return json.dumps(['id']), 400

    try:
        int_ids = map(int, ids)
    except:
        return '', 400

    user = util.get_user_by_username(username)
    deleted_msgs = list()
    for message in user.received:
        if message.id in int_ids:
            deleted_msgs.append(message.id)
            db.session.delete(message)

    db.session.commit()
    return jsonify(deleted_msgs), 200


@app.route('/user/<string:username>/messages', methods=['GET'])
@user_must_exist
def get_messages_for_interval(username):
    missing_params = [x for x in ['start', 'stop'] if x not in request.args]
    if missing_params:
        return json.dumps(missing_params), 400

    try:
        start = abs(int(request.args.get('start')))
        stop = abs(int(request.args.get('stop')))

    except ValueError:
        return '', 400

    rows = stop - start + 1

    messages = Message.query.join(Message.receiver, aliased=True) \
        .filter_by(name=username) \
        .order_by(desc(Message.timestamp)) \
        .offset(start).limit(rows)

    return jsonify(map(util.get_message_repr_as_dict, messages))
