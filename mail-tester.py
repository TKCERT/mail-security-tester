#!/usr/bin/env python3
# Test framework for mail security solutions

import argparse
import sys
from tests.discovery import get_tests, get_evasions
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

class BlacklistArgumentParser(argparse.Action):
    """Read each blacklist file and consolidate all entries into one list"""
    def __call__(self, parser, args, values, optstr=None):
        blacklist = set()
        for value in values:
            try:
                f = open(value, "r")
            except (IOError, OSError) as e:
                print("Failed to open blacklist file '{}': {}".format(value, str(e)), file=sys.stderr)
                sys.exit(1)
            blacklist.update([l.strip() for l in f.readlines()])
        setattr(args, self.dest, sorted(list(blacklist)))

class MailTesterArgumentParser(argparse.ArgumentParser):

    def __init__(self, *args, **kwargs):
        super().__init__(
            description="Test framework for mail security solutions",
            epilog="Parameters can be read from a file by a @filename parameter. The file should contain one parameter per line. Dashes may be omitted.",
            fromfile_prefix_chars="@",
        )

    def convert_arg_line_to_args(self, line : str):
        return ("--" + line.lstrip("--")).split()

argparser = MailTesterArgumentParser()
argparser.add_argument("--smtp-server", "-s", default="localhost", help="SMTP server that is tested")
argparser.add_argument("--secondary-smtp-server", "-S", help="SMTP server that is used for test cases that require a third-party SMTP server, e.g. for generation of bounces")
argparser.add_argument("--sender", "-f", default="sender@test.invalid", help="Sender address")
argparser.add_argument("--to", "-t", action="append", help="Recipient address. Multiple addresses can be given by repetition of parameter")
argparser.add_argument("--send-one", "-1", action="store_true", help="Send one mail for all recipients instead of one per recipients")
argparser.add_argument("--delay", "-d", type=float, help="Delay delivery by given number of seconds after each mail")
argparser.add_argument("--auto-delay", "-D", action="store_true", help="Automatically increase delay on 4xx SMTP errors. Uses --delay as initial send delay, increases by --delay-step seconds until --delay-max is reached.")
argparser.add_argument("--delay-step", "-Ds", type=float, default=0.2, help="Delay is increased by this amount of seconds on 4xx SMTP error codes if --auto-delay is enabled. Default: %(default)s seconds")
argparser.add_argument("--delay-max", "-Dm", type=float, default=5.0, help="Automatic delay is not increased over this threshold. Default: %(default)s seconds")
argparser.add_argument("--include-test", "-i", action="append", help="Select test classes (see --list for choices)")
argparser.add_argument("--exclude-test", "-x", action="append", help="Select test classes that should be excluded (see --list for choices)")
argparser.add_argument("--testcases", "-T", nargs="+", action=TestcaseArgumentParser, help="Select specified test cases for execution, e.g. test:1,2,10-20")
argparser.add_argument("--list", "-l", action="store_true", help="List test classes and evasion modules.")
argparser.add_argument("--log", "-L", help="Test result log in CSV format")
argparser.add_argument("--output", "-o", help="Dump tests into files in this path. By default one plain file is created per message. Further formats can be created by usage of --mbox and --maildir.")
argparser.add_argument("--backconnect-domain", "-b", default="localhost", help="Domain that is used for test cases where a communication backchannel is required. This should be a domain that allows the recognition of DNS queries.")
argparser.add_argument("--spoofed-sender", "-F", help="Mail address used for testing of internal sender spoofing from the Internet. If this is not set, the first recipient address is used.")
argparser.add_argument("--blacklist", "-B", action=BlacklistArgumentParser, default=list(), nargs="+", help="Files containing black lists. One mail address per line. Entries beginning with @ are prepended with local part 'test'.")
argparser.add_argument("--spam-folder", "-j", nargs="+", default=list(), help="Folder with spam messages in EML format")
argparser.add_argument("--malware-folder", "-w", default=list(), nargs="+", help="Folder with malware samples that are sent as attachment")
argparser.add_argument("--evasion", "-e", action="append", default=list(), help="Enable evasion modules")
mailbox_format_group = argparser.add_mutually_exclusive_group()
mailbox_format_group.add_argument("--mbox", "-m", action="store_true", help="Dump test cases in mbox file format.")
mailbox_format_group.add_argument("--maildir", "-M", action="store_true", help="Dump test cases in maildir directory.")
args = argparser.parse_args()

tests = get_tests()

if args.list:   # print test list
    evasions = get_evasions()
    print("Tests")
    print("=====")
    print("{:30s} | {:40} | {}".format("Test ID", "Test", "Description"))
    print("-" * 31 + "+" + "-" * 42 + "+" + "-" * 56)
    print("\n".join(["{:30s} | {:40s} | {}".format(test.identifier, test.name, test.description) for test in sorted(tests, key=lambda test: test.identifier)]))
    print()
    print("Evasions")
    print("========")
    print("{:30s} | {:40} | {}".format("Evasion ID", "Evasion", "Description"))
    print("-" * 31 + "+" + "-" * 42 + "+" + "-" * 56)
    print("\n".join(["{:30s} | {:40s} | {}".format(evasion.identifier, evasion.name, evasion.description) for evasion in sorted(evasions, key=lambda evasion: evasion.identifier)]))
    sys.exit(0)

# Construct final recipient list (one mail per recipient or one for all recipients?)
recipients = args.to
if args.send_one:
    recipients = [ recipients ]

# Choose delivery class
if args.output:
    file_delivery_args = (args.output, args.sender, recipients, args)
    if args.mbox:
        delivery = MBoxDelivery(*file_delivery_args)
    elif args.maildir:
        delivery = MaildirDelivery(*file_delivery_args)
    else:
        delivery = FileDelivery(*file_delivery_args)
else:
    delivery = SMTPDelivery(args.smtp_server, args.sender, recipients, args)

for test in tests:
    if args.include_test and test.identifier not in args.include_test \
    or args.exclude_test and test.identifier in args.exclude_test:
        continue
    delivery.deliver_testcases(test)

delivery.close()
