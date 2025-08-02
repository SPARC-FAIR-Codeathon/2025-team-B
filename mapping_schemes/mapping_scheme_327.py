descriptor = {
    "id": "matlab_mapping_rr_327",
    "sparc_id": 327,
    "format": ".mat",
    "parser": {
        "module": "scipy.io",
        "function": "loadmat",
        "args": ["<filepath>"],
        "output_var": "mat"
    },
    "mapping": {
        # Direct access without needing intermediate filtering
        "time": "mat['timePlot05'].squeeze() if 'timePlot05' in mat else None",
        "signals": "[mat['RRint05'].squeeze()] if 'RRint05' in mat else None",
        "sampling_frequency": "1.0 / (mat['timePlot05'][1,0] - mat['timePlot05'][0,0]) if 'timePlot05' in mat else None",
        "channel_names": "['RR Interval']",
        "channel_units": "['s']",
        "metadata": {
            "experimenter": "'Unknown'",
            "species": "'Rat'",
            "institution": "'Unknown'"
        },
        "annotations": []
    },
    "validation": {
        "required_fields": ["time", "signals", "sampling_frequency"]
    },
    "score_function": (
        "lambda ctx: int(ctx['time'] is not None) + int(ctx['signals'] is not None)"
    )
}
