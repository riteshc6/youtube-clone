from app import app
from app import celery
from flask_login import current_user, logout_user, login_user, login_required


@celery.task(bind=True)
@login_required
def my_background_task(self):
    from app import app
    from app.models import Video
    with app.app_context():

        # videos = Video.query.all()
        # print(videos)
        # # content = []
        # for video in videos:
        #     print(video)
            # d = {}
            # d['id'] = video.id
            # d['title'] = video.title
            # d['timestamp'] = str(video.timestamp)
            # d['description'] = video.description
            # content.append(d)
        # print(content)
        import time
        total = 100
        message = "test"
        for i in range(50):
            time.sleep(1)
            self.update_state(state='PROGRESS',
                            meta={'current': i, 'total': total,
                                    'status': message})
            print(i)
        return {'current': 100, 'total': 100, 'status': 'Task Completed', 'result': 15}
