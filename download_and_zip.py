import pandas as pd
import os
import requests
from zipfile import ZipFile
from pathlib import Path
from urllib.parse import urlparse

# Placeholder for paths
csv_file_path = os.environ.get('CSV_FILE_PATH', 'path_to_your_csv_file.csv')  # Update with the actual CSV file path or set CSV_FILE_PATH env var
record_file_path = 'downloaded_urls.csv'  # Path to the CSV tracking downloaded URLs

# Load the CSV file
df = pd.read_csv(csv_file_path)

# Extract URLs from the 'poster URL' column
urls = df['poster URL'].dropna().tolist()  # Ensure the CSV file has a column named 'poster URL'

# Correct the URLs by adding the scheme if missing
corrected_urls = ["https://" + url if not url.startswith("http") else url for url in urls]

# Load the record of downloaded URLs
if os.path.exists(record_file_path):
    downloaded_df = pd.read_csv(record_file_path)
    downloaded_urls = set(downloaded_df['url'])
else:
    downloaded_urls = set()

# Directory to save downloaded files
downloads_path = str(Path.home() / 'Downloads')
file_dir = os.path.join(downloads_path, 'files')
os.makedirs(file_dir, exist_ok=True)

# Function to download a file
def download_file(url, save_path):
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

# Download all files, only if not already downloaded
file_paths = []
new_urls = []
for i, url in enumerate(corrected_urls):
    if url in downloaded_urls:
        print(f"Already downloaded {url}")
        continue
    parsed_url_path = urlparse(url).path
    file_extension = os.path.splitext(parsed_url_path)[1]
    file_name = f"file_{i+1}{file_extension}"
    local_file_path = os.path.join(file_dir, file_name)
    if download_file(url, local_file_path):
        file_paths.append(local_file_path)
        new_urls.append(url)

# Update the record of downloaded URLs
if new_urls:
    new_urls_df = pd.DataFrame(new_urls, columns=['url'])
    if os.path.exists(record_file_path):
        new_urls_df.to_csv(record_file_path, mode='a', header=False, index=False)
    else:
        new_urls_df.to_csv(record_file_path, index=False)

# Create a zip file containing all files in ``file_dir``
zip_file_path = os.path.join(downloads_path, 'files.zip')

# Collect all existing files in ``file_dir`` to ensure the archive always
# contains every downloaded file even when the script is rerun without new
# URLs.
all_existing_files = [
    os.path.join(file_dir, f) for f in os.listdir(file_dir) if os.path.isfile(os.path.join(file_dir, f))
]

# Merge newly downloaded file paths with the existing ones, avoiding duplicates
all_files_to_zip = list(dict.fromkeys(all_existing_files + file_paths))

with ZipFile(zip_file_path, 'w') as zipf:
    for file_path in all_files_to_zip:
        zipf.write(file_path, os.path.basename(file_path))

print(f"Files have been downloaded and zipped into {zip_file_path}")
