descriptor = {
    "id": "mapping_scheme_323",
    "sparc_id": 323,
    "format": ".csv",
    "parser": {
        "module": "pandas",
        "function": "read_csv",
        "args": ["<filepath>"],
        "kwargs": {
            "header": 0,
            "encoding": "utf-8"
        },
        "output_var": "df"
    },
    "preprocess": (
        "df.columns = df.columns.str.strip(); "
        "df['Time'] = df['Time'].astype(str).str.strip(); "
        "parsed_time = pd.to_datetime(df['Time'], format='%I:%M:%S.%f %p', errors='coerce'); "
        "mask = parsed_time.notna(); "
        "df = df.loc[mask].reset_index(drop=True); "
        "df['_parsed_time'] = parsed_time.loc[mask].reset_index(drop=True)"
    ),
    "mapping": {
        "time": "(df['_parsed_time'] - df['_parsed_time'].iloc[0]).dt.total_seconds().values",
        "signals": "df.iloc[:, 3:-1].transpose().values",  # exclude _parsed_time
        "sampling_frequency": "1.0 / (df['_parsed_time'].iloc[1] - df['_parsed_time'].iloc[0]).total_seconds()",
        "channel_names": "list(df.columns[3:-1])",
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
