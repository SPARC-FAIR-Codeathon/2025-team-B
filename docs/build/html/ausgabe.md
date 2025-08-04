<div class="document" role="main" itemscope="itemscope" itemtype="http://schema.org/Article">

<div itemprop="articleBody">

<div id="module-sparc_fuse_core" class="section">

<span id="documentation"></span>

# Documentation<a href="#module-sparc_fuse_core" class="headerlink" title="Link to this heading"></a>

<span class="sig-prename descclassname"><span class="pre">sparc_fuse_core.</span></span><span class="sig-name descname"><span class="pre">consolidate_s3_metadata</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">bucket</span></span>*, *<span class="n"><span class="pre">remote_path</span></span>*, *<span class="n"><span class="pre">region</span></span><span class="o"><span class="pre">=</span></span><span class="default_value"><span class="pre">'eu-north-1'</span></span>*<span class="sig-paren">)</span><a href="_modules/sparc_fuse_core.html#consolidate_s3_metadata" class="reference internal"><span class="viewcode-link"><span class="pre">[source]</span></span></a><a href="#sparc_fuse_core.consolidate_s3_metadata" class="headerlink" title="Link to this definition"></a>  
Consolidates Zarr metadata for a given S3 bucket and remote path.

This function connects to an S3 bucket using the specified region, accesses the Zarr store at the given remote path, and consolidates its metadata to improve read performance and compatibility.

Parameters<span class="colon">:</span>  
- **bucket** (<a href="https://docs.python.org/3/library/stdtypes.html#str" class="reference external" title="(in Python v3.13)"><em>str</em></a>) – Name of the S3 bucket containing the Zarr store.

- **remote_path** (<a href="https://docs.python.org/3/library/stdtypes.html#str" class="reference external" title="(in Python v3.13)"><em>str</em></a>) – Path within the S3 bucket to the Zarr store.

- **region** (<a href="https://docs.python.org/3/library/stdtypes.html#str" class="reference external" title="(in Python v3.13)"><em>str</em></a>*,* *optional*) – AWS region where the S3 bucket is located. Defaults to “eu-north-1”.

Raises<span class="colon">:</span>  
- **zarr.errors.PathNotFoundError** – If the specified path does not exist in the S3 bucket.

- **botocore.exceptions.BotoCoreError** – If there is an error connecting to S3.

<!-- -->

<span class="sig-prename descclassname"><span class="pre">sparc_fuse_core.</span></span><span class="sig-name descname"><span class="pre">convert_imaging_file</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">local_path</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="https://docs.python.org/3/library/pathlib.html#pathlib.Path" class="reference external" title="(in Python v3.13)"><span class="pre">Path</span></a></span>*, *<span class="o"><span class="pre">\*</span></span>*, *<span class="n"><span class="pre">output_dir</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="https://docs.python.org/3/library/pathlib.html#pathlib.Path" class="reference external" title="(in Python v3.13)"><span class="pre">Path</span></a></span>*, *<span class="n"><span class="pre">ome_zarr_version</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="https://docs.python.org/3/library/stdtypes.html#str" class="reference external" title="(in Python v3.13)"><span class="pre">str</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><a href="https://docs.python.org/3/library/constants.html#None" class="reference external" title="(in Python v3.13)"><span class="pre">None</span></a></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">None</span></span>*, *<span class="n"><span class="pre">method</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="https://docs.python.org/3/library/stdtypes.html#str" class="reference external" title="(in Python v3.13)"><span class="pre">str</span></a></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">'dask_image_gaussian'</span></span>*, *<span class="n"><span class="pre">output_scale</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="https://docs.python.org/3/library/stdtypes.html#str" class="reference external" title="(in Python v3.13)"><span class="pre">str</span></a></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">'3'</span></span>*<span class="sig-paren">)</span> <span class="sig-return"><span class="sig-return-icon">→</span> <span class="sig-return-typehint"><a href="https://docs.python.org/3/library/pathlib.html#pathlib.Path" class="reference external" title="(in Python v3.13)"><span class="pre">Path</span></a></span></span><a href="_modules/sparc_fuse_core.html#convert_imaging_file" class="reference internal"><span class="viewcode-link"><span class="pre">[source]</span></span></a><a href="#sparc_fuse_core.convert_imaging_file" class="headerlink" title="Link to this definition"></a>  
Converts *local_path* to an OME-Zarr store and returns its Path.

