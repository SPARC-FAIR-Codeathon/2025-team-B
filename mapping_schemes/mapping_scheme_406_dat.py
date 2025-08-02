# mapping_schemes/postprocess_intan_316.py
import numpy as np


def process_dat(reader, _=None):
    

    # TODO




    data = []
    d = reader.readlines()


    # for l in d:
    #     if l.contains("Start"):
    #         data.append([])
    #     k = i.rstrip().split(",")
    #     data.append([float(i) if is_float(i) else i for i in k]) 
    # reader.close()

    
    #sig = sig.T                            #   → (n_chan, n_samples)
    # t   = np.arange(n_samples) / fs

    return {
        "time":               [],
        "signals":            [],
        "sampling_frequency": 0,
        "channel_names": [],
        "channel_units": [],
        "metadata": {
            "experimenter": "",
            "species":      "Human",
        },
        "annotations": []
    }

descriptor = {
    "id":       "mapping_406",
    "sparc_id": 406,
    "format":   ".dat",
    "parser": {
        "module":     "os",
        "function":   "open",
        "args":       ["<filepath>"],
        "output_var": "file",
        "postprocess": process_dat
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


