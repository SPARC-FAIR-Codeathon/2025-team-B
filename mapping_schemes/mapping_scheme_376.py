# ── mapping_schemes/matlab_mapping_emg_376.py ─────────────────────────
import numpy as np

# ---------------------------------------------------------------------
# post‑processor
# ---------------------------------------------------------------------
def process_matlab_emg(mat, context=None):
    """
    Expect keys:
        • t          : 1‑D time vector
        • emg        : 1‑D signal vector
        • freq       : stimulation frequency          (scalar)
        • pulseno    : number of pulses               (scalar)
        • amp        : pulse amplitude                (scalar)
        • ampBCT     : ? (scalar)
    Returns the standard SPARCFuse result‑dict.
    """
    # --- sanity checks ------------------------------------------------
    required = ("t", "emg")
    if not all(k in mat for k in required):
        raise ValueError(f"MAT‑file missing one of {required}")

    t   = np.asarray(mat["t"]).squeeze()
    sig = np.asarray(mat["emg"]).squeeze()

    if t.ndim != 1 or sig.ndim != 1:
        raise ValueError("`t` and `emg` must be 1‑D vectors")

    if t.size != sig.size:
        raise ValueError("t and emg vectors have different lengths")

    fs = 1.0 / np.mean(np.diff(t)) if t.size > 1 else None

    # --- assemble result ---------------------------------------------
    return {
        "time":               t,
        "signals":            sig[np.newaxis, :],      # shape (1, N)
        "sampling_frequency": fs,
        "channel_names":      ["emg"],
        "channel_units":      ["mV"],                  # adjust if known
        "metadata": {
            "modality": "emg",
            "freq_hz":  float(mat.get("freq",   np.nan)),
            "pulses":   int(mat.get("pulseno", np.nan)),
            "amp_v":    float(mat.get("amp",    np.nan)),
            "ampBCT":   float(mat.get("ampBCT", np.nan)),
        },
        "annotations": []
    }


# ---------------------------------------------------------------------
# descriptor
# ---------------------------------------------------------------------
descriptor = {
    "id":        "matlab_mapping_376",
    "sparc_id":  376,          # pick an unused SPARC‑ID in your set‑up
    "format":    ".mat",

    "parser": {
        "module":      "scipy.io",
        "function":    "loadmat",
        "args":        ["<filepath>"],
        "kwargs":      {"squeeze_me": True, "struct_as_record": False},
        "output_var":  "mat",
        "postprocess": process_matlab_emg,
    },

    # mapping block is empty – everything done in post‑process
    "mapping": {},

    "validation": {
        "required_fields": ["time", "signals", "sampling_frequency"]
    },

    "score_function":
        "lambda ctx: int(ctx.get('signals') is not None and ctx.get('time') is not None)"
}
