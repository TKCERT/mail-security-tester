# Dangerous attachments test

from .base import MailAttachmentTestBase
from email.mime.application import MIMEApplication

class DangerousFileAttachment(MailAttachmentTestBase):
    """Generates attachments with known bad suffixes"""
    active = True
    identifier = "bad_filetypes"
    name = "Bad File Types"
    description = "Attach files with known bad suffixes"
    subject = "Known bad attachment type - {}"
    known_bad_suffixes = (
            "ade", "adp", "app", "asp", "bas", "bat", "bhx", "cab", "ceo", "chm",
            "cmd", "com", "cpl", "crt", "csr", "der", "exe", "fxp", "hlp", "hta",
            "inf", "ins", "isp", "its", "js", "jse", "lnk", "mad", "maf", "mag",
            "mam", "mar", "mas", "mat", "mde", "mim", "msc", "msi", "msp", "mst",
            "ole", "pcd", "pif", "reg", "scr", "sct", "shb", "shs", "vb", "vbe",
            "vbmacros", "vbs", "vsw", "wmd", "wmz", "ws", "wsc", "wsf", "wsh", "xxe",
            "docm", "xlsm"
            )
    file_name = "badsuffix.{}"
    file_content = b"foobar " * 100

    def generateAttachments(self):
        for suffix in self.known_bad_suffixes:
            attachment = MIMEApplication(self.file_content)
            attachment.add_header("Content-Disposition", "attachment", filename=self.file_name.format(suffix))
            yield suffix, attachment
