import os
import time
import requests
from mega import Mega
from animeflv import AnimeFLV, EpisodeInfo, AnimeInfo

# Función para abrir enlace en el reproductor predeterminado
def open_video(video_src):
    try:
        os.startfile(video_src)
    except Exception as e:
        print(f"No se pudo abrir el archivo: {e}")

# Función para descargar archivo desde Mega
def download_from_mega(url, filename):
    mega = Mega()
    m = mega.login()
    print(f"Descargando desde Mega: {url}")
    m.download_url(url, dest_filename=filename)
    print(f"Archivo descargado como: {filename}")

# Función para descargar archivo
def download_file(url, filename):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    with requests.Session() as session:
        response = session.get(url, headers=headers, stream=True, allow_redirects=True)
        final_url = response.url

        print(f"URL final: {final_url}")
        
        if response.status_code == 200 and 'video' in response.headers.get('Content-Type', ''):
            with open(filename, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
            print(f"Archivo descargado como: {filename}")
        else:
            print(f"Error al descargar el archivo: {response.status_code} - Tipo de contenido: {response.headers.get('Content-Type', '')}")

# Función principal para buscar y descargar episodios de anime
def main():
    try:
        with AnimeFLV() as api:
            try:
                anime_name = input("Anime: ")
                anime_list = api.search(anime_name)
                for i, anime in enumerate(anime_list):
                    print(f"{i} - {anime.title}")

                while True:
                    try:
                        select = int(input("Opción: "))
                        if 0 <= select < len(anime_list):
                            break
                        else:
                            print("Por favor, ingresa un número dentro del rango.")
                    except ValueError:
                        print("Por favor, ingresa un número válido.")

                selected_anime = anime_list[select]
                info = api.get_anime_info(selected_anime.id)
                info.episodes.reverse()

                for j, episode in enumerate(info.episodes):
                    print(f"{j} - {episode.id}")

                while True:
                    try:
                        ep = int(input("Opción de episodio: "))
                        if 0 <= ep < len(info.episodes):
                            break
                        else:
                            print("Por favor, ingresa un número dentro del rango.")
                    except ValueError:
                        print("Por favor, ingresa un número válido.")

                serie = selected_anime.id
                capitulo = info.episodes[ep].id
                links = api.get_links(serie, capitulo)

                for index, link in enumerate(links):
                    print(f"{index} - {link.server} - {link.url}")

                while True:
                    try:
                        link_select = int(input("Opción de enlace: "))
                        if 0 <= link_select < len(links):
                            break
                        else:
                            print("Por favor, ingresa un número dentro del rango.")
                    except ValueError:
                        print("Por favor, ingresa un número válido.")

                selected_link = links[link_select]
                download_filename = f"{selected_anime.title} - Episode {info.episodes[ep].id}.mp4"

                if "mega" in selected_link.server.lower():
                    download_from_mega(selected_link.url, download_filename)
                else:
                    download_file(selected_link.url, download_filename)
                
                # Esperar un momento para asegurarse de que la descarga se haya completado
                time.sleep(5)
                
                # Abrir el archivo descargado
                open_video(download_filename)

            except Exception as e:
                print(f"Error al obtener los enlaces del anime: {e}")

    except Exception as e:
        print(f"Error al obtener el enlace del video: {e}")

if __name__ == "__main__":
    main()
