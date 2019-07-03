import os
from werkzeug.utils import secure_filename
from flask import render_template, redirect, render_template, url_for, flash, request
from flask_login import current_user, logout_user, login_user, login_required
from app import app, db
from app.forms import LoginForm, RegistrationForm, UploadForm
from app.models import User, Video
from config import basedir
from flask import send_from_directory
from flask import g
from app.forms import SearchForm
from flask_babel import _, get_locale
import json
from flask import send_from_directory, jsonify
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from app.tasks import download_content


# ---------------- Authentication Functions --------------------------- #

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


# ----- /index, /upload, /delete, /watch, /before_request, /edit_video ------ #

@app.before_request
def before_request():
    if current_user.is_authenticated:
        g.search_form = SearchForm()


@app.route('/')
@app.route('/index')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    videos = Video.query.order_by(Video.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('index', page=videos.next_num)\
        if videos.has_next else None
    prev_url = url_for('index', page=videos.prev_num)\
        if videos.has_prev else None
    return render_template('index.html', videos=videos.items,
                           next_url=next_url, prev_url=prev_url)


@app.route('/videos/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        video = Video(title=form.title.data,
                      description=form.description.data, user=current_user)
        db.session.add(video)
        db.session.flush()
        f = form.upload.data
        filename = secure_filename(f.filename)
        f1, ext = os.path.splitext(filename)
        path = os.path.join(basedir, "app/static", str(video.id)) + ext
        f.save(path)
        video.path = "/static/" + str(video.id) + ext
        db.session.commit()
        # video.path = path
        # db.session.add
        flash('Congratulations, your video has been uploaded!')
        return redirect(url_for('watch', video_id=video.id))
    return render_template('upload.html', title='Upload', form=form)


@app.route('/edit_video/<video_id>', methods=['GET', 'POST'])
@login_required
def edit_video(video_id):
    video = Video.query.filter_by(id=video_id).first()
    form = UploadForm()
    del form.upload
    if current_user.id == video.user_id:
        if form.validate_on_submit():
            video.title = form.title.data if form.title.data else video.title
            video.description = form.description.data
            db.session.commit()
            flash("Your Video has been Edited")
            return redirect(url_for('watch', video_id=video.id))
        else:
            form.title.data = video.title
            form.description.data = video.description
            return render_template("edit_video.html", video=video, form=form)
    else:
        return "PERMISSION DENIED"


@app.route('/delete/<video_id>')
@login_required
def delete(video_id):
    video = Video.query.filter_by(id=video_id).first()
    db.session.delete(video)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/videos/<video_id>')
@login_required
def watch(video_id):
    video = Video.query.filter_by(id=video_id).first()
    return render_template('watch.html', video=video)


# ------------------- /like, /unlike, /liked videos ------------------------- #

@app.route('/like/<video_id>')
@login_required
def like(video_id):
    video = Video.query.filter_by(id=video_id).first()
    if video is None:
        flash('Video {} not found'.format(video.title))
        return redirect(url_for('index'))
    current_user.like(video)
    db.session.commit()
    flash('{} added to your liked videos'.format(video.title))
    return redirect(url_for('watch', video_id=video.id))


@app.route('/unlike/<video_id>')
@login_required
def unlike(video_id):
    video = Video.query.filter_by(id=video_id).first()
    if video is None:
        flash('Video {} not found'.format(video.title))
        return redirect(url_for('index'))
    current_user.unlike(video)
    db.session.commit()
    flash('{} removed from your liked videos'.format(video.title))
    return redirect(url_for('watch', video_id=video.id))


@app.route('/videos/liked')
@login_required
def liked():
    videos = current_user.liked_videos()
    return render_template('liked.html', videos=videos)


# ------------------------ /profile -------------------------------- #
@app.route('/profile/<user_id>')
@login_required
def profile(user_id):
    videos = Video.query.filter_by(user_id=user_id)
    user = User.query.filter_by(id=user_id).first()
    print(user.id)
    return render_template('profile.html', videos=videos, username=user.username)


# -------------------------- Elastic Search ------------------------ #
@app.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    videos, total = Video.search(g.search_form.q.data, page,
                                 app.config['POSTS_PER_PAGE'])
    next_url = url_for('search', q=g.search_form.q.data, page=page + 1)\
        if total > page * app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('search', q=g.search_form.q.data, page=page - 1)\
        if page > 1 else None
    return render_template('search.html', title=_('search'), videos=videos,
                           next_url=next_url, prev_url=prev_url)


# -------------------------- Download File ----------------------------- #

@app.route('/download', methods=['POST'])
@login_required
def download():
    job = download_content.delay(current_user.id)
    return jsonify({}), 202, {'Location': url_for('status', job_id=job.id)}


@app.route('/status/<job_id>')
@login_required
def status(job_id):
    job = download_content.AsyncResult(job_id)
    if job.state == 'PENDING':
        response = {
            'state': job.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif job.state != 'FAILURE':
        response = {
            'state': job.state,
            'current': job.info.get('current', 0),
            'total': job.info.get('total', 1),
            'satus': job.info.get('status', '')
        }
        if 'result' in job.info:
            response['result'] = job.info['result']
    else:
        response = {
            'state': job.state,
            'current': 1,
            'total': 1,
            'status': str(job.info),
        }
    return jsonify(response)


@app.route('/download_file')
@login_required
def download_file():
    path = str(current_user.id) + '.json'
    filename = current_user.username + ".json"
    return send_from_directory(directory=os.path.join(basedir, "app/static/"), filename=path, as_attachment=True, cache_timeout=None, attachment_filename=filename)
