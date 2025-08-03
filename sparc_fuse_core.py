# ── standard library ────────────────────────────────────────────────────────
from __future__ import annotations 
import json
import os
import shutil
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import quote
import tempfile

# ── third-party ─────────────────────────────────────────────────────────────
import imageio.v3 as iio
import matplotlib.pyplot as plt
import numpy as np
import requests
import tifffile
import zarr
from nd2reader import ND2Reader
from packaging.version import parse as vparse
from tqdm import tqdm
import s3fs
import xarray as xr
from datetime import datetime

# ── project-specific / local ────────────────────────────────────────────────
from utils import (
    load_all_descriptors,
    match_best_mapping,
    save_standardized_output,
)
from sparc.client import SparcClient


client = SparcClient(connect=False, config_file='config.ini')

def fetch_dataset_metadata(dataset_id):
    """
    Fetches metadata for a specified dataset from the Pennsieve Discover API.
    
    Args:
        dataset_id (str or int): The unique identifier of the dataset to fetch metadata for.
    
    Returns:
        dict: The metadata of the specified dataset as returned by the API.
    
    Raises:
        requests.HTTPError: If the HTTP request to the API fails.
    """
    metadata_url = f"https://api.pennsieve.io/discover/datasets/{dataset_id}/versions/1/metadata"
    resp = requests.get(metadata_url)
    resp.raise_for_status()
    return resp.json()

def list_primary_files(dataset_id):
    """
    Retrieve primary files from a dataset's metadata.
    
    Args:
        dataset_id (str): The unique identifier of the dataset.
   
     Returns:
        tuple: A tuple containing:
            - primary_files (list): A list of file dictionaries whose paths start with "files/primary/".
            - metadata (dict): The complete metadata dictionary for the dataset.
    
    Raises:
        Any exceptions raised by fetch_dataset_metadata.
    """
    metadata = fetch_dataset_metadata(dataset_id)
    primary_files = [
        f for f in metadata.get("files", [])
        if f.get("path", "").startswith("files/primary/")
    ]
    return primary_files, metadata

def print_project_metadata(metadata):
    """
    Prints the 'item' field from the provided metadata dictionary in a formatted JSON structure.
    
    Args:
        metadata (dict): A dictionary containing project metadata. Expected to have an 'item' key.
    
    Returns:
        None
    """
    project = metadata.get("item", {})
    print(json.dumps(project, indent=2))

def download_and_move_sparc_file(rel_path, dataset_id, output_dir):
    """
    Downloads a file from a SPARC dataset using the provided relative path and dataset ID,
    then moves the downloaded file to the specified output directory.

    The function ensures the relative path starts with 'primary/', constructs the appropriate
    query path for the SPARC API, and handles file download and movement. If the file is not
    found or an error occurs during download or movement, an error message is printed.

    Args:
        rel_path (str): The relative path to the file within the SPARC dataset.
        dataset_id (str): The identifier of the SPARC dataset to download from.
        output_dir (str): The directory where the downloaded file should be moved.

    Raises:
        FileNotFoundError: If no matching file is found in the SPARC dataset.
        Exception: For any other errors encountered during download or file movement.
    """
    if not rel_path.startswith("primary/"):
        rel_path = f"primary/{rel_path}"

    # SPARC expects 'files/primary/...'
    query_path = f"files/{rel_path}"
    local_filename = os.path.basename(rel_path)

    print(f"[INFO] Downloading {rel_path} from SPARC dataset {dataset_id}...")

    try:
        files = client.pennsieve.list_files(dataset_id=dataset_id, query=query_path)
        if not files:
            raise FileNotFoundError(f"No matching file for {query_path}")

        result = client.pennsieve.download_file(file_list=files[0])
        print(f"[INFO] Download result: {result}")

        # Move file to output directory
        os.makedirs(output_dir, exist_ok=True)
        src_path = os.path.abspath(local_filename)
        dest_path = os.path.join(output_dir, local_filename)
        shutil.move(src_path, dest_path)
        print(f"[INFO] Moved file to: {dest_path}")

        # TODO: your actual file conversion logic goes here

    except Exception as e:
        print(f"[ERROR] Could not download or move file: {e}")


