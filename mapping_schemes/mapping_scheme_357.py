from mapping_schemes.matlab_mapping_generic import process_matlab_generic

descriptor = {
    "id":        "matlab_mapping_357",
    "sparc_id":  357,          # pick an unused ID in your catalogue
    "format":    ".mat",

    "parser": {                # SciPy loader
        "module":     "scipy.io",
        "function":   "loadmat",
        "args":       ["<filepath>"],
        "kwargs":     {},
        "output_var": "mat",
        "postprocess": process_matlab_generic
    },

    # mapping block left empty – everything done in post‑process
    "mapping": {},

    "validation": {
        "required_fields": ["time", "signals"]    # fs might be None for EMG
    },

    "score_function":
        "lambda ctx: int(ctx.get('signals') is not None and ctx.get('time') is not None)"
}
