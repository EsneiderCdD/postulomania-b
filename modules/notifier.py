from plyer import notification


def notify(title, message):
    try:
        notification.notify(
            title=title,
            message=message,
            app_name="Postulomaniaco",
            timeout=10
        )
    except Exception:
        pass
