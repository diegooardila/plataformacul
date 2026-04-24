import os
import smtplib
import threading
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "Plataforma CUL")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "")

_BASE_STYLE = """
    body { font-family: Arial, sans-serif; background: #f4f6f8; margin: 0; padding: 0; }
    .wrapper { max-width: 600px; margin: 40px auto; background: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
    .header { background: #0a2463; padding: 28px 32px; text-align: center; }
    .header h1 { color: #ffffff; font-size: 22px; margin: 0; letter-spacing: 1px; }
    .header p { color: #a8c0e8; font-size: 13px; margin: 6px 0 0; }
    .body { padding: 32px; color: #333333; }
    .body h2 { color: #0a2463; font-size: 18px; margin-top: 0; }
    .body p { line-height: 1.6; font-size: 15px; }
    .info-box { background: #f0f4ff; border-left: 4px solid #0a2463; border-radius: 4px; padding: 16px 20px; margin: 20px 0; }
    .info-box p { margin: 4px 0; font-size: 14px; }
    .info-box strong { color: #0a2463; }
    .badge { display: inline-block; padding: 4px 12px; border-radius: 12px; font-size: 13px; font-weight: bold; }
    .badge-success { background: #d4edda; color: #155724; }
    .badge-warning { background: #fff3cd; color: #856404; }
    .badge-danger { background: #f8d7da; color: #721c24; }
    .footer { background: #f0f4ff; padding: 18px 32px; text-align: center; font-size: 12px; color: #888888; border-top: 1px solid #e0e6f0; }
    .footer a { color: #0a2463; text-decoration: none; }
"""

