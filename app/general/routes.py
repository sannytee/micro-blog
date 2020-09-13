from flask import render_template, url_for, redirect, request, flash
from flask_login import current_user

from app.general import general_bp
from app.general.forms import CreatePostForm
from app.models import Post
from app import db


@general_bp.route('/', methods=['GET', 'POST'])
def main():
    if current_user.is_authenticated:
        form = CreatePostForm()
        if form.validate_on_submit():
            post = Post(
                title=form.title.data,
                body=form.post.data,
                author=current_user
            )
            db.session.add(post)
            db.session.commit()
            flash('Post successfully created', 'alert-success')
            return redirect(url_for('general.main'))
        page = request.args.get('page', 1, type=int)
        posts = current_user.followed_posts().paginate(
            page, 6, False
        )

        next_url = url_for('general.main', page=posts.next_num) if \
            posts.has_next else None
        prev_url = url_for('general.main', page=posts.prev_num) if \
            posts.has_prev else None
        return render_template(
            'index.html', title='Home', form=form,
            authenticated=True, posts=posts.items, next_url=next_url, prev_url=prev_url
        )
    return redirect(url_for('general.explore'))


@general_bp.route('/explore')
def explore():
    authenticated = False
    form = CreatePostForm()
    if current_user.is_authenticated:
        authenticated = True
    page = request.args.get('page', 1, int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, 6, False
    )

    next_url = url_for('general.explore', page=posts.next_num) if \
        posts.has_next else None
    prev_url = url_for('general.explore', page=posts.prev_num) if \
        posts.has_prev else None

    return render_template(
        'index.html', title='Explore', authenticated=authenticated,
        posts=posts.items, next_url=next_url, prev_url=prev_url,
        form=form
    )
