import os
import pandas as pd
import requests
from zipfile import ZipFile
from pathlib import Path
from urllib.parse import urlparse
from typing import Iterable, Callable, List

from helpers import ensure_scheme, append_to_log


def download_file(url: str, save_path: str) -> bool:
    """Download a single file and save it locally."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"Successfully downloaded {url}")
        return True
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return False


def download_files(
    urls: Iterable[str],
    download_dir: str,
    record_file_path: str,
    progress_callback: Callable[[int, int], None] | None = None,
) -> List[str]:
    """Download multiple files and update the record file."""
    if os.path.exists(record_file_path):
        downloaded_df = pd.read_csv(record_file_path)
        downloaded_urls = set(downloaded_df['url'])
    else:
        downloaded_urls = set()

    os.makedirs(download_dir, exist_ok=True)
    file_paths: List[str] = []
    new_urls: List[str] = []
    total = len(list(urls)) if not isinstance(urls, list) else len(urls)

    for index, url in enumerate(urls, start=1):
        if url in downloaded_urls:
            print(f"Already downloaded {url}")
            if progress_callback:
                progress_callback(index, total)
            continue
        parsed_url_path = urlparse(url).path
        extension = os.path.splitext(parsed_url_path)[1] or '.jpg'
        file_name = f"file_{index}{extension}"
        local_file = os.path.join(download_dir, file_name)
        if download_file(url, local_file):
            file_paths.append(local_file)
            new_urls.append(url)
        if progress_callback:
            progress_callback(index, total)

    if new_urls:
        append_to_log(record_file_path, new_urls)

    return file_paths


def create_zip(file_paths: Iterable[str], zip_file_path: str) -> None:
    """Create a zip archive containing all provided file paths."""
    with ZipFile(zip_file_path, 'w') as zipf:
        for file_path in file_paths:
            if os.path.isfile(file_path):
                zipf.write(file_path, os.path.basename(file_path))


def main() -> None:
    csv_file_path = os.environ.get('CSV_FILE_PATH', 'path_to_your_csv_file.csv')
    record_file_path = 'downloaded_urls.csv'
    downloads_path = str(Path.home() / 'Downloads')
    file_dir = os.path.join(downloads_path, 'files')
    zip_file_path = os.path.join(downloads_path, 'files.zip')

    df = pd.read_csv(csv_file_path)
    urls = [ensure_scheme(u) for u in df['poster URL'].dropna().tolist()]

    file_paths = download_files(urls, file_dir, record_file_path)
    create_zip(file_paths, zip_file_path)
    print(f"Files have been downloaded and zipped into {zip_file_path}")


if __name__ == "__main__":
    main()
