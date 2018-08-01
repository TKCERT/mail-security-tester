# Spam mails from folder with EMLs

from pathlib import Path
from email import message_from_bytes
from .base import MailTestBase

class SpamMailTest(MailTestBase):
    active = True
    identifier = "spam"
    name = "Spam Mails"
    description = "Spam messages (.eml) from folders given by --spam-folder parameter"

    def generateTestCases(self):
        for folder in self.args.spam_folder:
            for eml in Path(folder).glob("*.eml"):
                try:
                    msg = message_from_bytes(eml.read_bytes())
                except IOError:
                    print("! Failed to read from {}".format(eml.name))

                del msg["To"]

                yield msg
