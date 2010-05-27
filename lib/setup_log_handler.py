import logging, logging.handlers
from django.conf import settings

# Big ugly logging setup handler.
def setup_handler():
    if len(logging.getLogger('').handlers) != 0:
        return

    if not settings.LOCAL_SETTINGS.getboolean('log','enabled'):
        return

    root = logging.getLogger('')

    handler = logging.handlers.RotatingFileHandler(
        settings.LOCAL_SETTINGS.get('log','file'),
        maxBytes=500000, backupCount=2)
    handler.setLevel(logging.DEBUG)

    # set a format which is simpler for console use
    formatter = logging.Formatter('%(asctime)s %(name)-35s: %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)

    # add the handler to the root logger
    root.addHandler(handler)
    #logging.getLogger('MARKDOWN').setLevel(logging.INFO)

    if settings.DEBUG:
        root.setLevel(logging.DEBUG)
        stream = logging.StreamHandler()
        stream.setLevel(logging.DEBUG)
        root.addHandler( stream )
    else:
        logging.getLogger('').setLevel(logging.INFO)
        email = logging.handlers.SMTPHandler(
            settings.EMAIL_HOST,
            settings.DEFAULT_MAIL_FROM,
            [x[1] for x in settings.ADMINS],
            settings.EMAIL_ERROR_SUBJECT
        )
        email.setLevel(logging.ERROR)
        logging.getLogger('').addHandler(email)

    logging.set_up_done=True
    logging.debug("Logging started.")
