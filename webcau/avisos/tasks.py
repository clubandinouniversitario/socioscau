from enum import auto
from celery import shared_task, Celery
from django.utils import timezone as tz

from avisos.models import BaseNotice

celery = Celery('tasks', broker='amqp://guest@localhost//') #!

import os

os.environ[ 'DJANGO_SETTINGS_MODULE' ] = "webcau.settings"

@shared_task
def add(x, y):
    return x + y

@shared_task(auto_retry=True, max_retries=3)
def wait_for_start_time(notice_id):
  print("notice_Task_start")
  notice = BaseNotice.objects.get(id=notice_id)
  if notice.status == notice.PUBLISHED:
    notice.activate_notice()

@shared_task(auto_retry=True, max_retries=3)
def wait_for_max_end_time(notice_id):
  print("notice_Task_end")
  notice = BaseNotice.objects.get(id=notice_id)
  if notice.status == notice.ACTIVE:
    notice.late_notice()

@shared_task(auto_retry=True, max_retries=3)
def enqueue_mail(notice_id, publication=False, arrival=False, late=False, cancel=False, mail_content=None):
  notice = BaseNotice.objects.get(id=notice_id)
  notice.mail(publication, arrival, late, cancel, mail_content)