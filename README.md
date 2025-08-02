# SPARC FUSE
This is the official repository of Team-B of the 2025 NIH SPARC FAIR Codeathon. 
<img src="./assets/logo.png" width="1000"/>

## 🚀 Quick start

### Command-line interface

```bash
# Clone and install
git clone https://github.com/SPARC-FAIR-Codeathon/2025-team-B.git
cd 2025-team-B/sparcfuse
pip install -e .
cd ..
```

```bash
# Convert a file
sparc-fuse 224 primary/sub-ChAT-Male-Subject-1/20_1021.acq --output-dir ./converted
```

```bash
# View options
sparc-fuse --help
```
<img src="./assets/help_view.png" width="1000"/>

---

### Use as a Python library

#### Try it out on oSPARC
<a href="https://osparc.io/#/study/06fbaa3a-6fbc-11f0-bae3-0242ac179953" target="_blank"><img src="./assets/osparc-logo.png" width="200"></a>

#### 0 – Clone the project
```python
git clone https://github.com/SPARC-FAIR-Codeathon/2025-team-B.git
cd 2025-team-B
```

#### 1 – Convert a single primary file

```python
from sparc_fuse_core import download_and_convert_sparc_data, list_primary_files

DATASET_ID = 224  # Any valid SPARC dataset ID

files, _ = list_primary_files(DATASET_ID)
print("primary files:", [f["path"] for f in files])

download_and_convert_sparc_data(
    DATASET_ID,
    primary_paths=files[0]["path"].replace("files/", ""),
    output_dir="./output_single",
    file_format="zarr"          # or "zarr.zip"
)
```
<img src="./assets/single_file_conversion.png" width="1000"/>

#### 2 – Bulk-convert an entire dataset

```python
bulk_report = download_and_convert_sparc_data(
    DATASET_ID,
    output_dir="./output_bulk",
    file_format="zarr"          # zarr directories; use "npz", "zarr.zip", etc. if preferred
)

from pprint import pprint
pprint(bulk_report)
```
<img src="./assets/full_database_conversion.png" width="1000"/>

#### 3 – Convert a subset of primary files

```python
# Grab (for example) the first three primary files
files, _ = list_primary_files(DATASET_ID)
subset_paths = [f["path"].replace("files/", "") for f in files[:3]]

report = download_and_convert_sparc_data(
    DATASET_ID,
    primary_paths=subset_paths,   # any iterable works
    output_dir="./output_subset",
    file_format="npz",            # or "zarr", "zarr.zip", ...
    overwrite=True                # regenerate if outputs already exist
)

from pprint import pprint
pprint(report)
```
<img src="./assets/multi_file_conversion.png" width="1000"/>

> **Tip:** `file_format` accepts `"zarr"`, `"zarr.zip"`, `"npz"`, or `"mat"`. Choose the one that best matches your downstream workflow.

## ❓ Why SPARC FUSE?

### The headache  
* SPARC hosts **80 + heterogeneous file formats** and countless sub-variants – each with its own quirks.  
* Researchers lose precious hours hunting converters and writing glue code instead of analysing data.  
* This format jungle breaks reproducibility and puts FAIR principles at risk.
  
<p align="center">
  <img src="./assets/file_extensions_wordcloud.png" width="500"
       alt="Word cloud of ≈ 80 SPARC file extensions"><br/>
  <sub><em><strong>Figure&nbsp;1.</strong> A pletora of file formats.</em> Relative frequency of every extension found in public SPARC datasets (log-scaled word cloud).</sub>
</p>

<p align="center">
  <img src="./assets/combined_2x2_summary.png" width="800"
       alt="Bar-chart dashboard: file counts by modality and top extensions"><br/>
<sub><em><strong>Figure&nbsp;2.</strong> Diversity over volume.</em>The SPARC database contains <strong>20 + distinct time-series formats</strong> and <strong>20 + imaging formats</strong>, each hiding additional proprietary structures inside the files.</sub></p>

