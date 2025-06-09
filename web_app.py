import os
import threading
from pathlib import Path
from flask import (
    Flask,
    request,
    redirect,
    url_for,
    jsonify,
    send_file,
    send_from_directory,
    Response,
)
import pandas as pd
from download_and_zip import download_files, create_zip
from helpers import ensure_scheme

app = Flask(__name__)

progress = {
    "total": 0,
    "completed": 0,
    "done": False,
    "zip_path": "",
}

def download_worker(urls):
    downloads_path = str(Path.home() / 'Downloads')
    file_dir = os.path.join(downloads_path, 'files')
    zip_file = os.path.join(downloads_path, 'files.zip')

    def update_progress(current, total):
        progress["total"] = total
        progress["completed"] = current

    file_paths = download_files(urls, file_dir, 'downloaded_urls.csv', update_progress)
    create_zip(file_paths, zip_file)
    progress["done"] = True
    progress["zip_path"] = zip_file

@app.route('/', methods=['GET'])
def index():
    return Response(
        """
        <html>
        <body>
            <h1>Bulk Image Downloader</h1>
            <form action="/upload" method="post" enctype="multipart/form-data">
                <input type="file" name="file" accept=".csv" required>
                <input type="submit" value="Upload">
            </form>
            <div id="status"></div>
            <script>
            async function poll(){
                const res = await fetch('/progress');
                const data = await res.json();
                if(data.total){
                    document.getElementById('status').innerText = `Downloaded ${data.completed} of ${data.total}`;
                }
                if(data.done){
                    document.getElementById('status').innerHTML += '<br><a href="/download">Download Zip</a><br><a href="/thumbnails">View Thumbnails</a>';
                    clearInterval(interval);
                }
            }
            const interval = setInterval(poll, 2000);
            </script>
        </body>
        </html>
        """,
        mimetype='text/html'
    )

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    if not file:
        return redirect(url_for('index'))
    df = pd.read_csv(file)
    urls = [ensure_scheme(u) for u in df['poster URL'].dropna().tolist()]
    progress.update({"total": len(urls), "completed": 0, "done": False, "zip_path": ""})
    thread = threading.Thread(target=download_worker, args=(urls,))
    thread.start()
    return redirect(url_for('index'))

@app.route('/progress')
def get_progress():
    return jsonify(progress)

@app.route('/download')
def download_zip():
    if progress.get("zip_path") and os.path.exists(progress["zip_path"]):
        return send_file(progress["zip_path"], as_attachment=True)
    return "No file", 404

@app.route('/thumbnails')
def thumbnails():
    downloads_path = str(Path.home() / 'Downloads' / 'files')
    if not os.path.isdir(downloads_path):
        return "No images", 404
    items = os.listdir(downloads_path)
    images = ''.join(f'<img src="/files/{f}" height="100">' for f in items)
    html = f"<html><body>{images}</body></html>"
    return Response(html, mimetype='text/html')

@app.route('/files/<path:filename>')
def serve_file(filename: str):
    downloads_path = str(Path.home() / 'Downloads' / 'files')
    return send_from_directory(downloads_path, filename)

if __name__ == '__main__':
    app.run(debug=True)

