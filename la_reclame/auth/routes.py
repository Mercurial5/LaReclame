from flask import request, render_template
from la_reclame.auth import auth


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