### The cure  
* **SPARC FUSE** automatically remaps *any* supported file (time-series & imaging) into a **uniform, chunked Zarr store**<br>
  – optionally also `.mat`, `.npz`, or zipped Zarr for legacy tools.
  
<p align="center">
  <img src="./assets/sparc_fuse_overview.png" width="800"
       alt="Many formats in – one clean Zarr/MAT/NPZ out">
</p>

* Works three ways:  
  1. **Python API** – bulk-convert or cherry-pick files in a single call.  
  2. **CLI** – one-liner on the command line.  
  3. **Browser button** *(WIP)* – “Convert & Download” directly from the SPARC portal.  
* Keeps full provenance: every conversion is logged, making pipelines **fully reproducible**.

### Why it matters  
* **Hours → seconds:** spend time on science, not format wrangling.  
* **Interoperability out-of-the-box:** unified layout means the same loader works for every dataset.  
* **Cloud-ready chunks:** Zarr’s design unlocks scalable, parallel analysis on HPC or S3-style storage.  
* **FAIR boost:** data become immediately *Accessible*, *Interoperable* and *Reusable* across toolchains.

---
## 🌩️ Zarr + AWS: super-charging SPARC data

 <p align="center">
  <img src="./assets/aws_and_zarr.png" width="300" alt="AWS and zarr"><br/>
 </p>

> **TL;DR** — Zarr is a cloud-native chunked-array format that lets you *stream* only the bytes you need.  
> SPARC datasets are now mirrored on **Amazon S3 via the AWS Registry of Open Data**, so Zarr fits like a glove.

| Why Zarr? | Why now? |
|-----------|----------|
| *“Zarr is like Parquet for arrays.”* It stores N-D data in tiny, independent chunks—perfect for parallel reads/writes and lazy loading. | SPARC just announced that **all public datasets are directly accessible on AWS S3** (Requester Pays) and even have a listing on the AWS Open Data Registry.|
| Plays nicely with `xarray`, Dask, PyTorch, TensorFlow, MATLAB (via `zarr-matlab`), and more. | With data already in S3, a converted Zarr store can be queried **in-place** from an EC2, Lambda, or SageMaker job—no re-download cycles. |
| Open spec, community-driven, language-agnostic. | SPARC FUSE’s one-line `sparc-fuse <id> … --file-format zarr` command gives you an **analysis-ready** cloud-optimised dataset in seconds. |

### What is Zarr?

<p align="center">
  <img src="./assets/zarr_overview.png" width="500"
       alt="Schematic of Zarr: JSON metadata plus many tiny chunk files"><br/>
<sub><em><strong>Figure&nbsp;3.</strong> Zarr Overview.</em> Diagram adapted from the Earthmover blog post <a href="https://earthmover.io/blog/what-is-zarr">“What is Zarr?”</a>.</sub>
</p>

* **Chunked storage** – data are broken into independently readable/writable tiles.  
* **Cloud-optimised layout** – each chunk is just an object in S3 / GCS, so you stream only the bytes you need.  
* **Parallel-ready** – Dask, Ray, Spark, etc. slurp different chunks concurrently for massive speed-ups.  
* **Open spec** – language-agnostic, community-governed, and already adopted by NASA, OME-Zarr, Pangeo, and more.

