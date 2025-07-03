from django.apps import AppConfig


class NewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news'

    def ready(self):
        # Код здесь запускается после полной загрузки приложений
        import news.signals  # Активируйте сигнал здесь