def _build_email(subject: str, body_html: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><style>{_BASE_STYLE}</style></head>
<body>
  <div class="wrapper">
    <div class="header">
      <h1>Plataforma CUL</h1>
      <p>Corporación Universitaria Latinoamericana</p>
    </div>
    <div class="body">
      {body_html}
    </div>
    <div class="footer">
      <p>Este es un correo automático, por favor no responda a este mensaje.</p>
      <p>&copy; 2026 Plataforma CUL &mdash; Todos los derechos reservados.</p>
    </div>
  </div>
</body>
</html>"""


def _send(to_email: str, subject: str, html: str):
    if not SMTP_USER or not SMTP_PASSWORD:
        print(f"[Email] SMTP no configurado — omitiendo notificación a {to_email}")
        return
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{SMTP_FROM_NAME} <{SMTP_USER}>"
        msg["To"] = to_email
        msg.attach(MIMEText(html, "html", "utf-8"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, [to_email], msg.as_string())
        print(f"[Email] Enviado a {to_email} | {subject}")
    except Exception as exc:
        print(f"[Email] Error al enviar a {to_email}: {exc}")


def _send_async(to_email: str, subject: str, html: str):
    threading.Thread(target=_send, args=(to_email, subject, html), daemon=True).start()


# ─── Notificaciones de Usuario ────────────────────────────────────────────────

def notify_user_created(full_name: str, user_email: str, role: str):
    subject = "Bienvenido a la Plataforma CUL"
    body = f"""
        <h2>¡Bienvenido, {full_name}!</h2>
        <p>Tu cuenta en la Plataforma CUL ha sido creada exitosamente.</p>
        <div class="info-box">
            <p><strong>Correo:</strong> {user_email}</p>
            <p><strong>Rol asignado:</strong> {role}</p>
        </div>
        <p>Ya puedes iniciar sesión con tu documento de identidad y la contraseña asignada por el administrador.</p>
        <p>Si tienes alguna duda, comunícate con el área académica.</p>
    """
    _send_async(user_email, subject, _build_email(subject, body))


def notify_user_deleted(full_name: str, user_email: str, admin_email: str):
    subject_user = "Tu cuenta ha sido eliminada — Plataforma CUL"
    body_user = f"""
        <h2>Cuenta eliminada</h2>
        <p>Hola <strong>{full_name}</strong>,</p>
        <p>Te informamos que tu cuenta en la Plataforma CUL ha sido <span class="badge badge-danger">Eliminada</span>.</p>
        <p>Si crees que esto es un error, comunícate con el administrador del sistema.</p>
    """
    _send_async(user_email, subject_user, _build_email(subject_user, body_user))

    if admin_email:
        subject_admin = f"Usuario eliminado: {full_name}"
        body_admin = f"""
            <h2>Notificación: Usuario eliminado</h2>
            <p>Se ha eliminado el siguiente usuario de la plataforma:</p>
            <div class="info-box">
                <p><strong>Nombre:</strong> {full_name}</p>
                <p><strong>Correo:</strong> {user_email}</p>
            </div>
            <p>Esta acción fue registrada en el sistema.</p>
        """
        _send_async(admin_email, subject_admin, _build_email(subject_admin, body_admin))


# ─── Notificaciones de Certificados (Reportes) ───────────────────────────────

def notify_certificate_created(
    student_name: str,
    student_email: str,
    course_name: str,
    verification_code: str,
    issue_date: str,
):
    subject = "Certificado generado — Plataforma CUL"
    body = f"""
        <h2>¡Tu certificado ha sido generado!</h2>
        <p>Hola <strong>{student_name}</strong>,</p>
        <p>Nos complace informarte que se ha emitido un certificado para el siguiente curso:</p>
        <div class="info-box">
            <p><strong>Curso:</strong> {course_name}</p>
            <p><strong>Código de verificación:</strong> {verification_code}</p>
            <p><strong>Fecha de emisión:</strong> {issue_date}</p>
        </div>
        <p>Guarda este código para verificar la autenticidad de tu certificado en cualquier momento.</p>
    """
    _send_async(student_email, subject, _build_email(subject, body))


# ─── Notificaciones de Inscripciones ─────────────────────────────────────────

def notify_enrollment_created(
    student_name: str,
    student_email: str,
    course_name: str,
    registration_date: str,
):
    subject = "Inscripción registrada — Plataforma CUL"
    body = f"""
        <h2>Inscripción confirmada</h2>
        <p>Hola <strong>{student_name}</strong>,</p>
        <p>Tu inscripción ha sido registrada exitosamente en la plataforma.</p>
        <div class="info-box">
            <p><strong>Curso:</strong> {course_name}</p>
            <p><strong>Fecha de registro:</strong> {registration_date}</p>
            <p><strong>Estado:</strong> <span class="badge badge-success">Activa</span></p>
        </div>
        <p>Si tienes preguntas sobre tu inscripción, comunícate con el área académica.</p>
    """
    _send_async(student_email, subject, _build_email(subject, body))


def notify_enrollment_updated(
    student_name: str,
    student_email: str,
    course_name: str,
    new_status: str,
):
    subject = "Actualización de inscripción — Plataforma CUL"
    body = f"""
        <h2>Tu inscripción fue actualizada</h2>
        <p>Hola <strong>{student_name}</strong>,</p>
        <p>Se ha realizado una actualización en tu inscripción:</p>
        <div class="info-box">
            <p><strong>Curso:</strong> {course_name}</p>
            <p><strong>Nuevo estado:</strong> {new_status}</p>
        </div>
        <p>Si tienes alguna pregunta, comunícate con el área académica.</p>
    """
    _send_async(student_email, subject, _build_email(subject, body))


# ─── Notificaciones de Notas ──────────────────────────────────────────────────

def notify_grade_registered(
    student_name: str,
    student_email: str,
    course_name: str,
    final_grade: float,
    observations: str | None = None,
):
    subject = "Nota registrada — Plataforma CUL"
    obs_block = f"<p><strong>Observaciones:</strong> {observations}</p>" if observations else ""
    grade_color = "badge-success" if final_grade >= 3.0 else "badge-danger"
    body = f"""
        <h2>Tu nota ha sido registrada</h2>
        <p>Hola <strong>{student_name}</strong>,</p>
        <p>Se ha registrado tu calificación final en el sistema:</p>
        <div class="info-box">
            <p><strong>Curso:</strong> {course_name}</p>
            <p><strong>Nota final:</strong> <span class="badge {grade_color}">{final_grade:.1f}</span></p>
            {obs_block}
        </div>
        <p>Puedes consultar tus calificaciones en la plataforma en cualquier momento.</p>
    """
    _send_async(student_email, subject, _build_email(subject, body))


def notify_grade_updated(
    student_name: str,
    student_email: str,
    course_name: str,
    final_grade: float,
    observations: str | None = None,
):
    subject = "Nota actualizada — Plataforma CUL"
    obs_block = f"<p><strong>Observaciones:</strong> {observations}</p>" if observations else ""
    grade_color = "badge-success" if final_grade >= 3.0 else "badge-danger"
    body = f"""
        <h2>Tu nota fue actualizada</h2>
        <p>Hola <strong>{student_name}</strong>,</p>
        <p>Se ha actualizado tu calificación en el sistema:</p>
        <div class="info-box">
            <p><strong>Curso:</strong> {course_name}</p>
            <p><strong>Nueva nota:</strong> <span class="badge {grade_color}">{final_grade:.1f}</span></p>
            {obs_block}
        </div>
        <p>Si crees que hay un error, comunícate con tu docente.</p>
    """
    _send_async(student_email, subject, _build_email(subject, body))