def list_sparc_datasets(max_id=1000):
    """
    Retrieves and categorizes SPARC datasets by their type.

    This function queries the metadata client for datasets with IDs in the range 0 to `max_id` (inclusive),
    then counts and groups the datasets by their type name. It prints the response and a summary of dataset
    type counts.

    Args:
        max_id (int, optional): The maximum dataset ID to include in the query. Defaults to 1000.

    Returns:
        dict: A mapping from dataset type names to lists of dataset IDs belonging to each type.
    """
    ids = list(range(0, 1001))
    id_strings = [f'"{i}"' for i in ids]
    id_list_str = ", ".join(id_strings)

    body = f'''
    {{
    "size": {max_id},
    "query": {{
        "terms": {{
        "_id": [ {id_list_str} ]
        }}
    }}
    }}
    '''
    body_json = json.loads(body)
    response = client.metadata.search_datasets(body_json)
    type_counter = Counter()
    type_id_map = defaultdict(list)

    print("response: ", json.dumps(response, indent=2))

    for d in response["hits"]["hits"]:
        try:
            type_name = d["_source"]["item"]["types"][0]["name"]
        except (KeyError, IndexError, TypeError):
            type_name = "<invalid type>"
        dataset_id = d.get("_id", "<no id>")
        type_counter[type_name] += 1
        type_id_map[type_name].append(dataset_id)

    print("Dataset type counts:")
    for t, count in type_counter.items():
        print(f"  {t}: {count}")
    return type_id_map

def get_sparc_datasets_by_id(ids):
    """
    Retrieve SPARC datasets from the metadata client by their IDs and group them by type.

    Args:
        ids (int, list, tuple, or set): A single dataset ID or a collection of dataset IDs to query.

    Returns:
        dict: A dictionary mapping dataset type names to lists of dataset IDs that belong to each type.

    Raises:
        TypeError: If the input is not an int, list, tuple, or set.

    Notes:
        - The function prints the constructed query and the response for debugging purposes.
        - If a dataset does not have a valid type, it is grouped under the key "<invalid type>".
        - If a dataset does not have an ID, it is represented as "<no id>" in the result.
    """
    # Normalize to list
    if isinstance(ids, int):
        ids = [ids]
    elif not isinstance(ids, (list, tuple, set)):
        raise TypeError("Input must be an int or a list/tuple/set of ints")

    # Build query
    id_strings = [f'"{i}"' for i in ids]
    id_list_str = ", ".join(id_strings)
    body = f'''
    {{
      "size": 1000,
      "query": {{
        "terms": {{
          "_id": [ {id_list_str} ]
        }}
      }}
    }}
    '''
    print("Query:", body)

    # Submit search
    body_json = json.loads(body)
    response = client.metadata.search_datasets(body_json)
    type_counter = Counter()
    type_id_map = defaultdict(list)

    print("Response:", json.dumps(response, indent=2))

    for d in response["hits"]["hits"]:
        try:
            type_name = d["_source"]["item"]["types"][0]["name"]
        except (KeyError, IndexError, TypeError):
            type_name = "<invalid type>"
        dataset_id = d.get("_id", "<no id>")
        type_counter[type_name] += 1
        type_id_map[type_name].append(dataset_id)

    return type_id_map

# -------------------------------------------------------------------------
# 1. decide default OME-Zarr version (zarr<3 → v0.4, else v0.5)
# -------------------------------------------------------------------------
_ZARR_GE_3 = vparse(zarr.__version__) >= vparse("3.0.0b2")
_DEFAULT_OZ_VER = "0.5" if _ZARR_GE_3 else "0.4"

