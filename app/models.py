from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from flask_login import current_user
from app import login
from app.search import add_to_index, remove_from_index, query_index


likes = db.Table('likes',
                 db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                 db.Column('video_id', db.Integer, db.ForeignKey('video.id'))
                 )


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    videos = db.relationship('Video', backref='user', lazy='dynamic')
    comments = db.relationship('Comment', backref="user", lazy="dynamic")

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    liked = db.relationship(
        'Video', secondary=likes,
        # primaryjoin=(likes.c.user_id == id),
        # secondaryjoin=(likes.c.video_id == 'Video.id'),
        backref=db.backref('users', lazy='dynamic'), lazy='dynamic')

    def like(self, video):
        if not self.is_liked(video):
            self.liked.append(video)

    def unlike(self, video):
        if self.is_liked(video):
            self.liked.remove(video)

    def is_liked(self, video):
        return self.liked.filter(
            likes.c.video_id == video.id).count() > 0 

    def liked_videos(self):
        liked = Video.query.join(
            likes, (likes.c.video_id == Video.id)).filter(likes.c.user_id==self.id)
        return liked.order_by(Video.timestamp.desc())


class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = query_index(
            cls.__tablename__, expression, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)


class Video(SearchableMixin, db.Model):
    __searchable__ = ['title']
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    description = db.Column(db.String(140))
    path = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comments = db.relationship("Comment", backref="video", lazy="dynamic")

    def __repr__(self):
        return '<Video {}>'.format(self.title)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(240))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'))

    def __repr__(self):
        return '<Comment {}>'.format(self.body)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)