- RGB images (.jpg/.png/…) are re-packed to channel-first OME-TIFF.

- ND2 is converted with nd2reader.

- LIF + a long list of bio-formats-compatible slide formats go through bfconvert.

- Plain TIFFs are sent directly to ngff-zarr.

- Everything else is attempted “as is” (ngff-zarr can open many types).

Parameters<span class="colon">:</span>  
- **local_path** (*Path*) – Path to the input imaging file.

- **output_dir** (*Path*) – Directory where the OME-Zarr store will be created.

- **ome_zarr_version** (<a href="https://docs.python.org/3/library/stdtypes.html#str" class="reference external" title="(in Python v3.13)"><em>str</em></a> *\|* *None,* *optional*) – OME-Zarr version to use. Defaults to a module-level default if None.

- **method** (<a href="https://docs.python.org/3/library/stdtypes.html#str" class="reference external" title="(in Python v3.13)"><em>str</em></a>*,* *optional*) – Downsampling method for ngff-zarr. Defaults to “dask_image_gaussian”.

- **output_scale** (<a href="https://docs.python.org/3/library/stdtypes.html#str" class="reference external" title="(in Python v3.13)"><em>str</em></a>*,* *optional*) – Output scale for ngff-zarr. Defaults to “3”.

Returns<span class="colon">:</span>  
Path to the generated OME-Zarr store.

Return type<span class="colon">:</span>  
Path

Raises<span class="colon">:</span>  
<a href="https://docs.python.org/3/library/exceptions.html#ValueError" class="reference external" title="(in Python v3.13)"><strong>ValueError</strong></a> – If an RGB image does not have the expected shape.

<!-- -->

<span class="sig-prename descclassname"><span class="pre">sparc_fuse_core.</span></span><span class="sig-name descname"><span class="pre">create_xarray_zarr_from_raw</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">bucket</span></span>*, *<span class="n"><span class="pre">raw_zarr_path</span></span>*, *<span class="n"><span class="pre">xarray_zarr_path</span></span>*, *<span class="n"><span class="pre">region</span></span><span class="o"><span class="pre">=</span></span><span class="default_value"><span class="pre">'eu-north-1'</span></span>*<span class="sig-paren">)</span><a href="_modules/sparc_fuse_core.html#create_xarray_zarr_from_raw" class="reference internal"><span class="viewcode-link"><span class="pre">[source]</span></span></a><a href="#sparc_fuse_core.create_xarray_zarr_from_raw" class="headerlink" title="Link to this definition"></a>  
Reads raw Zarr data from an S3 bucket, constructs an xarray Dataset, and writes it back to S3 in Zarr format.

Parameters<span class="colon">:</span>  
- **bucket** (<a href="https://docs.python.org/3/library/stdtypes.html#str" class="reference external" title="(in Python v3.13)"><em>str</em></a>) – Name of the S3 bucket containing the Zarr data.

- **raw_zarr_path** (<a href="https://docs.python.org/3/library/stdtypes.html#str" class="reference external" title="(in Python v3.13)"><em>str</em></a>) – Path within the S3 bucket to the raw Zarr store.

- **xarray_zarr_path** (<a href="https://docs.python.org/3/library/stdtypes.html#str" class="reference external" title="(in Python v3.13)"><em>str</em></a>) – Path within the S3 bucket where the xarray Zarr store will be saved.

- **region** (<a href="https://docs.python.org/3/library/stdtypes.html#str" class="reference external" title="(in Python v3.13)"><em>str</em></a>*,* *optional*) – AWS region name for the S3 bucket (default is “eu-north-1”).

Notes

- Assumes the raw Zarr store contains “signals” and “time” arrays.

- The resulting xarray Dataset will have dimensions (“channel”, “time”), where “channel” is inferred from the shape of “signals”.

- Requires s3fs, zarr, xarray, and numpy to be installed.

<!-- -->

