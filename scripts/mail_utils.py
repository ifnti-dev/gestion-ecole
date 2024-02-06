from django.core.mail import send_mail
from django.conf import settings
from celery import shared_task
from time import sleep


@shared_task
def send_email_task(subject, message, email_address):
    sleep(5)
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=email_address,
        fail_silently=False,
    )

