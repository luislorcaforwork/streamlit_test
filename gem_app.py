import streamlit as st
import datetime
import os
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURATION ---
# Paste your Shared Drive folder ID here (from its URL)
# Example: https://drive.google.com/drive/folders/XXXXXXXXXXXXXXXX
SHARED_FOLDER_ID = "https://drive.google.com/drive/u/0/folders/1LP7n1gcyNtud0O5KKY8XYrKV9L89X-dV"
LOCAL_TEMP_DIR = "temp_images"


def authenticate_google_drive():
    """Authenticates with Google Drive using a service account."""
    try:
        scopes = ['https://www.googleapis.com/auth/drive']

        # --- OPTION A: local JSON file (development) ---
        if os.path.exists("service_account.json"):
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                "service_account.json", scopes
            )

        # --- OPTION B: Streamlit secrets (deployment) ---
        elif "gdrive_sa" in st.secrets:
            creds = ServiceAccountCredentials.from_json_keyfile_dict(
                dict(st.secrets["gdrive_sa"]), scopes
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
    """Uploads a file to a specific Google Drive folder (Shared Drive)."""
    try:
        file_metadata = {
            "title": os.path.basename(file_path),
            "parents": [{"id": folder_id}]
        }
        file = drive_service.CreateFile(file_metadata)
        file.SetContentFile(file_path)
        file.Upload()
        return file["id"]
    except Exception as e:
        st.error(f"Upload failed: {e}")
        return None


def gem_app():
    st.title("📸 Android Camera Capture & Google Drive Uploader (Shared Drive)")

    st.header("Opciones de Carga")
    upload_option = st.radio(
        "Elige cómo quieres subir la imagen:",
        ("Tomar una foto con la cámara", "Subir desde la galería"),
    )

    image_data = None
    filename_to_save = None

    if upload_option == "Tomar una foto con la cámara":
        picture = st.camera_input("Toma una foto")
        if picture:
            image_data = picture.getvalue()
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename_to_save = f"capture_{timestamp}.jpg"
            st.image(picture, caption="Foto capturada")

    elif upload_option == "Subir desde la galería":
        uploaded_file = st.file_uploader(
            "Sube una imagen de la galería", type=["png", "jpg", "jpeg"]
        )
        if uploaded_file is not None:
            image_data = uploaded_file.getvalue()
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            base, extension = os.path.splitext(uploaded_file.name)
            filename_to_save = f"{base}_{timestamp}{extension}"
            st.image(uploaded_file, caption="Imagen de la galería")

    # If an image has been captured or uploaded
    if image_data:
        st.write("---")
        st.subheader("Subiendo a Google Drive (Shared Drive)...")

        # Ensure the local temporary directory exists
        if not os.path.exists(LOCAL_TEMP_DIR):
            os.makedirs(LOCAL_TEMP_DIR)

        file_path = os.path.join(LOCAL_TEMP_DIR, filename_to_save)

        # Save the image locally
        with open(file_path, "wb") as f:
            f.write(image_data)

        st.success(f"Imagen guardada localmente como: {filename_to_save}")

        # Authenticate and upload to Google Drive
        drive = authenticate_google_drive()

        if drive:
            file_id = upload_to_drive(drive, file_path, SHARED_FOLDER_ID)
            if file_id:
                st.success(f"✅ ¡Subida exitosa! ID del archivo: {file_id}")
                os.remove(file_path)  # Clean up
        else:
            st.warning("❌ La autenticación de Google Drive falló. Revisa tus credenciales.")
