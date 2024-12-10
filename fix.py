import re
from argparse import ArgumentParser
from pathlib import Path

from ebooklib.epub import read_epub, write_epub
from epubcheck import EpubCheck
from rich import print
from rich.prompt import Prompt


def main():
    parser = ArgumentParser()
    parser.add_argument("filename", help="the file to read")
    args = parser.parse_args()
    title = Prompt.ask(
        "Enter a title for this book",
        default=Path(args.filename).stem,
        show_default=True,
    )

    print("checking for issues")
    result = EpubCheck(args.filename, autorun=False)
    result.run()

    if not result.messages:
        print("No issues found")
        exit(0)

    book = read_epub(args.filename, {"ignore_ncx": False})

    for message in result.messages:
        print(message)
        msg = message.message
        if (
            msg
            == 'The "direction" property must not be included in an EPUB Style Sheet.'
        ):
            (item,) = book.get_items_of_media_type("text/css")

            item.content = re.sub(
                r"(direction: [^;]+;)",
                lambda *args: "",
                item.content.decode("utf-8"),
            ).encode("utf-8")
        elif (
            msg
            == 'Warning while parsing file: The "head" element should have a "title" child element.'
        ):
            name, row, col = message.location.split(":")
            name = name.split("/", 2)[-1]
            item = next(i for i in book.items if i.file_name == name)
            if name.endswith("toc.xhtml"):
                item.title = title
            else:
                item.title = Prompt.ask(
                    "Enter a title for this item",
                    default=default_title,
                    show_default=True,
                )
        else:
            raise Exception(f"Unknown issue: {msg}")

    if book.title == "Unknown Title":
        book.title = title

    authors = book.get_metadata("DC", "creator")
    if authors[0][0] == "Unknown Author":
        book.author = Prompt.ask("Enter an author for this book")

    write_epub(args.filename + ".fixed.epub", book)


if __name__ == "__main__":
    main()
