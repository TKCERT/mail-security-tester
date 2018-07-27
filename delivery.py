# Test case delivery classes
import smtplib
import mailbox

# Base class
class DeliveryBase:
    def __init__(self, target, sender, recipients):
        """Initializes target for test case delivery, e.g. connection to server"""
        self.target = target
        self.sender = sender
        self.recipients = recipients

    def deliver_testcase(self, testcase, recipient):
        """Delivers test case to target"""
        raise NotImplementedError("Test delivery not implemented")

    def deliver_testcases(self, test):
        """Deliver all test cases of a test suite to the target"""
        self.recipient_index = 1
        for recipient in self.recipients:
            self.testcase_index = 1
            self.testcases = test(self.sender, recipient)

            for testcase in self.testcases:
                self.deliver_testcase(testcase, recipient)
                self.testcase_index += 1
            self.recipient_index += 1

    def close(self):
        """Finalizing delivery, e.g. for cleanup or freeing resources"""
        pass

class SMTPDelivery(DeliveryBase):
    """Deliver test cases to a SMTP server"""
    def __init__(self, target, sender, recipients):
        super().__init__(target, sender, recipients)
        self.smtp = smtplib.SMTP(target)

    def deliver_testcase(self, testcase, recipient):
        print("Sending test case {} from test '{}' to {}".format(self.testcase_index, self.testcases.name, recipient))
        try:
            result = self.smtp.send_message(testcase)
            for failed_recipient, (code, message) in result.items():
                print("! Sending to recipient {} failed with error code {}: {}".format(failed_recipient, code, message))
        except smtplib.SMTPRecipientsRefused as e:
            print("! Reciepent refused")
            for failed_recipient, (code, message) in e.recipients.items():
                print("! Sending to recipient {} failed with error code {}: {}".format(failed_recipient, code, str(message, "iso-8859-1")))
        except smtplib.SMTPHeloError as e:
            print("! SMTP error while HELO: " + str(e))
        except smtplib.SMTPSenderRefused as e:
            print("! SMTP server rejected sender address: " + str(e))
        except smtplib.SMTPDataError as e:
            print("! Unexpected SMTP error: " + str(e))
        except smtplib.SMTPNotSupportedError as e:
            print("! SMTP server doesn't supports SMTPUTF8: " + str(e))

class FileDelivery(DeliveryBase):
    """Dumps each test case into separate plain file"""
    def deliver_testcase(self, testcase, recipient):
        outname = "{}/{}-{:04d}-{:02d}.msg".format(
                self.target,
                self.testcases.identifier,
                self.testcase_index,
                self.recipient_index
                )
        try:
            out = open(outname, "wb")
            out.write(testcase.as_bytes())
            out.close()
        except ( IOError, OSError ) as e:
            print("! Error while creation of test file {}: {}".format(outname, str(e)))

class MailboxDeliveryBase(DeliveryBase):
    """Base class for delivery methods using the mailbox module"""
    mailbox_class = mailbox.Mailbox

    def __init__(self, target, sender, recipients):
        super().__init__(target, sender, recipients)
        self.mailbox = self.mailbox_class(target)

    def deliver_testcase(self, testcase, recipient):
        self.mailbox.add(testcase)

    def close(self):
        self.mailbox.close()

class MBoxDelivery(MailboxDeliveryBase):
    mailbox_class = mailbox.mbox

class MaildirDelivery(MailboxDeliveryBase):
    mailbox_class = mailbox.Maildir
