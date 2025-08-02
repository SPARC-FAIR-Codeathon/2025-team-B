import numpy as np

def process_matlab_dict(mat, context=None):

    try:
        print("[DEBUG] Keys in MATLAB dict:", mat.keys())

        # Try extracting 't' and 'v'
        t = mat["t"]
        v = mat["v"]

        print("[DEBUG] Shapes before squeeze:", "t =", t.shape, "v =", v.shape)

        t = t.squeeze()  # should become shape (N,)
        v = v  # shape should be (100, N)

        print("[DEBUG] Shapes after squeeze:", "t =", t.shape, "v =", v.shape)

        result = {
            "time": t,
            "signals": v,
            "sampling_frequency": 1.0 / np.mean(np.diff(t)),
            "channel_names": [f"CH{i+1}" for i in range(v.shape[0])],
            "metadata": {
                "Ncell": int(mat["Ncell"].item()),
                "achDensity": float(mat["achDensity"].item())
            },
            "annotations": []
        }

        return result

    except Exception as e:
        print("[ERROR in process_matlab_dict]", str(e))
        return {}

descriptor = {
    "id": "matlab_mapping_310",
    "sparc_id": 310,
    "format": ".mat",
    "parser": {
        "module": "scipy.io",
        "function": "loadmat",
        "args": ["<filepath>"],
        "output_var": "mat",
        "postprocess":process_matlab_dict
    },
    "mapping": {},  # ← ✅ REQUIRED even if empty
    "validation": {
        "required_fields": ["signals", "time", "sampling_frequency"]
    },
    "score_function": "lambda ctx: int(ctx.get('signals') is not None and ctx.get('time') is not None)"
}
