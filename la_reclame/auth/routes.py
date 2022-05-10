from flask import request, render_template, flash, get_flashed_messages
from flask import redirect, url_for
from passlib.hash import sha256_crypt
from la_reclame.models import Users
from la_reclame.auth import auth
from la_reclame import db


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('password-confirm')

    if password != confirm_password:
        flash('Passwords does not match', 'danger')

    if Users.query.filter_by(username=username).first() is not None:
        flash('Username is already taken!', 'danger')

    if Users.query.filter_by(email=email).first() is not None:
        flash('Email is already taken!', 'danger')

    if len(get_flashed_messages()) != 0:
        return render_template('register.html')

    user = Users(username=username, email=email, password=sha256_crypt.hash(password))
    db.session.add(user)
    db.session.commit()

    flash('User was created!', 'success')

    return redirect(url_for('auth.login'))