# -------------------------------------------------------------------------
# 2. sets of extensions that need special treatment
# -------------------------------------------------------------------------
IMAGING_EXTS = {
    ".tif", ".tiff", ".czi", ".nd2", ".lsm", ".jpx", ".svs", ".ims", ".png",
    ".jpg", ".jpeg", ".bmp", ".vsi", ".jp2", ".roi", ".dm3", ".pxp", ".ipf",
    ".lif", ".ima", ".mrxs", ".obj", ".avi", ".exf", ".cxd"
}


_RGB_EXTS      = {".jpg", ".jpeg", ".png", ".bmp"}
_BF_EXTS       = {
    ".jpx", ".jp2", ".svs", ".ims", ".czi", ".vsi", ".mrxs",
    ".obj", ".exf", ".cxd", ".ima", ".dm3", ".pxp", ".ipf", ".roi", ".lsm"
}

def _run(cmd: list[str]) -> None:
    """
    (subprocess.run with nice error surfacing) --> Executes a command using subprocess.run and raises a RuntimeError with detailed output if the command fails.

    Args:
        cmd (list[str]): The command and its arguments to execute as a list of strings.

    Raises:
        RuntimeError: If the command returns a non-zero exit code, includes the command, stdout, and stderr in the error message.
    """
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(
            f"Command failed ({' '.join(cmd)}):\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )

# -------------------------------------------------------------------------
# 3. main helper
# -------------------------------------------------------------------------
def convert_imaging_file(
    local_path: Path,
    *,
    output_dir: Path,
    ome_zarr_version: str | None = None,
    method: str = "dask_image_gaussian",
    output_scale: str = "3",
) -> Path:
    """
    Converts *local_path* to an OME-Zarr store and returns its Path.

    * RGB images (.jpg/.png/…) are re-packed to channel-first OME-TIFF.
    * ND2 is converted with nd2reader.
    * LIF + a long list of bio-formats-compatible slide formats go through
      `bfconvert`.
    * Plain TIFFs are sent directly to ngff-zarr.
    * Everything else is attempted “as is” (ngff-zarr can open many types).

    Parameters:
        local_path (Path): Path to the input imaging file.
        output_dir (Path): Directory where the OME-Zarr store will be created.
        ome_zarr_version (str | None, optional): OME-Zarr version to use. Defaults to a module-level default if None.
        method (str, optional): Downsampling method for ngff-zarr. Defaults to "dask_image_gaussian".
        output_scale (str, optional): Output scale for ngff-zarr. Defaults to "3".

    Returns:
        Path: Path to the generated OME-Zarr store.

    Raises:
        ValueError: If an RGB image does not have the expected shape.
    """
    ome_zarr_version = ome_zarr_version or _DEFAULT_OZ_VER
    ext     = local_path.suffix.lower()
    tmp_tif = None                       # will hold any intermediate TIFF

    # ---------- A. convert to (OME)-TIFF if needed -------------------------
    if ext in {".tif", ".tiff"}:
        tif_path = local_path

    elif ext == ".nd2":
        with ND2Reader(str(local_path)) as nd2:
            arr = (np.stack([img for img in nd2])
                   if len(nd2) > 1 else nd2.get_frame_2D(c=0))
        tmp_tif = local_path.with_suffix(".ome.tif")
        iio.imwrite(tmp_tif, arr.astype(np.uint16))
        tif_path = tmp_tif

    elif ext in _RGB_EXTS:
        # RGB → channel-first, then write real TIFF
        img = iio.imread(local_path)
        if img.ndim != 3 or img.shape[2] not in (3, 4):
            raise ValueError(f"Expected HxWxC RGB/RGBA image, got shape {img.shape}")
        img_cyx = np.transpose(img, (2, 0, 1))           # (C, Y, X)
        tmp_tif = local_path.with_suffix(".ome.tif")
        tifffile.imwrite(tmp_tif, img_cyx, photometric="rgb")
        tif_path = tmp_tif

    elif ext == ".lif" or ext in _BF_EXTS:
        tmp_tif = local_path.with_suffix(".ome.tif")
        _run(["bfconvert", str(local_path), str(tmp_tif)])
        tif_path = tmp_tif

    else:
        # hope ngff-zarr can open it directly
        tif_path = local_path

    # ---------- B. run ngff-zarr ------------------------------------------
    zarr_out = output_dir / f"{tif_path.stem}.ome.zarr"
    cmd = [
        "ngff-zarr",
        "-i", str(tif_path),
        "-o", str(zarr_out),
        "--ome-zarr-version", ome_zarr_version,
        "--method", method,
        "--output-scale", output_scale,
    ]
    _run(cmd)

    # ---------- C. clean up and return ------------------------------------
    if tmp_tif and tmp_tif.exists():
        tmp_tif.unlink()
    return zarr_out


# -------------------------------------------------------------------------
# 0. build sets for fast membership checks
# -------------------------------------------------------------------------
modality_lookup = {
    # Imaging formats
    ".tif": "Imaging", ".tiff": "Imaging", ".czi": "Imaging", ".nd2": "Imaging", ".lsm": "Imaging",
    ".jpx": "Imaging", ".svs": "Imaging", ".ims": "Imaging", ".png": "Imaging", ".jpg": "Imaging",
    ".jpeg": "Imaging", ".bmp": "Imaging", ".vsi": "Imaging", ".jp2": "Imaging", ".roi": "Imaging",
    ".dm3": "Imaging", ".pxp": "Imaging", ".ipf": "Imaging", ".lif": "Imaging", ".ima": "Imaging",
    ".mrxs": "Imaging", ".obj": "Imaging", ".avi": "Imaging", ".exf": "Imaging", ".cxd": "Imaging",

    # Time Series formats
    ".mat": "Time Series", ".smr": "Time Series", ".csv": "Time Series",
    ".adicht": "Time Series", ".hdf5": "Time Series", ".h5": "Time Series", ".ets": "Time Series",
    ".abf": "Time Series", ".rhd": "Time Series", ".nev": "Time Series", ".ns5": "Time Series",
    ".ns2": "Time Series", ".ns1": "Time Series", ".smrx": "Time Series", ".wav": "Time Series",
    ".acq": "Time Series", ".tbk": "Time Series", ".tdx": "Time Series", ".tev": "Time Series",
    ".tin": "Time Series", ".tnt": "Time Series", ".tsq": "Time Series", ".eeg": "Time Series",
    ".vmrk": "Time Series", ".vhdr": "Time Series", ".sev": "Time Series", ".sam": "Time Series",
    ".pss": "Time Series", ".psmethod": "Time Series",

    # Documentation formats
    ".pdf": "Docs", ".docx": "Docs", ".doc": "Docs", ".txt": "Docs",
    ".xlsx": "Docs", ".xls": "Docs", ".tsv": "Docs", ".json": "Docs", 
    ".xml": "Docs", ".db": "Docs", ".xfg": "Docs",
    
    # Other formats
    ".inf": "Other", ".zip": "Other", "": "Other", "(no ext)": "Other",
    ".s2r": "Other", ".ini": "Other", ".cmgui": "Other",
    ".mp4": "Other", ".gz": "Other", ".xlsm": "Other",
    ".db3": "Other", ".ccf": "Other", ".ex": "Other",
    ".conf": "Other", ".rdf": "Other", ".vtk": "Other", ".proj": "Other", ".pnp": "Other",
    ".hoc": "Other", ".fig	": "Other", ".dat": "Other"
}

IMAGING_EXTS     = {ext for ext, kind in modality_lookup.items() if kind == "Imaging"}
TIMESERIES_EXTS  = {ext for ext, kind in modality_lookup.items() if kind == "Time Series"}
SUPPORTED_EXTS   = IMAGING_EXTS | TIMESERIES_EXTS

def download_and_convert_sparc_data(
    dataset_id: int,
    primary_paths=None,
    *,
    output_dir: str | Path = "./output",
    descriptors_dir: str | Path = "./mapping_schemes",
    file_format: str = "npz",
    overwrite: bool = False,
):
    """
    Download → convert → clean-up pipeline.

    Imaging files are routed through `convert_imaging_file`;
    everything else goes through the descriptor-based mapper.
    Raw downloads are stored only in a TemporaryDirectory and are
    deleted as soon as conversion finishes.

    Parameters:
        dataset_id (int): The unique identifier of the SPARC dataset to process.
        primary_paths (list[str] | str | None, optional): List of relative paths to primary files within the dataset.
            If None, all primary files will be fetched from the dataset metadata.
        output_dir (str | Path, optional): Directory where converted files will be saved. Defaults to "./output".
        descriptors_dir (str | Path, optional): Directory containing mapping descriptors. Defaults to "./mapping_schemes".
        file_format (str, optional): Output file format for standardized data. Defaults to "npz".
        overwrite (bool, optional): If True, existing standardized files will be overwritten. Defaults to False.
        
    Returns:
        list[dict]: A list of dictionaries containing the results of the conversion process for each file.
            Each dictionary includes:
                - rel_path: Relative path of the file within the dataset.
                - local_path: Temporary local path where the file was downloaded.
                - std_path: Path to the standardized output file.
                - descriptor_id: ID of the mapping descriptor used (if applicable).
                - mapping_score: Score of the mapping (if applicable).
                - status: Status of the processing ("ok", "pending", "failed", "unsupported").
                - error: Error message if processing failed.

    Raises:
        ValueError: If no primary files are found to process.
        RuntimeError: If the download fails or the file cannot be processed.
        FileNotFoundError: If no matching file is found in the dataset for the given relative path.
        Exception: For any other errors encountered during the download or conversion process.
    
    Notes:
        - The function uses a temporary directory for downloading files, which is automatically cleaned up after processing.
        - The output directory is created if it does not exist.
        - Metadata from the SPARC dataset is fetched and included in the standardized output.
    - The function supports both imaging and time series data, routing them through appropriate conversion methods.
    """

    output_dir = Path(output_dir).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)

    # fetch metadata for the dataset
    sparc_meta = fetch_dataset_metadata(dataset_id)  # full JSON dict

    
    # ---------- A. figure out which primary files to work on --------------
    if primary_paths is None:
        files, _ = list_primary_files(dataset_id)
        primary_paths = [f["path"].replace("files/", "") for f in files]
    elif isinstance(primary_paths, str):
        primary_paths = [primary_paths]
    else:
        primary_paths = list(primary_paths)

    if not primary_paths:
        raise ValueError("No primary files to process.")

    # ---------- B. load mapping descriptors once --------------------------
    descriptors = load_all_descriptors(directory=str(descriptors_dir))
    results = []

    # ---------- C. main loop ----------------------------------------------
    for rel_path in tqdm(primary_paths, desc=f"Dataset {dataset_id}"):
        rec = {
            "rel_path": rel_path,
            "local_path": None,      # tmp path (will vanish)
            "std_path": None,
            "descriptor_id": None,
            "mapping_score": None,
            "status": "pending",
            "error": None,
        }

        ext = Path(rel_path).suffix.lower()
        if ext not in SUPPORTED_EXTS:
            rec.update(status="unsupported",
                       error=f"Extension '{ext}' not supported by pipeline")
            results.append(rec)
            continue                         # ── skip to next file ──


        try:
            # ===== 1. download into a fresh tmp dir =======================
            with tempfile.TemporaryDirectory() as tmpdir:
                tmpdir = Path(tmpdir)
                if not rel_path.startswith("primary/"):
                    rel_path_ds = f"primary/{rel_path}"
                else:
                    rel_path_ds = rel_path
                query_path = f"files/{rel_path_ds}"
                filename   = os.path.basename(rel_path_ds)

                files = client.pennsieve.list_files(dataset_id=dataset_id, query=query_path)
                if not files:
                    raise FileNotFoundError(f"No matching file for {query_path}")

                # Pennsieve will write into the *current* working directory.
                old_cwd = os.getcwd()
                try:
                    os.chdir(tmpdir)
                    client.pennsieve.download_file(file_list=files[0])   # ← no destination_dir
                finally:
                    os.chdir(old_cwd)

                local_file = tmpdir / filename
                if not local_file.exists():
                    # Some Pennsieve builds create a sub-folder; fall back to glob search
                    matches = list(tmpdir.rglob(filename))
                    if matches:
                        local_file = matches[0]
                    else:
                        raise RuntimeError(f"Download failed: {filename} not found in {tmpdir}")


                rec["local_path"] = str(local_file)  # for logging/debug

                # ===== 2. decide which conversion branch to use ===========
                ext = local_file.suffix.lower()
                if ext in IMAGING_EXTS:
                    # ---------- imaging branch ----------------------------
                    zarr_path = convert_imaging_file(
                        local_file, output_dir=output_dir
                    )
                    try:
                        root = zarr.open_group(str(zarr_path), mode="a")   # reopen for attrs
                        root.attrs["sparc_metadata"] = sparc_meta
                        root.attrs["sparc_dataset_id"] = dataset_id
                    finally:
                        root.store.close()

                    rec.update(
                        std_path=str(zarr_path),
                        descriptor_id="imaging-pipeline",
                        status="ok",
                    )

                else:
                    # ---------- signal-mapping branch ----------------------
                    mapping = match_best_mapping(
                        descriptors, filepath=str(local_file), sparc_id=dataset_id
                    )
                    if mapping["descriptor"] is None:
                        raise RuntimeError("No usable mapping descriptor found")

                    descriptor   = mapping["descriptor"]
                    result_dict  = mapping["result"]
                    std_base     = output_dir / f"{local_file.stem}_std"

                    if overwrite or not std_base.with_suffix(f".{file_format}").exists():
                        save_standardized_output(
                            output_path=str(std_base),
                            result_dict=result_dict,
                            descriptor=descriptor,
                            original_filename=local_file.name,
                            file_format=file_format,
                            metadata_overrides={"sparc_metadata": sparc_meta}
                        )

                    rec.update(
                        std_path=str(std_base.with_suffix(f".{file_format}")),
                        descriptor_id=descriptor.get("id"),
                        mapping_score=mapping["score"],
                        status="ok",
                    )

                # tmpdir (and raw download) are deleted automatically here
        except Exception as exc:
            rec.update(status="failed", error=str(exc))

        results.append(rec)

    return results

