from datetime import datetime
from flask import render_template, url_for, redirect, request, flash, g, current_app
from flask_login import current_user, login_required

from app.general import general_bp
from app.general.forms import CreatePostForm, EmptyForm, EditProfileForm, SearchForm
from app.models import Post, User
from app import db


@general_bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()
        g.create_post_form = CreatePostForm()


@general_bp.after_request
def set_response_header(response):
    if 'Cache-Control' not in response.headers:
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response


@general_bp.route('/', methods=['GET', 'POST'])
@login_required
def main():
    if current_user.is_authenticated:
        form = CreatePostForm()
        if g.create_post_form.validate_on_submit():
            post = Post(
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
            'index.html', title='Home', form=form, posts=posts.items,
            next_url=next_url, prev_url=prev_url
        )
    return redirect(url_for('general.explore'))


@general_bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, 6, False
    )

    next_url = url_for('general.explore', page=posts.next_num) if \
        posts.has_next else None
    prev_url = url_for('general.explore', page=posts.prev_num) if \
        posts.has_prev else None

    return render_template(
        'index.html', title='Explore', posts=posts.items, next_url=next_url,
        prev_url=prev_url
    )


@general_bp.route('/user/<username>')
@login_required
def user(username):
    user_info = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user_info.posts.order_by(Post.timestamp.desc()).paginate(
        page, 3, False)
    next_url = url_for('general.user', username=user_info.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('general.user', username=user_info.username, page=posts.prev_num) \
        if posts.has_prev else None
    follow_form = EmptyForm()
    edit_form = EditProfileForm(current_user.username)

    edit_form.username.data = current_user.username
    edit_form.bio.data = current_user.bio

    return render_template(
        'user.html', title='Profile', posts=posts.items,
        user=user_info, next_url=next_url, prev_url=prev_url,
        follow_form=follow_form, edit_form=edit_form
    )


@general_bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user_info = User.query.filter_by(username=username).first()
        if user_info is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('general.index'))
        if user_info == current_user:
            flash('You cannot follow yourself!', 'alert-info')
            return redirect(url_for('general.user', username=username))
        current_user.follow(user_info)
        db.session.commit()
        flash('You are following {}!'.format(username), 'alert-success')
        return redirect(url_for('general.user', username=username))
    else:
        return redirect(url_for('general.main'))


@general_bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user_info = User.query.filter_by(username=username).first()
        if user_info is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('general.index'))
        if user_info == current_user:
            flash('You cannot unfollow yourself!', 'alert-info')
            return redirect(url_for('general.user', username=username))
        current_user.unfollow(user_info)
        db.session.commit()
        flash('You have unfollowed {}!'.format(username), 'alert-success')
        return redirect(url_for('general.user', username=username))
    else:
        return redirect(url_for('general.main'))


@general_bp.route('/edit_profile', methods=['POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.bio = form.bio.data
        db.session.commit()
        flash('Your changes have been saved', 'alert-success')
    if form.errors:
        for error in form.errors:
            flash(form.errors[error][0], 'alert-danger')
    return redirect(url_for('general.user', username=current_user.username))


@general_bp.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('general.explore'))
    page = request.args.get('page', 1, type=int)
    posts, total = Post.search(g.search_form.q.data, page,
                               current_app.config['POSTS_PER_PAGE'])
    next_url = url_for('general.search', q=g.search_form.q.data, page=page + 1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('general.search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None
    return render_template('index.html', title='Explore', posts=posts,
                           next_url=next_url, prev_url=prev_url)
