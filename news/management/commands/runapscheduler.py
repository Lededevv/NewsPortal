from django.core.mail import send_mass_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

from ...models import Post, Category, User  # импорт нужных моделей

from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import register_events

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import timedelta
from django.utils.timezone import now


# Очень простое задание для проверки работы планировщика

def send_weekly_digest():
    print('Начало выполнения send_weekly_digest!')
    one_week_ago = now() - timedelta(days=7)
    users_with_subscriptions = User.objects.exclude(subscribed_categories=None)

    for user in users_with_subscriptions:
        print(user)
        subscribed_categories = user.subscribed_categories.all()
        recent_posts = Post.objects.filter(
            category__in=subscribed_categories,
            time_in__gte=one_week_ago
        ).distinct().prefetch_related('category')

        if recent_posts.exists():
            context = {'posts': list(recent_posts)}
            print(list(recent_posts))

            # Генерируем HTML и текстовую версии письма
            html_message = render_to_string('emails/weekly_digest.html', context)
            plain_message = render_to_string('emails/weekly_digest.txt', context)

            subject = '[Новости портала]: Ваши избранные статьи за неделю'
            from_email = settings.DEFAULT_FROM_EMAIL
            to_emails = [user.email]

            # Отправляем письмо с двумя версиями
            msg = EmailMultiAlternatives(subject, plain_message, from_email, to_emails)
            msg.attach_alternative(html_message, "text/html")
            msg.send()

    print('Завершение выполнения send_weekly_digest.')


class Command(BaseCommand):
    help = "Test the AP Scheduler functionality"

    def handle(self, *args, **options):
        scheduler = BackgroundScheduler(timezone="Asia/Yekaterinburg")  # устанавливаем часовой пояс

        # Зарегистрируем событие очистки старых записей
        register_events(scheduler)
        scheduler.add_job(
            send_weekly_digest,
            'cron',
            day_of_week='thu',
            hour=1, minute=15
        )

        try:
            self.stdout.write("Запуск планировщика...")
            scheduler.start()

            # Поддерживаем планировщик активным, чтобы дождаться выполнения заданий
            while True:
                pass
        except KeyboardInterrupt:
            self.stdout.write("Остановка планировщика...")
            scheduler.shutdown()
            self.stdout.write("Планировщик остановлен!")
