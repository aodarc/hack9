from kombu.utils.url import quote
from api import settings
import os
from celery import Celery


aws_access_key = quote(settings.AWS_ACCESS_KEY)
aws_secret_key = quote(settings.AWS_SECRET_KEY)

broker_url = "sqs://{aws_access_key}:{aws_secret_key}@".format(
    aws_access_key=aws_access_key, aws_secret_key=aws_secret_key,
)


app = Celery("hack8")


task_routes = (
    [
        ("api.tasks.*", {"queue": "fast_queue"}),
    ],
)

app.conf.task_default_queue = "fast_queue"
app.conf.update(CELERY_ROUTES=task_routes)

