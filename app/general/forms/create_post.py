from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length


class CreatePostForm(FlaskForm):
    post = TextAreaField('Post', validators=[
        Length(min=3, max=140)
    ])
    submit = SubmitField('Submit')
