import os
import shutil
import zipfile
import urllib.parse
from flask import Flask, request, jsonify, send_file, render_template
import instaloader

# Initialize Flask app
app = Flask(__name__)

# Initialize Instaloader instance
L = instaloader.Instaloader()

# Set download folder
DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Helper function to create a zip archive
def create_zip(folder):
    zip_filename = folder + ".zip"
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for root, dirs, files in os.walk(folder):
            for file in files:
                zipf.write(os.path.join(root, file), file)
    return zip_filename

# Helper function to clear previous downloads
def clear_download_folder():
    if os.path.exists(DOWNLOAD_FOLDER):
        shutil.rmtree(DOWNLOAD_FOLDER)
    os.makedirs(DOWNLOAD_FOLDER)

# Helper function to download Instagram posts or reels
def download_post_or_reel(shortcode):
    post = instaloader.Post.from_shortcode(L.context, shortcode)
    L.download_post(post, target=DOWNLOAD_FOLDER)

# Helper function to download Instagram stories by username
def download_stories_by_username(username):
    profile = instaloader.Profile.from_username(L.context, username)
    L.download_stories(userids=[profile.userid], filename_target=DOWNLOAD_FOLDER)

# Route for homepage
@app.route('/')
def index():
    return render_template('index.html')

# Download Instagram photos, reels, or stories
@app.route('/download', methods=['POST'])
def download_instagram_content():
    # Clear previous downloads
    clear_download_folder()

    url = request.form['url']
    parsed_url = urllib.parse.urlparse(url)
    path = parsed_url.path.strip("/").split("/")

    try:
        if "reel" in path or "p" in path:
            # Handle Instagram Post or Reel (based on shortcode)
            shortcode = path[-1]
            download_post_or_reel(shortcode)
        elif len(path) == 1:
            # Handle Instagram Story (based on username)
            username = path[0]
            download_stories_by_username(username)
        else:
            return jsonify({"error": "Invalid URL format or content type."})
        
        # Create a zip of the downloaded content
        zip_file = create_zip(DOWNLOAD_FOLDER)
        return send_file(zip_file, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    # Run the app, accessible via external IP
    app.run(debug=True, host='0.0.0.0', port=5000)