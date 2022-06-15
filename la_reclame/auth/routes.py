from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
from flask import request, render_template, flash, get_flashed_messages
from flask import redirect, url_for, session
from passlib.hash import sha256_crypt
from la_reclame.models import Users
from la_reclame.auth import auth
from la_reclame import db
from utils import not_auth, auth_required, send_email
from os import getenv


url_serializer = URLSafeTimedSerializer(getenv('SECRET_KEY'))


@auth.route('/login', methods=['GET', 'POST'])
@not_auth
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form.get('username')
    password = request.form.get('password')

    user = Users.query.filter_by(username=username).first()

    if user is None or sha256_crypt.verify(password, user.password) is False:
        flash('Username or password is wrong', 'danger')
        return render_template('login.html')

    if user.is_active is False:
        flash('User was not activated yet', 'danger')
        return render_template('login.html')

    session['user'] = user
    return redirect(url_for('items.items_home'))


@auth.route('/register', methods=['GET', 'POST'])
@not_auth
def register():
    if request.method == 'GET':
        return render_template('register.html')

    username = request.form.get('username')
    barcode = request.form.get('barcode')
    password = request.form.get('password')
    confirm_password = request.form.get('password-confirm')

    if password != confirm_password:
        flash('Passwords does not match', 'danger')

    if Users.query.filter_by(username=username).first() is not None:
        flash('Username is already taken!', 'danger')

    if Users.query.filter_by(barcode=barcode).first() is not None:
        flash('Email is already taken!', 'danger')

    if len(get_flashed_messages()) != 0:
        return render_template('register.html')

    user = Users(username=username, barcode=barcode, password=sha256_crypt.hash(password))
    db.session.add(user)
    db.session.commit()

    token = url_serializer.dumps(barcode, salt=getenv('SECRET_KEY_EMAIL_CONFIRM'))
    token_link = url_for('auth.confirm_email', token=token, _external=True)

    send_email(barcode + '@astanait.edu.kz', token_link)

    flash('User was created!', 'success')

    return redirect(url_for('auth.login'))


@auth.route('/logout')
@auth_required
def logout():
    del session['user']

    return redirect(url_for('auth.login'))


@auth.route('/confirm-email/<token>')
def confirm_email(token: str):
    try:
        email = url_serializer.loads(token, salt=getenv('SECRET_KEY_EMAIL_CONFIRM'), max_age=900)
    except SignatureExpired:
        return '<h1>The token is expired!</h1>'
    except BadTimeSignature:
        return '<h1>This isn\'t the right token!</h1>'

    user = Users.query.filter_by(email=email).first()
    user.is_active = True
    db.session.commit()

    flash('User was activated!', 'success')

    return redirect(url_for('auth.login'))
