# Empty and almost empty mails

from .base import MailTestBase
from email.mime.text import MIMEText

class EmptyMailTest(MailTestBase):
    active = True
    identifier = "empty"
    name = "Empty Mail"
    description = "Minimail mail without any content"

    def generateTestCases(self):
        msg = MIMEText("")
        yield msg

        msg["Subject"] = ""
        yield msg

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
