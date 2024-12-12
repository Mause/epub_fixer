from os.path import basename
from pathlib import Path
from urllib.request import urlretrieve

from click.testing import CliRunner
from pytest import fixture

from .__main__ import epub_fixer


@fixture
def happy_epub(tmp_path):
    url = "https://github.com/IDPF/epub3-samples/releases/download/20230704/accessible_epub_3.epub"
    return get_epub(tmp_path, url)


def get_epub(tmp_path: Path, url: str) -> Path:
    out = tmp_path / basename(url)
    urlretrieve(url, out)
    return out


def test_all_good(happy_epub):
    runner = CliRunner()

    result = runner.invoke(epub_fixer, [str(happy_epub)])
    assert result.exit_code == 0
    assert result.output == "No issues found\n"
