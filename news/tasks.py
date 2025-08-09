from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from datetime import timedelta
from django.utils.timezone import now
from .models import Post, Category, User


@shared_task
def send_weekly_digest():
    print('Начало выполнения send_weekly_digest!')
    one_week_ago = now() - timedelta(days=7)
    users_with_subscriptions = User.objects.exclude(subscribed_categories=None)

    for user in users_with_subscriptions:
        subscribed_categories = user.subscribed_categories.all()
        recent_posts = Post.objects.filter(category__in=subscribed_categories,
                                           time_in__gte=one_week_ago).distinct().prefetch_related('category')

        if recent_posts.exists():
            context = {'posts': list(recent_posts)}

            # Генерируем HTML и текстовую версию письма
            html_message = render_to_string('emails/weekly_digest.html', context)
            plain_message = render_to_string('emails/weekly_digest.txt', context)

            subject = '[Новости портала]: Ваши избранные статьи за неделю'
            from_email = settings.DEFAULT_FROM_EMAIL
            to_emails = [user.email]

            # Создаем и отправляем письмо
            msg = EmailMultiAlternatives(subject, plain_message, from_email, to_emails)
            msg.attach_alternative(html_message, "text/html")
            msg.send()

    print('Завершение выполнения send_weekly_digest.')


@shared_task
def send_notification(instance_id):
    print('начало выполнения send_notification')
    instance = Post.objects.get(id=instance_id)
    categories = instance.category.all()
    recipients = set()

    # Собираем подписчиков каждой категории
    for category in categories:
        subscribers = category.subscribers.all()
        for subscriber in subscribers:
            recipients.add(subscriber.email)

    if len(recipients) > 0:
        subject = f"{instance.heading}"
        event_type = "Новое"
        text_body = f'{instance.text[:50]}...'
        category_names = ', '.join([cat.name for cat in categories])
        post_link = instance.get_absolute_url()
        domain = settings.SITE_DOMAIN
        absolute_post_link = f"{domain}{post_link}"

        # Формируем сообщение и отправляем письма
        for email in recipients:
            user = next((sub for sub in subscribers if sub.email == email), None)
            if not user:
                continue

            html_message = render_to_string('message_template.html', {
                'type_event': event_type,
                'username': user.username,
                'categories': category_names,
                'subject': subject,
                'body_text': text_body,
                'post_link': absolute_post_link
            })

            msg = EmailMultiAlternatives(
                subject=f'News Portal: {subject}',
                body='',  # Пустое тело, так как используется HTML
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email]
            )
            msg.attach_alternative(html_message, "text/html")
            msg.send()