<span class="sig-prename descclassname"><span class="pre">sparc_fuse_core.</span></span><span class="sig-name descname"><span class="pre">download_and_convert_sparc_data</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">dataset_id</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="https://docs.python.org/3/library/functions.html#int" class="reference external" title="(in Python v3.13)"><span class="pre">int</span></a></span>*, *<span class="n"><span class="pre">primary_paths</span></span><span class="o"><span class="pre">=</span></span><span class="default_value"><span class="pre">None</span></span>*, *<span class="o"><span class="pre">\*</span></span>*, *<span class="n"><span class="pre">output_dir</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="https://docs.python.org/3/library/stdtypes.html#str" class="reference external" title="(in Python v3.13)"><span class="pre">str</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><a href="https://docs.python.org/3/library/pathlib.html#pathlib.Path" class="reference external" title="(in Python v3.13)"><span class="pre">Path</span></a></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">'./output'</span></span>*, *<span class="n"><span class="pre">descriptors_dir</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="https://docs.python.org/3/library/stdtypes.html#str" class="reference external" title="(in Python v3.13)"><span class="pre">str</span></a><span class="w"> </span><span class="p"><span class="pre">\|</span></span><span class="w"> </span><a href="https://docs.python.org/3/library/pathlib.html#pathlib.Path" class="reference external" title="(in Python v3.13)"><span class="pre">Path</span></a></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">'./mapping_schemes'</span></span>*, *<span class="n"><span class="pre">file_format</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="https://docs.python.org/3/library/stdtypes.html#str" class="reference external" title="(in Python v3.13)"><span class="pre">str</span></a></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">'npz'</span></span>*, *<span class="n"><span class="pre">overwrite</span></span><span class="p"><span class="pre">:</span></span><span class="w"> </span><span class="n"><a href="https://docs.python.org/3/library/functions.html#bool" class="reference external" title="(in Python v3.13)"><span class="pre">bool</span></a></span><span class="w"> </span><span class="o"><span class="pre">=</span></span><span class="w"> </span><span class="default_value"><span class="pre">False</span></span>*<span class="sig-paren">)</span><a href="_modules/sparc_fuse_core.html#download_and_convert_sparc_data" class="reference internal"><span class="viewcode-link"><span class="pre">[source]</span></span></a><a href="#sparc_fuse_core.download_and_convert_sparc_data" class="headerlink" title="Link to this definition"></a>  
Download → convert → clean-up pipeline.

Imaging files are routed through convert_imaging_file; everything else goes through the descriptor-based mapper. Raw downloads are stored only in a TemporaryDirectory and are deleted as soon as conversion finishes.

Parameters<span class="colon">:</span>  
- **dataset_id** (<a href="https://docs.python.org/3/library/functions.html#int" class="reference external" title="(in Python v3.13)"><em>int</em></a>) – The unique identifier of the SPARC dataset to process.

- **primary_paths** (<a href="https://docs.python.org/3/library/stdtypes.html#list" class="reference external" title="(in Python v3.13)"><em>list</em></a>*\[*<a href="https://docs.python.org/3/library/stdtypes.html#str" class="reference external" title="(in Python v3.13)"><em>str</em></a>*\]* *\|* <a href="https://docs.python.org/3/library/stdtypes.html#str" class="reference external" title="(in Python v3.13)"><em>str</em></a> *\|* *None,* *optional*) – List of relative paths to primary files within the dataset. If None, all primary files will be fetched from the dataset metadata.

- **output_dir** (<a href="https://docs.python.org/3/library/stdtypes.html#str" class="reference external" title="(in Python v3.13)"><em>str</em></a> *\|* *Path,* *optional*) – Directory where converted files will be saved. Defaults to “./output”.

- **descriptors_dir** (<a href="https://docs.python.org/3/library/stdtypes.html#str" class="reference external" title="(in Python v3.13)"><em>str</em></a> *\|* *Path,* *optional*) – Directory containing mapping descriptors. Defaults to “./mapping_schemes”.

- **file_format** (<a href="https://docs.python.org/3/library/stdtypes.html#str" class="reference external" title="(in Python v3.13)"><em>str</em></a>*,* *optional*) – Output file format for standardized data. Defaults to “npz”.

- **overwrite** (<a href="https://docs.python.org/3/library/functions.html#bool" class="reference external" title="(in Python v3.13)"><em>bool</em></a>*,* *optional*) – If True, existing standardized files will be overwritten. Defaults to False.

