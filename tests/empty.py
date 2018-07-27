# Empty and almost empty mails

from .base import MailTestBase
from email.mime.text import MIMEText
from email.message import Message

class EmptyMailTest(MailTestBase):
    active = True
    identifier = "empty"
    name = "Empty Mail"
    description = "Minimail mail without any content"

    def generateTestCases(self):
        # Entirely empty message
        msg = Message()
        yield msg

        # Non-MIME message with subject
        msg = Message()
        msg["Subject"] = ""
        yield msg

        # Empty MIME text without subject
        msg = MIMEText("")
        yield msg

        # Empty MIME text with empty subject
        msg = MIMEText("")
        msg["Subject"] = ""
        yield msg

class TotallyEmptyMailTest(EmptyMailTest):
    identifier = "totally_empty"
    name = "Totally Empty Mail"
    description = "Empty mails without sender and recipient information"

    def finalizeMessage(self, msg):
        return msg

class AlmostEmptyMailTest(MailTestBase):
    active = True
    identifier = "almost_empty"
    name = "Almost Empty Mail"
    description = "Minimail mail without any content but with subject"

    subject = "Mail without content"

    def generateTestCases(self):
        msg = MIMEText("")
        msg["Subject"] = self.subject
        yield msg
