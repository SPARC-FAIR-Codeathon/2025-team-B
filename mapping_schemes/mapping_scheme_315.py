
import numpy as np

def process_smr_block(block, filepath=None):
    seg = block.segments[0] if block.segments else None
    if seg is None or not seg.analogsignals:
        return {
            "signals": None,
            "time": None,
            "sampling_frequency": None,
            "channel_names": None,
            "metadata": {
                "species": "unknown",
                "anatomical_location": "unknown",
                "modality": "pressure",
                "institution": "unknown",
                "experimenter": ["unknown"],
                "time_auto_generated": False
            }
        }

    signals = np.stack([
        asig.magnitude.flatten()
        for asig in seg.analogsignals
    ], axis=0)

    sr = float(seg.analogsignals[0].sampling_rate)
    n_samples = seg.analogsignals[0].shape[0]
    time = np.arange(n_samples) / sr
    channel_names = [
        str(asig.name) if asig.name else f"CH{i+1}"
        for i, asig in enumerate(seg.analogsignals)
    ]

    return {
        "signals": signals,
        "time": time,
        "sampling_frequency": sr,
        "channel_names": channel_names,
        "metadata": {
            "species": "unknown",
            "anatomical_location": "unknown",
            "modality": "pressure",
            "institution": "unknown",
            "experimenter": ["unknown"],
            "time_auto_generated": False
        }
    }

descriptor = {
    "id": "smrx_mapping_315",
    "sparc_id": 315,
    "format": ".smrx",
    "parser": {
        "module": "neo.io",
        "class": "Spike2IO",
        "init_args": {
            "filename": "<filepath>"
        },
        "load_method": "read_block",
        "output_var": "block",
        "postprocess": process_smr_block
    },
    "validation": {
        "required_fields": ["signals", "time", "sampling_frequency"]
    }
}
