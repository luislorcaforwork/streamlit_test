from __future__ import annotations

import json
import os
from pathlib import Path
import datetime
import streamlit as st

try:
    from pydrive2.auth import GoogleAuth
    from pydrive2.drive import GoogleDrive
    from oauth2client.service_account import ServiceAccountCredentials
except Exception:
    GoogleAuth = None
    GoogleDrive = None
    ServiceAccountCredentials = None

LOCAL_TEMP_DIR = Path("temp_images")

def _get_shared_folder_id() -> str:
    return json.loads(st.secrets["DRIVE"])


def _get_service_account_json_path() -> str:
    return json.loads(st.secrets["DRIVE"])

def authenticate_google_drive():
    if GoogleAuth is None:
        return None
    json_path = _get_service_account_json_path()
    if not json_path or not Path(json_path).exists():
        return None

    gauth = GoogleAuth()
    gauth.auth_method = "service"
    gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(
        json_path,
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    try:
        drive = GoogleDrive(gauth)
        return drive
    except Exception:
        return None

def upload_to_drive(drive, file_path: Path, folder_id: str | None = None) -> str | None:
    if drive is None:
        return None
    try:
        metadata = {"title": file_path.name}
        if folder_id:
            metadata["parents"] = [{"id": folder_id}]
        f = drive.CreateFile(metadata)
        f.SetContentFile(str(file_path))
        f.Upload()
        return f["id"]
    except Exception:
        return None

def _save_bytes_to_temp(content: bytes, ext: str = ".jpg") -> Path:
    LOCAL_TEMP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    path = LOCAL_TEMP_DIR / f"capture_{timestamp}{ext}"
    path.write_bytes(content)
    return path

def gem_app() -> list[Path]:
    st.header("Capture / Upload a photo")
    saved: list[Path] = []

    camera_img = st.camera_input("Take a photo (optional)")
    if camera_img is not None:
        content = camera_img.getvalue()
        saved_path = _save_bytes_to_temp(content, ext=".jpg")
        st.success(f"Saved: {saved_path}")
        saved.append(saved_path)

    files = st.file_uploader("Or upload one or more images", type=["jpg","jpeg","png","webp","tif","tiff","pdf"], accept_multiple_files=True)
    if files:
        for f in files:
            content = f.getvalue()
            ext = "." + f.type.split("/")[-1] if f.type and "/" in f.type else ".bin"
            if ext.lower() not in {".jpg",".jpeg",".png",".webp",".tif",".tiff",".pdf"}:
                ext = ".jpg"
            saved_path = _save_bytes_to_temp(content, ext=ext)
            st.success(f"Saved: {saved_path}")
            saved.append(saved_path)

    with st.expander("Optional: Upload last saved file to Google Drive"):
        folder_id = _get_shared_folder_id()
        st.text_input("Shared Folder ID (optional)", value=folder_id, key="drive_folder_id")
        if st.button("Upload last file to Drive", disabled=(len(saved) == 0)):
            drive = authenticate_google_drive()
            if not drive:
                st.warning("Drive auth not configured. Provide a service account JSON.")
            else:
                target = saved[-1]
                fid = upload_to_drive(drive, target, folder_id=st.session_state.get("drive_folder_id", ""))
                if fid:
                    st.success(f"Uploaded to Drive. File ID: {fid}")
    return saved