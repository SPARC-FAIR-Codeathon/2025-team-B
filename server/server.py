from unittest import result
from flask import Flask, request, send_file, send_from_directory, jsonify
import scipy.io
import pandas as pd
import io
from flask_cors import CORS
import re
import requests
import zipfile
import shutil
from pathlib import Path
import os



from sparcfuse.sparc_fuse_core import (get_sparc_datasets_by_id, list_primary_files,
                      print_project_metadata, 
                      download_and_move_sparc_file, list_sparc_datasets,
                      download_and_convert_sparc_data)



app = Flask(__name__)
CORS(app)


DOWNLOAD_DIR = Path("../downloads")
CONVERTED_DIR = Path("../converted")
DESCRIPTOR_DIR = Path("../mapping_schemes")


def zip_items(output_zip, items_to_zip):
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for item in items_to_zip:
            print(f"Adding item to zip: {item}")
            if os.path.isfile(item):
                # Add file with relative path
                zipf.write(item, arcname=os.path.basename(item))
            elif os.path.isdir(item):
                # Recursively add directory contents
                for root, _, files in os.walk(item):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Store relative path inside the zip
                        arcname = os.path.relpath(file_path, start=os.path.dirname(item))
                        zipf.write(file_path, arcname=arcname)

def remove_items(paths):
    for path in paths:

        try:
            if os.path.isfile(path):
                os.remove(path)
                print(f"Removed file: {path}")
            elif os.path.isdir(path):
                shutil.rmtree(path)
                print(f"Removed directory: {path}")
            else:
                print(f"Not found: {path}")
        except Exception as e:
            print(f"Error removing {path}: {e}")

@app.route('/download', methods=['POST'])
def download():

    # TODO: check file. "../../../etc/passwd"

    data = request.get_json()
    download_file = data.get("file")
    if not download_file:
        return {"error": "Missing file"}, 400

    # Validate that file exists
    download_file = Path(f"{CONVERTED_DIR}/{download_file}")
    print(f"Attempting to download file: {download_file}")
    if not os.path.isfile(download_file):
        return {"error": "File not found"}, 404

    print(download_file.name)
    return send_file(
        path_or_file=Path(f"{download_file}"),
        as_attachment=True,
        download_name=download_file.name,
    )



@app.route('/download_and_convert', methods=['POST'])
def download_and_convert_entire_dataset():
    data = request.get_json()
    dataset_id = data["dataset_id"]
    path = data.get("path", None)
    dst_format = data["dst_format"]
    add_unsupported = data.get("add_unsupported", False)

    result = download_and_convert_sparc_data(
        dataset_id,
        primary_paths=path,
        output_dir=CONVERTED_DIR, 
        file_format=dst_format,  # zarr or "zarr.zip",
        descriptors_dir=DESCRIPTOR_DIR
    )

    unsupported_files = []

    result_paths = []
    for r in result:
        if r["status"] == "ok":
            result_paths.append(r["std_path"])
        elif r["status"] == "unsupported":
            print(f"unsupported {r['rel_path']}")
            if not add_unsupported:
                unsupported_files.append(r["rel_path"])
                continue
            try:
                download_and_move_sparc_file(
                    rel_path= r["rel_path"],
                    dataset_id=dataset_id,
                    output_dir=f"{CONVERTED_DIR}/" + "/".join(r["rel_path"].split('/')[:-1]),
                )
                result_paths.append(f"{CONVERTED_DIR}/{r['rel_path']}")
            except Exception as e:
                print(f"Error downloading {r['rel_path']}: {e}")
        else:
            print(f"Error converting {r}")

    if unsupported_files:
        unsupported_files_path = Path(f'{CONVERTED_DIR}/unsupported_files.txt')
        with open(unsupported_files_path, 'w') as f:
            f.writelines(unsupported_files)
        result_paths.append(unsupported_files_path)


    if not result_paths:
        return jsonify({
            'status': 'error',
            'message': 'No files were converted or downloaded successfully.'
        }), 500
    
    converted_path = Path(result_paths[0])
    converted_filename = converted_path.name

    if len(result_paths) > 1 or dst_format == "zarr":
        if path is None:
            converted_filename = f"{dataset_id}.{dst_format}.zip"
        else: 
            converted_filename = f"{converted_filename}.zip"
        zip_items(Path(f"{CONVERTED_DIR}/{converted_filename}"), result_paths)
        remove_items(result_paths)
    
    return jsonify({
        'status': 'success',
        'file': str(converted_filename)
    })

    
    




if __name__ == '__main__':
    app.run(port=5000)

