descriptor = {
    "id": "csv_mapping_108",
    "sparc_id": 108,
    "format": ".csv",
    "parser": {
        "module": "pandas",
        "function": "read_csv",
        "args": ["<filepath>"],
        "kwargs": {
            "header": None,          # or 0, depending on file
            "encoding": "utf-16",
            "sep": "\t"     
        },
        "output_var": "df"
    },
    "mapping": {
        "time": "df.iloc[:, 0].values",
        "signals": "df.iloc[:, 1:].transpose().values",
        "sampling_frequency": "1.0 / (df.iloc[1, 0] - df.iloc[0, 0])",
        "channel_names": "[f'CH{i}' for i in range(1, df.shape[1])]",
        "metadata": {
            "experimenter": "'Unknown'",
            "species": "'Unknown'",
            "institution": "'Unknown'"
        },
        "annotations": []
    },
    "validation": {
        "required_fields": ["time", "signals", "sampling_frequency"]
    },
    "score_function": "lambda ctx: int(ctx['time'] is not None) + int(ctx['signals'] is not None)"
}
