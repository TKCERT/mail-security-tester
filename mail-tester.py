#!/usr/bin/env python3
# Test framework for mail security solutions

import argparse
import sys
import smtplib
from tests.discovery import getTests

argparser = argparse.ArgumentParser(
        description="Test framework for mail security solutions",
        fromfile_prefix_chars="@"
        )
argparser.add_argument("--smtp-server", "-s", default="localhost", help="SMTP server that is tested")
argparser.add_argument("--secondary-smtp-server", "-S", help="SMTP server that is used for test cases that require a third-party SMTP server, e.g. for generation of bounces")
argparser.add_argument("--sender", "-f", default="sender@test.invalid", help="Sender address")
argparser.add_argument("--to", "-t", action="append", help="Recipient address. Multiple addresses can be given by repetition of parameter")
argparser.add_argument("--send-one", "-1", action="store_true", help="Send one mail for all recipients instead of one per recipients")
argparser.add_argument("--testcase", "-T", action="append", help="Select test classes (see --list for choices)")
argparser.add_argument("--list", "-l", action="store_true", help="List test classes")
argparser.add_argument("--output", "-o", help="Dump tests into message files in this path")
args = argparser.parse_args()

tests = getTests()

if args.list:
    print("{:20s} | {:20} | {}".format("Test ID", "Test", "Description"))
    print("-" * 21 + "+" + "-" * 22 + "+" + "-" * 76)
    print("\n".join(["{:20s} | {:20s} | {}".format(test.identifier, test.name, test.description) for test in tests]))
    sys.exit(0)

smtp = smtplib.SMTP(args.smtp_server)
for test in tests:
    if args.testcase and test.identifier not in args.testcase:
        continue

    recipients = args.to
    if args.send_one:
        recipients = [", ".join(recipients)]

    j = 1
    for to in recipients:
        testcases = test(args.sender, to)
        i = 1
        for testcase in testcases:
            if args.output:       # dump test cases to files
                outname = "{}/{}-{:04d}-{:02d}.msg".format(args.output, testcases.identifier, i, j)
                try:
                    out = open(outname, "wb")
                    out.write(testcase.as_bytes())
                    out.close()
                except ( IOError, OSError ) as e:
                    print("! Error while creation of test file {}: {}".format(outname, str(e)))
            else:               # send test cases via SMTP
                print("Sending test {} from test case '{}' to {}".format(i, testcases.name, to))
                try:
                    result = smtp.send_message(testcase)
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
            i += 1
        j += 1
