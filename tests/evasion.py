# Evasion techniques

# Base classes

class BaseEvasion(object):
    """
    Base evasion class. This should be instantiated by a evasion factory class derived from BaseEvasionFactory.
    """
    def __init__(self, msg, *args, **kwargs):
        self.msg = msg
        self.args = args
        self.kwargs = kwargs

    def generate(self):
        """Yield manipulations of MIME part"""
        yield self.msg

class BaseEvasionFactory(object):
    """
    Base factory class for evasion modules. This is instantiated on mail tester invocation with a parameter
    that determines if evasion should be active. Depending on this, the method getEvasionGenerator() returns an
    evasion class or one that yields default changes to a MIME part.
    """
    active = False
    identifier = "evasion_base"
    name = "Evasion Base Class"
    description = "Implements base of an evasion factory class."
    generator_evasion = BaseEvasion       # Instantiated if evasion is enabled
    generator_default = BaseEvasion       # Instantiated if evasion is disabled

    def __init__(self, enabled):
        if enabled:
            self.generator_class = self.generator_evasion
        else:
            self.generator_class = self.generator_default

    def getEvasionGenerator(self, *args, **kwargs):
        """
        Returns a evasion class instance according to the test configuration. Arguments are passed to the
        evasion class constructor.
        """
        return self.generator_class(*args, **kwargs)

# Content-Disposition header evasion
# Try to evade security components by intentionally broken Content-Disposition headers of MIME attachment parts.
# Previous research has shown that some security appliances don't recognize attachments with broken
# Content-Disposition header.

class ContentDispositionEvasionBase(BaseEvasion):
    """Base class for Content-Disposition generation"""
    content_disposition_headers = ()    # list of elements (description, arg, **kwargs) that will be passed to Message.add_header() after the "Content-Disposition" header name

    def __init__(self, attachment, filename):
        super().__init__(attachment, filename)
        self.filename = filename

    def generate(self):
        for desc, arg, kwargs in self.content_disposition_headers:
            del self.msg["Content-Disposition"]
            self.msg.add_header(
                    "Content-Disposition",
                    arg.format(self.filename),
                    **{ key: value.format(self.filename)
                        for key, value in kwargs.items()
                      }
                    )
            yield desc, self.msg

class ContentDispositionDefault(ContentDispositionEvasionBase):
    """Returns MIME part with proper Content-Disposition header"""
    content_disposition_headers = (
            ("", "attachment", { "filename": "{}" }),
            )

class ContentDispositionEvasion(ContentDispositionEvasionBase):
    """Return MIME parts with evasion attempts for the Content-Disposition header"""
    content_disposition_headers = ContentDispositionDefault.content_disposition_headers + (
            ("Filename with single quotes", "attachment; filename='{}'", {}),
            ("Filename without quotes", "attachment; filename={}", {}),
            ("Empty filename", "attachment", { "filename": "" }),
            ("Without filename", "attachment", {}),
            ("Double filename, harmless first", "attachment; filename=\"harmless.txt\"; filename=\"{}\"", {}),
            ("Double filename, harmless last", "attachment; filename=\"{}\"; filename=\"harmless.txt\"", {}),
            ("Inline without filename", "inline", {}),
            ("Inline with filename", "inline", { "filename": "{}" }),
            )

class ContentDispositionEvasionFactory(BaseEvasionFactory):
    active = True
    identifier = "content_disposition"
    name = "Content-Disposition Header Variation"
    description = "Try to evade attachment recognition by intentionally broken MIME Content-Disposition headers"
    generator_evasion = ContentDispositionEvasion
    generator_default = ContentDispositionDefault
