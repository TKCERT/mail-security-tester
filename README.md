# Mail Security Testing Framework

A testing framework for mail security and filtering solutions.

**IMPORTANT:** Don't do anything evil with this! Tests of cloud or otherwise hosted solutions should always be approved
by the tested provider. Only use your own test accounts and don't annoy anyone with a load of test mails.

## Installation

The mail security testing framework works with with Python >=3.5. Just pull this repository and go ahead. No further
dependencies are required.

## Usage

The script *mail-tester.py* runs the tests. Read the help message with `./mail-tester.py --help` and check the list of
test and evasion modules with `./mail-tester.py -l` to get an overview about the capabilities and the usage of the
script. Some hints:

* At least the parameters `--smtp-server` and `--to` should be given for a minimal test run.
* All parameters can also be stored in configuration files without the prefix `--`. These configuration files can be
  used by invoking `./mail-tester.py @tester.conf` (configuration contained in *tester.conf*).
* Multiple recipients can be configured with `--to` for testing of different filter configurations.
* Some mail filtering solutions may reject messages after a while. Use `--auto-delay` for automatic throttling of the
  mails. This can be fine-tuned with `--delay-step`, `--delay-max` and `--delay`.
* Some tests (Spam and Malware) require samples. Put these in directories and configure these directories with
  `--spam-folder` and `--malware-folder` parameters. The samples are not included in this repository (and will not be).
  Good places to get malware are [theZoo](https://github.com/ytisf/theZoo), [Das Malwerk](http://dasmalwerk.eu/) or
  other collections. Spam can be exported straight from yout Spam folder, but must be in EML format.
* Blacklists can be supplied with the `--blacklist` parameter and are used as sender addresses.
* The Shellshock and subject XSS test cases should have a valid backconnect domain, where you are able to see any backconnects
  (especially DNS requests). The free [Canary Tokens service](http://canarytokens.org/generate) can be used for this
  purpose. Thanks to [Thinkst](https://thinkst.com/) for providing this awesome service!
* Some neat attachment recognition evasion tricks can be enabled with `--evasion content-disposition`. These were used
  in the past to confuse AV/sandboxing solutions and let them pass malicious mails.
* Don't forget to log the test results with `--log`. Mail filtering providers often reject mails in the SMTP dialog,
  which is reflected in the generated log.
* Test cases can be dumped with `--output` as plain files in a directory, in MBox (`--mbox`) or MailDir (`--maildir`)
  format. This is useful to test mail user agents without sending any mails, to document or review generated test cases.

## Development and Extension

### Tests

Own tests can be implemented with a class in one of the iexisting or newly created Python files in the `tests/`
directory. The class must be a subclass of `MailTestBase` located in the module `tests.base` of this project. Newly
implemented tests are discovered automatically when the class variable `active` is set to `True`. Further (if you plan
to contribute tests back to the main repository), the class variables *identifier*, *name* and *description* should be
set appropriately.

The following base classes exist with methods or class variables intended for overriding:

* `MailTestBase`: Test class for generic tests.
  * `generateTestCases()`: Yields test messages. These should be generated with the `MIME*` classes from the Python
    `email.mime.*` packages or with the `Message` class from `email.message` to ensure valid mail messages.
  * `active`: Boolean value if test should be active.
  * `identifier`: Short identifier of the test. This one is used to enable or disable tests in parameters.
  * `name`: Short test title.
  * `description`: Longer test description, should fit within approximately 100 characters.
  * `delivery_sender` and `delivery_recipient`: Boolean values, *False* by default. Normally, the sender and recipients are set in the
    message and the Python SMTP module takes them over from there. Sometimes it is desirable to set them explicitely in
    the SMTP library, which can be configured by setting this values to *True*.
  * `finalizeMessage(msg)`: By default, the base test class sets the *From* and *To* headers accrodingly. This
    behaviour can be overridden if required for the test case.
* `MailAttachmentTestBase`: Test class for attachment test cases. This generates a complete valid mail with a Subject
  and a text part and attaches the test case to it. Derived from `MailTestBase`, therefore the methods/variables from it
  can be overridden here, too.
  * `generateAttachments()`: Yields test cases as (description, attachment) tuples.
  * `subject`: Sets the subject. The place holder `{}` is replaced by the description yielded by
    `generateAttachments()`.
  * `generateTestCases()`: is already overridden with an implementation of the message generation described above, but may be further
    adapted if required.

Setting the subjects of generated messages is highly recommended to be able to recongize the tests in the receiving
inbox.

### Evasions

Evasion classes implement techniques for evading recognition of particular mail properties by mail security solutions.
Currently, a evasion technique that tries to hide attachments from such solutions by intentionally broken
*Content-Disposition* headers is implemented.

#### Implement new Evasions

Evasions are implemented by a factory class pattern. The `DeliveryBase` class instantiaties a factory class derived from
the `BaseEvasionFactory` class. The factory constructor receives a flag that indicates if the evasion is activated. The
evasion factory instance is then passed to the test class and stored in its `evasions` attribute that contains a dict
with the evasion identifiers as keys. Inside the test, a evasion class (based on `EvasionBase`) is instantiated with
`getEvasionGenerator()`. The constructor parameter are defined individually per evasion technique.

The following base classes are used to implement evasions:

* `BaseEvasionFactory`: Evasion factories must be based on this class. Usually, only the following class variables
  should be set:
  * `active`: Set to *True* if the evasion should be active.
  * `identifier`: Short identifier of the evasion module used for enabling it in the test configuration.
  * `name`: Short title of the evasion technique.
  * `description`: Longer description of the evasion technique. Should fit in approximately 100 characters.
  * `generator_evasion`: Evasion class that is instantiated if the evasion is enabled.
  * `generator_default`: Evasion class that is instantiated if the evasion is disabled.
* `BaseEvasion`: Implementation of evasions must be a subclass of this base class. The following method must be
  overridden:
  * `__init__()`: Should instantiate the class with the base message or attachment that should be manipulated with
    evasion techniques.
  * `generate()`: Apply the evasion technique to the object passed to the constructor and yield it to the caller as
    (description, object with evasion applied) tuple.

Generally, the evasion class should yield all evasion variants and pass the default as dedicated test case, while the
default evasion classes only pass the given object or create the required data structures, like headers.

#### Using Evasion Techniques in Test Cases

Evasion techniques are used in test cases where they are applicable. E.g. if an evasion technique manipulates the header
of a mail or attachment, the following steps have to be implemented:

1. Generate the base object (mail or attachment) without consideration of the evasion.
2. Instantiate the appropriate evasion class by utilization of the evasion factory instance from `self.evasions`, e.g.:
   `evasion_items = self.evasions["evasion_identifier"].getEvasionGenerator(message)`
3. Iterate over the generator and yield the test cases:
```
for evasion_item in evasion_items:
    yield evasion_item
```

#### Usage of the Content Disposition Evasion Technique

The content disposition evasion technique is already implemented in the framework and should be used for all test cases
that target on the recognition of malicious attachments. The constructor receives an attachment and the intended file
name. The evasion class then yields (evasion name, attachment with applied evasion technique) tuples that can directly
be yielded by the tests `generateAttachments()` method.
