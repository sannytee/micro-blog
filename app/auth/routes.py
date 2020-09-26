from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse

from app import db
from app.auth import auth_bp
from app.auth.forms import *
from app.email import send_password_reset_email
from app.models import User


@auth_bp.after_request
def set_response_header(response):
    if 'Cache-Control' not in response.headers:
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('general.main'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User.query.filter(
            (User.username == form.username.data) |
            (User.email == form.email.data)
        ).first()
        if user is None:
            user = User(
                username=form.username.data,
                email=form.email.data,
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            login_user(user, remember=False)
            flash('Account created successfully', 'alert-info')
            return redirect(url_for('general.main'))
        if user.username == form.username.data:
            flash('username already exist', 'alert-danger')
        if user.email == form.email.data:
            flash('email already exist', 'alert-danger ')
        return redirect(url_for('auth.register'))
    return render_template('auth/register.html', title='Register', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('general.main'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'alert-danger')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('general.main')
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form=form)


@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out', 'alert-success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('general.main'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password', 'alert-success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html',
                           title='Reset Password', form=form)


@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('general.main'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('general.main'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.', 'alert-success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)
