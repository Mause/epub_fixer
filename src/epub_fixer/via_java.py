import jpype
import jpype.imports
from epubcheck.const import EPUBCHECK

jpype.startJVM(
    classpath=[
        EPUBCHECK,
    ]
)

from com.adobe.epubcheck.api import EPUBProfile  # noqa: E402
from com.adobe.epubcheck.ocf import OCFChecker  # noqa: E402
from com.adobe.epubcheck.opf import ValidationContext  # noqa: E402
from com.adobe.epubcheck.util import (  # noqa: E402
    DefaultReportImpl,
    FileResourceProvider,
)
from java.io import File  # noqa: E402
from org.w3c.epubcheck.constants import MIMEType  # noqa: E402
from org.w3c.epubcheck.util.url import URLUtils  # noqa: E402


def via_java(filename):
    epubFile = File(filename)
    report = DefaultReportImpl(filename)
    vc = (
        ValidationContext.of(URLUtils.toURL(epubFile))
        .report(report)
        .mimetype(MIMEType.EPUB.toString())
        .resourceProvider(FileResourceProvider(epubFile))
        .profile(EPUBProfile.DEFAULT)
    )
    checker = OCFChecker(vc.build())
    checker.check()
    report.generate()
    d = report.getDictionary()
    for message_id in report.allReportedMessageIds:
        message = d.getMessage(message_id)
        print(message.getMessage())

    raise Exception()
    return report
