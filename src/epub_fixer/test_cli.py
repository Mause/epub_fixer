from os.path import basename
from urllib.request import urlretrieve

from pytest import fixture

from .__main__ import main


@fixture
def happy_epub(tmp_path):
    url = "https://github.com/IDPF/epub3-samples/releases/download/20230704/accessible_epub_3.epub"
    out = tmp_path / basename(url)
    urlretrieve(url, out)
    return out


def test_all_good(happy_epub):
    assert main([str(happy_epub)], standalone_mode=False) == 0
