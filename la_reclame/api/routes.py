from flask import request
from passlib.hash import sha256_crypt
from la_reclame.models import Users, Items
from la_reclame.api import api
from la_reclame import db
from utils import picturesDB


@api.route('/auth/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    if None in [username, password]:
        return dict(status='error', error='Not all data was given.')

    user = Users.query.filter_by(username=username).first()

    if user is None or not sha256_crypt.verify(password, user.password):
        return dict(status='error', error='Username or password is incorrect.')

    return dict(status='ok')


@api.route('/auth/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')

    if None in [username, password, email]:
        return dict(status='error', error='Not all data was given.')

    if Users.query.filter_by(username=username).first() is not None:
        return dict(status='error', error='Username is already taken.')

    if Users.query.filter_by(email=email).first() is not None:
        return dict(status='error', error='Email is already taken.')

    user = Users(username=username, email=email, password=sha256_crypt.hash(password))
    db.session.add(user)
    db.session.commit()

    return dict(status='ok')


@api.route('/items', methods=['POST'])
def get_items():
    items = [item.serialize() for item in Items.query.all()]
    return dict(status='ok', items=items)


@api.route('/add/item', methods=['POST'])
def add_item():
    user_id = request.form.get('user_id')
    title = request.form.get('title')
    description = request.form.get('description')

    if None in [user_id, title, description]:
        return dict(status='error', error='Not all data was given.')

    item = Items(user_id=user_id, title=title, description=description)
    db.session.add(item)
    db.session.commit()

    return dict(status='ok')


@api.route('/update/profile-picture', methods=['POST'])
def update_profile_picture():
    user_id = request.form.get('user_id')
    encoded_image = request.form.get('encodedImage')

    if None in [user_id, encoded_image]:
        return dict(status='error', error='Not all data was given.')

    user = Users.query.get(user_id)

    if user is None:
        return dict(status='error', error='User with such ID does not exist.')

    filename = picturesDB.add_picture_from_app('profile-pictures', encoded_image)
    user.picture = filename
    db.session.commit()

    return 'a'
