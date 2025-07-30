import logging

from django.core.exceptions import ValidationError
from django.dispatch import receiver
from allauth.socialaccount.signals import social_account_added
from django.contrib.auth.models import Group
from django.db.models.signals import post_save, m2m_changed, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.timezone import now

from .models import Post, Category, PostCategory


@receiver(social_account_added)
def add_to_common_group(sender, request, sociallogin, **kwargs):
    user = sociallogin.user
    try:
        group = Group.objects.get(name='common')
        group.user_set.add(user)
    except Group.DoesNotExist:
        pass


logger = logging.getLogger(__name__)


def send_notification(instance):
    categories = instance.category.all()
    print('categories')
    recipients = set()  # уникальный набор email подписчиков

    # Собираем подписчиков каждой категории
    for category in categories:
        subscribers = category.subscribers.all()
        print(subscribers)
        for subscriber in subscribers:
            recipients.add(subscriber.email)
    print(recipients)
    if len(recipients) > 0:
        subject = f"{instance.heading}"  # тема письма равна заголовку поста
        event_type = "Новое"
        text_body = f'{instance.text[:50]}...'  # первые 50 символов текста
        category_names = ', '.join([cat.name for cat in categories])  # список категорий
        post_link = instance.get_absolute_url()  # Получаем относительный URL


        domain = settings.SITE_DOMAIN  # пример: 'http://example.com'
        absolute_post_link = f"{domain}{post_link}"

        # Формирование письма
        for email in recipients:
            user = next((sub for sub in subscribers if sub.email == email), None)
            if not user:
                continue  # пропускаем пользователя, если не найден
            print("send")
            html_message = render_to_string('message_template.html', {
                'type_event': event_type,
                'username': user.username,
                'categories': category_names,
                'subject': subject,
                'body_text': text_body,
                'post_link': absolute_post_link  # Передаем полную ссылку'
            })

            # Создание и отправка письма
            msg = EmailMultiAlternatives(
                subject=f'News Portal: {subject}',
                body='',  # пустой текст, так как используем HTML
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email]
            )
            msg.attach_alternative(html_message, "text/html")

            try:
                msg.send()
                logger.info(f"Письмо отправлено на {email} успешно.")
            except Exception as e:
                logger.error(f"Ошибка отправки письма на {email}: {str(e)}")


# Сигнал post_save обрабатывает создание поста
# @receiver(post_save, sender=Post)
# def notify_subscribers_post_save(sender, instance, created, **kwargs):
#     send_notification(instance)


# Сигнал m2m_changed обрабатывает изменения связей many-to-many
@receiver(m2m_changed, sender=Post.category.through, weak= False)
def notify_subscribers_m2m(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action == 'post_add':  # обрабатываем только добавление категорий
        # отправляем уведомления после добавления категорий
        print(instance.heading, instance.category.all())
        send_notification(instance)


@receiver(pre_save, sender=Post)
def check_posts_limit(sender, instance, **kwargs):
    today = now().date()
    posts_today_count = Post.objects.filter(
        author=instance.author,
        time_in__date=today
    ).count()
    print(posts_today_count)
    if posts_today_count > 3:
        raise ValidationError("Вы превысили дневной лимит публикаций!")