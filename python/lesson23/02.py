import pytest
from importlib import util
from pathlib import Path


def load_parser():
    path = Path(__file__).with_name("01_parser.py")
    spec = util.spec_from_file_location("lesson_23_parser", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("module load failed: 01_parser.py")

    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


parser = load_parser()
parse_price = parser.parse_price
parse_quote = parser.parse_quote


def test_parse_price_yen():
    assert parse_price("¥1,500") == 1500


def test_parse_price_dollar():
    assert parse_price("$29.99") == 29.99


def test_parse_price_en():
    assert parse_price("1,000円") == 1000


def test_parse_price_plain():
    assert parse_price("1000") == 1000


def test_parse_price_invalid():
    with pytest.raises(ValueError):
        parse_price("")


VALID_HTML = """
<div class="quote">
  <span class="text">&#8220;The world as we have created it...&#8221;</span>
  <span><small class="author">Albert Einstein</small></span>
</div>
"""

MISSING_HTML = """
<div>
  <p>何もない</p>
</div>
"""


def test_parse_quote_valid():
    result = parse_quote(VALID_HTML)
    assert result is not None
    assert "Einstein" in result["author"]


def test_parse_quote_author():
    result = parse_quote(VALID_HTML)
    assert result["author"] == "Albert Einstein"


def test_parse_quote_missing():
    assert parse_quote(MISSING_HTML) is None


def test_parse_quote_empty():
    assert parse_quote("") is None
