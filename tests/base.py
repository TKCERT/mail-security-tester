# Base classes for test description

class MailTestBase:
    """Mail test base class"""
    active = False
    identifier = "base"
    name = "Mail Test Base"
    description = "Base class for mail tests"
    delivery_server = "main"        # one of "main" or "secondary" (for simulations of bounces etc.)
    delivery_sender = False         # Add sender explicitely in SMTP dialog
    delivery_recipient = False      # Add recipient explicitely in SMTP dialog

    def __init__(self, sender, recipient, config=None):
        self.sender = sender
        self.recipient = recipient
        self.config = config

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
        yield from [self.finalizeMessage(self.passAttributes(msg)) for msg in self.generateTestCases()]
