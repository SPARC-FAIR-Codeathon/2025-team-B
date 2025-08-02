import numpy as np
import h5py


def process_ep_hdf5_flat(f, context=None):
    """
    Traverse EPs/<date>/<region>/<trial>/… and produce one flat dict per trial:
      - date, region, trial (str)
      - threshold   (float)
      - levels      (np.ndarray)
      - responses   (np.ndarray)
      - one entry per waveform dataset, named exactly as in the file
    Returns:
      {
        "records": [ {...}, {...}, … ],
        "metadata": { "source_file": ..., "n_records": ..., "dates": [...] },
        "annotations": []
      }
    """
    records = []
    ep_root = f.get("EPs")
    if ep_root is None:
        raise ValueError("No top‑level EPs group found")

    # For each date under EPs/
    for date_key, date_grp in ep_root.items():
        # date_grp should be a Group
        if not isinstance(date_grp, h5py.Group):
            continue
        # For each region under date
        for region_key, region_grp in date_grp.items():
            if not isinstance(region_grp, h5py.Group):
                continue
            prefix = f"w_{region_key}"

            # For each trial under region
            for trial_key, trial_grp in region_grp.items():
                # skip non-groups (datasets at region level)
                if not isinstance(trial_grp, h5py.Group):
                    continue

                rec = {
                    "date":      date_key,
                    "region":    region_key,
                    "trial":     trial_key,
                    "threshold": None,
                    "levels":    None,
                    "responses": None
                }

                # Scalar threshold
                if "v_Threshold" in trial_grp:
                    rec["threshold"] = float(trial_grp["v_Threshold"][()])

                # Level & response arrays
                if "w_Level" in trial_grp:
                    rec["levels"]    = trial_grp["w_Level"][()]
                if "w_Response" in trial_grp:
                    rec["responses"] = trial_grp["w_Response"][()]

                # Any waveform dataset matching prefix
                for ds_name, ds in trial_grp.items():
                    if ds_name.startswith(prefix) and isinstance(ds, h5py.Dataset):
                        rec[ds_name] = ds[()]

                records.append(rec)

    # Build metadata
    dates = sorted({r["date"] for r in records})
    metadata = {
        "source_file": context or "unknown",
        "n_records":   len(records),
        "dates":       dates
    }

    return {
        "records":     records,
        "metadata":    metadata,
        "annotations": []
    }


descriptor = {
    "id":       "ep_hdf5_flat_mapping_391",
    "sparc_id": 391,
    "format":   ".hdf5",

    "parser": {
        "module":     "h5py",
        "function":   "File",
        "args":       ["<filepath>", "r"],
        "output_var": "f",
        "postprocess": process_ep_hdf5_flat
    },

    # mapping empty → postprocess returns final result
    "mapping": {},

    "validation": {
        "required_fields": ["records", "metadata"]
    },

    "score_function":
        # accept if we got at least one record
        "lambda ctx: int(ctx.get('records') is not None and len(ctx.get('records', [])) > 0)"
}
