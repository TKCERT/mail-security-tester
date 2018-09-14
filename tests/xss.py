# Cross-site scripting test cases

from email.mime.text import MIMEText
from .base import MailTestBase

class SubjectXSSTest(MailTestBase):
    active = True
    identifier = "xss-subject"
    name = "XSS in mail subjects"
    description = "Attempting XSS in subjects for discovery of issues in web interfaces"

    subject = "Subject XSS Test: <img src=\"http://{}/xss.png\" onerror=\"alert(1)\">"
    text = "This is a test mail with XSS payload in the subject."

    def generateTestCases(self):
        msg = MIMEText(self.text)
        msg["Subject"] = self.subject.format(self.args.backconnect_domain)
        yield msg
