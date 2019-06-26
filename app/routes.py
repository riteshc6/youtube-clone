import os
from werkzeug.utils import secure_filename
from flask import render_template, redirect, render_template, url_for, flash
from flask_login import current_user, logout_user, login_user, login_required
from app import app, db
from app.forms import LoginForm, RegistrationForm, UploadForm
from app.models import User, Video
from config import basedir
from flask import send_from_directory


@app.route('/')
@app.route('/index')
@login_required
def index():
    videos = Video.query.all()
    return render_template('index.html', videos=videos)


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
                # next_page = request.args.get('next')
        # if not next_page or url_parse(next_page).netloc != '':
        #     next_page = url_for('index')
        # return redirect(next_page)
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

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        video = Video(title=form.title.data, description=form.description.data, user=current_user)
        db.session.add(video)
        db.session.commit()
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


@app.route('/watch/<video_id>')
@login_required
def watch(video_id):
    video = Video.query.filter_by(id=video_id).first()
    return render_template('watch.html', video=video)


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

@app.route('/uploads')
@login_required
def uploads():
    videos = Video.query.filter_by(user_id=current_user.id)
    return render_template('uploads.html', videos=videos)


@app.route('/delete/<video_id>')
@login_required
def delete(video_id):
    video = Video.query.filter_by(id=video_id)
    db.session.delete(video)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/profile/<user_id>')
@login_required
def profile(user_id):
    videos = Video.query.filter_by(user_id=user_id)
    user = User.query.filter_by(id=user_id).first()
    print(user.id)
    return render_template('profile.html', videos=videos, username=user.username)
