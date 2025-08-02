from flask import Flask, request, send_file, send_from_directory, jsonify
import scipy.io
import pandas as pd
import io
from flask_cors import CORS
import re
from sparc.client import SparcClient
import requests

from pathlib import Path
import os
import sys
sys.path.insert(1, '..')

from utils import match_best_mapping, load_all_descriptors, save_standardized_output

### https://docs.pennsieve.io/reference/createdataset

# https://sparc.science/datasets/file/436/1?path=files/primary/female/sub-1-2022-04-01/perf-1-2022-04-01-ST-MT/13-31-13-Amp-100-PW-300-Freq-020/PilotExpt26-220401-133140/PilotExpt26_220401_133140.rhd

# POST https://api.pennsieve.io/discover/datasets/436/versions/1/files/download-manifest
# paths[0] =                                     files/primary/female/sub-1-2022-04-01/perf-1-2022-04-01-ST-MT/13-31-13-Amp-100-PW-300-Freq-020/PilotExpt26-220401-133140/PilotExpt26_220401_133140.rhd

# https://api.pennsieve.io/discover

app = Flask(__name__)
CORS(app)
client = SparcClient(connect=False, config_file='config/config.ini')

# response = client.pennsieve.list_files(dataset_id=436, query='manifest', file_type='rhd')  
# response
# response = client.pennsieve.get('https://api.pennsieve.io/discover/datasets/436/versions/1/files/browse', params={'limit':20})
# response

# file_list = [{"datasetId": 436, "datasetVersion": 1}]
# response = client.pennsieve.()


DOWNLOAD_DIR = Path("../downloads")
CONVERTED_DIR = Path("../converted")
DESCRIPTORS = load_all_descriptors(directory="../mapping_schemes")



def download_file(dataset_id, dataset_version, file_path, output_name=None):
    print(f"Downloading file from dataset {dataset_id}, version {dataset_version}, path {file_path}")
    
    # #pennsieve_url = f"https://api.pennsieve.io/discover/datasets/{dataset_id}/versions/{dataset_version}/files/download-manifest"
    # pennsieve_url = f"https://api.pennsieve.io/zipit/discover"

    # #paths = ["files/primary/female/sub-1-2022-04-01/perf-1-2022-04-01-ST-MT/13-31-13-Amp-100-PW-300-Freq-020/PilotExpt26-220401-133140/PilotExpt26_220401_133140.rhd"]
    paths = [file_path]
    # pennsieve_json = {
        
    #     "paths": paths,
    #     "datasetId": dataset_id,
    #     "version": dataset_version,
    #     "archiveName":"sparc-portal-dataset-436-version-1-data"
    # }
    # # {
    # # "paths":["files/primary/female/sub-1-2022-04-01/perf-1-2022-04-01-ST-MT/13-31-13-Amp-100-PW-300-Freq-020/PilotExpt26-220401-133140/PilotExpt26_220401_133140.rhd","manifest.json"],
    # # "datasetId":"436",
    # # "version":"1",
    # # "archiveName":"sparc-portal-dataset-436-version-1-data"
    # # }
    # headers = {"content-type": "application/x-www-form-urlencoded"}
    # #headers = {"content-type": "multipart/form-data"}
    

    # url = "https://api.pennsieve.io/discover/datasets/436/versions/1/files/download-manifest"

    # payload = { "paths": ["files/primary/female/sub-1-2022-04-01/perf-1-2022-04-01-ST-MT/13-31-13-Amp-100-PW-300-Freq-020/PilotExpt26-220401-133140/PilotExpt26_220401_133140.rhd"] }
    
    src_format = file_path.split('.')[-1]
    
    json = {
        "data": {
            "paths": paths,
            "datasetId": dataset_id,
            "version": dataset_version,
        }
    }

    # download the files with zipit service
    url = "https://api.pennsieve.io/zipit/discover"
    headers = {"content-type": "application/json"}
    response = requests.post(url, json=json, headers=headers)

    # replace extension of the file with '.gz' if downloading more than 1 file
    if output_name is None and len(paths) > 1:
        output_name = "download.gz"
    elif output_name is None:
        output_name = f"download.{src_format}"
    
    output_file = Path(f"{DOWNLOAD_DIR}/{output_name}")
    with open(output_file, mode="wb+") as f:
        f.write(response.content)

    return output_file

    # response = requests.post(url, json=payload, headers=headers)


    # response = requests.post(pennsieve_url, data=pennsieve_json, headers=headers)

    # with open("file.rhd", mode="wb+") as f:
    #     f.write(response.content)

