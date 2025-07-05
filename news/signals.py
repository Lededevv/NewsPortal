import logging

from django.dispatch import receiver
from allauth.socialaccount.signals import social_account_added
from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string

from .models import Post, Category


@receiver(social_account_added)
def add_to_common_group(sender, request, sociallogin, **kwargs):
    user = sociallogin.user
    try:
        group = Group.objects.get(name='common')
        group.user_set.add(user)
    except Group.DoesNotExist:
        pass




logger = logging.getLogger(__name__)

@receiver(post_save, sender=Post)
def notify_subscribers(sender, instance, **kwargs):
    categories = instance.category.all()
    recipients = set()
    for category in categories:
        subscribers = category.subscribers.all()
        for subscriber in subscribers:
            recipients.add(subscriber.email)

    if len(recipients) > 0:
        subject = instance.heading
        first_fifty_chars = instance.text[:50]

        # Индивидуально отправляем письма каждому подписчику
        for email in recipients:
            user = next((sub for sub in subscribers if sub.email == email), None)
            if user:
                # Рендерим HTML-шаблон письма с данными пользователя
                html_message = render_to_string('message_template.html', {
                    'username': user.username,
                    'subject': subject,
                    'first_fifty_chars': first_fifty_chars
                })

                # Создаем электронное письмо с HTML-контентом
                msg = EmailMultiAlternatives(
                    subject=subject,
                    body='',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[email]
                )
                msg.attach_alternative(html_message, "text/html")  # Присоединяем HTML-контент
                try:
                    msg.send()
                    logger.info(f"Письмо отправлено на {email} успешно.")
                except Exception as e:
                    logger.error(f"Ошибка отправки письма на {email}: {str(e)}")