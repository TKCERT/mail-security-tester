from .base import MailTestBase
from email.mime.text import MIMEText
from email.message import Message

class AlmostEmptyMailTest(MailTestBase):
    active = True
    identifier = "bounce"
    name = "Bounce-like mail"
    description = "Mail with empty envelope"

    subject = "Mail Delivery System"
    message = """
This message was created automatically by mail delivery software.

A message that you sent could not be delivered to all of its recipients.
This is a permanent error. The following address(es) failed:

test@testinvalid
    """

    def generateTestCases(self):
        msg = MIMEText(self.message)
        msg["Subject"] = self.subject
        msg["From"] ="<>"
        yield msg