def convert_file(downloaded_file, src_path, src_filename, converted_path, dst_format="npz"):

    # Load all descriptor files from folder
    

    # Optional: specify SPARC ID for faster mapping
    result = match_best_mapping(DESCRIPTORS, downloaded_file, sparc_id=None)

    # Check if mapping was successful
    if result["descriptor"] is None:
        raise RuntimeError("No suitable mapping descriptor found.")

    # Show mapping result
    print("Selected mapping:", result['descriptor']['id'])
    print("Score:", result['score'])


    

    save_standardized_output(
        output_path=Path(f"{converted_path}/{src_filename.split('.')[0]}"),
        result_dict=result["result"],
        descriptor=result["descriptor"],
        original_filename=src_filename.split(".")[0],  # Remove extension
        annotations=result["result"].get("annotations", []),
        metadata_overrides=None,
        file_format=dst_format
    )

    return Path(f"{converted_path}/{src_filename.split('.')[0]}.{dst_format}")


@app.route('/convert', methods=['POST'])
def convert():
    data = request.get_json()
    href = data["href"]
    dst_format = data["type"]

    
    #https://sparc.science/datasets/file/436/1?path=files/primary/female/sub-1-2022-04-01/perf-1-2022-04-01-ST-MT/13-31-13-Amp-100-PW-300-Freq-020/PilotExpt26-220401-133140/PilotExpt26_220401_133140.rhd
    match = re.search(r'file/(\d+)/(\d+)\?path=(.*)', href)
    if not match:
        return "Invalid file URL", 400
    dataset_id = match.group(1)
    dataset_version = match.group(2)
    file_path = match.group(3)  # files/primary/female/sub-1-2022-04-01/perf-1-2022-04-01-ST-MT/13-31-13-Amp-100-PW-300-Freq-020/PilotExpt26-220401-133140/PilotExpt26_220401_133140.rhd"

    src_path = "/".join(file_path.split('/')[:-1]) # files/primary/female/sub-1-2022-04-01/perf-1-2022-04-01-ST-MT/13-31-13-Amp-100-PW-300-Freq-020/PilotExpt26-220401-133140
    src_filename = file_path.split('/')[-1] # PilotExpt26_220401_133140.rhd"
    src_format = src_filename.split('.')[-1] # rhd

    downloaded_name = f"download.{src_format}" # download.rhd
    converted_filename = f"{src_filename.split('.')[0]}.{dst_format}" # PilotExpt26_220401_133140.npz
    
    converted_path = Path(f"{CONVERTED_DIR}/{dataset_id}/{dataset_version}/{src_path}") # ../converted/files/primary/female/sub-1-2022-04-01/perf-1-2022-04-01-ST-MT/13-31-13-Amp-100-PW-300-Freq-020/PilotExpt26-220401-133140
    os.makedirs(converted_path, exist_ok=True)

    downloaded_file = download_file(dataset_id, dataset_version, file_path, output_name=downloaded_name)
    print(f"downloaded_file: {downloaded_file}")
    print(f"src_path: {src_path}")
    print(f"src_filename: {src_filename}")
    print(f"converted_path: {converted_path}")
    converted_file = convert_file(downloaded_file, src_path, src_filename, converted_path, dst_format=dst_format)

    #return send_file(converted_file, download_name=converted_name, as_attachment=True)

    return {"file": f"{converted_file}", "filename": converted_filename}, 200
    mat = scipy.io.loadmat(file)
    
    # For simplicity, use first variable
    key = next(k for k in mat.keys() if not k.startswith("__"))
    df = pd.DataFrame(mat[key])

    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)

    return send_file(io.BytesIO(output.getvalue().encode()), download_name='converted.csv', as_attachment=True)



@app.route('/download', methods=['POST'])
def download():

    # TODO: check file. "../../../etc/passwd"

    data = request.get_json()
    download_file = data.get("file")
    if not download_file:
        return {"error": "Missing file"}, 400

    # Validate that file exists
    download_file = Path(download_file)
    print(f"Attempting to download file: {download_file}")
    if not os.path.isfile(download_file):
        return {"error": "File not found"}, 404

    return send_file(
        path_or_file=Path(f"{download_file}"),
        as_attachment=True
    )




if __name__ == '__main__':
    app.run(port=5000)

