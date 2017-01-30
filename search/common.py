from django.utils import timezone

def datetime_formatter(t):
    return str(t.year) + '-'+ str(t.month) + '-' + str(t.day) + 'T' + str(t.hour) + ':' + str(t.minute) + ':' + str(t.second)
