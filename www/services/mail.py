import json, requests, logging

class MailService(object):
    """
    The MailService implements functionality required to send emails
    via Mailgun.
    """

    _CONFIG = None
    _CONFIG_KEY = 'services.mail'
    _DEV_WHITELIST_ONLY = None
    _SENDER_URI_TEMPLATE = 'https://api.mailgun.net/v3/%s/messages'

    def __init__(self, app, sender="no-reply@hackillinois.org"):
        if not MailService._CONFIG:
            self._initialize(app.config)
        self.sender = sender

    @classmethod
    def _initialize(cls, config):
        cls._CONFIG = config[cls._CONFIG_KEY]
        cls._DEV_WHITELIST_ONLY = config['development']

    def _recipient_allowed(self, recipient):
        if MailService._DEV_WHITELIST_ONLY:
            whitelisted = False
            for allowed in MailService._CONFIG['dev_whitelist']:
                if allowed in recipient:
                    whitelisted = True
                    break
            if not whitelisted:
                return False
        return True

    def send(self, recipient, subject, body, html=False):
        payload = {
            "from": self.sender,
            "to": recipient,
            "subject": subject,
        }
        if html:
            payload["html"] = body
        else:
            payload["text"] = body

        uri = MailService._SENDER_URI_TEMPLATE % MailService._CONFIG.get('mailgun_domain')
        auth = ("api", MailService._CONFIG.get('mailgun_secret'))

        if not self._recipient_allowed(recipient):
            logging.warning("Email to %s not sent (recipient address not allowed)" % recipient)
            return None
        return requests.post(uri, auth = auth, data = payload)
