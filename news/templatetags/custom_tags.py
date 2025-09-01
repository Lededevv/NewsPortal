from datetime import datetime

import pytz
from django import template
from django.utils import timezone

register = template.Library()


@register.simple_tag()
def current_time(format_string='%b %d %Y'):
   return datetime.utcnow().strftime(format_string)



@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
   d = context['request'].GET.copy()
   for k, v in kwargs.items():
       d[k] = v
   return d.urlencode()


@register.simple_tag(takes_context=True)
def get_session_time(context):
    """
    Возвращает текущее время, учитывая установленную временную зону в сессии.
    """
    request = context.get('request')
    if request:
        user_tz = request.session.get('django_timezone')
        if user_tz:
            timezone.activate(pytz.timezone(user_tz))
            return timezone.localtime()
    return timezone.now()


@register.simple_tag(takes_context=True)
def get_timezones(context):
     # request = context.get('request')
     return pytz.common_timezones


@register.simple_tag(takes_context=True)
def get_times(context):
    request = context.get('request')
    if request:
        # Пробуем получить временную зону из сессии
        user_tz = request.session.get('django_timezone')

        # Если временная зона не установлена, возвращаем UTC
        if not user_tz:
            return 'UTC'

        return user_tz
    return ''