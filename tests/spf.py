# SPF Tests, sending from domains that have strict SPF records with high probability

from .base import MailTestBase
from email.mime.text import MIMEText

class SPFMailTest(MailTestBase):
    active = True
    identifier = "spf"
    name = "Spoofed SPF-enabled domain"
    description = "Mails spoofed from domains with valid SPF configuration"

    domains = (
            "gmail.com",
            "microsoft.com",
            "facebook.com"
            )
    spoofed_sender = "spf-test@{}"
    subject = "SPF Check - {}"

    def generateTestCases(self):
        for domain in self.domains:
            msg = MIMEText("This is a SPF verification check.")
            msg["Subject"] = self.subject.format(domain)
            msg["From"] = self.spoofed_sender.format(domain)
            yield msg
