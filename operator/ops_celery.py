import os
from celery import Celery


# noinspection PyPep8Naming,PyPropertyAccess
def make_celery(app):
    app.config.update(
        CELERY_BROKER_URL=os.getenv("CELERY_BROKER"),
        CELERY_RESULT_BACKEND=os.getenv("CELERY_BROKER")
    )
    celery = Celery(app.import_name, backend=app.config["CELERY_RESULT_BACKEND"],
                    broker=app.config["CELERY_BROKER_URL"], include=[app.import_name])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery
