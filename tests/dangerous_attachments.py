# Dangerous attachments test

from io import BytesIO
import zipfile
import tarfile
import gzip
import bz2
from email.mime.application import MIMEApplication
from .base import MailAttachmentTestBase

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

class DangerousCompressedFileAttachment(MailAttachmentTestBase):
    """Generates attachments with known bad suffixes"""
    active = True
    identifier = "compressed_bad_filetypes"
    name = "Compressed Bad File Types"
    description = "Bad EXE file attachment contained in various archive formats"
    subject = "Known bad attachment type in archive - {}"
    exe_name = "test.exe"
    exe_content = b"MZ" + b"foobar " * 100
    zip_name = "test.zip"
    tar_formats = (     # Description, file name, tarfile format constant
            ("TAR - GNU"   , "test-gnu.tar"   , tarfile.GNU_FORMAT)   ,
            ("TAR - USTAR" , "test-ustar.tar" , tarfile.USTAR_FORMAT) ,
            ("TAR - PAX"   , "test-pax.tar"   , tarfile.PAX_FORMAT)   ,
            )
    compression = (     # Description, suffix, MIME subtype, compression function
            ("GZip compressed"  , ".gz"  , "gzip"   , gzip.compress) ,
            ("BZip2 compressed" , ".bz2" , "x-bzip" , bz2.compress)  ,
            )

    def generateAttachments(self):
        # ZIP
        f_zip = BytesIO()
        zip_file = zipfile.ZipFile(f_zip, "w", zipfile.ZIP_DEFLATED)
        zip_file.writestr(self.exe_name, self.exe_content)
        zip_file.close()

        attachment = MIMEApplication(f_zip.getvalue(), "zip")
        attachment.add_header("Content-Disposition", "attachment", filename=self.zip_name)
        f_zip.close()
        yield "ZIP", attachment

        # TAR
        f_exe = BytesIO(self.exe_content)
        tarinfo = tarfile.TarInfo(self.exe_name)
        tarinfo.size = len(f_exe.getvalue())
        tarinfo.mode = 0o755
        for desc, tar_name, tar_format in self.tar_formats:
            f_tar = BytesIO()
            tar = tarfile.TarFile(fileobj=f_tar, mode="w", format=tar_format)
            tar.addfile(tarinfo, f_exe)
            f_exe.seek(0)
            tar.close()
            attachment = MIMEApplication(f_tar.getvalue(), "x-tar")
            attachment.add_header("Content-Disposition", "attachment", filename=tar_name)
            yield desc, attachment

            # compressed
            for comp_desc, suffix, mime_subtype, compressor in self.compression:
                attachment = MIMEApplication(compressor(f_tar.getvalue()), mime_subtype)
                attachment.add_header("Content-Disposition", "attachment", filename=tar_name + suffix)
                yield desc + ", " + comp_desc, attachment
            f_tar.close()
        f_exe.close()

        # Further compression formats
        for comp_desc, suffix, mime_subtype, compressor in self.compression:
            attachment = MIMEApplication(compressor(self.exe_content), mime_subtype)
            attachment.add_header("Content-Disposition", "attachment", filename=self.exe_name + suffix)
            yield comp_desc, attachment