Returns<span class="colon">:</span>  
A list of dictionaries containing the results of the conversion process for each file.  
Each dictionary includes:  
- rel_path: Relative path of the file within the dataset.

- local_path: Temporary local path where the file was downloaded.

- std_path: Path to the standardized output file.

- descriptor_id: ID of the mapping descriptor used (if applicable).

- mapping_score: Score of the mapping (if applicable).

- status: Status of the processing (“ok”, “pending”, “failed”, “unsupported”).

- error: Error message if processing failed.

Return type<span class="colon">:</span>  
<a href="https://docs.python.org/3/library/stdtypes.html#list" class="reference external" title="(in Python v3.13)">list</a>\[<a href="https://docs.python.org/3/library/stdtypes.html#dict" class="reference external" title="(in Python v3.13)">dict</a>\]

Raises<span class="colon">:</span>  
- <a href="https://docs.python.org/3/library/exceptions.html#ValueError" class="reference external" title="(in Python v3.13)"><strong>ValueError</strong></a> – If no primary files are found to process.

- <a href="https://docs.python.org/3/library/exceptions.html#RuntimeError" class="reference external" title="(in Python v3.13)"><strong>RuntimeError</strong></a> – If the download fails or the file cannot be processed.

- <a href="https://docs.python.org/3/library/exceptions.html#FileNotFoundError" class="reference external" title="(in Python v3.13)"><strong>FileNotFoundError</strong></a> – If no matching file is found in the dataset for the given relative path.

- <a href="https://docs.python.org/3/library/exceptions.html#Exception" class="reference external" title="(in Python v3.13)"><strong>Exception</strong></a> – For any other errors encountered during the download or conversion process.

Notes

- The function uses a temporary directory for downloading files, which is automatically cleaned up after processing.

- The output directory is created if it does not exist.

- Metadata from the SPARC dataset is fetched and included in the standardized output.

- The function supports both imaging and time series data, routing them through appropriate conversion methods.

<!-- -->

<span class="sig-prename descclassname"><span class="pre">sparc_fuse_core.</span></span><span class="sig-name descname"><span class="pre">download_and_move_sparc_file</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">rel_path</span></span>*, *<span class="n"><span class="pre">dataset_id</span></span>*, *<span class="n"><span class="pre">output_dir</span></span>*<span class="sig-paren">)</span><a href="_modules/sparc_fuse_core.html#download_and_move_sparc_file" class="reference internal"><span class="viewcode-link"><span class="pre">[source]</span></span></a><a href="#sparc_fuse_core.download_and_move_sparc_file" class="headerlink" title="Link to this definition"></a>  
Downloads a file from a SPARC dataset using the provided relative path and dataset ID, then moves the downloaded file to the specified output directory.

The function ensures the relative path starts with ‘primary/’, constructs the appropriate query path for the SPARC API, and handles file download and movement. If the file is not found or an error occurs during download or movement, an error message is printed.

Parameters<span class="colon">:</span>  
- **rel_path** (<a href="https://docs.python.org/3/library/stdtypes.html#str" class="reference external" title="(in Python v3.13)"><em>str</em></a>) – The relative path to the file within the SPARC dataset.

- **dataset_id** (<a href="https://docs.python.org/3/library/stdtypes.html#str" class="reference external" title="(in Python v3.13)"><em>str</em></a>) – The identifier of the SPARC dataset to download from.

- **output_dir** (<a href="https://docs.python.org/3/library/stdtypes.html#str" class="reference external" title="(in Python v3.13)"><em>str</em></a>) – The directory where the downloaded file should be moved.

Raises<span class="colon">:</span>  
- <a href="https://docs.python.org/3/library/exceptions.html#FileNotFoundError" class="reference external" title="(in Python v3.13)"><strong>FileNotFoundError</strong></a> – If no matching file is found in the SPARC dataset.

- <a href="https://docs.python.org/3/library/exceptions.html#Exception" class="reference external" title="(in Python v3.13)"><strong>Exception</strong></a> – For any other errors encountered during download or file movement.

<!-- -->

