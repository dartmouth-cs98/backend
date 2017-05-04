import json
from datetime import datetime, timedelta
from django.utils import timezone
from authentication.models import CustomUser
from analytics.models import Day

def initialize_days():
    for cu in CustomUser.objects.all():

        t = (timezone.now() - timedelta(hours=cu.offset)).replace(minute=0)

        weekday = t.weekday() - 6

        if weekday < 0:
            weekday += 7

        start = datetime(t.year, t.month, t.day, tzinfo=t.tzinfo) - timedelta(days=13, hours=-cu.offset)
        end = start + timedelta(days=1)


        for i in range(14):
            pvs = cu.pagevisit_set.filter(visited__range=(start, end))

            domains = {}
            pages = {}

            for pv in pvs:
                if str(pv.page_id) in pages.keys():
                    pages[str(pv.page_id)] += 1
                else:
                    pages[str(pv.page_id)] = 1

                if pv.domain.base_url in domains.keys():
                    domains[pv.domain.base_url] += 1
                else:
                    domains[pv.domain.base_url] = 1

            d = Day(owned_by=cu, date=start.date(), weekday=weekday, pages=json.dumps(pages), domains=json.dumps(domains))
            d.save()

            start += timedelta(days=1)
            end += timedelta(days=1)
            weekday += 1
            if weekday > 6:
                weekday = 0

def initialize_admin_days():
    admin = CustomUser.objects.get(email='admin@hindsitehistory.com')


    t = (timezone.now() - timedelta(hours=admin.offset)).replace(minute=0)

    weekday = t.weekday() - 6

    if weekday < 0:
        weekday += 7

    date = datetime(t.year, t.month, t.day, tzinfo=t.tzinfo) - timedelta(days=25, hours=-admin.offset)

    for i in range(15):
        domains = {}
        pages = {}

        for day in Day.objects.filter(date=date.date()):
            pages.update(json.loads(day.pages))
            domains.update(json.loads(day.domains))

        d = Day(owned_by=admin, date=date.date(), weekday=weekday, pages=json.dumps(pages), domains=json.dumps(domains))
        d.save()

        date += timedelta(days=1)

        weekday += 1
        if weekday > 6:
            weekday = 0
