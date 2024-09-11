# File Downloader and Zipper Script

This script downloads files from a list of URLs in a CSV file, saves them locally, and then compresses them into a zip file. It also keeps a record of already downloaded files to avoid redundant downloads.

## Features
- Downloads files from a list of URLs in a CSV file.
- Checks for missing URL schemes and corrects them (adds `https://` if needed).
- Keeps track of already downloaded files using a separate CSV log (`downloaded_urls.csv`).
- Compresses all downloaded files into a zip file.
- Supports resuming from where you left off by checking the log file.

## Prerequisites

Ensure you have the following installed:

- [Python 3.x](https://www.python.org/downloads/)
- [Pandas](https://pandas.pydata.org/)
- [Requests](https://pypi.org/project/requests/)

## Installation

1. **Clone the repository:**

```bash
git clone https://github.com/bnishit/bulk-image-downloader-from-url.git
cd bulk-image-downloader-from-url
```

## Usage

1. **Prepare your CSV file**:  
   The script expects a CSV file with a column named `'poster URL'` containing the URLs of files you want to download.

2. **Modify paths**:  
   Update the `file_path` variable in the script to point to your CSV file containing URLs. You can also update the path for the `record_file_path` if needed (this is where already downloaded URLs are stored).

3. **Run the script**:

```bash
python download_and_zip.py
```

4. **Output**:
   - The downloaded files will be saved in a `files` directory within your `Downloads` folder.
   - The script will create a `files.zip` file containing all the downloaded files in your `Downloads` folder.

## Customization

- You can change the download folder and zip file location by modifying the `downloads_path` and `file_dir` variables.
- The `record_file_path` keeps track of already downloaded URLs. You can change or reset this log if necessary.
