from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.utils import timezone
from decouple import config
from .models import Notification


def send_email(to_email, subject, html_content, appointment, notification_type):
    if not to_email:
        return False

    notification = Notification.objects.create(
        appointment=appointment,
        type=notification_type,
        channel='email',
        status='pending'
    )

    try:
        message = Mail(
            from_email=config('DEFAULT_FROM_EMAIL', default='noreply@agendasaas.com'),
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )

        sg = SendGridAPIClient(config('SENDGRID_API_KEY'))
        sg.send(message)

        notification.status = 'sent'
        notification.sent_at = timezone.now()
        notification.save()
        return True

    except Exception as e:
        notification.status = 'failed'
        notification.error_message = str(e)
        notification.save()
        return False


def send_confirmation(appointment):
    owner_email = appointment.business.owner.email
    subject = f"Nueva cita agendada - {appointment.client_name}"
    html_content = f"""
    <h2>Nueva cita agendada</h2>
    <p>Se ha agendado una nueva cita en <strong>{appointment.business.name}</strong>:</p>
    <table>
        <tr><td><strong>Cliente:</strong></td><td>{appointment.client_name}</td></tr>
        <tr><td><strong>Teléfono:</strong></td><td>{appointment.client_phone}</td></tr>
        <tr><td><strong>Servicio:</strong></td><td>{appointment.service.name}</td></tr>
        <tr><td><strong>Profesional:</strong></td><td>{appointment.professional.user.get_full_name()}</td></tr>
        <tr><td><strong>Fecha:</strong></td><td>{appointment.start_datetime.strftime('%d/%m/%Y')}</td></tr>
        <tr><td><strong>Hora:</strong></td><td>{appointment.start_datetime.strftime('%I:%M %p')}</td></tr>
    </table>
    """
    return send_email(
        to_email=owner_email,
        subject=subject,
        html_content=html_content,
        appointment=appointment,
        notification_type='confirmation'
    )


def send_reminder(appointment, hours_before=24):
    owner_email = appointment.business.owner.email
    notification_type = 'reminder_24h' if hours_before == 24 else 'reminder_1h'
    tiempo = 'mañana' if hours_before == 24 else 'en 1 hora'
    subject = f"Recordatorio - Cita de {appointment.client_name} {tiempo}"
    html_content = f"""
    <h2>Recordatorio de cita</h2>
    <p>Recuerda que tienes una cita {tiempo} en <strong>{appointment.business.name}</strong>:</p>
    <table>
        <tr><td><strong>Cliente:</strong></td><td>{appointment.client_name}</td></tr>
        <tr><td><strong>Teléfono:</strong></td><td>{appointment.client_phone}</td></tr>
        <tr><td><strong>Servicio:</strong></td><td>{appointment.service.name}</td></tr>
        <tr><td><strong>Profesional:</strong></td><td>{appointment.professional.user.get_full_name()}</td></tr>
        <tr><td><strong>Fecha:</strong></td><td>{appointment.start_datetime.strftime('%d/%m/%Y')}</td></tr>
        <tr><td><strong>Hora:</strong></td><td>{appointment.start_datetime.strftime('%I:%M %p')}</td></tr>
    </table>
    """
    return send_email(
        to_email=owner_email,
        subject=subject,
        html_content=html_content,
        appointment=appointment,
        notification_type=notification_type
    )