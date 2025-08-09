from django.apps import AppConfig
import redis




class NewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news'

    def ready(self):
        # Код здесь запускается после полной загрузки приложений
        import  news.signals

# red = redis.Redis(
#     host='redis-10740.c245.us-east-1-3.ec2.redns.redis-cloud.com',
#     port=10740,
#     password='HsQ7EuLYd3Ya39wWRHD2RL8oahHNoCOn'
# )