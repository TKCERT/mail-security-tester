# Impostor protection tests

from email.mime.text import MIMEText
from textwrap import dedent
from .base import MailTestBase

class KnownBadReplyToTest(MailTestBase):
    active = True
    identifier = "bad_replyto"
    name = "Bad Reply-To addresses"
    description = "Known bad reply to domains"

    subject = "Bad Reply-To - {}"
    reply_to = "impostor@{}"
    bad_domains = (
            "secureserver.net",
            "gmail.com"
            )

    def generateTestCases(self):
        for domain in self.bad_domains:
            msg = MIMEText("Bad Reply-To test mail")
            msg["Reply-To"] = self.reply_to.format(domain)
            msg["Subject"] = self.subject.format(domain)
            yield msg

class HomographAttackTestBase(MailTestBase):
    active = False
    identifier = "homograph-base"
    name = "Homograph attacks"
    description = "Obfuscation of faked domains by IDN homographs"

    homograph_domains = (
            ("plain cyrillic e", "thyssєnkrupp.com"),
            ("Punycode cyrillic e", "xn--thyssnkrupp-fvj.com"),
            ("Plain cyrillic o", "gооgle.com"),
            ("Punycode cyrillic o", "xn--ggle-55da.com"),
            )

class HTMLLinkHomographAttackTest(HomographAttackTestBase):
    active = True
    identifier = "homograph-link"
    name = "HTML link URL homograph attacks"
    description = "Obfuscation of faked domains by IDN homographs in HTML link"

    subject = "Homograph HTML Link - {}"

    def generateTestCases(self):
        for desc, domain in self.homograph_domains:
            html = dedent("""
            <html>
            <body>
            Please login <a href="https://login.{}">here</a>.
            </body>
            </html>
            """.format(domain))
            msg = MIMEText(html, "html")
            msg["Subject"] = self.subject.format(desc)
            yield msg

class SenderHomographAttackTest(HomographAttackTestBase):
    active = True
    identifier = "homograph-sender"
    name = "Sender address homograph attacks"
    description = "Obfuscation of faked domains by IDN homographs in sender address"

    subject = "Homograph sender address - {}"
    hsender = "impostor@{}"

    def generateTestCases(self):
        for desc, domain in self.homograph_domains:
            msg = MIMEText("This is a test mail.")
            msg["Subject"] = self.subject.format(desc)
            msg["From"] = self.hsender.format(domain)
            yield msg

class SenderHomographAttackwithSMTPDialogTest(SenderHomographAttackTest):
    active = True
    identifier = "homograph-sender-smtp"
    name = "Sender address homograph attacks (explicit SMTP sender)"
    description = "Obfuscation of faked domains by IDN homographs in sender address with explicit sender in SMTP dialog"
    delivery_sender = True
