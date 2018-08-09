# Base classes for test description

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class MailTestBase:
    """Mail test base class"""
    active = False
    identifier = "base"
    name = "Mail Test Base"
    description = "Base class for mail tests"
    delivery_sender = False         # Add sender explicitely in SMTP dialog
    delivery_recipient = False      # Add recipient explicitely in SMTP dialog

    def __init__(self, sender, recipient, evasions, args):
        self.sender = sender
        self.recipient = recipient
        self.evasions = evasions
        self.args = args

    def passAttributes(self, msg):
        """Pass test attributes to result test case"""
        msg.delivery_sender = self.delivery_sender
        msg.delivery_recipient = self.delivery_recipient

        return msg

    def finalizeMessage(self, msg):
        """Add sender and recipient address as From: and To: header to message"""
        if "From" not in msg:
            msg["From"] = self.sender

        if type(self.recipient) == list:
            msg["To"] = ", ".join(self.recipient)
        else:
            msg["To"] = self.recipient

        return msg
    
    def generateTestCases(self):
        """Test case generator - must be overridden"""
        raise NotImplementedError("Test case generator not implemented")

    def __iter__(self):
        """Generates test cases. By default, test cases from generateTestCases() are completed with finalizeMessage()."""
        yield from ( self.finalizeMessage(self.passAttributes(msg)) for msg in self.generateTestCases() )

class MailAttachmentTestBase(MailTestBase):
    """Base class for tests of attachments"""
    identifier = "base-attachment"
    name = "Mail Attachment Test Base"
    description = "Base class for mail attachment tests"
    subject = "Attachment Test - {}"        # place holder is replaced with test attachment description
    text_message = "This is a test mail"    # Message for text part

    def generateAttachments(self):
        """Generates attachment parts that are wrapped into a full mail message by generateTestCases() method"""
        raise NotImplementedError("Attachment generator is not implemented!")

    def generateTestCases(self):
        """Generates a mail per attachment from generator method generateAttachments()"""
        for desc, attachment in self.generateAttachments():
            msg = MIMEMultipart()
            msg["Subject"] = self.subject.format(desc)
            textpart = MIMEText(self.text_message)
            msg.attach(textpart)
            msg.attach(attachment)
            yield msg
