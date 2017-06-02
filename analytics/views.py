from rest_framework.views import APIView
from django.utils import timezone
from datetime import datetime, timedelta
import json
from collections import Counter
import operator
import ast, pytz
from django.db.models import Case, When
from rest_framework.response import Response
from history.models import PageVisit
from authentication.models import CustomUser
from analytics.models import Day
from hindsite.constants import weekdays
from analytics.serializers import AnalyticsSerializer, ProcrastinationSitesSerializer


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
                    },
                    'productivity': {
                        'procrastination_sites': ast.literal_eval(cu.procrastination_sites),
                        'visits': {
                            'day': [],
                            'week': [],
                            'month': []
                        },
                        'minutes': {
                            'day': [],
                            'week': [],
                            'month': []
                        }
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
        day_domains = [a for a in day_domains if a[0] is not '']

        admin_day_domains = Counter(json.loads(admin_today.domains))
        admin_day_domains = sorted(admin_day_domains.items(), key=operator.itemgetter(1))
        admin_day_domains.reverse()
        admin_day_domains = [a for a in admin_day_domains if a[0] is not '']

        pages = Counter({})
        domains = Counter({})

        # Current Week stats for user
        for d in current:
            p = Counter(json.loads(d.pages))
            pages += p
            domains += Counter(json.loads(d.domains))
            data['page_visits']['week']['current'].append({'datetime': weekdays[d.weekday],
                                                           'pages': len(p.keys()),
                                                           'pagevisits': sum(p.values())
                                                           })

        week_pages = sorted(pages.items(), key=operator.itemgetter(1))
        week_domains = sorted(domains.items(), key=operator.itemgetter(1))

        week_pages.reverse()

        week_domains.reverse()
        week_domains = [a for a in week_domains if a[0] is not '']

        domains = Counter({})

        # Current Week stats across hindsite
        for d in admin_current:
            domains += Counter(json.loads(d.domains))

        admin_week_domains = sorted(domains.items(), key=operator.itemgetter(1))
        admin_week_domains.reverse()
        admin_week_domains = [a for a in admin_week_domains if a[0] is not '']

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

        pages = Counter({})
        domains = Counter({})

        for i in range(31):
            if i < len(month):
                d = month[i]
                date = d.date
                p = Counter(json.loads(d.pages))
                pages += p
                domains += Counter(json.loads(d.domains))
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

        month_pages = sorted(pages.items(), key=operator.itemgetter(1))
        month_domains = sorted(domains.items(), key=operator.itemgetter(1))

        month_pages.reverse()

        month_domains.reverse()
        month_domains = [a for a in month_domains if a[0] is not '']

        domains = Counter({})

        for i in range(31):
            if i < len(admin_month):
                d = admin_month[i]
                domains += Counter(json.loads(d.domains))

        admin_month_domains = sorted(domains.items(), key=operator.itemgetter(1))
        admin_month_domains.reverse()
        admin_month_domains = [a for a in admin_month_domains if a[0] is not '']

        d5_pages = [int(p[0]) for p in day_pages[:8]]
        preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(d5_pages)])
        d5_pages = cu.page_set.filter(pk__in=d5_pages).order_by(preserved)
        data['user_pages']['day'] = [{'title': page.title, 'url': page.url} for page in d5_pages if page.title is not '']

        w5_pages = [int(p[0]) for p in week_pages[:8]]
        preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(w5_pages)])
        w5_pages = cu.page_set.filter(pk__in=w5_pages).order_by(preserved)
        data['user_pages']['week'] = [{'title': page.title, 'url': page.url} for page in w5_pages if page.title is not '']

        m5_pages = [int(p[0]) for p in month_pages[:8]]
        preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(m5_pages)])
        m5_pages = cu.page_set.filter(pk__in=m5_pages).order_by(preserved)
        data['user_pages']['month'] = [{'title': page.title, 'url': page.url} for page in m5_pages if page.title is not '']


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
            data['hindsite_domains']['day'] = [{'name': d[0], 'value': d[1]} for d in admin_day_domains[:10]]

        data['hindsite_domains']['week'] = [{'name': d[0], 'value': d[1]} for d in admin_week_domains[:10]]
        data['hindsite_domains']['month'] = [{'name': d[0], 'value': d[1]} for d in admin_month_domains[:10]]

        # productivity/procrastination stats
        prod = sum([d[1] for d in day_domains]) - today.procrastination_visits
        data['productivity']['visits']['day'] = [{'name': 'productivity', 'value': prod},
                            {'name': 'procrastination', 'value': today.procrastination_visits}]

        procr = sum([d.procrastination_visits for d in current])
        prod = sum([d[1] for d in week_domains]) - procr
        data['productivity']['visits']['week'] = [{'name': 'productivity', 'value': prod},
                                                {'name': 'procrastination', 'value': procr}]

        procr = sum([d.procrastination_visits for d in month])
        prod = sum([d[1] for d in month_domains]) - procr
        data['productivity']['visits']['month'] = [{'name': 'productivity', 'value': prod},
                                                {'name': 'procrastination', 'value': procr}]

        data['productivity']['minutes']['day'] = [{'name': 'productivity', 'value': today.productivity_mins},
                                                {'name': 'procrastination', 'value': today.procrastination_mins}]

        procr = sum([d.procrastination_mins for d in current])
        prod = sum([d.productivity_mins for d in current])
        data['productivity']['minutes']['week'] = [{'name': 'productivity', 'value': prod},
                                                {'name': 'procrastination', 'value': procr}]

        procr = sum([d.procrastination_mins for d in month])
        prod = sum([d.productivity_mins for d in month])
        data['productivity']['minutes']['month'] = [{'name': 'productivity', 'value': prod},
                                                {'name': 'procrastination', 'value': procr}]

        send = AnalyticsSerializer(data)

        return Response(send.data)


