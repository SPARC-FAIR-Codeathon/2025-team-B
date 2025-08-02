# mapping_schemes/postprocess_intan_316.py
import numpy as np

def process_intan_rhd(reader, _=None):
    reader.parse_header()

    fs = reader.header["signal_channels"][0]["sampling_rate"]
    n_samples = reader.get_signal_size(0, 0, 0)

    sig = reader.get_analogsignal_chunk(
        block_index=0, seg_index=0,
        i_start=0, i_stop=n_samples,
        stream_index=0                      # amplifier stream
    )                                      # shape (n_samples, n_chan)

    sig = sig.T                            #   → (n_chan, n_samples)
    t   = np.arange(n_samples) / fs

    return {
        "time":               t,
        "signals":            sig,
        "sampling_frequency": fs,
        "channel_names": [ch["name"] for ch in reader.header["signal_channels"]
                          if ch["stream_id"] == "0"],
        "channel_units": [ch["units"] for ch in reader.header["signal_channels"]
                          if ch["stream_id"] == "0"],
        "metadata": {
            "experimenter": "Unknown",
            "species":      "Rat",
            "institution":  "CWRU"
        },
        "annotations": []
    }


descriptor = {
    "id":       "intan_mapping_001",
    "sparc_id": 316,
    "format":   ".rhd",
    "parser": {
        "module":     "neo.rawio.intanrawio",
        "function":   "IntanRawIO",
        "args":       ["<filepath>"],
        "output_var": "reader",
        "postprocess": process_intan_rhd
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