def upload_to_s3(local_path, bucket, remote_path, region="eu-north-1"):
    """
    Uploads files from a local directory to an AWS S3 bucket using the AWS CLI.

    Args:
        local_path (str): The local directory path to upload.
        bucket (str): The name of the target S3 bucket.
        remote_path (str): The destination path within the S3 bucket.
        region (str, optional): The AWS region where the bucket is located. Defaults to "eu-north-1".

    Raises:
        subprocess.CalledProcessError: If the AWS CLI command fails.
    """
    subprocess.run([
        "aws", "s3", "sync",
        local_path,
        f"s3://{bucket}/{remote_path}",
        "--region", region
    ], check=True)

def consolidate_s3_metadata(bucket, remote_path, region="eu-north-1"):
    """
    Consolidates Zarr metadata for a given S3 bucket and remote path.

    This function connects to an S3 bucket using the specified region, accesses the Zarr store at the given remote path,
    and consolidates its metadata to improve read performance and compatibility.

    Args:
        bucket (str): Name of the S3 bucket containing the Zarr store.
        remote_path (str): Path within the S3 bucket to the Zarr store.
        region (str, optional): AWS region where the S3 bucket is located. Defaults to "eu-north-1".

    Raises:
        zarr.errors.PathNotFoundError: If the specified path does not exist in the S3 bucket.
        botocore.exceptions.BotoCoreError: If there is an error connecting to S3.
    """
    fs = s3fs.S3FileSystem(anon=False, client_kwargs={"region_name": region})
    store = zarr.storage.FSStore(f"s3://{bucket}/{remote_path}", fs=fs)
    zarr.consolidate_metadata(store)

