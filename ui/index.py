from __future__ import annotations
from pathlib import Path
import streamlit as st

from .gem_app import gem_app
from app.gui_leftover import process_local_folder, export_results_to_csv

TEMP_DIR = Path("temp_images")
CSV_OUT = Path("exports")

def main():
    st.set_page_config(page_title="Receipts → NuMind → CSV", page_icon="🧾", layout="centered")

    st.title("📸 → 🧠 → 📄 Pipeline (scaffold)")
    st.caption("This is a scaffold. The actual triggers to NuMind/Drive will be wired later.")

    st.subheader("1) Capture / Upload")
    saved_paths = gem_app()

    st.subheader("2) Extract with NuMind (entry point)")
    project_id = st.text_input("NuMind project id", value="", help="Provide when the SDK/Key are ready.")
    if st.button("Run extraction on temp_images", type="primary"):
        if not project_id:
            st.warning("Provide a project id first.")
        else:
            results = process_local_folder(TEMP_DIR, project_id)
            st.session_state["_last_results"] = results
            ok = sum(1 for r in results if "_error" not in r)
            err = sum(1 for r in results if "_error" in r)
            st.success(f"Done. {ok} succeeded, {err} failed. Results are held in session.")
            with st.expander("Raw results"):
                st.json(results)

    st.subheader("3) Export to CSV")
    template = st.selectbox("Template", ["facturas", "contractos", "tickets", "identifier"], index=0)
    if st.button("Export last results to CSV", disabled=("_last_results" not in st.session_state)):
        results = st.session_state.get("_last_results", [])
        if not results:
            st.warning("No results to export yet.")
        else:
            path = export_results_to_csv(results, template, CSV_OUT)
            st.success(f"Exported to: {path}")
            st.download_button("Download CSV", data=Path(path).read_bytes(), file_name=Path(path).name)

def index():
    return main()