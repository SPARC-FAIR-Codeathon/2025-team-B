descriptor = {
    "id": "csv_mapping_305",
    "sparc_id": 305,
    "format": ".csv",
    "parser": {
        "module": "pandas",
        "function": "read_csv",
        "args": ["<filepath>"],
        "kwargs": {
            "header": 0,
            "encoding": "utf-8",
            "sep": ","
        },
        "output_var": "df"
    },
    "mapping": {
        # Get unique channels
        "channel_names": "sorted(df['Stimulation Channel'].unique())",

        # Stack one signal per channel (e.g., Channel 1 to Channel 6)
        "signals": """
np.stack([
    df[df['Stimulation Channel'] == ch]['delta'].values
    for ch in sorted(df['Stimulation Channel'].unique())
], axis=0)
""",
        "time": "np.arange(df.shape[0] // len(df['Stimulation Channel'].unique()))",
        "sampling_frequency": "None",

        "metadata": {
            "modality": "'table_response'",
            "experimenter": "'Unknown'",
            "species": "'Unknown'",
            "institution": "'Unknown'",
            "stimulation_config": "df['Stimulation Configuration'].unique().tolist()"
        },
        "annotations": []
    },
    "validation": {
        "required_fields": ["signals", "time", "channel_names"]
    },
    "score_function": "lambda ctx: int(ctx['signals'] is not None)"
}
