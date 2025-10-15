from flask import Flask, render_template, request, url_for, jsonify, send_from_directory
import imageio.v3 as iio
import os
import time
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/create_gif', methods=['POST'])
def create_gif():
    uploaded_files = request.files.getlist('images')

    if len(uploaded_files) < 2:
        return jsonify({'error': 'Please upload at least two images.'}), 400

    images = []
    saved_paths = []
    for file in uploaded_files:
        filename = secure_filename(file.filename)
        if filename == '':
            continue
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        # ensure unique filename if conflicts
        base, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(filepath):
            filename = f"{base}-{counter}{ext}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            counter += 1
        file.save(filepath)
        saved_paths.append(filepath)
        images.append(iio.imread(filepath))

    # generate unique output filename
    ts = int(time.time() * 1000)
    output_name = f'output-{ts}.gif'
    output_gif = os.path.join(app.config['UPLOAD_FOLDER'], output_name)
    iio.imwrite(output_gif, images, duration=500, loop=0)

    gif_url = url_for('static', filename=output_name)
    download_url = url_for('download_gif', filename=output_name)
    return jsonify({'url': gif_url, 'download_url': download_url})


@app.route('/preview')
def preview():
    # serve the preview HTML page used by the client-side preview flow
    return render_template('preview.html')


@app.route('/download/<path:filename>')
def download_gif(filename):
    # send as attachment so browser downloads the file
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


if __name__ == '__main__':
    # Allow overriding the port with the PORT environment variable for easier local testing
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, port=port)