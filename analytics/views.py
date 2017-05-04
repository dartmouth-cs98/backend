from rest_framework.views import APIView
from django.utils import timezone
from datetime import datetime, timedelta
import json
from collections import Counter
import operator
from django.db.models import Case, When
from rest_framework.response import Response
from history.models import PageVisit
from authentication.models import CustomUser
from analytics.models import Day
from hindsite.constants import weekdays
from analytics.serializers import AnalyticsSerializer


class SendAnalytics(APIView):

    def get(self, request, format=None):
        cu = request.user
        admin = CustomUser.objects.get(email='admin@hindsitehistory.com')

        data = {'page_visits': {
                        'day': [],
                        'week': {
                            'current': [],
                            'last': [],
                            'average': []
                        },
                        'month': []
                    },
                    'user_domains': {
                        'day': [],
                        'week': [],
                        'month': []
                    },
                    'hindsite_domains': {
                        'day': [],
                        'week': [],
                        'month': []
                    },
                    'user_pages': {
                        'day': [],
                        'week': [],
                        'month': []
                    }
                }

        start = timezone.now().replace(minute=0) - timedelta(hours=23)
        end = start + timedelta(hours=1)

        for i in range(24):
            pvs = cu.pagevisit_set.filter(visited__range=(start, end))
            pv_count = pvs.count()
            page_count = pvs.order_by().values_list('page_id').distinct().count()

            data['page_visits']['day'].append({'datetime': (start - timedelta(hours=cu.offset)).strftime("%I%p").lstrip('0'),
                                               'pages': page_count,
                                               'pagevisits': pv_count})
            start = end
            end += timedelta(hours=1)

        days = cu.day_set.all().reverse()

        today = days.first()
        current = days[:7][::-1]
        last = days[7:14][::-1]
        month = days[:31]

        admin_days = admin.day_set.exclude(date__gt=today.date).reverse()

        admin_today = admin_days.first()
        admin_current = admin_days[:7][::-1]
        admin_month = admin_days[:31]


        day_pages = Counter(json.loads(today.pages))
        day_domains = Counter(json.loads(today.domains))

        day_pages = sorted(day_pages.items(), key=operator.itemgetter(1))
        day_domains = sorted(day_domains.items(), key=operator.itemgetter(1))

        day_pages.reverse()
        day_domains.reverse()

        admin_day_domains = Counter(json.loads(admin_today.domains))


        pages = {}
        domains = {}

        # Current Week stats for user
        for d in current:
            p = json.loads(d.pages)
            pages.update(p)
            domains.update(json.loads(d.domains))
            data['page_visits']['week']['current'].append({'datetime': weekdays[d.weekday],
                                                           'pages': len(p.keys()),
                                                           'pagevisits': sum(p.values())
                                                           })

        week_pages = Counter(pages)
        week_domains = Counter(domains)

        week_pages = sorted(week_pages.items(), key=operator.itemgetter(1))
        week_domains = sorted(week_domains.items(), key=operator.itemgetter(1))

        week_pages.reverse()
        week_domains.reverse()

        domains = {}

        # Current Week stats across hindsite
        for d in admin_current:
            domains.update(json.loads(d.domains))

        admin_week_domains = Counter(domains)
        admin_week_domains = sorted(admin_week_domains.items(), key=operator.itemgetter(1))
        admin_week_domains.reverse()

        # Last Week stats for user
        for d in last:
            p = json.loads(d.pages)
            data['page_visits']['week']['last'].append({'datetime': weekdays[d.weekday],
                                                           'pages': len(p.keys()),
                                                           'pagevisits': sum(p.values())
                                                           })

        for w in range(7):
            total_pages = 0
            total_pvs = 0
            num_days = days.filter(weekday=w).count()

            for d in days.filter(weekday=w):
                p = json.loads(d.pages)
                total_pvs += sum(p.values())
                total_pages += len(p.keys())

            if w==6:
                data['page_visits']['week']['average'].insert(0, {'datetime': weekdays[d.weekday],
                                                            'pages': total_pages/num_days,
                                                            'pagevisits': total_pvs/num_days
                                                           })
            else:
                data['page_visits']['week']['average'].append({'datetime': weekdays[d.weekday],
                                                            'pages': total_pages/num_days,
                                                            'pagevisits': total_pvs/num_days
                                                           })

        pages = {}
        domains = {}

        for i in range(31):
            if i < len(month):
                d = month[i]
                date = d.date
                p = json.loads(d.pages)
                pages.update(p)
                domains.update(json.loads(d.domains))
                data['page_visits']['month'].insert(0, {'datetime': date.strftime("%a %m/%d"),
                                                            'pages': len(p.keys()),
                                                            'pagevisits': sum(p.values())
                                                            })
            else:
                date = date - timedelta(days=1)
                data['page_visits']['month'].insert(0, {'datetime': date.strftime("%a %m/%d"),
                                                            'pages': 0,
                                                            'pagevisits': 0
                                                            })

        month_pages = Counter(pages)
        month_domains = Counter(domains)

        month_pages = sorted(month_pages.items(), key=operator.itemgetter(1))
        month_domains = sorted(month_domains.items(), key=operator.itemgetter(1))

        month_pages.reverse()
        month_domains.reverse()

        domains = {}

        for i in range(31):
            if i < len(month):
                d = month[i]
                domains.update(json.loads(d.domains))

        admin_month_domains = Counter(domains)
        admin_month_domains = sorted(admin_month_domains.items(), key=operator.itemgetter(1))
        admin_month_domains.reverse()

        d5_pages = [int(p[0]) for p in day_pages[:5]]
        preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(d5_pages)])
        d5_pages = cu.page_set.filter(pk__in=d5_pages).order_by(preserved)
        data['user_pages']['day'] = [{'title': page.title, 'url': page.url} for page in d5_pages]

        w5_pages = [int(p[0]) for p in week_pages[:5]]
        preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(w5_pages)])
        w5_pages = cu.page_set.filter(pk__in=w5_pages).order_by(preserved)
        data['user_pages']['week'] = [{'title': page.title, 'url': page.url} for page in w5_pages]

        m5_pages = [int(p[0]) for p in month_pages[:5]]
        preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(m5_pages)])
        m5_pages = cu.page_set.filter(pk__in=m5_pages).order_by(preserved)
        data['user_pages']['month'] = [{'title': page.title, 'url': page.url} for page in m5_pages]


        data['user_domains']['day'] = [{'name': d[0], 'value': d[1]} for d in day_domains[:10]]
        if len(day_domains) > 10:
            other = sum([o[1] for o in day_domains[10:]])
            data['user_domains']['day'].append({'name': 'other', 'value': other})

        data['user_domains']['week'] = [{'name': d[0], 'value': d[1]} for d in week_domains[:10]]
        if len(week_domains) > 10:
            other = sum([o[1] for o in week_domains[10:]])
            data['user_domains']['week'].append({'name': 'other', 'value': other})

        data['user_domains']['month'] = [{'name': d[0], 'value': d[1]} for d in month_domains[:10]]
        if len(month_domains) > 10:
            other = sum([o[1] for o in month_domains[10:]])
            data['user_domains']['month'].append({'name': 'other', 'value': other})


        if (Day.objects.filter(date=today.date)
            .exclude(domains='{}')
            .exclude(owned_by__email='admin@hindsitehistory.com')
            .count() >= 10):
            data['hindiste_domains']['day'] = [{'name': d[0], 'value': d[1]} for d in admin_day_domains[:10]]

        data['hindsite_domains']['week'] = [{'name': d[0], 'value': d[1]} for d in admin_week_domains[:10]]
        data['hindsite_domains']['month'] = [{'name': d[0], 'value': d[1]} for d in admin_month_domains[:10]]

        send = AnalyticsSerializer(data)

        return Response(send.data)
