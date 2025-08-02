"""
Command-line interface for SPARC-Fuse helpers.

Examples
--------
Bulk-convert every primary file in a dataset::

    sparc-fuse 224

Convert just two specific files::

    sparc-fuse 224 primary/imaging/scan1.nii.gz primary/imaging/scan2.nii.gz

Write results somewhere else::

    sparc-fuse 224 --output-dir ~/data/converted
"""
from __future__ import annotations

import argparse
from pathlib import Path
from .sparc_fuse_core import download_and_convert_sparc_data


# ── ASCII banner ─────────────────────────────────────────────────────────

_BANNER = r"""                                                                                                    
        ███      ████       ██      █████       ████      ████████  ██     ███    ████████ ████████ 
      ███████   ███████     ███     ███████    ██████    █████████ ███     ███  ████████████████████
      ███ ███   ███  ██    ████     ███  ███  ███  ███   ███       ███     ███ ████       ████      
       ████     ███  ██    ████     ███  ██   ███        █████████ ███     ███  ████████  █████████ 
         ███    ███████    █████    ███████   ███        █████████ ███     ███    █████████████████ 
      ███ ███   █████     ██████    ███ ███   ███  ███   ███       █████ █████████    ████████      
      ███ ███   ███       ███ ███   ███ ███    ███ ███   ███         ████████  ██████████ ██████████
       █████    ███       ██  ███   ███  ███    █████                                               
                         ███  ███                                                                   
      █████████████████████    ███ ███████████████████                                              
                               ██████                                                               
                                ████                                                                
                                ███                                                                 
                                 █                                                                                                                                                                                                                
"""
# ────────────────────────────────────────────────────────────────────────


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="sparc-fuse",
        description="Download, convert & standardise a SPARC dataset",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    p.add_argument("dataset_id", type=int, help="Numeric SPARC dataset ID")

    p.add_argument(
        "primary_paths",
        nargs="*",
        help="Specific primary-file paths (omit for all)",
    )

    p.add_argument(
        "--output-dir",
        type=Path,
        default=Path("./output"),
        help="Directory where converted files are saved",
    )

    return p


def main(argv: list[str] | None = None) -> None:
    print(_BANNER)
    parser = _build_parser()
    args = parser.parse_args(argv)

    # fixed settings you no longer want on the CLI
    descriptors_dir = Path("./mapping_schemes")
    file_format = "zarr"
    overwrite = False

    try:
        download_and_convert_sparc_data(
            dataset_id=args.dataset_id,
            primary_paths=args.primary_paths or None,
            output_dir=args.output_dir,
            descriptors_dir=descriptors_dir,
            file_format=file_format,
            overwrite=overwrite,
        )
    except Exception as exc:  # noqa: BLE001
        parser.error(str(exc))  # prints message + exits status-1

if __name__ == "__main__":  # so you can `python -m sparcfuse.cli …`
    main()