## Supported File Formats
![.mat Time-series](https://img.shields.io/badge/.mat-Time%20series-orange)
![.smr Time-series](https://img.shields.io/badge/.smr-Time%20series-orange)
![.csv Time-series](https://img.shields.io/badge/.csv-Time%20series-orange)
![.adicht Time-series](https://img.shields.io/badge/.adicht-Time%20series-orange)
![.hdf5 Time-series](https://img.shields.io/badge/.hdf5-Time%20series-orange)
![.h5 Time-series](https://img.shields.io/badge/.h5-Time%20series-orange)
![.ets Time-series](https://img.shields.io/badge/.ets-Time%20series-orange)
![.abf Time-series](https://img.shields.io/badge/.abf-Time%20series-orange)
![.rhd Time-series](https://img.shields.io/badge/.rhd-Time%20series-orange)
![.nev Time-series](https://img.shields.io/badge/.nev-Time%20series-orange)
![.ns5 Time-series](https://img.shields.io/badge/.ns5-Time%20series-orange)
![.ns2 Time-series](https://img.shields.io/badge/.ns2-Time%20series-orange)
![.ns1 Time-series](https://img.shields.io/badge/.ns1-Time%20series-orange)
![.smrx Time-series](https://img.shields.io/badge/.smrx-Time%20series-orange)
![.wav Time-series](https://img.shields.io/badge/.wav-Time%20series-orange)
![.acq Time-series](https://img.shields.io/badge/.acq-Time%20series-orange)
![.tbk Time-series](https://img.shields.io/badge/.tbk-Time%20series-orange)
![.tdx Time-series](https://img.shields.io/badge/.tdx-Time%20series-orange)
![.tev Time-series](https://img.shields.io/badge/.tev-Time%20series-orange)
![.tin Time-series](https://img.shields.io/badge/.tin-Time%20series-orange)
![.tnt Time-series](https://img.shields.io/badge/.tnt-Time%20series-orange)
![.tsq Time-series](https://img.shields.io/badge/.tsq-Time%20series-orange)
![.eeg Time-series](https://img.shields.io/badge/.eeg-Time%20series-orange)
![.vmrk Time-series](https://img.shields.io/badge/.vmrk-Time%20series-orange)
![.vhdr Time-series](https://img.shields.io/badge/.vhdr-Time%20series-orange)
![.sev Time-series](https://img.shields.io/badge/.sev-Time%20series-orange)
![.sam Time-series](https://img.shields.io/badge/.sam-Time%20series-orange)
![.pss Time-series](https://img.shields.io/badge/.pss-Time%20series-orange)
![.psmethod Time-series](https://img.shields.io/badge/.psmethod-Time%20series-orange)
![.tif Imaging](https://img.shields.io/badge/.tif-Imaging-blueviolet)
![.tiff Imaging](https://img.shields.io/badge/.tiff-Imaging-blueviolet)
![.czi Imaging](https://img.shields.io/badge/.czi-Imaging-blueviolet)
![.nd2 Imaging](https://img.shields.io/badge/.nd2-Imaging-blueviolet)
![.lsm Imaging](https://img.shields.io/badge/.lsm-Imaging-blueviolet)
![.jpx Imaging](https://img.shields.io/badge/.jpx-Imaging-blueviolet)
![.svs Imaging](https://img.shields.io/badge/.svs-Imaging-blueviolet)
![.ims Imaging](https://img.shields.io/badge/.ims-Imaging-blueviolet)
![.png Imaging](https://img.shields.io/badge/.png-Imaging-blueviolet)
![.jpg Imaging](https://img.shields.io/badge/.jpg-Imaging-blueviolet)
![.jpeg Imaging](https://img.shields.io/badge/.jpeg-Imaging-blueviolet)
![.bmp Imaging](https://img.shields.io/badge/.bmp-Imaging-blueviolet)
![.vsi Imaging](https://img.shields.io/badge/.vsi-Imaging-blueviolet)
![.jp2 Imaging](https://img.shields.io/badge/.jp2-Imaging-blueviolet)
![.roi Imaging](https://img.shields.io/badge/.roi-Imaging-blueviolet)
![.dm3 Imaging](https://img.shields.io/badge/.dm3-Imaging-blueviolet)
![.pxp Imaging](https://img.shields.io/badge/.pxp-Imaging-blueviolet)
![.ipf Imaging](https://img.shields.io/badge/.ipf-Imaging-blueviolet)
![.lif Imaging](https://img.shields.io/badge/.lif-Imaging-blueviolet)
![.ima Imaging](https://img.shields.io/badge/.ima-Imaging-blueviolet)
![.mrxs Imaging](https://img.shields.io/badge/.mrxs-Imaging-blueviolet)
![.obj Imaging](https://img.shields.io/badge/.obj-Imaging-blueviolet)
![.avi Imaging](https://img.shields.io/badge/.avi-Imaging-blueviolet)
![.exf Imaging](https://img.shields.io/badge/.exf-Imaging-blueviolet)
![.cxd Imaging](https://img.shields.io/badge/.cxd-Imaging-blueviolet)
### Time-series formats


| Extension  | Description |
|------------|-------------|
| `.mat`     | MathWorks MATLAB file |
| `.smr`     | CED Spike2 binary recording |
| `.csv`     | Comma-separated values text (generic) |
| `.adicht`  | ADInstruments LabChart binary trace |
| `.hdf5`    | Hierarchical Data Format v5 container |
| `.h5`      | Same as `.hdf5` |
| `.ets`     | TDT electrophysiology time-series block |
| `.abf`     | Molecular Devices Axon Binary File (pClamp) |
| `.rhd`     | Intan RHD2000 amplifier data |
| `.nev`     | Blackrock NeuroPort event file |
| `.ns5`     | Blackrock continuous 30 kHz signal |
| `.ns2`     | Blackrock 1 kHz LFP signal |
| `.ns1`     | Blackrock low-rate summary signal |
| `.smrx`    | CED Spike2 v9+ extended recording |
| `.wav`     | Waveform audio (PCM) |
| `.acq`     | AxoScope raw acquisition |
| `.tbk`     | TDT DataTank “block” metadata |
| `.tdx`     | TDT DataTank index (time-stamp) |
| `.tev`     | TDT event / continuous data stream |
| `.tin`     | TDT Synapse experiment info (zip) |
| `.tnt`     | TDT block annotations |
| `.tsq`     | TDT global time-stamp table |
| `.eeg`     | BrainVision binary signal data |
| `.vmrk`    | BrainVision marker/events |
| `.vhdr`    | BrainVision header |
| `.sev`     | TDT RS4 single-channel stream |
| `.sam`     | Sequence Alignment/Map (SAM) or NREL SAM simulation file |
| `.pss`     | PicoScope oscilloscope settings snapshot |
| `.psmethod`| PalmSens electrochemistry method definition |

---

### Imaging formats

| Extension | Description |
|-----------|-------------|
| `.tif`    | Tagged Image File Format (high-bit-depth microscopy) |
| `.tiff`   | Same as `.tif` |
| `.czi`    | Carl Zeiss ZEN container |
| `.nd2`    | Nikon NIS-Elements microscope image |
| `.lsm`    | Zeiss laser-scanning-microscope stack |
| `.jpx`    | JPEG-2000 (JPX) image |
| `.svs`    | Aperio/Leica whole-slide image |
| `.ims`    | Bitplane Imaris 3-D/4-D scene |
| `.png`    | Portable Network Graphics (lossless) |
| `.jpg`    | JPEG compressed image |
| `.jpeg`   | Same as `.jpg` |
| `.bmp`    | Windows bitmap |
| `.vsi`    | Olympus virtual-slide “wrapper” file |
| `.ets`    | Olympus VS series full-resolution tile set |
| `.jp2`    | JPEG-2000 codestream |
| `.roi`    | ImageJ/Fiji region-of-interest set |
| `.dm3`    | Gatan DigitalMicrograph EM image |
| `.pxp`    | Igor Pro packed experiment (can embed images) |
| `.ipf`    | Igor Pro procedure/data file |
| `.lif`    | Leica Image File (LAS X) |
| `.ima`    | Amira/Avizo volumetric raw image |
| `.mrxs`   | 3DHISTECH Mirax whole-slide image |
| `.obj`    | Wavefront 3-D mesh |
| `.avi`    | Uncompressed/codec AVI video (time-lapse stacks) |
| `.exf`    | Zeiss experiment file (ZEN) |
| `.cxd`    | Olympus cellSens dataset |

