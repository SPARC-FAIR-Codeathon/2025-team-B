import numpy as np
import h5py
from datetime import datetime

def process_hdf5_dict(f, context=None):
    """
    Post‐process an HDF5 file for SPARC conversion.  
    - Automatically picks the first top‐level group (e.g. 'subject-1').  
    - Parses its subgroups as ISO timestamps, computes wall‐clock offsets.  
    - Concatenates ECG, HR and neural segments, builds true time vectors.  
    """
    try:
        # --- 1) Discover your subject group and its segment keys ---
        first_group_key = next(iter(f.keys()))
        print("[DEBUG] Using top‐level group:", first_group_key)
        subject_group = f[first_group_key]

        segment_keys = list(subject_group.keys())
        # sort chronologically (ISO format sorts naturally, but be safe)
        segment_keys.sort(key=lambda ts: datetime.fromisoformat(ts))
        print("[DEBUG] Segment timestamps:", segment_keys)

        # parse segment start times and compute offsets (sec) from t0
        segment_times = [datetime.fromisoformat(ts) for ts in segment_keys]
        t0 = segment_times[0]
        offsets = [(ts - t0).total_seconds() for ts in segment_times]

        # --- 2) Load and concatenate each modality ---
        ecg_segs    = [subject_group[k]["ecg"][()]    for k in segment_keys]  # each (N, 3)
        hr_segs     = [subject_group[k]["hr"][()]     for k in segment_keys]  # each (M, 2)
        neural_segs = [subject_group[k]["neural"][()] for k in segment_keys]  # each (L, 4)

        # transpose so channels×samples
        ecg    = np.concatenate(ecg_segs,    axis=0).T  # (3, total_samples_ecg)
        hr     = np.concatenate(hr_segs,     axis=0).T  # (2, total_samples_hr)
        neural = np.concatenate(neural_segs, axis=0).T  # (4, total_samples_neural)

        # --- 3) Build true time vectors for each modality ---
        ecg_times    = np.concatenate([
            np.arange(seg.shape[0]) / 1000.0 + off
            for seg, off in zip(ecg_segs, offsets)
        ])
        hr_times     = np.concatenate([
            np.arange(seg.shape[0]) /  500.0 + off
            for seg, off in zip(hr_segs, offsets)
        ])
        neural_times = np.concatenate([
            np.arange(seg.shape[0]) /30000.0 + off
            for seg, off in zip(neural_segs, offsets)
        ])

        print("[DEBUG] Shapes:")
        print(f" - ECG:    {ecg.shape}, time length {ecg_times.shape}")
        print(f" - HR:     {hr.shape}, time length {hr_times.shape}")
        print(f" - Neural: {neural.shape}, time length {neural_times.shape}")

        # --- 4) Package result dict ---
        return {
            # ECG
            "time":                ecg_times,
            "signals":             ecg,
            "sampling_frequency":  1000.0,
            "channel_names":       [f"ECG{i+1}" for i in range(ecg.shape[0])],
            "channel_units":       ["mV"] * ecg.shape[0],

            # HR
            "time_hr":             hr_times,
            "signals_hr":          hr,
            "sampling_frequency_hr": 500.0,
            "channel_names_hr":    [f"HR{i+1}" for i in range(hr.shape[0])],
            "channel_units_hr":    ["bpm"] * hr.shape[0],

            # Neural
            "time_neural":         neural_times,
            "signals_neural":      neural,
            "sampling_frequency_neural": 30000.0,
            "channel_names_neural": [f"NEURAL{i+1}" for i in range(neural.shape[0])],
            "channel_units_neural": ["uV"] * neural.shape[0],

            # Metadata
            "metadata": {
                "top_group":         first_group_key,
                "n_segments":        len(segment_keys),
                "start_time":        t0.isoformat(),
                "end_time":          segment_times[-1].isoformat(),
                "source_file":       context or "unknown"
            },
            "annotations": []
        }

    except Exception as e:
        print("[ERROR in process_hdf5_dict]", str(e))
        return {}

# Descriptor for match_best_mapping
descriptor = {
    "id":       "hdf5_mapping_subject1_full",
    "sparc_id": 349,
    "format":   ".hdf5",

    "parser": {
        "module":     "h5py",
        "function":   "File",
        "args":       ["<filepath>", "r"],
        "output_var": "f",
        "postprocess": process_hdf5_dict
    },

    "mapping": {},

    "validation": {
        "required_fields": ["time", "signals", "sampling_frequency"]
    },

    "score_function":
        "lambda ctx: int(ctx.get('time') is not None and ctx.get('signals') is not None)"
}
