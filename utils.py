# ── standard library ────────────────────────────────────────────────────
from __future__ import annotations 
import glob
import importlib
import importlib.util
import json
import os
import textwrap
from datetime import datetime
from pathlib import Path

# ── third-party ─────────────────────────────────────────────────────────
import matplotlib.pyplot as plt
import numpy as np
import zarr
from zarr import DirectoryStore, ZipStore
from scipy.io import savemat


def load_file_with_descriptor(descriptor, filepath):
    """
    Loads a file using a parser specified by a descriptor.

    The descriptor defines how to import and use a parser, which can be either a class or a function,
    to process the given file. The parser's module, class/function name, initialization arguments,
    and method/function to call are all specified in the descriptor.

    Args:
        descriptor (dict): A dictionary specifying the parser configuration. It must contain a 'parser' key,
            which itself is a dictionary with the following possible keys:
                - 'module' (str): The module to import.
                - 'class' (str, optional): The class name to instantiate (if using a class-based parser).
                - 'init_args' (dict, optional): Arguments to pass to the class constructor. Use '<filepath>' as a placeholder for the file path.
                - 'load_method' (str, optional): The method to call on the class instance to load the file.
                - 'function' (str, optional): The function name to call (if using a function-based parser).
                - 'args' (list, optional): Positional arguments for the function. Use '<filepath>' as a placeholder for the file path.
                - 'kwargs' (dict, optional): Keyword arguments for the function.
                - 'output_var' (str): The key name to use for the output in the returned dictionary.
        filepath (str): The path to the file to be loaded.

    Returns:
        dict: A dictionary containing:
            - The output of the parser, keyed by 'output_var' from the descriptor.
            - The original 'filepath'.

    Raises:
        ValueError: If neither 'class' nor 'function' is specified in the descriptor.
    """
    mod = importlib.import_module(descriptor['parser']['module'])

    if 'class' in descriptor['parser']:
        cls = getattr(mod, descriptor['parser']['class'])
        init_args = {
            k: (filepath if v == '<filepath>' else v)
            for k, v in descriptor['parser']['init_args'].items()
        }
        obj = cls(**init_args)
        load_method = getattr(obj, descriptor['parser']['load_method'])
        output = load_method()
    elif 'function' in descriptor['parser']:
        func = getattr(mod, descriptor['parser']['function'])
        args = [
            filepath if arg == '<filepath>' else arg
            for arg in descriptor['parser'].get('args', [])
        ]
        kwargs = {
            k: v for k, v in descriptor['parser'].get('kwargs', {}).items()
        }
        output = func(*args, **kwargs)
    else:
        raise ValueError("Descriptor must specify either 'class' or 'function'.")

    return {descriptor['parser']['output_var']: output, 'filepath': filepath}

def evaluate_mapping_fields(descriptor, context):
    """
    Evaluates mapping expressions defined in a descriptor using the provided context.

    This function processes the 'mapping' field of the descriptor, evaluating each expression
    (as a string) in the context of the given variables. It supports special handling for
    'metadata' (dict of expressions) and 'annotations' (list of dicts of expressions).
    For other keys, the expression is evaluated directly.

    If the 'time' field is not present or evaluates to None, but 'signals' is available,
    a default time array is generated based on the shape of 'signals'. The function also
    tracks whether the 'time' field was auto-generated in the 'metadata'.

    Args:
        descriptor (dict): A dictionary containing a 'mapping' key, which maps field names
            to expressions (as strings), or for 'metadata' and 'annotations', to dicts/lists
            of expressions.
        context (dict): A dictionary representing the context in which to evaluate the expressions.

    Returns:
        dict: A dictionary containing the evaluated results for each mapping field, including
            'metadata' and 'annotations' if present. If 'time' was auto-generated, this is
            indicated in the 'metadata' under 'time_auto_generated'.
    """
    results = {}
    for key, expr in descriptor['mapping'].items():
        if key == 'metadata' or key == 'annotations':
            results[key] = {}
            if isinstance(expr, dict):  # metadata
                for mkey, mexpr in expr.items():
                    try:
                        cleaned_expr = textwrap.dedent(mexpr).strip()
                        results[key][mkey] = eval(cleaned_expr, {}, context)
                    except Exception:
                        results[key][mkey] = None
            elif isinstance(expr, list):  # annotations
                results[key] = []
                for annot in expr:
                    try:
                        results[key].append({
                            field: eval(textwrap.dedent(val).strip(), {}, context)
                            for field, val in annot.items()
                        })
                    except Exception:
                        continue
        else:
            try:
                cleaned_expr = textwrap.dedent(expr).strip()
                results[key] = eval(cleaned_expr, {}, context)
            except Exception:
                results[key] = None

    # Fallback: if time is None, generate from signal shape
    if results.get("time") is None and results.get("signals") is not None:
        n_samples = results["signals"].shape[1]
        results["time"] = np.arange(n_samples)
        results.setdefault("metadata", {})["time_auto_generated"] = True
    else:
        results.setdefault("metadata", {})["time_auto_generated"] = False

    return results

