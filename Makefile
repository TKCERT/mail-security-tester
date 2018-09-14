.PHONY: test
COVSCOPE = ./*.py,tests/*.py

test:
	coverage erase
	coverage run -a --include=$(COVSCOPE) ./mail-tester.py --help
	coverage run -a --include=$(COVSCOPE) ./mail-tester.py --list
	coverage run -a --include=$(COVSCOPE) ./mail-tester.py @ci-tests/mbox-all.conf
	mkdir -p test.maildir/cur test.maildir/new test.maildir/tmp; coverage run -a --include=$(COVSCOPE) ./mail-tester.py @ci-tests/maildir-noevasion.conf
	mkdir -p test.mails; coverage run -a --include=$(COVSCOPE) ./mail-tester.py @ci-tests/output-plain.conf
	coverage run -a --include=$(COVSCOPE) ./mail-tester.py @ci-tests/testcases.conf
	python -m smtpd -c DebuggingServer -n localhost:2525 &
	coverage run -a --include=$(COVSCOPE) ./mail-tester.py @ci-tests/smtp-all.conf
	coverage run -a --include=$(COVSCOPE) ./mail-tester.py @ci-tests/delay.conf
	coverage run -a --include=$(COVSCOPE) ./mail-tester.py @ci-tests/autodelay.conf
	coverage report --fail-under 90
	coverage erase
	rm -fr test.log test.mbox test.maildir test.mails
