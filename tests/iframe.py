# Frames in mails

from email.mime.text import MIMEText
from textwrap import dedent
from .base import MailTestBase

class IFrameMailTest(MailTestBase):
    active = True
    identifier = "iframe"
    name = "HTML with frames"
    description = "HTML mails containing iFrames with different targets"

    subject = "Testmail with frame - {}"
    targets = (
            ("HTTPS URL", "https://www.thyssenkrupp.com"),
            ("about:blank URL", "about:blank"),
            ("File URL", "file:///etc/passwd"),
            ("Data URL", "data:text/plain;charset=utf-8;base64,Q29udGVudCBmcm9tIGRhdGEgVVJM"),
            )

    def generateTestCases(self):
        for desc, target in self.targets:
            html = dedent("""
            <html>
            <body>
            <iframe src="{}"></iframe>
            </body>
            </html>
            """.format(target))
            msg = MIMEText(html, "html")
            msg["Subject"] = self.subject.format(desc)
            yield msg
