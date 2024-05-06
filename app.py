from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS, cross_origin
import sys
from K_Means import K_Means
from k_means_utils import get_timestamp_str

app = Flask(__name__)
CORS(app)

APP_PATH = "http://127.0.0.1:8000"
result_path = ""


@app.route('/upload', methods=['POST'])
@cross_origin()
def upload_image():
    global result_path
    # Check for missing file
    if 'imageFile' not in request.files:
        print("No file received", file=sys.stderr)  # Print error message to stderr
        return jsonify({'message': 'No file received'}), 400
    # Get file and k value
    file = request.files['imageFile']
    k = int(request.form['k'])

    if file:
        # Save file into src_images
        file_path = "src_images/" + file.filename
        file.save(file_path)

        # Run k-means
        project_name = file.filename.rsplit(".", 1)[0]  # Get filename w/o extension
        k_values = (k, k, 1)
        num_runs = 1
        img_extension = ".jpeg"  # to change later?
        palette_replace = True
        resize_level = 100
        log_file_name = f"{get_timestamp_str()}__{project_name}_{str(num_runs)}x_{k_values[0]}"
        # END DEFAULTS
        k_means_process = K_Means(project_name, k_values, file_path, num_runs, log_file_name, img_extension,
                                  palette_replace, resize_level)
        result_path = k_means_process.run()

        return jsonify({'message': f'File {file.filename} received with number {k}'}), 200


@app.route('/result', methods=['GET'])
@cross_origin()
def get_result():
    actual_path = result_path.rsplit("/", 1)[1]
    return send_from_directory("./results", actual_path)


if __name__ == '__main__':
    app.run(port=8000)
