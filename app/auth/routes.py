from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_user

from app import db
from app.auth import auth_bp
from app.auth.forms import *
from app.models import User


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('general.main'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user, remember=False)
        flash('Account created successfully')
        return redirect(url_for('general.main'))
    return render_template('auth/register.html', title='Register', form=form)
