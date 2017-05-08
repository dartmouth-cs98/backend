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

# @periodic_task(run_every=(crontab(hour="9", minute="0", day_of_week="*")),
#     ignore_result=True)
# def analytics():
#     for user in CustomUser.objects.all():
#         count = Counter(json.loads(user.word_count))
#         sort = sorted(count.items(), key=operator.itemgetter(1))
#         sort.reverse()
#
#         if len(sort) > 100:
#             sort = sort[0:100]
#         user.top_100_words = json.dumps(dict(sort))
#         user.word_count = '{}'
#
#         day = timezone.now() - timedelta(days=1)
#         week = timezone.now() - timedelta(days=7)
#
#         day_count = Counter(user.page_set.filter(Q(pagevisit__visited__gte=day)))
#         week_count = Counter(user.page_set.filter(Q(pagevisit__visited__gte=week)))
#
#         day_sort = sorted(day_count.items(), key=operator.itemgetter(1))
#         day_sort.reverse()
#         week_sort = sorted(week_count.items(), key=operator.itemgetter(1))
#         week_sort.reverse()
#
#         if len(day_sort) > 10:
#             day_ten = day_sort[0:10]
#         else:
#             day_ten = day_sort
#
#         if len(week_sort) > 10:
#             week_ten = week_sort[0:10]
#         else:
#             week_ten = week_sort
#
#         user.pages_day = json.dumps({c[0].pk: c[1] for c in day_ten})
#         user.pages_week = json.dumps({c[0].pk: c[1] for c in week_ten})
#
#         user.save()

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
