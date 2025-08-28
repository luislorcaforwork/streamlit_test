import csv
import os
from pathlib import Path

def numind_to_csv(factura_data: dict, csv_path: Path) -> str:
    headers = [
        "fecha","proveedor","CIF proveedor","cliente","nif cliente","atendió","número factura",
        "product","cantidad","precio",
        "product next","cantidad next","precio next",
        "product next next","cantidad next next","precio next next",
        "product next next next","cantidad next next next","precio next next next",
        "base imponible 21 %","cuota 21 %","importe 21 %",
        "base imponible 10 %","cuota 10 %","importe 10 %",
        "Importe total","forma de pago","nº cuenta","número tarjeta","artista","datos actuacion","importe del contrato"
    ]

    datos_linea = [
        factura_data.get("fecha"),
        factura_data.get("proveedor"),
        factura_data.get("CIF proveedor"),
        factura_data.get("cliente"),
        factura_data.get("nif cliente"),
        factura_data.get("atendió"),
        factura_data.get("número factura"),
        factura_data.get("product "),
        factura_data.get("cantidad"),
        factura_data.get("precio"),
        factura_data.get("product next "),
        factura_data.get("cantidad next "),
        factura_data.get("precio next"),
        factura_data.get("product next next "),
        factura_data.get("cantidad next next"),
        factura_data.get("precio next next"),
        factura_data.get("product next next next"),
        factura_data.get("cantidad next next next"),
        factura_data.get("precio next next next"),
        factura_data.get("base imponible 21 %"),
        factura_data.get("cuota 21 %"),
        factura_data.get("importe 21 %"),
        factura_data.get("base imponible 10 %"),
        factura_data.get("cuota 10 %"),
        factura_data.get("importe 21 %"),
        factura_data.get("Importe total"),
        factura_data.get("forma de pago"),
        factura_data.get("nº cuenta"),
        factura_data.get("número tarjeta"),
        factura_data.get("artista"),
        factura_data.get("datos actuacion"),
        factura_data.get("importe del contrato")



    ]

    try:
        write_header = not Path(csv_path).exists()
        with open(csv_path, 'a', newline='', encoding='utf-8') as archivo_csv:
            writer = csv.writer(archivo_csv, delimiter=';')
            if write_header:
                writer.writerow(headers)
            writer.writerow(datos_linea)
        return str(csv_path)

    except Exception as e:
        print(f"Error while exporting: {e}")
        return ""
