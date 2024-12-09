from argparse import ArgumentParser
from ebooklib.epub import read_epub, write_epub
import re
from epubcheck import EpubCheck

parser = ArgumentParser()
parser.add_argument("filename", help="the file to read")
args = parser.parse_args()

print("checking for issues")
result = EpubCheck(args.filename, autorun=False)
result.run()

if not result.messages:
    print("No issues found")
    exit(0)

book = read_epub(args.filename, {"ignore_ncx": False})
if book.title == "Unknown Title":
    raise ValueError("Unknown title")

for message in result.messages:
    print(message)
    if message.level == "ERROR":
        (item,) = book.get_items_of_media_type("text/css")

        item.content = re.sub(
            r"(direction: [^;]+;)",
            lambda *args: "",
            item.content.decode("utf-8"),
        ).encode("utf-8")
    else:
        raise Exception(f"Unknown issue: {message.message}")


write_epub(args.filename + ".fixed.epub", book)