<span class="sig-prename descclassname"><span class="pre">sparc_fuse_core.</span></span><span class="sig-name descname"><span class="pre">fetch_dataset_metadata</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">dataset_id</span></span>*<span class="sig-paren">)</span><a href="_modules/sparc_fuse_core.html#fetch_dataset_metadata" class="reference internal"><span class="viewcode-link"><span class="pre">[source]</span></span></a><a href="#sparc_fuse_core.fetch_dataset_metadata" class="headerlink" title="Link to this definition"></a>  
Fetches metadata for a specified dataset from the Pennsieve Discover API.

Parameters<span class="colon">:</span>  
**dataset_id** (<a href="https://docs.python.org/3/library/stdtypes.html#str" class="reference external" title="(in Python v3.13)"><em>str</em></a> *or* <a href="https://docs.python.org/3/library/functions.html#int" class="reference external" title="(in Python v3.13)"><em>int</em></a>) – The unique identifier of the dataset to fetch metadata for.

Returns<span class="colon">:</span>  
The metadata of the specified dataset as returned by the API.

Return type<span class="colon">:</span>  
<a href="https://docs.python.org/3/library/stdtypes.html#dict" class="reference external" title="(in Python v3.13)">dict</a>

Raises<span class="colon">:</span>  
**requests.HTTPError** – If the HTTP request to the API fails.

<!-- -->

<span class="sig-prename descclassname"><span class="pre">sparc_fuse_core.</span></span><span class="sig-name descname"><span class="pre">generate_and_upload_manifest</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">dataset_id</span></span>*, *<span class="n"><span class="pre">bucket</span></span>*, *<span class="n"><span class="pre">xarray_zarr_path</span></span>*, *<span class="n"><span class="pre">region</span></span><span class="o"><span class="pre">=</span></span><span class="default_value"><span class="pre">'eu-north-1'</span></span>*<span class="sig-paren">)</span><a href="_modules/sparc_fuse_core.html#generate_and_upload_manifest" class="reference internal"><span class="viewcode-link"><span class="pre">[source]</span></span></a><a href="#sparc_fuse_core.generate_and_upload_manifest" class="headerlink" title="Link to this definition"></a>  
Generates a manifest JSON file for a given dataset and uploads it to an S3 bucket.

Parameters<span class="colon">:</span>  
- **dataset_id** (<a href="https://docs.python.org/3/library/stdtypes.html#str" class="reference external" title="(in Python v3.13)"><em>str</em></a>) – The unique identifier for the dataset.

- **bucket** (<a href="https://docs.python.org/3/library/stdtypes.html#str" class="reference external" title="(in Python v3.13)"><em>str</em></a>) – The name of the S3 bucket where the manifest will be uploaded.

- **xarray_zarr_path** (<a href="https://docs.python.org/3/library/stdtypes.html#str" class="reference external" title="(in Python v3.13)"><em>str</em></a>) – The path to the Zarr dataset within the S3 bucket.

- **region** (<a href="https://docs.python.org/3/library/stdtypes.html#str" class="reference external" title="(in Python v3.13)"><em>str</em></a>*,* *optional*) – The AWS region where the S3 bucket is located. Defaults to “eu-north-1”.

Raises<span class="colon">:</span>  
<a href="https://docs.python.org/3/library/subprocess.html#subprocess.CalledProcessError" class="reference external" title="(in Python v3.13)"><strong>subprocess.CalledProcessError</strong></a> – If the AWS CLI command fails during upload.

The manifest contains metadata about the dataset, including its ID, Zarr path, generation timestamp, and file format.

<!-- -->

<span class="sig-prename descclassname"><span class="pre">sparc_fuse_core.</span></span><span class="sig-name descname"><span class="pre">get_sparc_datasets_by_id</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">ids</span></span>*<span class="sig-paren">)</span><a href="_modules/sparc_fuse_core.html#get_sparc_datasets_by_id" class="reference internal"><span class="viewcode-link"><span class="pre">[source]</span></span></a><a href="#sparc_fuse_core.get_sparc_datasets_by_id" class="headerlink" title="Link to this definition"></a>  
Retrieve SPARC datasets from the metadata client by their IDs and group them by type.

