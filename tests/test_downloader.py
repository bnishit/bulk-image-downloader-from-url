import pandas as pd
from unittest.mock import patch
from helpers import ensure_scheme, append_to_log


def test_ensure_scheme_adds_https():
    assert ensure_scheme('example.com/img.jpg') == 'https://example.com/img.jpg'
    assert ensure_scheme('http://example.com') == 'http://example.com'
    assert ensure_scheme('https://example.com') == 'https://example.com'


def test_append_to_log_appends_unique_urls():
    existing_df = pd.DataFrame(['http://old.com/img.jpg'], columns=['url'])
    with patch('helpers.os.path.exists', return_value=True), \
         patch('helpers.pd.read_csv', return_value=existing_df), \
         patch('helpers.pd.DataFrame.to_csv', autospec=True) as mock_to_csv:
        append_to_log('downloaded_urls.csv', ['http://old.com/img.jpg', 'http://new.com/img.jpg'])
        mock_to_csv.assert_called_once()
        written_df = mock_to_csv.call_args.args[0]
        assert written_df['url'].tolist() == ['http://new.com/img.jpg']
        assert mock_to_csv.call_args.args[1] == 'downloaded_urls.csv'
        assert mock_to_csv.call_args.kwargs['mode'] == 'a'
