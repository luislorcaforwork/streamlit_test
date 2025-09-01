from __future__ import annotations
from pathlib import Path
from typing import Iterable, Callable, List, Dict, Optional
import os
try:
    from numind import NuMind  # type: ignore
except Exception:
    NuMind = None  # type: ignore

def _read_api_key() -> Optional[str]:
    key = os.getenv("NUMIND_API_KEY")
    if key:
        return key.strip()
    legacy = Path("env/keynumind.txt")
    if legacy.exists():
        try:
            return legacy.read_text(encoding="utf-8").strip()
        except Exception:
            pass
    return None

def use_numind(file_path: Path, project_id: str) -> Dict:
    api_key = _read_api_key()
    if NuMind is None:
        raise RuntimeError("NuMind SDK is not installed yet. Install/enable it later.")
    if not api_key:
        raise RuntimeError("NUMIND_API_KEY is not set and env/keynumind.txt was not found.")

    client = NuMind(api_key=api_key)
    input_bytes = Path(file_path).read_bytes()
    output_schema = client.post_api_projects_projectid_extract(project_id, input_bytes)  # type: ignore[attr-defined]
    return getattr(output_schema, "result", output_schema)

def extract_from_paths(paths: Iterable[Path], project_id: str) -> List[Dict]:
    results: List[Dict] = []
    for p in paths:
        try:
            results.append(use_numind(Path(p), project_id))
        except Exception as e:
            results.append({"_error": str(e), "_file": str(p)})
    return results

def extract_from_provider(provider: Callable[[], Iterable[Path]], project_id: str) -> List[Dict]:
    try:
        paths = list(provider())
    except Exception as e:
        return [{"_error": f"provider failed: {e}"}]
    return extract_from_paths(paths, project_id)