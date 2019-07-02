from app import app
from app import app
from app import celery
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.models import User, Video
from config import Config
import json



@celery.task(bind=True)
def my_background_task(self, user_id):
    app = Flask(__name__)
    app.config.from_object(Config)
    # celery.conf.update(app.config)
    db = SQLAlchemy(app)
    with app.app_context():

        videos = Video.query.filter_by(user_id=user_id)
        content = []
        total = len(list(videos))
        i = 0
        for video in videos:
            import time
            time.sleep(1)
            i += 1
            d = {}
            d['id'] = video.id
            d['title'] = video.title
            d['timestamp'] = str(video.timestamp)
            d['description'] = video.description
            d['likes'] = video.users.count()
            content.append(d)
            self.update_state(state='PROGRESS', meta={'current': i, 'total': total,
                                                      'status': ''})

        with open('app/static/'+str(user_id)+'.json', 'w') as f:
            json.dump(content, f, indent=4, ensure_ascii=False)

        return {'current': i, 'total': total, 'status': 'File Downloaded!', 'result': content}
