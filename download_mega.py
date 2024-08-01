import os
from mega import Mega

def open_video(video_src, folder):
    try:
        file_path = os.path.join(folder, video_src)
        os.startfile(file_path)
    except Exception as e:
        print(f"No se pudo abrir el archivo: {e}")

def download_from_mega(url, filename, dest_path):
    mega = Mega()
    m = mega.login()
    print(f"Descargando desde Mega: {url}")
    m.download_url(url, dest_path=dest_path, dest_filename=filename)
    print(f"Archivo descargado como: {filename}")