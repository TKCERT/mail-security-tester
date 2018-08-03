# Test case delivery classes
import smtplib
import mailbox
from time import sleep
from logging import CSVLogger, DummyLogger

# Base class
class DeliveryBase:
    def __init__(self, target, sender, recipients, args):
        """Initializes target for test case delivery, e.g. connection to server"""
        self.target = target
        self.sender = sender
        self.recipients = recipients
        self.args = args
        self.testcase_selection = args.testcases

        # Initiate logging
        if args.log:
            self.logger = CSVLogger(args.log)
        else:
            self.logger = DummyLogger()

    def deliver_testcase(self, testcase, recipient):
        """Delivers test case to target"""
        pass

    def deliver_testcases(self, test):
        """Deliver all test cases of a test suite to the target"""
        self.recipient_index = 1
        for recipient in self.recipients:
            self.recipient = recipient
            self.testcase_index = 1
            self.testcases = test(self.sender, recipient, self.args)
            try:
                testcase_set = self.testcase_selection[test.identifier]
            except KeyError:        # Definition was given, but not for this test
                testcase_set = {}
            except TypeError:       # No definition was given at all
                testcase_set = None

            for testcase in self.testcases:
                if testcase_set is None or self.testcase_index in testcase_set:
                    self.deliver_testcase(testcase, recipient)
                self.testcase_index += 1
            self.recipient_index += 1

    def close(self):
        """Finalizing delivery, e.g. for cleanup or freeing resources"""
        self.logger.close()

class DelayMixin:
    """Implements delaying of test cases and automatic delay incremention. Should be mixed in for all network-based delivery classes."""
    def __init__(self, target, sender, recipients, args):
        super().__init__(target, sender, recipients, args)
        self.delay = self.args.delay or 0
        self.auto_delay = self.args.auto_delay
        self.delay_step = self.args.delay_step
        self.delay_max = self.args.delay_max
        self.allow_delay_increase()

    def allow_delay_increase(self):
        """Allow automatic increase of delay after it was increased. This prevents multiple increments per test case on multiple errors."""
        self.allow_increase_delay = True

    def increase_delay(self):
        """Increase the send delay automatically as configured in arguments. Disable delay increase until next call of .allow_delay_increase()"""
        if self.auto_delay and self.allow_increase_delay:
            old_delay = self.delay
            self.delay += self.delay_step
            if self.delay > self.delay_max:
                self.delay = self.delay_max
        self.allow_increase_delay = False
        print("! Increased delay from {:0.1f} to {:0.1f}".format(old_delay, self.delay))

    def do_delay(self):
        """Sleep for the amount currently set as delay."""
        sleep(self.delay)

    def deliver_testcase(self, *args, **kwargs):
        """Add delay to each test case"""
        super().deliver_testcase(*args, **kwargs)
        self.do_delay()

class SMTPDelivery(DelayMixin, DeliveryBase):
    """Deliver test cases to a SMTP server"""
    delay_increasing_status = range(400, 500)

    def __init__(self, target, sender, recipients, args):
        super().__init__(target, sender, recipients, args)
        self.target = target
        self.smtp = smtplib.SMTP(target)

    def deliver_testcase(self, testcase, recipient):
        super().deliver_testcase(testcase, recipient)
        print("Sending test case {} from test '{}' to {}".format(self.testcase_index, self.testcases.name, recipient))
        self.allow_delay_increase()
        try:
            try:
                if testcase.delivery_sender:
                    sender = self.sender
                else:
                    sender = None
            except AttributeError:
                sender = None

            try:
                if testcase.delivery_recipient:
                    recipient = recipient
                else:
                    recipient = None
            except AttributeError:
                recipient = None

            result = self.smtp.send_message(testcase, sender, recipient)
            if result:
                for failed_recipient, (code, message) in result.items():
                    print("! Sending to recipient {} failed with error code {}: {}".format(failed_recipient, code, message))
                    self.logger.log(self.testcases.identifier, self.testcase_index, self.recipient, False, code, message)
                    if code in self.delay_increasing_status:
                        self.increase_delay()
            else:
                self.logger.log(self.testcases.identifier, self.testcase_index, self.recipient)
        except smtplib.SMTPRecipientsRefused as e:
            print("! Reciepent refused")
            for failed_recipient, (code, message) in e.recipients.items():
                print("! Sending to recipient {} failed with error code {}: {}".format(failed_recipient, code, str(message, "iso-8859-1")))
                self.logger.log(self.testcases.identifier, self.testcase_index, failed_recipient, False, code, str(message, "iso-8859-1"))
                if code in self.delay_increasing_status:
                    self.increase_delay()
        except smtplib.SMTPHeloError as e:
            print("! SMTP error while HELO: " + str(e))
            if e.smtp_code in self.delay_increasing_status:
                self.increase_delay()
        except smtplib.SMTPSenderRefused as e:
            print("! SMTP server rejected sender address: " + str(e))
            self.logger.log(self.testcases.identifier, self.testcase_index, self.recipient, False, e.smtp_code, e.smtp_error)
            if e.smtp_code in self.delay_increasing_status:
                self.increase_delay()
        except smtplib.SMTPDataError as e:
            print("! Unexpected SMTP error: " + str(e))
            self.logger.log(self.testcases.identifier, self.testcase_index, self.recipient, False, e.smtp_code, e.smtp_error)
            if e.smtp_code in self.delay_increasing_status:
                self.increase_delay()
        except smtplib.SMTPNotSupportedError as e:
            print("! SMTP server doesn't supports: " + str(e))
            self.logger.log(self.testcases.identifier, self.testcase_index, self.recipient, False, -1, str(e))
        except smtplib.SMTPServerDisconnected as e:
            self.logger.log(self.testcases.identifier, self.testcase_index, self.recipient, False, -2, str(e))
            print("! SMTP server disconnected unexpected - reconnecting: " + str(e))
            self.smtp = smtplib.SMTP(self.target)

    def close(self):
        super().close()
        self.smtp.quit()

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

    def __init__(self, target, sender, recipients, args):
        super().__init__(target, sender, recipients, args)
        self.mailbox = self.mailbox_class(target)

    def deliver_testcase(self, testcase, recipient):
        self.mailbox.add(testcase)

    def close(self):
        super().close()
        self.mailbox.close()

class MBoxDelivery(MailboxDeliveryBase):
    mailbox_class = mailbox.mbox

class MaildirDelivery(MailboxDeliveryBase):
    mailbox_class = mailbox.Maildir
