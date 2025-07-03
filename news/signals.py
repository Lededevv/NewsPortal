from django.dispatch import receiver
from allauth.socialaccount.signals import social_account_added
from django.contrib.auth.models import Group

@receiver(social_account_added)
def add_to_common_group(sender, request, sociallogin, **kwargs):
    user = sociallogin.user
    try:
        group = Group.objects.get(name='common')
        group.user_set.add(user)
    except Group.DoesNotExist:
        pass