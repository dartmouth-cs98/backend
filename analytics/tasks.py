from authentication.models import CustomUser
from django.utils import timezone
import pytz
import json
from collections import Counter
import operator
from celery import task
from datetime import timedelta, datetime
from celery.decorators import periodic_task
from celery.task.schedules import crontab
from analytics.models import Day


@periodic_task(run_every=(crontab(hour="*", minute="1", day_of_week="*")),
    ignore_result=True)
def newday():
    t = timezone.now()
    admin = CustomUser.objects.get(email='admin@hindsitehistory.com')

    for cu in CustomUser.objects.exclude(email='admin@hindsitehistory.com'):
        day = cu.day_set.last()
        newdate = day.date + timedelta(days=1)
        nextday = datetime.combine(newdate, datetime.min.time()).replace(tzinfo=pytz.UTC)

        #positive timezone offsets compared to UTC
        if t >= nextday and cu.offset >= 0:
            if cu.offset * 3600 < (t-nextday).seconds:
                d = Day(owned_by=cu, date=newdate, weekday=newdate.weekday())
                d.save()
                if not admin.day_set.filter(date=newdate).exists():
                    d = Day(owned_by=admin, date=newdate, weekday=newdate.weekday())
                    d.save()
        #negative timezone offsets compared to UTC
        if t < nextday and cu.offset < 0:
            if -cu.offset * 3600 - 300 < (nextday-t).seconds:
                d = Day(owned_by=cu, date=newdate, weekday=newdate.weekday())
                d.save()
                if not admin.day_set.filter(date=newdate).exists():
                    d = Day(owned_by=admin, date=newdate, weekday=newdate.weekday())
                    d.save()
