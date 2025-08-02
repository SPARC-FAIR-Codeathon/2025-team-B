# postprocess_matlab.py
import numpy as np

def process_matlab_dict(mat, context=None):
    t = mat["t_sim"].flatten()
    y = mat["force"].flatten()
    sr = 1.0 / np.mean(np.diff(t))

    annotations = []
    if "stimvect" in mat:
        stimvect = mat["stimvect"].flatten()
        if len(stimvect) == 2:
            annotations.append({
                "label": "stimulation",
                "start_time": float(stimvect[0]),
                "end_time": float(stimvect[1])
            })

    metadata = {
        "modality": "biomechanical force",
        "species": "unknown",
        "institution": "unknown",
        "experimenter": ["unknown"],
        "force_impulse": float(mat["force_impulse"].squeeze()),
        "force_norm": float(mat["force_norm"].squeeze()),
        "forceAvgNorm": mat["forceAvgNorm"].flatten().tolist()  # 30 values
    }

    return {
        "time": t,
        "signals": np.expand_dims(y, axis=0),
        "sampling_frequency": sr,
        "channel_names": ["force"],
        "annotations": annotations,
        "metadata": metadata
    }

descriptor = {
    "id": "matlab_mapping_302",
    "sparc_id": 309,
    "format": ".mat",
    "parser": {
        "module": "scipy.io",
        "function": "loadmat",
        "args": ["<filepath>"],
        "kwargs": {},
        "output_var": "mat",
        "postprocess": process_matlab_dict
    },
    "validation": {
        "required_fields": ["signals", "time", "sampling_frequency"]
    }
}
