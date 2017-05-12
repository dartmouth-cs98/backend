from celery import task
from django.utils import timezone
from datetime import timedelta
from django.core.mail import EmailMessage
from authentication.models import CustomUser
from history.models import Category
from analytics.models import Day
from history.utils import create_page_login
from django.utils import timezone
from history.common import is_blacklisted


@task
def complete_signup(user_pk):

    customuser = CustomUser.objects.get(pk=user_pk)

    email = EmailMessage('Successfully Created Account!',
            'Thank you for signing up to use Hindsite! \n\nThe Hindsite Team',
            to=[customuser.email])

    email.send()

    date = (timezone.now() - timedelta(hours=customuser.offset)).date()

    day = Day(owned_by=customuser, date=date, weekday=date.weekday())
    day.save()

    research = Category(title='Research', owned_by=customuser, color='#FA6E59')
    cooking = Category(title='Cooking', owned_by=customuser, color='#77F200')
    travel = Category(title='Travel', owned_by=customuser, color='#FFDB5C')
    news = Category(title='News', owned_by=customuser, color='#F8A055')
    research.save()
    cooking.save()
    travel.save()
    news.save()

    return True

@task
def forgot_password(user_pk):
    new_pw = CustomUser.objects.make_random_password()

    customuser = CustomUser.objects.get(pk=user_pk)

    customuser.set_password(new_pw)

    customuser.save()

    email = EmailMessage('New Password',
            'The new password for your account is: ' + new_pw,
            to=[email_send])

    email.send()

@task
def change_password(user_pk, new_pw):
    customuser = CustomUser.objects.get(pk=user_pk)

    customuser.set_password(new_pw)
    customuser.save()

    email = EmailMessage('Changed Password',
            'You have successfully changed your password! \n\n If this was not you please reply to this email.\n\nThe Hindsite Team',
            to=[customuser.email])

    email.send()

@task
def close_all(user_pk):
    cu = CustomUser.objects.get(pk=user_pk)
    time = timezone.now()

    for d in cu.domain_set.filter(closed__isnull=True):
        d.closed = time
        d.save()
        d.tab.closed = time
        d.tab.save()

    ta = cu.timeactive_set.filter(end__isnull=True)

    if ta.exists():
        ta = ta.first()
        ta.end = time
        ta.save()
