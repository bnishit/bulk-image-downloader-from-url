import os
import pandas as pd


def ensure_scheme(url: str) -> str:
    """Prepend https:// to the URL if no scheme is present."""
    if url.startswith(('http://', 'https://')):
        return url
    return 'https://' + url


def append_to_log(record_file_path: str, urls: list[str]) -> None:
    """Append unique URLs to the CSV log file."""
    existing_urls = set()
    if os.path.exists(record_file_path):
        existing_df = pd.read_csv(record_file_path)
        if 'url' in existing_df.columns:
            existing_urls = set(existing_df['url'])
    unique_urls = [u for u in urls if u not in existing_urls]
    if not unique_urls:
        return
    df = pd.DataFrame(unique_urls, columns=['url'])
    mode = 'a' if os.path.exists(record_file_path) else 'w'
    header = not os.path.exists(record_file_path)
    df.to_csv(record_file_path, mode=mode, header=header, index=False)