def score_mapping_result(result, descriptor):
    """
    Calculates a score based on the presence of required fields in the result.

    Args:
        result (dict): The dictionary containing the fields to be checked.
        descriptor (dict): A dictionary that may contain a 'validation' key with a 'required_fields' list.

    Returns:
        int: The number of required fields present (not None) in the result.
    """
    required = descriptor.get('validation', {}).get('required_fields', [])
    score = 0
    for field in required:
        value = result.get(field)
        if value is not None:
            score += 1
    return score


def match_best_mapping(descriptors, filepath, sparc_id=None):
    """
    Attempts to find and apply the best mapping descriptor for a given file.

    The function selects candidate descriptors based on the provided SPARC ID or the file extension.
    It then applies each candidate's parser to the file, optionally using a postprocess function if defined.
    Each mapping result is scored, and the best-scoring result and its descriptor are returned.

    Args:
        descriptors (list): A list of descriptor dictionaries, each describing how to parse and map a file.
        filepath (str): The path to the file to be mapped.
        sparc_id (str, optional): An optional SPARC ID to prioritize matching descriptors.

    Returns:
        dict: A dictionary containing:
            - 'descriptor': The best-matching descriptor dictionary.
            - 'result': The result of applying the mapping.
            - 'score': The score of the best mapping result.
    """
    file_ext = os.path.splitext(filepath)[1].lower()

    # Prefer descriptors explicitly matching SPARC ID
    if sparc_id is not None:
        candidates = [d for d in descriptors if d.get('sparc_id') == sparc_id]
    else:
        candidates = [d for d in descriptors if d.get('format', '').lower() == file_ext]

    if not candidates:
        print(f"[WARN] No descriptor matched sparc_id={sparc_id} or file extension '{file_ext}', trying all...")
        candidates = descriptors  # fallback to all

    best_score = -1
    best_result = None
    best_descriptor = None

    for desc in candidates:
        try:
            context = load_file_with_descriptor(desc, filepath)

            # If postprocess function is defined, use it instead of eval
            postprocess_fn = desc['parser'].get("postprocess", None)
            if callable(postprocess_fn):
                result = postprocess_fn(context[desc["parser"]["output_var"]], context.get("filepath"))
            else:
                result = evaluate_mapping_fields(desc, context)
            score = score_mapping_result(result, desc)
            if score > best_score:
                best_score = score
                best_result = result
                best_descriptor = desc
        except Exception as e:
            print(f"[WARN] Mapping {desc['id']} failed: {e}")
            continue

    return {
        'descriptor': best_descriptor,
        'result': best_result,
        'score': best_score
    }

