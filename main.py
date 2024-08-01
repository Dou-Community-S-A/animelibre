import requests
from animeflv import AnimeFLV
from download_mega import *

def erase_episode(folder):
    try:
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Archivo eliminado: {file_path}")
    except Exception as e:
        print(f"Error al eliminar archivos: {e}")


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
                    download_from_mega(selected_link.url, download_filename, "downloads")
                
                open_video(download_filename, "downloads")

                input("Presiona Enter para continuar y eliminar el episodio...")

                erase_episode("downloads")


            except Exception as e:
                print(f"Error al obtener los enlaces del anime: {e}")
                pass

            open_video(download_filename, "downloads")

            input("Presiona Enter para continuar y eliminar el episodio...")

            erase_episode("downloads")


    except Exception as e:
        print(f"Error al obtener el enlace del video: {e}")

if __name__ == "__main__":
    main()
