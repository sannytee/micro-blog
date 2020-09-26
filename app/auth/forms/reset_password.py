from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, EqualTo
from wtforms import PasswordField, SubmitField


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
