from app import app, db

from app.models import User, Video, Comment


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Video': Video, 'Comment': Comment}
