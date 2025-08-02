# mapping_schemes/postprocess_intan_316.py
import numpy as np

def process_blackrock_ns5(reader, _=None):
    reader.parse_header()

    fs = reader.header["signal_channels"][0]["sampling_rate"]
    n_samples = reader.get_signal_size(0, 0, 0)

    sig = reader.get_analogsignal_chunk(
        block_index=0, seg_index=0,
        i_start=0, i_stop=n_samples,
        stream_index=0                      # amplifier stream
    )                                      # shape (n_samples, n_chan)

    float_chunk = reader.rescale_signal_raw_to_float(sig, stream_index=0)
    float_chunk = float_chunk.T

    #sig = sig.T                            #   → (n_chan, n_samples)
    t   = np.arange(n_samples) / fs

    return {
        "time":               t,
        "signals":            float_chunk, #sig,
        "sampling_frequency": fs,
        "channel_names": [str(ch["name"]) for ch in reader.header["signal_channels"]],
        "channel_units": [str(ch["units"]) for ch in reader.header["signal_channels"]],
        "metadata": {
            "experimenter": "",
            "species":      "Cat",
        },
        "annotations": []
    }

descriptor = {
    "id":       "mapping_435",
    "sparc_id": 435,
    "format":   ".ns5",
    "parser": {
        "module":     "neo.rawio.blackrockrawio",
        "function":   "BlackrockRawIO",
        "args":       ["<filepath>"],
        "output_var": "reader",
        "postprocess": process_blackrock_ns5
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