Parameters<span class="colon">:</span>  
**ids** (<a href="https://docs.python.org/3/library/functions.html#int" class="reference external" title="(in Python v3.13)"><em>int</em></a>*,* <a href="https://docs.python.org/3/library/stdtypes.html#list" class="reference external" title="(in Python v3.13)"><em>list</em></a>*,* <a href="https://docs.python.org/3/library/stdtypes.html#tuple" class="reference external" title="(in Python v3.13)"><em>tuple</em></a>*, or* <a href="https://docs.python.org/3/library/stdtypes.html#set" class="reference external" title="(in Python v3.13)"><em>set</em></a>) – A single dataset ID or a collection of dataset IDs to query.

Returns<span class="colon">:</span>  
A dictionary mapping dataset type names to lists of dataset IDs that belong to each type.

Return type<span class="colon">:</span>  
<a href="https://docs.python.org/3/library/stdtypes.html#dict" class="reference external" title="(in Python v3.13)">dict</a>

Raises<span class="colon">:</span>  
<a href="https://docs.python.org/3/library/exceptions.html#TypeError" class="reference external" title="(in Python v3.13)"><strong>TypeError</strong></a> – If the input is not an int, list, tuple, or set.

Notes

- The function prints the constructed query and the response for debugging purposes.

- If a dataset does not have a valid type, it is grouped under the key “\<invalid type\>”.

- If a dataset does not have an ID, it is represented as “\<no id\>” in the result.

<!-- -->

<span class="sig-prename descclassname"><span class="pre">sparc_fuse_core.</span></span><span class="sig-name descname"><span class="pre">list_primary_files</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">dataset_id</span></span>*<span class="sig-paren">)</span><a href="_modules/sparc_fuse_core.html#list_primary_files" class="reference internal"><span class="viewcode-link"><span class="pre">[source]</span></span></a><a href="#sparc_fuse_core.list_primary_files" class="headerlink" title="Link to this definition"></a>  
Retrieve primary files from a dataset’s metadata.

Parameters<span class="colon">:</span>  
**dataset_id** – The unique identifier of the dataset.

Raises<span class="colon">:</span>  
**Any exceptions raised by fetch_dataset_metadata.** –

<!-- -->

<span class="sig-prename descclassname"><span class="pre">sparc_fuse_core.</span></span><span class="sig-name descname"><span class="pre">list_sparc_datasets</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">max_id</span></span><span class="o"><span class="pre">=</span></span><span class="default_value"><span class="pre">1000</span></span>*<span class="sig-paren">)</span><a href="_modules/sparc_fuse_core.html#list_sparc_datasets" class="reference internal"><span class="viewcode-link"><span class="pre">[source]</span></span></a><a href="#sparc_fuse_core.list_sparc_datasets" class="headerlink" title="Link to this definition"></a>  
Retrieves and categorizes SPARC datasets by their type.

This function queries the metadata client for datasets with IDs in the range 0 to max_id (inclusive), then counts and groups the datasets by their type name. It prints the response and a summary of dataset type counts.

Parameters<span class="colon">:</span>  
**max_id** (<a href="https://docs.python.org/3/library/functions.html#int" class="reference external" title="(in Python v3.13)"><em>int</em></a>*,* *optional*) – The maximum dataset ID to include in the query. Defaults to 1000.

Returns<span class="colon">:</span>  
A mapping from dataset type names to lists of dataset IDs belonging to each type.

Return type<span class="colon">:</span>  
<a href="https://docs.python.org/3/library/stdtypes.html#dict" class="reference external" title="(in Python v3.13)">dict</a>

<!-- -->

<span class="sig-prename descclassname"><span class="pre">sparc_fuse_core.</span></span><span class="sig-name descname"><span class="pre">open_zarr_from_s3</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">bucket</span></span>*, *<span class="n"><span class="pre">zarr_path</span></span>*, *<span class="n"><span class="pre">region</span></span><span class="o"><span class="pre">=</span></span><span class="default_value"><span class="pre">'eu-north-1'</span></span>*<span class="sig-paren">)</span><a href="_modules/sparc_fuse_core.html#open_zarr_from_s3" class="reference internal"><span class="viewcode-link"><span class="pre">[source]</span></span></a><a href="#sparc_fuse_core.open_zarr_from_s3" class="headerlink" title="Link to this definition"></a>  
Lazily open a Zarr dataset stored in an S3 bucket using Xarray.

