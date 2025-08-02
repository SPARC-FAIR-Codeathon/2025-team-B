# mapping_schemes/postprocess_intan_316.py
import numpy as np

def process_wav(reader, _=None):
    
    sig = reader[1]
    sig = np.expand_dims(sig, axis=0)

    fs = reader[0]
    n_samples = sig.shape[1]


    
    #sig = sig.T                            #   → (n_chan, n_samples)
    t   = np.arange(n_samples) / fs

    print(t)
    print(sig)
    print(fs)

    return {
        "time":               t,
        "signals":            sig,
        "sampling_frequency": fs,
        "channel_names": ["unknown"] * len(sig.shape[1]),
        "channel_units": ["unknown"] * len(sig.shape[1]),
        "metadata": {
            "experimenter": "",
            "species":      "Human",
        },
        "annotations": []
    }

descriptor = {
    "id":       "mapping_406",
    "sparc_id": 406,
    "format":   ".wav",
    "parser": {
        "module":     "scipy.io.wavfile",
        "function":   "read",
        "args":       ["<filepath>"],
        "output_var": "reader",
        "postprocess": process_wav
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


