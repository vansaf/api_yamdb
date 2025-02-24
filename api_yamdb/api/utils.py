from random import choice
from django.core.mail import send_mail


def generate_confirmation_code():
    return ''.join(choice('0123456789') for _ in range(6))


def send_confirmation_code(email, confirmation_code):
    subject = 'Подтверждение регистрации'
    message = f'Код подтверждения: {confirmation_code}'
    from_email = 'support_yamdb@yandex.ru'
    recipient_list = (email, )
    send_mail(subject, message, from_email, recipient_list)
