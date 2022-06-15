from itsdangerous import URLSafeTimedSerializer
from flask import request, url_for, send_file
from passlib.hash import sha256_crypt
from la_reclame.models import Users, Items, Categories, Reviews, Ratings
from la_reclame.api import api
from la_reclame import db
from utils import picturesDB, send_email, PriceTypes
from urllib.parse import quote
from os import getenv
import base64
import ast

url_serializer = URLSafeTimedSerializer(getenv('SECRET_KEY'))


@api.route('/auth/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    if None in [username, password]:
        return dict(status='error', error='Not all data was given.')

    user = Users.query.filter_by(username=username).first()

    if user is None or not sha256_crypt.verify(password, user.password):
        return dict(status='error', error='Username or password is incorrect.')

    if user.is_active is False:
        return dict(status='error', error='User was not activated yet.')

    return dict(status='ok', user=user.serialize())


@api.route('/auth/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    barcode = request.form.get('barcode')

    if None in [username, password, barcode]:
        return dict(status='error', error='Not all data was given.')

    if Users.query.filter_by(username=username).first() is not None:
        return dict(status='error', error='Username is already taken.')

    if Users.query.filter_by(barcode=barcode).first() is not None:
        return dict(status='error', error='Barcode is already taken.')

    user = Users(username=username, barcode=barcode, password=sha256_crypt.hash(password))
    db.session.add(user)
    db.session.commit()

    token = url_serializer.dumps(barcode, salt=getenv('SECRET_KEY_EMAIL_CONFIRM'))
    token_link = url_for('auth.confirm_email', token=token, _external=True)

    send_email(barcode + '@astanait.edu.kz', token_link)

    return dict(status='ok')


@api.route('/items', methods=['POST'])
def get_items():
    user_id = request.form.get('user_id', '')
    if user_id != '':
        items_list = Items.query.filter_by(user_id=user_id)
    else:
        items_list = Items.query

    search = request.form.get('search', '')
    if search != '':
        title_like = Items.title.like("%{}%".format(search))
        description_like = Items.description.like("%{}%".format(search))
        items_list = items_list.filter(title_like | description_like)

    filter_by = request.form.get('filter_by', '')
    if filter_by != '':
        items_list = items_list.filter_by(category_id=filter_by)

    items_list = items_list.order_by(Items.id.desc()).all()

    return dict(status='ok', items=[item.serialize() for item in items_list])


@api.route('/get/item', methods=['POST'])
def get_item():
    item_id = request.form.get('item_id')

    if None in [item_id]:
        return dict(status='error', error='Not all data was given.')

    item = Items.query.get(item_id)

    if item is None:
        return dict(status='error', error='Item not found.')

    return dict(status='ok', item=item.serialize())


@api.route('/add/item', methods=['POST'])
def add_item():
    user_id = int(request.form.get('user_id'))
    category_id = int(request.form.get('category_id'))
    title = request.form.get('title')
    description = request.form.get('description')
    price_type = request.form.get('price_type')
    price = request.form.get('price')
    pictures = request.form.get('pictures')

    pictures = ast.literal_eval(pictures)

    if len(pictures) != 0:
        main_picture = pictures[0]
        pictures = pictures[1:]

    main_picture = picturesDB.add_picture_from_app('item-pictures', main_picture)
    pictures = [picturesDB.add_picture_from_app('item-pictures', picture) for picture in pictures]

    if None in [user_id, title, description, category_id, price_type] or price_type == 'fixed' and price is None:
        return dict(status='error', error='Not all data was given.')

    price = int(price) if price is not None else 0

    if Users.query.get(user_id) is None:
        return dict(status='error', error='User with such id not found.')

    if Categories.query.get(category_id) is None:
        return dict(status='error', error='Category with such id not found.')

    item = Items(user_id=user_id, title=title, description=description, category_id=category_id,
                 price_type=PriceTypes[price_type], price=price, main_picture=main_picture, pictures=','.join(pictures))
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

    return dict(status='ok')


@api.route('/get-image', methods=['POST'])
def get_item_image():
    table = request.form.get('table')
    filename = request.form.get('filename')

    try:
        filenames = ast.literal_eval(filename)
        filenames = [quote(base64.b64encode(open(picturesDB.get_picture_path(table, filename), 'rb').read()), safe='')
                     for filename in filenames]
        return dict(status='ok', image=filenames)
    except:
        path = picturesDB.get_picture_path(table, filename)
        image_base64 = base64.b64encode(open(path, 'rb').read())
        return dict(status='ok', image=quote(image_base64, safe=''))


@api.route('/categories', methods=['POST'])
def get_categories():
    categories = [category.serialize() for category in Categories.query.order_by(Categories.id.asc()).all()]

    return dict(status='ok', categories=categories)


@api.route('/<item_id>/reviews', methods=['POST'])
def item_reviews(item_id: int):
    reviews = [review.serialize() for review in Reviews.query.filter_by(item_id=item_id).order_by(Reviews.id.desc()).all()]
    return dict(status='ok', reviews=reviews)


@api.route('/update-user-info', methods=['POST'])
def update_user_info():
    user_id = request.form.get('user_id')
    username = request.form.get('username')
    bio = request.form.get('bio')
    password = request.form.get('password')

    if user_id is None:
        return dict(status='error', error='Not all data was given.')

    user = Users.query.get(user_id)

    if user is None:
        return dict(status='error', error='User with such id not found.')

    username = user.username if username in [None, ''] else username
    bio = user.bio if bio in [None, ''] else bio
    password = user.password if password in [None, ''] else sha256_crypt.hash(password)

    if username != user.username and Users.query.filter_by(username=username).first() is not None:
        return dict(status='error', error='%s already taken!' % username)

    user.username = username
    user.bio = bio
    user.password = password

    db.session.commit()

    return dict(status='ok')


@api.route('/get-user-info', methods=['POST'])
def get_user_info():
    user_id = request.form.get('user_id')

    user = Users.query.get(user_id)

    filename = user.picture
    if filename is not None:
        table = 'profile-pictures'
        path = picturesDB.get_picture_path(table, filename)
        image_base64 = base64.b64encode(open(path, 'rb').read())
        image = quote(image_base64, safe='')
    else:
        image = ''

    return dict(id=user.id, username=user.username, image=image)


@api.route('/add/review', methods=['POST'])
def add_review():
    user_id = request.form.get('user_id')
    item_id = request.form.get('item_id')
    title = request.form.get('title')
    description = request.form.get('description')
    rating_score = int(request.form.get('rating'))

    print(rating_score)

    review = Reviews(item_id=item_id, user_id=user_id, title=title, description=description, rating=rating_score)

    item = Items.query.get(item_id)
    rating = Ratings.query.filter_by(user_id=item.user_id).first()

    if rating is None:
        rating = Ratings(user_id=item.user_id, rating=rating_score, review_count=1)
        db.session.add(rating)
    else:
        rating.rating += rating_score
        rating.review_count += 1

    db.session.add(review)
    db.session.commit()

    return dict(status='ok')
