#!/usr/bin/env python3
# Test framework for mail security solutions

import argparse
import sys
from tests.discovery import getTests
from delivery import SMTPDelivery, FileDelivery, MBoxDelivery, MaildirDelivery

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
argparser.add_argument("--output", "-o", help="Dump tests into files in this path. By default one plain file is created per message. Further formats can be created by usage of --mbox and --maildir.")
mailbox_format_group = argparser.add_mutually_exclusive_group()
mailbox_format_group.add_argument("--mbox", "-m", action="store_true", help="Dump test cases in mbox file format.")
mailbox_format_group.add_argument("--maildir", "-M", action="store_true", help="Dump test cases in maildir directory.")
args = argparser.parse_args()

tests = getTests()

if args.list:   # print test list
    print("{:20s} | {:20} | {}".format("Test ID", "Test", "Description"))
    print("-" * 21 + "+" + "-" * 22 + "+" + "-" * 76)
    print("\n".join(["{:20s} | {:20s} | {}".format(test.identifier, test.name, test.description) for test in tests]))
    sys.exit(0)

# Construct final recipient list (one mail per recipient or one for all recipients?)
recipients = args.to
if args.send_one:
    recipients = [", ".join(recipients)]

# Choose delivery class
if args.output:
    if args.mbox:
        delivery = MBoxDelivery(args.output, args.sender, recipients)
    elif args.maildir:
        delivery = MaildirDelivery(args.output, args.sender, recipients)
    else:
        delivery = FileDelivery(args.output, args.sender, recipients)
else:
    delivery = SMTPDelivery(args.smtp_server, args.sender, recipients)

for test in tests:
    if args.testcase and test.identifier not in args.testcase:
        continue
    delivery.deliver_testcases(test)

delivery.close()
