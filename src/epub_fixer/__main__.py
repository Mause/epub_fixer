import logging
import re
from functools import cache
from os.path import basename
from pathlib import Path
from typing import Annotated, Literal

import rich_click as click
from ebooklib.epub import read_epub, write_epub
from epubcheck import EpubCheck
from lxml import etree, html
from pydantic import BaseModel, Field, TypeAdapter
from rich import print
from rich.console import Console
from rich.prompt import Prompt

logger = logging.getLogger(__name__)


class Location(BaseModel):
    url: dict[str, bool]
    path: str
    line: int
    column: int
    context: str | None


class Message(BaseModel):
    message: str
    id: Annotated[str, Field(alias="ID")]
    severity: Literal["ERROR", "WARNING", "INFO"]
    additionalLocations: int
    suggestion: str | None
    locations: list[Location]


@click.command
@click.argument("filename")
def epub_fixer(filename: Path):
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
    with Console().status("checking for issues"):
        result = EpubCheck(filename, autorun=False)
        result.run()

    book = read_epub(filename, {"ignore_ncx": False})

    generator = book.get_metadata("OPF", "generator")
    if generator:
        print(generator[0][1]["content"])

    if not result.messages:
        print("No issues found")
        return 0

    for message in TypeAdapter(list[Message]).validate_python(
        result.result_data["messages"]
    ):
        print(message)
        msg = message.message
        location, = message.locations
        name = location.path
        row = location.line
        col = location.column
        name = basename(name)
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
            item = next(i for i in book.items if i.file_name == name)
            if name.endswith("toc.xhtml"):
                item.title = title()
            else:
                item.title = Prompt.ask(
                    "Enter a title for this item",
                    show_default=True,
                )
        elif msg.startswith(
            "Error while parsing file: "
            'element "bold" not allowed here; expected the element'
        ) or msg.startswith(
            "Fatal Error while parsing file: "
            'The element type "p" must be terminated by the matching end-tag "</p>".'
        ):
            breakpoint()
            item = next(i for i in book.items if i.file_name == name)
            for node in html.fromstring(item.content).iter():
                if node.sourceline == int(row):
                    print(f"Fixing node {node.tag} on line {row}")
            logger.warning(msg)
        else:
            logger.error("Unknown issue: %s", msg)

    if book.title == "Unknown Title":
        book.get_metadata("DC", "title")[0] = (title(), {})

    authors = book.get_metadata("DC", "creator")
    if authors[0][0] == "Unknown Author":
        authors[0] = (Prompt.ask("Enter an author for this book"), {})

    fixed = filename.with_suffix(".fixed.epub")
    write_epub(
        fixed,
        book,
        {
            "raise_exceptions": True,
        },
    )
    print("Fixed book written to", fixed)


if __name__ == "__main__":
    breakpoint()
    epub_fixer()
