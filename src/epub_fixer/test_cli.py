from os.path import basename
from urllib.request import urlretrieve

from .__main__ import main


def test_all_good(tmp_path):
    url = "https://github.com/IDPF/epub3-samples/releases/download/20230704/accessible_epub_3.epub"
    out = tmp_path / basename(url)
    urlretrieve(url, out)

    main([str(out)])