def create_xarray_zarr_from_raw(bucket, raw_zarr_path, xarray_zarr_path, region="eu-north-1"):
    """
    Reads raw Zarr data from an S3 bucket, constructs an xarray Dataset, and writes it back to S3 in Zarr format.

    Parameters
    ----------
    bucket : str
        Name of the S3 bucket containing the Zarr data.
    raw_zarr_path : str
        Path within the S3 bucket to the raw Zarr store.
    xarray_zarr_path : str
        Path within the S3 bucket where the xarray Zarr store will be saved.
    region : str, optional
        AWS region name for the S3 bucket (default is "eu-north-1").

    Notes
    -----
    - Assumes the raw Zarr store contains "signals" and "time" arrays.
    - The resulting xarray Dataset will have dimensions ("channel", "time"), where "channel" is inferred from the shape of "signals".
    - Requires `s3fs`, `zarr`, `xarray`, and `numpy` to be installed.
    """
    fs = s3fs.S3FileSystem(anon=False, client_kwargs={"region_name": region})
    raw_store = zarr.storage.FSStore(f"s3://{bucket}/{raw_zarr_path}", fs=fs)
    root = zarr.open_consolidated(raw_store)
    signals = root["signals"][:]
    time = root["time"][:]
    ds = xr.Dataset(
        {"signals": (("channel", "time"), signals)},
        coords={"time": ("time", time), "channel": ("channel", np.arange(signals.shape[0]))},
    )
    xarray_store = zarr.storage.FSStore(f"s3://{bucket}/{xarray_zarr_path}", fs=fs)
    ds.to_zarr(xarray_store, mode="w", consolidated=True)

