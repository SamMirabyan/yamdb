from django.conf import settings
from django.core.mail import send_mail

EMAIL_MESSAGE = '''
    Добро пожаловать в YaMDb!.

    Ваше имя на портале: {username}.
    Ваш код подтверждения: {code}.
    Для получения токена доступа используйте этот код подтверждения и ваше имя.

    Ссылка на получение токена доступа: {url}.

    Если вы получили это письмо по ошибке, скорее всего, другой пользователь
    случайно ввел адрес вашей электронной почты.

    Если вы не направляли запрос на получение данных, мы просим вас
    игнорировать указанную в настоящем письме информацию.

    С заботой о вас,
    Команда YaMDb API.
'''


def send_confirmation_email(username, email, confirmation_code,
                            raw_message=EMAIL_MESSAGE,
                            token_url=settings.TOKEN_OBTAIN_URL,
                            subject='Message from YaMDb Team!',
                            *args, **kwargs):
    message = raw_message.format(username=username, code=confirmation_code,
                                 url=token_url)
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )
