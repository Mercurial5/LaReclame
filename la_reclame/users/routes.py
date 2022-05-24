from flask import render_template, request, session
from flask import flash
from la_reclame.users import users
from la_reclame.models import Users, Items, Ratings
from utils import auth_required, picturesDB
from la_reclame import db


@users.route('/<username>')
@auth_required
def profile(username: str):
    user = Users.query.filter_by(username=username).first()

    if user is None:
        return '404\nUser not found'

    items = Items.query.filter_by(user_id=user.id).all()
    rating = Ratings.query.filter_by(user_id=user.id).first()

    if rating is None or rating.review_count == 0:
        rating = 0.0
    else:
        rating = rating.rating / rating.review_count

    return render_template('profile.html', user=user, items=items, rating=rating)


@users.route('/settings', methods=['GET', 'POST'])
@auth_required
def settings():
    if request.method == 'GET':
        return render_template('settings.html', user=session['user'])

    username = request.form.get('username')
    user = Users.query.get(session['user'].id)

    if user.username != username and Users.query.filter_by(username=username).first() is not None:
        flash('Username is already taken', 'danger')
    elif user.username != username:
        user.username = username
        db.session.commit()

        session['user'] = user

        flash('Username is changes', 'success')

    picture = request.files.get('profile-picture')
    if picture:
        if user.picture is not None:
            picturesDB.delete_picture('profile-pictures', user.picture)

        picture_name = picturesDB.add_picture('profile-pictures', picture)
        user.picture = picture_name
        db.session.commit()

        session['user'] = user

        flash('Picture is updated!', 'success')

    return render_template('settings.html', user=session['user'])
