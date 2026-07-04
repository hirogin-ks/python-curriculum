from importlib import util
from pathlib import Path
from unittest.mock import Mock, patch

import requests


def load_scraper():
    path = Path(__file__).with_name("03_scraper.py")
    spec = util.spec_from_file_location("lesson_23_scraper", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("module load failed: 03_scraper.py")

    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


scraper = load_scraper()
fetch_urls = scraper.fetch_urls


def test_fetch_urls_calls_requests_get():
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.raise_for_status.return_value = None

    with patch("scraper.requests.get", return_value=mock_response) as mock_get:
        fetch_urls(["https://example.com"])

    mock_get.assert_called_once_with("https://example.com", timeout=10)


def test_fetch_urls_handles_http_error():
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404")

    with patch("scraper.requests.get", return_value=mock_response):
        fetch_urls(["https://example.com"])
