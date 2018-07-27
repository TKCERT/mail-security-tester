# Empty and almost empty mails

from .base import MailTestBase
from email.mime.text import MIMEText

class EmptyMailNoMimeNoSubjectTest(MailTestBase):
    active = True
    identifier = "empty_no_mime"
    name = "Empty mail without mime header"
    description = "Minimail mail without any content and mime header"

    def generateTestCases(self):
        msg = ""
        yield msg

class EmptyMailNoMimeButSubjectTest(MailTestBase):
    active = True
    identifier = "empty_no_mime_subject"
    name = "Empty mail without mime header, but with a subject header"
    description = "Minimail mail without any content and mime header, but with a subject header"

    def generateTestCases(self):
        msg = "subject: "
        yield msg

class EmptyMailMimeNoSubjectTest(MailTestBase):
    active = True
    identifier = "empty_mime_no_subject_subject"
    name = "Empty mail wit mime header, but without a subject header"
    description = "Minimail mail without any content and subject header, but with mime header"

    def generateTestCases(self):
        msg = MIMEText("")
        yield msg

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
