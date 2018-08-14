# Bulk mails

from email.mime.text import MIMEText
from .base import MailTestBase

class MailingListTest(MailTestBase):
    active = True
    identifier = "mailinglist"
    name = "Mailing list headers"
    description = "Mails that contain mailing list headers (List-*)"

    subject = "Mailing List"
    body = "Mailing list header test"
    headers = (
            ("List-Id", "<foobar.test.invalid>"),
            ("List-Unsubscribe", "<http://test.invalid/unsubscribe>"),
            ("List-Unsubscribe-Post", "List-Unsubscribe=One-Click"),
            ("X-ulpe", "foobar@test.invalid"),
            ("DKIM-Signature", "v=1; a=rsa-sha256; c=relaxed; s=mailing; d=test.invalid; h=Date:From:Reply-To:To:Message-ID:Subject:MIME-Version:Content-Type:List-Id: X-CSA-Complaints:List-Unsubscribe:List-Unsubscribe-Post:X-ulpe:Feedback-ID; bh=Zm9vYmFyCg==; b=Zm9vYmFyCg=="),
            )

    def generateTestCases(self):
        msg = MIMEText(self.body)
        msg["Subject"] = self.subject
        for header, value in self.headers:
            msg[header] = value
        yield msg
