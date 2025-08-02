descriptor = {
    "id": "csv_mapping_301",
    "sparc_id": 301,
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
