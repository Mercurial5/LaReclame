from la_reclame import db
from datetime import datetime
from utils import PriceTypes


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    bio = db.Column(db.Text)
    password = db.Column(db.String(255), nullable=False)
    barcode = db.Column(db.Integer, nullable=False, unique=True)
    telegram = db.Column(db.String(255), default=None)
    registered = db.Column(db.DATETIME, nullable=False, default=datetime.now)
    is_active = db.Column(db.Boolean, nullable=False, default=False)
    picture = db.Column(db.String(255))

    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'bio': self.bio,
            'rating': self.get_rating(),
            'password': self.password,
            'barcode': self.barcode,
            'telegram': self.telegram,
            'registered': str(self.registered),
            'is_active': self.is_active,
            'picture': self.picture
        }

    def get_rating(self):
        rating = Ratings.query.filter_by(user_id=self.id).first()

        if rating is None or rating.review_count == 0:
            rating = 0.0
        else:
            rating = rating.rating / rating.review_count

        return rating


class Items(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    category_id = db.Column(db.Integer, index=True)
    created = db.Column(db.DATETIME, nullable=False, default=datetime.now)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    price_type = db.Column(db.Enum(PriceTypes), nullable=False)
    price = db.Column(db.Integer, index=True)
    pictures = db.Column(db.Text)
    main_picture = db.Column(db.String(255))

    def serialize(self):
        pictures = [] if self.main_picture in ['', None] else [self.main_picture]
        pictures.extend(self.pictures.split(',') if self.pictures not in ['', None] else [])
        return {
            'id': self.id,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'created': str(self.created),
            'title': self.title,
            'description': self.description,
            'is_active': self.is_active,
            'price_type': self.price_type.name,
            'price': self.price,
            'pictures': pictures
        }


class Categories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(255), nullable=False, unique=True)

    def serialize(self):
        return {
            'id': self.id,
            'category_name': self.category_name
        }


class Reviews(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    created = db.Column(db.DATETIME, nullable=False, default=datetime.now)

    def serialize(self):
        return {
            'id': self.id,
            'item_id': self.item_id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'rating': self.rating,
            'created': str(self.created),
        }


class Ratings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, unique=True, nullable=False)
    rating = db.Column(db.Integer, nullable=False, default=0)
    review_count = db.Column(db.Integer, nullable=False, default=0)
