import numpy as np
from scipy.io import loadmat

try:
    import mat73
except ImportError:
    mat73 = None

def _load_any_mat(fp):
    try:
        d = loadmat(fp, squeeze_me=True, struct_as_record=False)
        return {k: v for k, v in d.items() if not k.startswith("__")}
    except NotImplementedError:
        if mat73 is None:
            raise RuntimeError("MAT v7.3 — install mat73")
        return mat73.loadmat(fp)

def process_mat_neuroamp(mat_dict, filepath=None):
    """
    Pull out:
      - data       : 1D or (N,1) array
      - samplerate : scalar
      - datastart  : scalar (1‑based index)
      - unittext   : string
      - titles     : string or list-of-strings
    Force `data` into shape (1, N) so `signals` is always (n_ch, n_samples).
    """
    data       = mat_dict.get("data")
    samplerate = float(mat_dict.get("samplerate", np.nan))
    datastart  = float(mat_dict.get("datastart", 1.0))
    unit       = mat_dict.get("unittext", "")
    titles     = mat_dict.get("titles", None)

    if data is None or not np.isfinite(samplerate) or samplerate <= 0:
        raise ValueError("Missing ‘data’ or invalid ‘samplerate’")

    # --- normalize `data` into 1D array of length N ---
    arr = np.asarray(data)
    # squeeze out singleton dims → if (N,1) becomes (N,)
    arr = np.squeeze(arr)
    # ensure 1D
    if arr.ndim != 1:
        arr = arr.flatten()

    # --- build signals array shape (n_ch, N) ---
    if isinstance(titles, str) or titles is None:
        # single channel
        sigs     = arr[np.newaxis, :]    # shape (1, N)
        ch_names = [titles or "CH1"]
    else:
        # multiple channels: assume arr was (N, n_ch) 
        # after flatten above, arr may be 1D—this is rare for NeuroAmp
        arr2 = np.atleast_2d(arr)
        # guess: if arr2.shape[0] == len(titles) → channels×samples
        # else transpose
        if arr2.shape[0] == len(titles):
            sigs = arr2
        else:
            sigs = arr2.T
        ch_names = list(titles)

    # --- time vector accounting for datastart (1‑based) ---
    n_samp = sigs.shape[1]
    offset = datastart - 1.0
    time   = (np.arange(n_samp) + offset) / samplerate

    metadata = {
        "modality":           "neuroamp_mat",
        "source_file":        filepath,
        "sampling_frequency": samplerate,
        "unit":               unit
    }

    return {
        "time":               time,
        "signals":            sigs,
        "sampling_frequency": samplerate,
        "channel_names":      ch_names,
        "channel_units":      [unit] * len(ch_names),
        "metadata":           metadata,
        "annotations":        []
    }

descriptor = {
    "id":       "neuroamp_mat_mapping_400",
    "sparc_id": 400,
    "format":   ".mat",

    "parser": {
        "module":      "mat73" if mat73 else "scipy.io",
        "function":    "loadmat",
        "args":        ["<filepath>"],
        "output_var":  "mat_dict",
        "postprocess": process_mat_neuroamp
    },

    "mapping": {},

    "validation": {
        "required_fields": ["time", "signals", "sampling_frequency"]
    },

    "score_function":
        "lambda ctx: int(ctx.get('signals') is not None and ctx.get('time') is not None)"
}
