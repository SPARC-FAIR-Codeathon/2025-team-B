import numpy as np, adi

def _first_non_empty(ch):
    """
    Return (record_id, data) for the first non‑empty record of channel `ch`.
    If **all** records are empty → return (None, None).
    """
    for r_id in range(1, ch.n_records + 1):
        try:
            data = ch.get_data(r_id)
            if len(data):
                return r_id, np.asarray(data, dtype=float)
        except ValueError:
            continue
    return None, None


def process_adi(rec, filepath=None):
    """
    Postprocess an ADI SDK record `rec`, aligning all channels to the highest sampling rate
    by linear interpolation, then trimming to the shortest duration. Returns standardized dict.
    """
    good_chs   = []
    data_stack = []
    fs_list    = []

    # Collect all non-empty channels and their data + sampling rates
    for ch in rec.channels:
        rec_id, data = _first_non_empty(ch)
        if data is None:
            continue
        good_chs.append(ch)
        data_stack.append(data)
        # uni-dimensional fs (list or scalar)
        fs_val = ch.fs[0] if isinstance(ch.fs, (list, tuple)) else ch.fs
        fs_list.append(float(fs_val))

    if not data_stack:
        raise ValueError("No channel with data found in this ADI file.")

    # Determine the highest sampling frequency to upsample to
    fs_target = max(fs_list)

    # Upsample slower channels via linear interpolation
    upsampled = []
    for data, fs_orig in zip(data_stack, fs_list):
        if fs_orig == fs_target:
            upsampled.append(data)
        else:
            n_orig = data.shape[0]
            t_orig = np.arange(n_orig) / fs_orig
            n_new  = int(np.round(n_orig * fs_target / fs_orig))
            t_new  = np.arange(n_new) / fs_target
            data_new = np.interp(t_new, t_orig, data)
            upsampled.append(data_new)

    # Trim all channels to the shortest length to allow stacking
    lengths = [arr.shape[0] for arr in upsampled]
    min_len = min(lengths)
    if any(l != min_len for l in lengths):
        upsampled = [arr[:min_len] for arr in upsampled]
        trimmed = True
    else:
        trimmed = False

    # Stack into array and build time vector
    signals = np.vstack(upsampled)
    time    = np.arange(min_len) / fs_target

    # Build output metadata
    metadata = {
        "modality":           "adinstruments",
        "source_file":        filepath,
        "original_sampling":  fs_list,
        "upsampled_to":       fs_target,
        "upsampled_performed": any(fs_orig != fs_target for fs_orig in fs_list),
        "trimmed_to_samples": min_len,
        "trimmed":            trimmed
    }

    return {
        "time":               time,
        "signals":            signals,
        "sampling_frequency": fs_target,
        "channel_names":      [ch.name for ch in good_chs],
        "channel_units":      [ch.units for ch in good_chs],
        "metadata":           metadata,
        "annotations":        []
    }

# Descriptor definition for SPARC ADI files
descriptor = {
    "id":       "adinstruments_mapping_378",
    "sparc_id": 400,
    "format":   (".adicht", ".adidat", ".adidatx"),

    "parser": {
        "module":      "adi",
        "function":    "read_file",
        "args":        ["<filepath>"],
        "output_var":  "rec",
        "postprocess": process_adi
    },

    "mapping": {},

    "validation": {"required_fields": ["time", "signals", "sampling_frequency"]},

    "score_function": "lambda ctx: int(ctx.get('signals') is not None and ctx.get('time') is not None)"
}
