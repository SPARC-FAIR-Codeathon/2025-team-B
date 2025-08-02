# postprocess_abf.py
import numpy as np

def postprocess_abf_block(block, descriptor=None):
    if not block.segments:
        return {}

    n_sweeps = len(block.segments)
    n_channels = len(block.segments[0].analogsignals)
    n_samples = block.segments[0].analogsignals[0].shape[0]
    sr = float(block.segments[0].analogsignals[0].sampling_rate)

    # Shape: (n_channels, n_sweeps, n_samples)
    signals = np.stack([
        np.stack([
            seg.analogsignals[ch_idx].magnitude.flatten()
            for seg in block.segments
        ], axis=0).T  # transpose to shape (n_sweeps, n_samples)
        for ch_idx in range(n_channels)
    ], axis=0)  # final shape: (n_channels, n_sweeps, n_samples)

    # Time vector: shared across sweeps
    time = np.arange(n_samples) / sr

    # Channel names
    channel_names = [
        asig.name if asig.name else f"CH{i+1}"
        for i, asig in enumerate(block.segments[0].analogsignals)
    ]

    return {
        "signals": signals,  # shape: (n_channels, n_sweeps, n_samples)
        "time": time,
        "sampling_frequency": sr,
        "channel_names": channel_names,
        "metadata": {
            "species": "unknown",
            "anatomical_location": "unknown",
            "modality": "electrophysiology",
            "institution": "unknown",
            "experimenter": ["unknown"],
            "sweep_mode": True,
        }
    }

descriptor = {
    "id": "abf_mapping_001",
    "sparc_id": 297,
    "format": ".abf",
    "parser": {
        "module": "neo.io",
        "class": "AxonIO",
        "init_args": {
            "filename": "<filepath>"
        },
        "load_method": "read_block",
        "output_var": "block",
        "postprocess": postprocess_abf_block
    },
    "validation": {
        "required_fields": ["signals", "time", "sampling_frequency"]
    }
}
