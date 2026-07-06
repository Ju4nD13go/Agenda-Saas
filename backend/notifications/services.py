from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.utils import timezone
from decouple import config
from .models import Notification


def send_email(to_email, subject, html_content, appointment, notification_type):
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
    subject = f"Cita confirmada - {appointment.service.name}"
    html_content = f"""
    <h2>¡Tu cita está confirmada!</h2>
    <p>Hola <strong>{appointment.client_name}</strong>,</p>
    <p>Tu cita ha sido confirmada con los siguientes detalles:</p>
    <table>
        <tr><td><strong>Servicio:</strong></td><td>{appointment.service.name}</td></tr>
        <tr><td><strong>Profesional:</strong></td><td>{appointment.professional.user.get_full_name()}</td></tr>
        <tr><td><strong>Fecha:</strong></td><td>{appointment.start_datetime.strftime('%d/%m/%Y')}</td></tr>
        <tr><td><strong>Hora:</strong></td><td>{appointment.start_datetime.strftime('%I:%M %p')}</td></tr>
        <tr><td><strong>Negocio:</strong></td><td>{appointment.business.name}</td></tr>
        <tr><td><strong>Dirección:</strong></td><td>{appointment.business.address}</td></tr>
    </table>
    <p>Si necesitas cancelar tu cita, contáctanos al {appointment.business.phone}.</p>
    """
    return send_email(
        to_email=None,
        subject=subject,
        html_content=html_content,
        appointment=appointment,
        notification_type='confirmation'
    )


def send_reminder(appointment, hours_before=24):
    notification_type = 'reminder_24h' if hours_before == 24 else 'reminder_1h'
    subject = f"Recordatorio - Tu cita es {'mañana' if hours_before == 24 else 'en 1 hora'}"
    html_content = f"""
    <h2>Recordatorio de cita</h2>
    <p>Hola <strong>{appointment.client_name}</strong>,</p>
    <p>Te recordamos que tienes una cita {'mañana' if hours_before == 24 else 'en 1 hora'}:</p>
    <table>
        <tr><td><strong>Servicio:</strong></td><td>{appointment.service.name}</td></tr>
        <tr><td><strong>Profesional:</strong></td><td>{appointment.professional.user.get_full_name()}</td></tr>
        <tr><td><strong>Fecha:</strong></td><td>{appointment.start_datetime.strftime('%d/%m/%Y')}</td></tr>
        <tr><td><strong>Hora:</strong></td><td>{appointment.start_datetime.strftime('%I:%M %p')}</td></tr>
        <tr><td><strong>Dirección:</strong></td><td>{appointment.business.address}</td></tr>
    </table>
    <p>Si necesitas cancelar, contáctanos al {appointment.business.phone}.</p>
    """
    return send_email(
        to_email=None,
        subject=subject,
        html_content=html_content,
        appointment=appointment,
        notification_type=notification_type
    )