class AddProcrastination(APIView):

    def post(self, request, format=None):
        cu = request.user

        new_site = request.data['domain']

        procr_sites = ast.literal_eval(cu.procrastination_sites)

        if new_site.startswith('http://'):
            new_site = new_site[7:]
        elif new_site.startswith('https://'):
            new_site = new_site[8:]

        if new_site not in procr_sites:
            procr_sites.insert(0, new_site)
            cu.procrastination_sites = str(procr_sites)
            cu.save()

        # days = cu.day_set.all()
        #
        # for d in days:
        #     start = datetime(month=d.date.month, day=d.date.day, year=d.date.year, tzinfo=pytz.UTC) - timedelta(hours=cu.offset)
        #     end = start + timedelta(hours=24)
        #     procr_doms = cu.domain_set.filter(closed__range=(start, end), base_url=new_site)
        #
        #     procr_mins = 0
        #     procr_visits = 0
        #     for dom in procr_doms:
        #         procr_mins += dom.timeactive()[0]
        #         procr_visits += dom.pagecount
        #
        #     d.procrastination_mins = d.procrastination_mins + procr_mins
        #     d.productivity_mins = d.productivity_mins - procr_mins
        #     d.procrastination_visits = d.procrastination_visits + procr_visits
        #     d.save()
        #
        #
        # data = {'productivity': {
        #             'procrastination_sites': procr_sites,
        #             'visits': {
        #                 'day': [],
        #                 'week': [],
        #                 'month': []
        #             },
        #             'minutes': {
        #                 'day': [],
        #                 'week': [],
        #                 'month': []
        #             }
        #         }
        #     }
        #
        # days = days.reverse()
        #
        # today = days.first()
        # week = days[:7][::-1]
        # last = days[7:14][::-1]
        # month = days[:31]
        #
        # today_start = datetime(month=today.date.month, day=today.date.day, year=today.date.year, tzinfo=pytz.UTC) - timedelta(hours=cu.offset)
        # week_start = datetime(month=week[6].date.month, day=week[6].date.day, year=week[6].date.year, tzinfo=pytz.UTC) - timedelta(hours=cu.offset)
        # month_start = datetime(month=month[30].date.month, day=month[30].date.day, year=month[30].date.year, tzinfo=pytz.UTC) - timedelta(hours=cu.offset)
        #
        # pvs_day = cu.pagevisit_set.filter(visited__gt=today_start).count()
        # pvs_week = cu.pagevisit_set.filter(visited__gt=week_start).count()
        # pvs_month = cu.pagevisit_set.filter(visited__gt=month_start).count()
        #
        # data['productivity']['visits']['day'] = [{'name': 'productivity', 'value': pvs_day - today.procrastination_visits},
        #                     {'name': 'procrastination', 'value': today.procrastination_visits}]
        #
        # procr = sum([d.procrastination_visits for d in week])
        # data['productivity']['visits']['week'] = [{'name': 'productivity', 'value': pvs_week - procr},
        #                                         {'name': 'procrastination', 'value': procr}]
        #
        # procr = sum([d.procrastination_visits for d in month])
        # data['productivity']['visits']['month'] = [{'name': 'productivity', 'value': pvs_month - procr},
        #                                         {'name': 'procrastination', 'value': procr}]
        #
        # data['productivity']['minutes']['day'] = [{'name': 'productivity', 'value': today.productivity_mins},
        #                                         {'name': 'procrastination', 'value': today.procrastination_mins}]
        #
        # procr = sum([d.procrastination_mins for d in week])
        # prod = sum([d.productivity_mins for d in week])
        # data['productivity']['minutes']['week'] = [{'name': 'productivity', 'value': prod},
        #                                         {'name': 'procrastination', 'value': procr}]
        #
        # procr = sum([d.procrastination_mins for d in month])
        # prod = sum([d.productivity_mins for d in month])
        # data['productivity']['minutes']['month'] = [{'name': 'productivity', 'value': prod},
        #                                         {'name': 'procrastination', 'value': procr}]
        #
        # send = ProcrastinationSitesSerializer(data)

        send = ProcrastinationSitesSerializer({'procrastination_sites': procr_sites})

        return Response(send.data)

