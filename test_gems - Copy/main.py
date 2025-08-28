import os
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, filedialog

from use_numind import use_numind
from numind_to_csv import numind_to_csv

# ---------------------------
# Config
# ---------------------------
CSV_FILE = "facturas.csv"

# NuMind Project IDs
PROJECTS = {
    "facturas": "c504c511-2646-4e52-9e39-1ba851a32922",
    "contratos": "43852263-146b-43a8-88bb-1ccb9868d04e",
    "tickets": "f7b37e7a-5bd5-47f0-8d2e-9a72496fb0fd",
    "identificar": "8ce0425f-4755-4d2e-ad3f-f83d45ab871d"
}


# ---------------------------
# Core Processing (Local)
# ---------------------------
def process_local_folder(folder_path: Path, project_id: str):
    if not folder_path.exists() or not folder_path.is_dir():
        messagebox.showerror("Error", f"{folder_path} is not a valid folder.")
        return

    # delete CSV if exists
    csv_path = folder_path / CSV_FILE
    if csv_path.exists():
        os.remove(csv_path)

    pdf_files = [f for f in folder_path.glob("*.pdf")]
    if not pdf_files:
        messagebox.showinfo("Info", "No PDFs found in the folder.")
        return

    for pdf_file in pdf_files:
        # process with NuMind
        numind_data = use_numind(pdf_file, project_id)
        numind_to_csv(numind_data, csv_path)

    messagebox.showinfo("Done", f"CSV saved to {csv_path}")


# ---------------------------
# Tkinter GUI
# ---------------------------
def start_gui():
    root = tk.Tk()
    root.title("PDF Processor (Local)")
    root.geometry("600x300")  # <- bigger window

    label = tk.Label(root, text="Select Local Folder Containing PDFs:")
    label.pack(pady=10)

    folder_var = tk.StringVar()

    folder_entry = tk.Entry(root, textvariable=folder_var, width=60)
    folder_entry.pack(pady=5)

    def browse_folder():
        folder = filedialog.askdirectory()
        if folder:
            folder_var.set(folder)

    browse_btn = tk.Button(root, text="Browse", command=browse_folder)
    browse_btn.pack(pady=5)

    def run_process(project_key):
        folder_path = Path(folder_var.get().strip())
        if not folder_path:
            messagebox.showerror("Error", "Please select a folder")
            return
        process_local_folder(folder_path, PROJECTS[project_key])

    btn_facturas = tk.Button(root, text="Process Facturas", command=lambda: run_process("facturas"))
    btn_facturas.pack(pady=10)

    btn_contratos = tk.Button(root, text="Process Contratos", command=lambda: run_process("contratos"))
    btn_contratos.pack(pady=10)

    btn_tickets = tk.Button(root, text="Process Tickets", command=lambda: run_process("tickets"))
    btn_tickets.pack(pady=10)

    btn_identificar = tk.Button(root, text="Process Identificar", command=lambda: run_process("identificar"))
    btn_identificar.pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    start_gui()
