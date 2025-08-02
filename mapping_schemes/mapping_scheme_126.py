descriptor = {
    "id": "acq_mapping_001",
    "sparc_id": 126,
    "format": ".acq",
    "parser": {
        "module": "bioread",
        "function": "read_file",
        "args": ["<filepath>"],
        "output_var": "reader"
    },
    "mapping": {
        "time": "reader.channels[0].time_index",  # shared time across all channels
        "signals": "[ch.data for ch in reader.channels]",
        "sampling_frequency": "1.0 / (reader.channels[0].time_index[1] - reader.channels[0].time_index[0])",
        "channel_names": "[ch.name for ch in reader.channels]",
        "channel_units": "[ch.units for ch in reader.channels]",
        "metadata": {
            "experimenter": "'Unknown'",
            "species": "'Unknown'",
            "institution": "'Unknown'"
        },
        "annotations": []  # no events in .acq by default
    },
    "validation": {
        "required_fields": ["time", "signals", "sampling_frequency"]
    },
    "score_function": "lambda ctx: int(ctx['time'] is not None) + int(ctx['signals'] is not None)"
}