def load_all_descriptors(directory="./mapping_schemes"):
    """
    Loads all Python modules from the specified directory, extracts their 'descriptor' attribute if present, and returns a list of these descriptors.

    Args:
        directory (str): The path to the directory containing Python files to load. Defaults to "./mapping_schemes".

    Returns:
        list: A list of 'descriptor' objects found in the loaded modules.

    Notes:
        - Only files ending with '.py' are considered.
        - If a module does not have a 'descriptor' attribute or fails to load, a warning is printed and the module is skipped.
        - Prints the number of successfully loaded descriptors.
    """
    descriptors = []

    py_files = glob.glob(os.path.join(directory, "*.py"))

    for file in py_files:
        try:
            module_name = os.path.splitext(os.path.basename(file))[0]
            spec = importlib.util.spec_from_file_location(module_name, file)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            if hasattr(mod, "descriptor"):
                descriptors.append(mod.descriptor)
        except Exception as e:
            print(f"[WARN] Failed to load descriptor from {file}: {e}")

    print(f"[INFO] Loaded {len(descriptors)} descriptor(s) from {directory}")
    return descriptors


# -------------------------------------------------------------------------
# save_standardized_output
# -------------------------------------------------------------------------
def save_standardized_output(
    output_path,
    result_dict,
    descriptor,
    *,
    original_filename: str = "unknown_file",
    annotations=None,
    metadata_overrides=None,
    file_format: str = "npz",          # "npz" | "zarr" | "zarr.zip"
    zarr_chunks=None,                  # e.g. (n_channels, 1024)
    zarr_compressor=None,              # e.g. zarr.Blosc(...)
):
    """
    Save *result_dict* (time, signals, annotations) in a standardized container.

    Supported containers
    --------------------
    • "npz"       → <output_path>.npz
    • "zarr"      → <output_path>.zarr/…
    • "zarr.zip"  → <output_path>.zarr.zip   (single-file store)
    """
    now = datetime.now().strftime("%Y-%m-%d")

    time        = result_dict.get("time")
    signals     = result_dict.get("signals", [])
    metadata_in = result_dict.get("metadata", {})
    samp_freq   = result_dict.get("sampling_frequency")

    channel_names = result_dict.get(
        "channel_names", [f"CH{i+1}" for i in range(len(signals))]
    )

    # ------------ build final metadata ------------------------------------
    meta = {
        "time_units": "seconds",
        "time_auto_generated": time is None,
        "source_format": descriptor.get("format", "unknown"),
        "database_id": "unknown",
        "sampling_frequency": samp_freq,
        "channel_names": channel_names,
        "channel_units": ["unknown"] * len(channel_names),
        "version": "v1.0",
        "upload_date": now,
        "conversion_date": now,
        "auto_mapped": True,
        "doi": "unknown",
        "original_file_name": original_filename,
        "sparc_subject_id": "unknown",
        "species": metadata_in.get("species", "unknown"),
        "anatomical_location": metadata_in.get("anatomical_location", "unknown"),
        "modality": metadata_in.get("modality", "unknown"),
        "experimenter": metadata_in.get("experimenter", ["unknown"]),
        "institution": metadata_in.get("institution", "unknown"),
        "sweep_mode": metadata_in.get("sweep_mode", False),
        "notes": "Mapped using SPARCFUSE",
    }
    if metadata_overrides:
        meta.update(metadata_overrides)

    output_path = Path(output_path)

    # ======================================================================
    # 1. NPZ container
    # ======================================================================
    if file_format == "npz":
        np.savez_compressed(
            output_path.with_suffix(".npz"),
            time=np.asarray(time, dtype="f8") if time is not None else None,
            signals=np.asarray(signals, dtype="f8"),
            annotations=np.asarray(annotations or [], dtype=object),
            metadata=meta,
        )
        return

    # ======================================================================
    # 2. Zarr containers (directory or zip)
    # ======================================================================
    elif file_format in ("zarr", "zarr.zip"):
        suffix     = ".zarr" if file_format == "zarr" else ".zarr.zip"
        store_path = output_path.with_suffix(suffix)

        store = (
            DirectoryStore(str(store_path))
            if file_format == "zarr"
            else ZipStore(str(store_path), mode="w")
        )

        try:
            root = zarr.open_group(store=store, mode="w")

            # ---- time ----------------------------------------------------
            if time is not None:
                root.array("time", np.asarray(time, dtype="f8"))

            # ---- signals -------------------------------------------------
            sig_kwargs = {}
            if zarr_chunks is not None:
                sig_kwargs["chunks"] = zarr_chunks
            if zarr_compressor is not None:
                sig_kwargs["compressor"] = zarr_compressor

            root.array("signals", np.asarray(signals, dtype="f8"), **sig_kwargs)

            # ---- annotations --------------------------------------------
            if annotations:
                ann_json = [
                    a if isinstance(a, str) else json.dumps(a, ensure_ascii=False)
                    for a in annotations
                ]
                maxlen = max(len(s) for s in ann_json)
                root.array("annotations", np.asarray(ann_json, dtype=f"<U{maxlen}"))

            # ---- metadata -----------------------------------------------
            root.attrs.update(meta)

        finally:
            if isinstance(store, ZipStore):
                store.close()

        return

    elif file_format == "mat":
        mat_dict = {
            "time": np.asarray(time, dtype="f8") if time is not None else np.empty(0),
            "signals": np.asarray(signals, dtype="f8"),
            "annotations": np.asarray(annotations or [], dtype=object),
            "metadata": meta,
        }
        savemat(str(output_path.with_suffix(".mat")), mat_dict)
        return
    # ======================================================================
    # 3. Unsupported formats
    # ======================================================================
    else:
        raise ValueError(f"Unsupported file format: {file_format}")


