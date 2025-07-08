from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import EmailSender
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()

# This signal ensures that a Profile instance is created whenever a new User is created,
# and that the Profile instance is saved whenever the User instance is saved.

@receiver(m2m_changed, sender=EmailSender.receivers.through)
def send_email_on_creation(sender, instance, action, **kwargs):
    if action == "post_add":
        for user in instance.receivers.all():
            if user.email:
                send_mail(
                    subject=instance.subject,
                    message=instance.message,
                    from_email='ssmartmine@gmail.com',
                    recipient_list=[user.email],
                    fail_silently=False,
                )
