#!/usr/bin/env python3
# Test framework for mail security solutions

import argparse
import sys
from tests.discovery import getTests
from delivery import SMTPDelivery, FileDelivery, MBoxDelivery, MaildirDelivery

class TestcaseArgumentParser(argparse.Action):
    """Parse test case selection definition, e.g. test:10-20,30 and returns a dict of sets"""
    def __call__(self, parser, args, values, optstr=None):
        result = dict()
        for value in values:
            try:
                test, iddefs = value.split(":")
            except ValueError:
                raise ValueError("Test case definition must have the syntax test:id-defs, there must be exactly one colon!")

            idset = set()
            for iddef in iddefs.split(","):
                if "-" in iddef:    # range
                    try:
                        id_from, id_to = iddef.split("-")
                    except ValueError:
                        raise ValueError("Testcase identifier definitions may be single numbers or ranges (from-to).")

                    try:
                        id_from = int(id_from)
                        id_to = int(id_to)
                    except ValueError:
                        raise ValueError("Test case identifiers must only contain numbers or ranges of numbers.")
                    idset.update(range(id_from, id_to + 1))
                else:               # single test case
                    try:
                        id_val = int(iddef)
                    except ValueError:
                        raise ValueError("Test case identifiers must only contain numbers or ranges of numbers.")
                    idset.add(id_val)

            result[test] = idset
        setattr(args, self.dest, result)

argparser = argparse.ArgumentParser(
        description="Test framework for mail security solutions",
        fromfile_prefix_chars="@"
        )
argparser.add_argument("--smtp-server", "-s", default="localhost", help="SMTP server that is tested")
argparser.add_argument("--secondary-smtp-server", "-S", help="SMTP server that is used for test cases that require a third-party SMTP server, e.g. for generation of bounces")
argparser.add_argument("--sender", "-f", default="sender@test.invalid", help="Sender address")
argparser.add_argument("--to", "-t", action="append", help="Recipient address. Multiple addresses can be given by repetition of parameter")
argparser.add_argument("--send-one", "-1", action="store_true", help="Send one mail for all recipients instead of one per recipients")
argparser.add_argument("--include-test", "-i", action="append", help="Select test classes (see --list for choices)")
argparser.add_argument("--exclude-test", "-x", action="append", help="Select test classes that should be excluded (see --list for choices)")
argparser.add_argument("--testcases", "-T", nargs="+", action=TestcaseArgumentParser, help="Select specified test cases for execution, e.g. test:1,2,10-20")
argparser.add_argument("--list", "-l", action="store_true", help="List test classes")
argparser.add_argument("--output", "-o", help="Dump tests into files in this path. By default one plain file is created per message. Further formats can be created by usage of --mbox and --maildir.")
argparser.add_argument("--backconnect-domain", "-b", default="localhost", help="Domain that is used for test cases where a communication backchannel is required. This should be a domain that allows the recognition of DNS queries.")
mailbox_format_group = argparser.add_mutually_exclusive_group()
mailbox_format_group.add_argument("--mbox", "-m", action="store_true", help="Dump test cases in mbox file format.")
mailbox_format_group.add_argument("--maildir", "-M", action="store_true", help="Dump test cases in maildir directory.")
args = argparser.parse_args()

tests = getTests()

if args.list:   # print test list
    print("{:20s} | {:40} | {}".format("Test ID", "Test", "Description"))
    print("-" * 21 + "+" + "-" * 42 + "+" + "-" * 56)
    print("\n".join(["{:20s} | {:40s} | {}".format(test.identifier, test.name, test.description) for test in tests]))
    sys.exit(0)

# Construct final recipient list (one mail per recipient or one for all recipients?)
recipients = args.to
if args.send_one:
    recipients = [ recipients ]

# Choose delivery class
if args.output:
    if args.mbox:
        delivery = MBoxDelivery(args.output, args.sender, recipients, args)
    elif args.maildir:
        delivery = MaildirDelivery(args.output, args.sender, recipients, args)
    else:
        delivery = FileDelivery(args.output, args.sender, recipients, args)
else:
    delivery = SMTPDelivery(args.smtp_server, args.sender, recipients, args)

for test in tests:
    if args.include_test and test.identifier not in args.include_test \
    or args.exclude_test and test.identifier in args.exclude_test:
        continue
    delivery.deliver_testcases(test)

delivery.close()