def load_and_plot_zarr(zarr_path_str: str | Path) -> None:
    """
    Open a Zarr archive (directory or .zarr.zip), plot the contained signals, and print metadata and annotations.

    Parameters:
        zarr_path_str (str | Path): Path to the Zarr archive. Can be a directory, a directory ending with '.zarr', or a '.zarr.zip' file.

    Behavior:
        - Opens the Zarr archive in read mode, supporting both zipped and directory formats.
        - Extracts 'time', 'signals', and optional 'annotations' arrays from the archive.
        - Retrieves metadata from the root group's attributes.
        - Plots each signal channel against time, labeling with channel names if available.
        - Prints metadata and, if present, annotations to the console.
        - Ensures proper closure of any opened stores.
    """
    zarr_path = Path(zarr_path_str).expanduser()

    # ── 1. open the root group safely ───────────────────────────────────
    if zarr_path.suffix == ".zip":                 # *.zarr.zip
        store = ZipStore(str(zarr_path), mode="r")
        root = zarr.open_group(store=store, mode="r")
        close_store = store.close                 # will be called later
    elif zarr_path.suffix == ".zarr":              # directory ending .zarr
        store = DirectoryStore(str(zarr_path))
        root = zarr.open_group(store=store, mode="r")
        close_store = store.close
    else:                                          # any other directory
        root = zarr.open_group(str(zarr_path), mode="r")
        close_store = lambda: None

    try:
        # ── 2. pull arrays ──────────────────────────────────────────────
        time    = root["time"][:]                 # (n_time,)
        signals = root["signals"][:]              # (n_chan, n_time)
        metadata = dict(root.attrs)
        chan_names = metadata.get(
            "channel_names", [f"CH{i+1}" for i in range(signals.shape[0])]
        )

        annotations = root["annotations"][:] if "annotations" in root else None

        # ── 3. plot ─────────────────────────────────────────────────────
        plt.figure(figsize=(10, 4))
        for i, ch in enumerate(signals):
            plt.plot(time, ch, label=chan_names[i])
        plt.xlabel("Time (s)")
        plt.ylabel("Signal")
        plt.title(f"Reloaded from {zarr_path.name}")
        plt.legend()
        plt.tight_layout()
        plt.show()

        # ── 4. print metadata & annotations ─────────────────────────────
        print("Metadata:")
        for k, v in metadata.items():
            print(f"  {k}: {v}")

        if annotations is not None and len(annotations):
            print("\nAnnotations:")
            for ann in annotations:
                print(" ", ann)

    finally:
        close_store()            # closes ZipStore or DirectoryStore if opened
