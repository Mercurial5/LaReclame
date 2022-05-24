from flask import session, redirect, url_for
from utils.PicturesDB import PicturesDB
from email.message import EmailMessage
from smtplib import SMTP_SSL
from os import getenv
from enum import Enum
import functools
picturesDB = PicturesDB()


def auth_required(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if session.get('user') is None:
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)

    return wrapper


def not_auth(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if session.get('user') is None:
            return func(*args, **kwargs)
        return redirect(url_for('items.items_home'))

    return wrapper


def send_email(to: str, token_link: str):
    message = EmailMessage()
    message['Subject'] = 'Email verification' 
    message['From'] = getenv('SMTP_SENDER')
    message['To'] = to
    message.set_content('Your verification link is %s' % token_link)

    with SMTP_SSL('smtp.gmail.com', int(getenv('SMTP_PORT'))) as smtp:
        smtp.login(getenv('SMTP_SENDER'), getenv('SMTP_PASSWORD'))
        smtp.send_message(message)


class PriceTypes(Enum):
    fixed = 1
    free = 2
    negotiable = 3
