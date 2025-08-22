import streamlit as st
import datetime
import os
import json
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials

# Configuration
DRIVE_FOLDER_NAME = "Test Images"
LOCAL_TEMP_DIR = "temp_images"

def authenticate_google_drive():
    """Authenticates with Google Drive using a service account."""
    try:
        scopes = ['https://www.googleapis.com/auth/drive']

        # --- OPTION A: Local file (for development) ---
        if os.path.exists("service_account.json"):
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                "service_account.json", scopes
            )

        # --- OPTION B: Streamlit secrets (for deployment) ---
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

def get_drive_folder(drive_service, folder_name):
    """Finds or creates a Google Drive folder by name and returns its ID."""
    folder_query = (
        f"title='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    )
    folder_list = drive_service.ListFile({"q": folder_query}).GetList()

    if not folder_list:
        folder = drive_service.CreateFile(
            {"title": folder_name, "mimeType": "application/vnd.google-apps.folder"}
        )
        folder.Upload()
        st.success(f"Created Google Drive folder: {folder_name}")
        return folder["id"]
    else:
        st.info(f"Found Google Drive folder: {folder_name}")
        return folder_list[0]["id"]


def upload_to_drive(drive_service, file_path, folder_id):
    """Uploads a file to a specific Google Drive folder."""
    file_metadata = {"title": os.path.basename(file_path), "parents": [{"id": folder_id}]}
    file = drive_service.CreateFile(file_metadata)
    file.SetContentFile(file_path)
    file.Upload()
    return file["id"]


def gem_app():
    st.title("📸 Android Camera Capture & Google Drive Uploader")

    st.sidebar.header("Settings")

    # Allow the user to change the folder name
    global DRIVE_FOLDER_NAME
    DRIVE_FOLDER_NAME = st.sidebar.text_input(
        "Google Drive Folder Name", value=DRIVE_FOLDER_NAME
    )

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
            now = datetime.datetime.now()
            timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
            filename_to_save = f"capture_{timestamp}.jpg"
            st.image(picture, caption="Foto capturada")

    elif upload_option == "Subir desde la galería":
        uploaded_file = st.file_uploader(
            "Sube una imagen de la galería", type=["png", "jpg", "jpeg"]
        )
        if uploaded_file is not None:
            image_data = uploaded_file.getvalue()
            now = datetime.datetime.now()
            timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
            # Use original filename but with timestamp
            base, extension = os.path.splitext(uploaded_file.name)
            filename_to_save = f"{base}_{timestamp}{extension}"
            st.image(uploaded_file, caption="Imagen de la galería")

    # If an image has been captured or uploaded
    if image_data:
        st.write("---")
        st.subheader("Subiendo a Google Drive...")

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
            drive_folder_id = get_drive_folder(drive, DRIVE_FOLDER_NAME)

            if drive_folder_id:
                try:
                    file_id = upload_to_drive(drive, file_path, drive_folder_id)
                    st.success(f"✅ ¡Subida exitosa! ID del archivo: {file_id}")
                    os.remove(file_path)  # Clean up the local file
                except Exception as e:
                    st.error(f"La subida falló: {e}")
            else:
                st.error(
                    f"No se pudo encontrar o crear la carpeta de Google Drive '{DRIVE_FOLDER_NAME}'."
                )
        else:
            st.warning(
                "La autenticación de Google Drive falló. Por favor, revisa tus credenciales."
            )
