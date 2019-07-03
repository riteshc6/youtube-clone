from app import app
from app import app
from app import celery
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.models import User, Video
from config import Config
import json



@celery.task(bind=True)
def download_content(self, user_id):
    app = Flask(__name__)
    app.config.from_object(Config)
    # celery.conf.update(DATABASE_URL='postgresql://ritesh:ritesh@127.0.0.1:5432/youtube')
    
    db = SQLAlchemy(app)
    with app.app_context():

        videos = Video.query.filter_by(user_id=user_id)
        content = []
        total = len(list(videos))
        i = 0
        for video in videos:
            i += 1
            video_details = {}
            video_details['id'] = video.id
            video_details['title'] = video.title
            video_details['timestamp'] = str(video.timestamp)
            video_details['description'] = video.description
            video_details['likes'] = video.users.count()
            content.append(video_details)
            self.update_state(state='PROGRESS', meta={'current': i, 'total': total,
                                                      'status': ''})

        with open('app/static/'+str(user_id)+'.json', 'w') as f:
            json.dump(content, f, indent=4, ensure_ascii=False)

        return {'current': i, 'total': total, 'status': 'File Downloaded!', 'result': content}
