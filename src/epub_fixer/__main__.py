import re
from functools import cache
from pathlib import Path

import rich_click as click
from ebooklib.epub import read_epub, write_epub
from epubcheck import EpubCheck
from rich import print
from rich.prompt import Prompt


@click.command
@click.argument("filename")
def main(filename: str):
    """
    filename\tthe file to fix
    """
    title = cache(
        lambda: Prompt.ask(
            "Enter a title for this book",
            default=Path(filename).stem,
            show_default=True,
        )
    )

    print("checking for issues")
    result = EpubCheck(filename, autorun=False)
    result.run()

    if not result.messages:
        print("No issues found")
        exit(0)

    book = read_epub(filename, {"ignore_ncx": False})

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
        elif msg.endswith('The "head" element should have a "title" child element.'):
            name, row, col = message.location.split(":")
            name = name.split("/", 2)[-1]
            item = next(i for i in book.items if i.file_name == name)
            if name.endswith("toc.xhtml"):
                item.title = title()
            else:
                item.title = Prompt.ask(
                    "Enter a title for this item",
                    show_default=True,
                )
        else:
            raise Exception(f"Unknown issue: {msg}")

    if book.title == "Unknown Title":
        book.get_metadata("DC", "title")[0] = (title(), {})

    authors = book.get_metadata("DC", "creator")
    if authors[0][0] == "Unknown Author":
        authors[0] = (Prompt.ask("Enter an author for this book"), {})

    fixed = filename + ".fixed.epub"
    write_epub(fixed, book)
    print(f"Fixed book written to {fixed}")


if __name__ == "__main__":
    main()
