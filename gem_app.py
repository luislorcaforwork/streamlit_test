# gem.py
import streamlit as st
import datetime
import os
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials

LOCAL_TEMP_DIR = "temp_images"

def _get_shared_folder_id() -> str:
    # Prefer Streamlit secrets → then env var → else empty
    return (
        st.secrets.get("drive", {}).get("shared_folder_id")
        or os.getenv("SHARED_FOLDER_ID", "")
    )

def authenticate_google_drive():
    """Authenticate with Google Drive using a Service Account (from Streamlit secrets or env)."""
    try:
        scopes = ["https://www.googleapis.com/auth/drive"]

        # Prefer Streamlit secrets (best for Streamlit Cloud)
        if "gdrive_sa" in st.secrets:
            creds = ServiceAccountCredentials.from_json_keyfile_dict(
                dict(st.secrets["gdrive_sa"]), scopes
            )
        # Fallback: env var with full JSON (optional)
        elif os.getenv("GDRIVE_SA_JSON"):
            import json
            sa_info = json.loads(os.getenv("GDRIVE_SA_JSON"))
            creds = ServiceAccountCredentials.from_json_keyfile_dict(sa_info, scopes)
        # Local dev fallback: file next to the code (ignored by git is fine)
        elif os.path.exists("service_account.json"):
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                "service_account.json", scopes
            )
        else:
            raise RuntimeError("No service account credentials found.")

        gauth = GoogleAuth()
        gauth.credentials = creds
        return GoogleDrive(gauth)
    except Exception as e:
        st.error(f"Authentication failed: {e}")
        return None

def upload_to_drive(drive_service, file_path, folder_id):
    """Upload a file into a specific Shared Drive folder ID."""
    try:
        file_metadata = {
            "title": os.path.basename(file_path),
            "parents": [{"id": folder_id}],
        }
        file = drive_service.CreateFile(file_metadata)
        file.SetContentFile(file_path)
        file.Upload()  # PyDrive2 adds supportsAllDrives automatically
        return file["id"]
    except Exception as e:
        st.error(f"Upload failed: {e}")
        return None

def gem_app():
    st.title("📸 Camera/Gallery → Google Drive (Shared Drive)")

    st.header("Upload options")
    upload_option = st.radio(
        "How do you want to upload?",
        ("Take a photo with the camera", "Choose from gallery"),
    )

    image_data = None
    filename_to_save = None

    if upload_option == "Take a photo with the camera":
        picture = st.camera_input("Take a photo")
        if picture:
            image_data = picture.getvalue()
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename_to_save = f"capture_{timestamp}.jpg"
            st.image(picture, caption="Captured photo")

    elif upload_option == "Choose from gallery":
        uploaded_file = st.file_uploader(
            "Upload an image", type=["png", "jpg", "jpeg"]
        )
        if uploaded_file is not None:
            image_data = uploaded_file.getvalue()
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            base, ext = os.path.splitext(uploaded_file.name)
            filename_to_save = f"{base}_{timestamp}{ext}"
            st.image(uploaded_file, caption="Selected image")

    if image_data:
        st.write("---")
        st.subheader("Uploading to Google Drive (Shared Drive)...")

        # Ensure temp dir
        os.makedirs(LOCAL_TEMP_DIR, exist_ok=True)
        file_path = os.path.join(LOCAL_TEMP_DIR, filename_to_save)

        # Save locally
        with open(file_path, "wb") as f:
            f.write(image_data)
        st.success(f"Saved locally: {filename_to_save}")

        # Read folder ID from secrets
        folder_id = _get_shared_folder_id()
        if not folder_id:
            st.error("Missing Shared Drive folder ID. Set it in secrets as [drive].shared_folder_id")
            return

        # Authenticate and upload
        drive = authenticate_google_drive()
        if not drive:
            st.warning("Google Drive authentication failed. Check your credentials.")
            return

        file_id = upload_to_drive(drive, file_path, folder_id)
        if file_id:
            st.success(f"✅ Uploaded! File ID: {file_id}")
            try:
                os.remove(file_path)
            except Exception:
                pass
