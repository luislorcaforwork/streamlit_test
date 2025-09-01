from __future__ import annotations
from pathlib import Path
from typing import List, Dict
from .use_numind import extract_from_paths
from .numind_to_csv import export_results

def list_image_files(folder: Path) -> List[Path]:
    exts = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".pdf"}
    return [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in exts]

def process_local_folder(folder: Path, project_id: str) -> List[Dict]:
    files = list_image_files(folder)
    return extract_from_paths(files, project_id)

def export_results_to_csv(results: List[Dict], template: str, csv_output_dir: Path) -> Path:
    return export_results(results, template, csv_output_dir)

def process_drive_folder(drive_folder_id: str, project_id: str) -> List[Dict]:
    raise NotImplementedError("Drive folder processing will be wired later via a provider.")