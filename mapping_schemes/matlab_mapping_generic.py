import numpy as np
from scipy.io.matlab import mat_struct

# ── helpers ───────────────────────────────────────────────────────────
def _mat_to_dict(obj):
    """Recursively convert MATLAB proxies to pure‑Python containers."""
    # mat_struct  (SciPy default)
    if isinstance(obj, mat_struct):
        return {f: _mat_to_dict(getattr(obj, f)) for f in obj._fieldnames}

    # scalar structured record  (np.void)
    if isinstance(obj, np.void) and obj.dtype.names:
        return {n: _mat_to_dict(obj[n]) for n in obj.dtype.names}

    # 1×1 object / structured array
    if isinstance(obj, np.ndarray) and obj.size == 1:
        return _mat_to_dict(obj.reshape(-1)[0])

    # dict from mat73
    if isinstance(obj, dict):
        return {k: _mat_to_dict(v) for k, v in obj.items()}

    # cell array
    if isinstance(obj, (list, tuple)):
        return [_mat_to_dict(x) for x in obj]

    return obj                              # numeric, str, …

def _as_2d_float(a):
    a = np.asarray(a, dtype=float).squeeze()
    if a.ndim == 0:                       # scalar
        a = a.reshape(1, 1)
    elif a.ndim == 1:                     # (N,) → (1, N)
        a = a[None, :]
    elif a.ndim == 2 and 1 in a.shape:    # 1×N or N×1 → (1, N)
        a = a.reshape(1, -1)
    elif a.ndim > 2:                      # flatten trailing axes
        a = a.reshape(a.shape[0], -1)
    return a

# ── post‑processor ────────────────────────────────────────────────────
def process_matlab_generic(mat_dict, context=None):
    """Handle BP structs **and** ‘naked’ EMG traces."""
    # strip helper keys
    mat_dict = {k: v for k, v in mat_dict.items() if not k.startswith("__")}

    # ---------- Case A : struct with ‘signals’ field ------------------
    for name, raw in mat_dict.items():
        struct = _mat_to_dict(raw)
        if isinstance(struct, dict) and "signals" in struct:
            sig = _as_2d_float(struct["signals"])
            t   = np.asarray(struct.get("time", []), float).flatten()
            if t.size == 0 and "sr" in struct:
                t = np.arange(sig.shape[1]) / float(struct["sr"])
            fs = float(struct.get("sr", 1/np.mean(np.diff(t)))) \
                 if t.size > 1 else None

            return {
                "time":               t,
                "signals":            sig,
                "sampling_frequency": fs,
                "channel_names":      [struct.get("chans", name)],
                "metadata":           {k: v for k, v in struct.items()
                                       if k not in ("signals", "time")},
                "annotations":        []
            }

    # ---------- Case B : first long numeric vector --------------------
    for name, val in mat_dict.items():
        if (isinstance(val, np.ndarray)
                and (val.ndim == 1 or (val.ndim == 2 and 1 in val.shape))):
            sig = _as_2d_float(val)
            return {
                "time":               np.arange(sig.shape[1]),
                "signals":            sig,
                "sampling_frequency": None,
                "channel_names":      [name],
                "metadata":           {"modality": "emg"},
                "annotations":        []
            }

    raise ValueError("MAT‑file structure not recognised by post‑processor.")
