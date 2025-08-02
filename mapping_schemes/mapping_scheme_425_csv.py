import numpy as np
import pandas as pd
import re

def process_csv_425(df: pd.DataFrame, filepath: str = ""):
    try:
        
        subject_frames = []
        for subject in df["subject"].unique().tolist():
            sub_df = df[df["subject"] == subject]
            sub_df = sub_df.rename(columns={old_name: f"{subject}_{old_name}" for old_name in sub_df.columns.to_list()[8:]})
            subject_frames.append(sub_df)
        new_df = df[df["subject"] == df["subject"].unique().tolist()[0]].iloc[:, :8]
        new_df = new_df.drop(["subject"], axis=1)
        for sub_df in subject_frames:
            for col in sub_df.columns[8:]:
                new_df[f"{col}"] = sub_df[col].to_list()

            
        # ---------- time vector ------------------------------------------------
        time = new_df["time since start (s)"].values                   # shape (N,)

        # ---------- signals ----------------------------------------------------
        data_cols = new_df.columns[7:]
        signals   = new_df[data_cols].to_numpy().T              # (n_chan, N)

        # ---------- sampling rate ---------------------------------------------
        # fs = None
        # if len(time) > 1:
        #     fs = 1.0 / np.mean(np.diff(time))
        fs = int(new_df["bin duration (s)"][0])

        channel_units = []
        for i, text in enumerate(data_cols):
            match = re.search(r'\(([^()]+)\)\s*$', text)
            if match:
                channel_units.append(match.group(1))
            else:
                channel_units.append("unknown")

        return {
            "time"              : time,
            "signals"           : signals,
            "sampling_frequency": fs,
            "channel_names"     : data_cols,
            "channel_units"     : channel_units, #["unknown"] * len(data_cols),
            "metadata"          : {
                "modality"   : "multisensor_csv",
                "source_file": filepath or "unknown",
            },
            "annotations"       : [],
        }

    except Exception as e:
        print("[ERROR in process_csv_425]", e)
        return {}


descriptor = {
    "id": "csv_mapping_425",
    "sparc_id": 425,
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
        "postprocess": process_csv_425
    },

    # empty mapping block – everything is done in postprocess
    "mapping": {},

    "validation": {
        "required_fields": ["time", "signals", "sampling_frequency"]
    },

    "score_function": "lambda ctx: int(ctx.get('signals') is not None and ctx.get('time') is not None)"
}