class RemoveProcrastination(APIView):

    def post(self, request, format=None):
        cu = request.user

        domain = request.data['domain']

        procr_sites = ast.literal_eval(cu.procrastination_sites)

        if domain in procr_sites:
            procr_sites.remove(domain)
            cu.procrastination_sites = str(procr_sites)
            cu.save()

        # days = cu.day_set.all()
        #
        # for d in days:
        #     start = datetime(month=d.date.month, day=d.date.day, year=d.date.year, tzinfo=pytz.UTC) - timedelta(hours=cu.offset)
        #     end = start + timedelta(hours=24)
        #     procr_doms = cu.domain_set.filter(closed__range=(start, end), base_url=domain)
        #
        #     procr_mins = 0
        #     procr_visits = 0
        #     for dom in procr_doms:
        #         procr_mins += dom.timeactive()[0]
        #         procr_visits += dom.pagecount
        #
        #     d.procrastination_mins = d.procrastination_mins - procr_mins
        #     d.productivity_mins = d.productivity_mins + procr_mins
        #     d.procrastination_visits = d.procrastination_visits - procr_visits
        #     d.save()
        #
        # data = {'productivity': {
        #             'procrastination_sites': procr_sites,
        #             'visits': {
        #                 'day': [],
        #                 'week': [],
        #                 'month': []
        #             },
        #             'minutes': {
        #                 'day': [],
        #                 'week': [],
        #                 'month': []
        #             }
        #         }
        #     }
        #
        # days = days.reverse()
        #
        # today = days.first()
        # week = days[:7][::-1]
        # last = days[7:14][::-1]
        # month = days[:31]
        #
        # today_start = datetime(month=today.date.month, day=today.date.day, year=today.date.year, tzinfo=pytz.UTC) - timedelta(hours=cu.offset)
        # week_start = datetime(month=week[6].date.month, day=week[6].date.day, year=week[6].date.year, tzinfo=pytz.UTC) - timedelta(hours=cu.offset)
        # month_start = datetime(month=month[30].date.month, day=month[30].date.day, year=month[30].date.year, tzinfo=pytz.UTC) - timedelta(hours=cu.offset)
        #
        # pvs_day = cu.pagevisit_set.filter(visited__gt=today_start).count()
        # pvs_week = cu.pagevisit_set.filter(visited__gt=week_start).count()
        # pvs_month = cu.pagevisit_set.filter(visited__gt=month_start).count()
        #
        # data['productivity']['visits']['day'] = [{'name': 'productivity', 'value': pvs_day - today.procrastination_visits},
        #                     {'name': 'procrastination', 'value': today.procrastination_visits}]
        #
        # procr = sum([d.procrastination_visits for d in week])
        # data['productivity']['visits']['week'] = [{'name': 'productivity', 'value': pvs_week - procr},
        #                                         {'name': 'procrastination', 'value': procr}]
        #
        # procr = sum([d.procrastination_visits for d in month])
        # data['productivity']['visits']['month'] = [{'name': 'productivity', 'value': pvs_month - procr},
        #                                         {'name': 'procrastination', 'value': procr}]
        #
        # data['productivity']['minutes']['day'] = [{'name': 'productivity', 'value': today.productivity_mins},
        #                                         {'name': 'procrastination', 'value': today.procrastination_mins}]
        #
        # procr = sum([d.procrastination_mins for d in week])
        # prod = sum([d.productivity_mins for d in week])
        # data['productivity']['minutes']['week'] = [{'name': 'productivity', 'value': prod},
        #                                         {'name': 'procrastination', 'value': procr}]
        #
        # procr = sum([d.procrastination_mins for d in month])
        # prod = sum([d.productivity_mins for d in month])
        # data['productivity']['minutes']['month'] = [{'name': 'productivity', 'value': prod},
        #                                         {'name': 'procrastination', 'value': procr}]
        #
        # send = ProcrastinationSitesSerializer(data)

        send = ProcrastinationSitesSerializer({'procrastination_sites': procr_sites})

        return Response(send.data)
