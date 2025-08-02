import numpy as np
import pandas as pd

def process_csv_351(df: pd.DataFrame, filepath: str = ""):
    try:
        # ---------- time vector ------------------------------------------------
        time = df["TimeStamp(sec)"].values                   # shape (N,)

        # ---------- signals ----------------------------------------------------
        data_cols = [c for c in df.columns if c != "TimeStamp(sec)"]
        signals   = df[data_cols].to_numpy().T              # (n_chan, N)

        # ---------- sampling rate ---------------------------------------------
        fs = None
        if len(time) > 1:
            fs = 1.0 / np.mean(np.diff(time))

        return {
            "time"              : time,
            "signals"           : signals,
            "sampling_frequency": fs,
            "channel_names"     : data_cols,
            "channel_units"     : ["unknown"] * len(data_cols),
            "metadata"          : {
                "modality"   : "multisensor_csv",
                "source_file": filepath or "unknown",
            },
            "annotations"       : [],
        }

    except Exception as e:
        print("[ERROR in process_csv_350]", e)
        return {}


descriptor = {
    "id": "csv_mapping_351",
    "sparc_id": 351,
    "format": ".csv",

    # -------------- loader ----------------------------------------------------
    "parser": {
        "module": "pandas",
        "function": "read_csv",
        "args": ["<filepath>"],
        "kwargs": {
            "header": 0,
            "encoding": "utf-8",
            "sep": ","
        },
        "output_var": "df",
        # tell match_best_mapping() to call the post‑processor
        "postprocess": process_csv_351
    },

    # empty mapping block – everything is done in postprocess
    "mapping": {},

    "validation": {
        "required_fields": ["time", "signals", "sampling_frequency"]
    },

    "score_function": "lambda ctx: int(ctx.get('signals') is not None and ctx.get('time') is not None)"
}

