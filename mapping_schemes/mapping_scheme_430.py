# mapping_schemes/postprocess_intan_316.py
import numpy as np

def process_abf(reader, _=None):
    

    sig = reader.data

    fs = reader.dataRate
    n_samples = sig.shape[1]

    
    #sig = sig.T                            #   → (n_chan, n_samples)
    t   = np.arange(n_samples) / fs

    return {
        "time":               t,
        "signals":            sig,
        "sampling_frequency": fs,
        "channel_names": [c for c in reader.dacNames],
        "channel_units": [u for u in reader.dacUnits],
        "metadata": {
            "experimenter": "",
            "species":      "Rat",
        },
        "annotations": []
    }

descriptor = {
    "id":       "mapping_430",
    "sparc_id": 430,
    "format":   ".abf",
    "parser": {
        "module":     "pyabf",
        "function":   "ABF",
        "args":       ["<filepath>"],
        "output_var": "reader",
        "postprocess": process_abf
    },
    "mapping": {},                        # handled in post‑processor
    "validation": {
        "required_fields": ["time", "signals", "sampling_frequency"]
    },
    "score_function": (
        "lambda ctx: int(ctx.get('time') is not None "
        "and ctx.get('signals') is not None)"
    )
}


