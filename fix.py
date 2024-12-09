from argparse import ArgumentParser
from ebooklib.epub import read_epub, write_epub
import re
from epubcheck import EpubCheck

parser = ArgumentParser()
parser.add_argument("filename", help="the file to read")
args = parser.parse_args()

result = EpubCheck(args.filename, autorun=False)
result.run()
print(result.valid)
print(result.messages)

if not result.messages:
    print("No issues found")
    exit(0)

book = read_epub(args.filename)
if book.title == "Unknown Title":
    raise ValueError("Unknown title")

for message in result.messages:
    if message.level == "ERROR":
        print(message.message)
        print(list(book.get_items_of_media_type("text/css")))

        (item,) = book.get_items_of_media_type("text/css")

        item.content = re.sub(
            r"(direction: [^;]+;)",
            lambda *args: "",
            item.content.decode("utf-8"),
        ).encode("utf-8")


write_epub(args.filename + ".fixed.epub", book)