def generate_and_upload_manifest(dataset_id, bucket, xarray_zarr_path, region="eu-north-1"):
    """
    Generates a manifest JSON file for a given dataset and uploads it to an S3 bucket.

    Args:
        dataset_id (str): The unique identifier for the dataset.
        bucket (str): The name of the S3 bucket where the manifest will be uploaded.
        xarray_zarr_path (str): The path to the Zarr dataset within the S3 bucket.
        region (str, optional): The AWS region where the S3 bucket is located. Defaults to "eu-north-1".

    Raises:
        subprocess.CalledProcessError: If the AWS CLI command fails during upload.

    The manifest contains metadata about the dataset, including its ID, Zarr path, generation timestamp, and file format.
    """
    manifest = {
        "dataset_id": dataset_id,
        "zarr_path": f"s3://{bucket}/{xarray_zarr_path}",
        "generated_at": f"{datetime.utcnow().isoformat()}Z",
        "file_format": "zarr"
    }
    with open("latest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    subprocess.run([
        "aws", "s3", "cp", "latest.json",
        f"s3://{bucket}/latest.json",
        "--region", region
    ], check=True)


def open_zarr_from_s3(bucket, zarr_path, region="eu-north-1"):
    """
    Lazily open a Zarr dataset stored in an S3 bucket using Xarray.

    Parameters:
        bucket (str): Name of the S3 bucket containing the Zarr dataset.
        zarr_path (str): Path to the Zarr dataset within the S3 bucket.
        region (str, optional): AWS region where the S3 bucket is located. Defaults to "eu-north-1".

    Returns:
        xarray.Dataset: The opened Zarr dataset as an Xarray Dataset object.

    Notes:
        - Requires appropriate AWS credentials to access the S3 bucket.
        - The function sets the AWS_DEFAULT_REGION environment variable if not already set.
        - The Zarr dataset must be consolidated.
    """
    os.environ.setdefault("AWS_DEFAULT_REGION", region)
    s3_uri = f"s3://{bucket}/{zarr_path}"
    return xr.open_zarr(s3_uri, consolidated=True)
