# Test black lists

from email.mime.text import MIMEText
from .base import MailTestBase

class BlacklistedSenderAddressTest(MailTestBase):
    active = True
    identifier = "sender_blacklist"
    name = "Blacklisted Senders"
    description = "Send mails with addresses from a black list (--blacklist)"

    domain_prefix = "test"      # if whole domains are blacklisted (address entry begins with @), this is prepended as local address part
    subject = "Blacklisted Sender"
    body = "The sender is blacklisted and the mail should be filtered"

    def generateTestCases(self):
        for addr in self.args.blacklist:
            if addr.startswith("@"):
                addr = self.domain_prefix + addr
            msg = MIMEText(self.body)
            msg["From"] = addr
            msg["Subject"] = self.subject
            yield msg
