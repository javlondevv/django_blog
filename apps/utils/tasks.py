from celery import shared_task
from django.core.mail import EmailMessage, send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from apps.models import User
from apps.utils.token import one_time_token
from root.settings import EMAIL_HOST_USER


@shared_task
def send_to_gmail(email, domain, _type='activation'):
    print('ACCEPT TASK')
    user = User.objects.get(email=email)
    context = {
        'domain': domain,
        'uid': urlsafe_base64_encode(force_bytes(str(user.pk))),
        'token': one_time_token.make_token(user),
    }
    subject = 'Activate your account'
    template = 'email_activation.html'
    if _type == 'reset':
        subject = 'Trouble signing in?'
        template = 'reset_email_password.html'
    elif _type == 'change':
        subject = ''
    else:
        context['username'] = user.username

    message = render_to_string(f'apps/auth/email/{template}', context)

    # from_email = EMAIL_HOST_USER
    recipient_list = [email]

    email = EmailMessage(subject, message, EMAIL_HOST_USER, recipient_list)
    email.content_subtype = 'html'
    result = email.send()
    print('Send to MAIL', template)
    return result




@shared_task
def send_message_to_gmail(email):
    subject = 'Thanks for your invitation!'
    message = 'Your offer has been reviewed.'
    from_email = EMAIL_HOST_USER
    recipient_list = [email]
    print(subject, message, from_email, recipient_list)
    result = send_mail(subject, message, from_email, recipient_list)
    return result



@shared_task
def send_to_contact(email):
    user = User.objects.get(email=email)
    subject = 'Thanks so much for sharing your experience with us.'
    message = render_to_string('admin/custom/email.html', {})

    # from_email = EMAIL_HOST_USER
    recipient_list = [email]

    email = EmailMessage(subject, message, EMAIL_HOST_USER, recipient_list)
    email.content_subtype = 'html'
    result = email.send()
    print('Send to', email)
    return result