Parameters<span class="colon">:</span>  
- **bucket** (<a href="https://docs.python.org/3/library/stdtypes.html#str" class="reference external" title="(in Python v3.13)"><em>str</em></a>) – Name of the S3 bucket containing the Zarr dataset.

- **zarr_path** (<a href="https://docs.python.org/3/library/stdtypes.html#str" class="reference external" title="(in Python v3.13)"><em>str</em></a>) – Path to the Zarr dataset within the S3 bucket.

- **region** (<a href="https://docs.python.org/3/library/stdtypes.html#str" class="reference external" title="(in Python v3.13)"><em>str</em></a>*,* *optional*) – AWS region where the S3 bucket is located. Defaults to “eu-north-1”.

Returns<span class="colon">:</span>  
The opened Zarr dataset as an Xarray Dataset object.

Return type<span class="colon">:</span>  
xarray.Dataset

Notes

- Requires appropriate AWS credentials to access the S3 bucket.

- The function sets the AWS_DEFAULT_REGION environment variable if not already set.

- The Zarr dataset must be consolidated.

<!-- -->

<span class="sig-prename descclassname"><span class="pre">sparc_fuse_core.</span></span><span class="sig-name descname"><span class="pre">print_project_metadata</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">metadata</span></span>*<span class="sig-paren">)</span><a href="_modules/sparc_fuse_core.html#print_project_metadata" class="reference internal"><span class="viewcode-link"><span class="pre">[source]</span></span></a><a href="#sparc_fuse_core.print_project_metadata" class="headerlink" title="Link to this definition"></a>  
Prints the ‘item’ field from the provided metadata dictionary in a formatted JSON structure.

Parameters<span class="colon">:</span>  
**metadata** (<a href="https://docs.python.org/3/library/stdtypes.html#dict" class="reference external" title="(in Python v3.13)"><em>dict</em></a>) – A dictionary containing project metadata. Expected to have an ‘item’ key.

Returns<span class="colon">:</span>  
None

<!-- -->

<span class="sig-prename descclassname"><span class="pre">sparc_fuse_core.</span></span><span class="sig-name descname"><span class="pre">upload_to_s3</span></span><span class="sig-paren">(</span>*<span class="n"><span class="pre">local_path</span></span>*, *<span class="n"><span class="pre">bucket</span></span>*, *<span class="n"><span class="pre">remote_path</span></span>*, *<span class="n"><span class="pre">region</span></span><span class="o"><span class="pre">=</span></span><span class="default_value"><span class="pre">'eu-north-1'</span></span>*<span class="sig-paren">)</span><a href="_modules/sparc_fuse_core.html#upload_to_s3" class="reference internal"><span class="viewcode-link"><span class="pre">[source]</span></span></a><a href="#sparc_fuse_core.upload_to_s3" class="headerlink" title="Link to this definition"></a>  
Uploads files from a local directory to an AWS S3 bucket using the AWS CLI.

Parameters<span class="colon">:</span>  
- **local_path** (<a href="https://docs.python.org/3/library/stdtypes.html#str" class="reference external" title="(in Python v3.13)"><em>str</em></a>) – The local directory path to upload.

- **bucket** (<a href="https://docs.python.org/3/library/stdtypes.html#str" class="reference external" title="(in Python v3.13)"><em>str</em></a>) – The name of the target S3 bucket.

- **remote_path** (<a href="https://docs.python.org/3/library/stdtypes.html#str" class="reference external" title="(in Python v3.13)"><em>str</em></a>) – The destination path within the S3 bucket.

- **region** (<a href="https://docs.python.org/3/library/stdtypes.html#str" class="reference external" title="(in Python v3.13)"><em>str</em></a>*,* *optional*) – The AWS region where the bucket is located. Defaults to “eu-north-1”.

Raises<span class="colon">:</span>  
<a href="https://docs.python.org/3/library/subprocess.html#subprocess.CalledProcessError" class="reference external" title="(in Python v3.13)"><strong>subprocess.CalledProcessError</strong></a> – If the AWS CLI command fails.

</div>

</div>

</div>
