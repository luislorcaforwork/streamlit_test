from __future__ import annotations
import csv
from pathlib import Path
from typing import Dict, List

TEMPLATE_HEADERS = {
    "facturas": [
        "fecha", "proveedor", "CIF proveedor", "cliente", "nif cliente", "atendió",
        "número factura", "cantidad", "product", "precio",
        "product next", "cantidad next", "precio next",
        "product next next", "cantidad next next", "precio next next",
        "product next next next", "cantidad next next next", "precio next next next",
        "base imponible 1", "cuota 1", "importe 1",
        "base imponible 2", "cuota 2", "importe 2",
        "base imponible 3", "cuota 3", "importe 3",
        "Importe total", "forma de pago", "nº cuenta", "нúmero tarjeta",
    ],
    "contractos": ["fecha", "cliente", "nif cliente", "importe", "concepto", "observaciones"],
    "tickets":    ["fecha", "proveedor", "importe", "concepto", "observaciones"],
    "identifier": ["uuid", "source_file"],
}

def _csv_path_for(template: str, csv_dir: Path) -> Path:
    name = f"{template}.csv"
    return csv_dir / name

def _row_for(data: Dict, headers: List[str]) -> List[str]:
    return [(str(data.get(h, "")) if data.get(h, "") is not None else "") for h in headers]

def append_row(data: Dict, template: str, csv_dir: Path) -> Path:
    if template not in TEMPLATE_HEADERS:
        raise ValueError(f"Unknown template: {template}")
    csv_dir.mkdir(parents=True, exist_ok=True)
    csv_path = _csv_path_for(template, csv_dir)

    headers = TEMPLATE_HEADERS[template]
    write_header = not csv_path.exists()

    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        if write_header:
            writer.writerow(headers)
        writer.writerow(_row_for(data, headers))
    return csv_path

def export_results(results: List[Dict], template: str, csv_dir: Path) -> Path:
    last_path = _csv_path_for(template, csv_dir)
    for item in results:
        append_row(item, template, csv_dir)
    return last_path