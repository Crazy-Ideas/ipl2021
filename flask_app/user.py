import os
from base64 import b64encode
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional

from firestore_ci.firestore_ci import FirestoreDocument
from flask import flash, redirect, url_for, render_template, request, current_app, Response, make_response
from flask_login import UserMixin, current_user, login_user, logout_user
from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.urls import url_parse
from wtforms import PasswordField, SubmitField, StringField
from wtforms.validators import DataRequired

from config import Config
from flask_app import ipl_app, login


def cookie_login_required(route_function):
    @wraps(route_function)
    def decorated_route(*args, **kwargs):
        if current_user.is_authenticated:
            return route_function(*args, **kwargs)
        user = User.check_token(request.cookies.get("token"))
        if user:
            login_user(user=user)
            return route_function(*args, **kwargs)
        return current_app.login_manager.unauthorized()

    return decorated_route


class User(FirestoreDocument, UserMixin):

    def __init__(self):
        super().__init__()
        self.username: str = str()
        self.password_hash: str = str()
        self.email: str = str()
        self.name: str = str()
        self.token: str = str()
        self.token_expiration: datetime = datetime.now(tz=Config.INDIA_TZ)
        self.balance: int = Config.BALANCE
        self.points: float = 0.0
        self.player_count: int = 0
        self.auto_bid: bool = False
        self.bidding: bool = False

    def __repr__(self) -> str:
        return f"{self.username.upper()}"

    def set_password(self, password) -> None:
        self.password_hash = generate_password_hash(password)
        self.save()

    def check_password(self, password) -> bool:
        return check_password_hash(self.password_hash, password)

    def get_id(self) -> str:
        return self.username

    @classmethod
    def check_token(cls, token) -> Optional["User"]:
        if not token:
            return None
        user: User = cls.objects.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.now(tz=Config.INDIA_TZ):
            return None
        return user

    def get_token(self, expires_in=Config.TOKEN_EXPIRY) -> str:
        now = datetime.now(tz=Config.INDIA_TZ)
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = b64encode(os.urandom(24)).decode()
        self.token_expiration = now + timedelta(seconds=expires_in)
        self.save()
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)
        self.save()


User.init()


@login.user_loader
def load_user(username: str) -> Optional[User]:
    user = User.objects.filter_by(username=username).first()
    return user


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')


@ipl_app.route("/login", methods=["GET", "POST"])
def login() -> str:
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if not form.validate_on_submit():
        return render_template("form_template.html", title="SFL - IPL 2021 - Sign In", form=form)
    user = User.objects.filter_by(username=form.username.data).first()
    if not user or not user.check_password(form.password.data):
        flash(f"Invalid email or password.")
        return redirect(url_for("login"))
    token = user.get_token()
    login_user(user=user)
    next_page = request.args.get("next")
    if not next_page or url_parse(next_page).netloc != str() or next_page == "/logout":
        next_page = url_for("home")
    response: Response = make_response(redirect(next_page))
    response.set_cookie("token", token, max_age=Config.TOKEN_EXPIRY, secure=Config.CI_SECURITY,
                        httponly=Config.CI_SECURITY, samesite="Strict")
    return redirect(next_page)


@ipl_app.route('/logout')
@cookie_login_required
def logout():
    current_user.revoke_token()
    logout_user()
    return redirect(url_for('home'))
