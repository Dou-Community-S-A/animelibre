#!/usr/sbin/python3

# Importamos las bibliotecas necesarias
from anime_scrapper import AnimeFLV
import os
import argparse
from requests import head, get

# Verificamos si el sistema operativo es Windows
if os.name == "nt":
    # Si yt-dlp.exe no existe, lo descargamos
    if not os.path.exists(os.path.dirname(__file__) + "\\yt-dlp.exe"):
        print("Descargando depencia yt-dlp: ...")
        open(f'{os.path.dirname(__file__)}\\yt-dlp.exe', 'wb').write(get('https://raw.githubusercontent.com/agus-balles/files/main/yt-dlp.exe').content)
    
    # Si libmpv-2.dll no existe, lo descargamos y extraemos
    if not os.path.exists(os.path.dirname(__file__) + "\\libmpv-2.dll"):
        from zipfile import ZipFile
        print("Descargando Dependencia libmpv: ...")
        open(f'{os.path.dirname(__file__)}\\libmpv-2.zip', 'wb').write(get('https://raw.githubusercontent.com/agus-balles/files/main/libmpv-2.zip').content)
        print("Extrayendo depencia libmpv-2.dll: ...")
        ZipFile(f"{os.path.dirname(__file__)}\\libmpv-2.zip", "r").extractall(os.path.dirname(__file__))
        os.remove(f"{os.path.dirname(__file__)}\\libmpv-2.zip")
    
    # Agregamos la ruta del directorio actual al PATH del sistema
    os.environ["PATH"] = os.path.dirname(__file__) + os.pathsep + os.environ["PATH"]

# Importamos la biblioteca mpv
import mpv

# Creamos una instancia de la API de AnimeFLV
api = AnimeFLV()

# Configuramos los argumentos del programa
parser = argparse.ArgumentParser(description="Mira anime subtitulado en español.")
parser.add_argument("-A", "--anime", type=str, help="Titulo del Anime")
parser.add_argument("-C", "--capitulo", type=int, help="Capitulo del Anime")
parser.add_argument("-S", "--buscar", type=str, help="Muestra Resultados de la busqueda de un anime")

# Parseamos los argumentos
args = parser.parse_args()

# Función para crear un reproductor mpv con configuraciones predeterminadas
def create_player():
    return mpv.MPV(ytdl=True, osc=True, input_default_bindings=True, input_vo_keyboard=True)

# Función para reproducir un video de un anime específico y capítulo
def watch_video(anime, episode_index, provider=0):
    # Obtenemos los enlaces del episodio
    episode_links = api.get_links(episode_index + 1)
    provider_string = episode_links[provider][:14]
    video = [link for link in episode_links if provider_string in link][0]
    
    # Creamos el reproductor
    player = create_player()
    print(f"Episodio {episode_index + 1}:\n{video}")
    
    # Configuramos el reproductor
    player["video-sync"] = "display-resample"
    player["force-media-title"] = f"{anime} - Episodio: {episode_index + 1}"
    player["title"] = f"{anime} - Episodio: {episode_index + 1}"
    
    # Reproducimos el video
    player.play("ytdl://" + video)
    player.wait_for_playback()
    player.terminate()

# Si se especifica el parámetro de búsqueda, mostramos los resultados de la búsqueda
if args.buscar:
    results = api.search(args.buscar)
    print("Resultados:")
    for j, result in enumerate(results, 1):
        print(f"[{j}] {result}")
    exit()

# Si se especifica un anime
if args.anime:
    # Verificamos si el anime existe
    r = head(f"https://m.animeflv.net/anime/{args.anime}")
    if r.status_code == 200:
        anime_id = args.anime
    else:
        anime_id = api.search(args.anime)[0]
    
    # Obtenemos la información del anime
    animeinfo = api.anime_info(anime_id)
    title = api.anime_title()
else:
    # Si no se especifica un anime, solicitamos al usuario que ingrese uno
    print("Que anime quieres ver?")
    possible_anime_id = api.search(input("Anime: "))

    print("\nResultados:\n")
    for j, anime in enumerate(possible_anime_id, 1):
        print(f"[{j}] {anime}")
    anime_num = int(input("Selecciona uno:")) - 1

    anime_id = possible_anime_id[anime_num]
    animeinfo = api.anime_info(anime_id)
    title = api.anime_title()
    status = api.anime_status()
    summary = api.anime_summary()

    print(f"\nTítulo: {title}")
    print(f"Estado: {status}")
    print(f"\nResumen: {summary}")

# Obtenemos la lista de episodios del anime
episode_list = api.anime_episodes()

# Si se especifica un anime y un capítulo
if args.anime and args.capitulo:
    episode_index = args.capitulo - 1
elif args.capitulo and not args.anime:
    parser.error("No se puede especificar el capitulo sin especificar el anime.")
else:
    # Si no se especifica un capítulo, mostramos la lista de episodios y solicitamos al usuario que seleccione uno
    print("\nEpisodios:")
    for j, episode in enumerate(episode_list, 1):
        print(f"[{j}] {episode}")

    episode_index = int(input("Selecciona que episodio ver:")) - 1

# Obtenemos los enlaces del episodio seleccionado
episode_links = api.get_links(episode_index + 1)

# Solicitamos al usuario que seleccione un proveedor de video
print("\nElige un proveedor:")
for j, provider in enumerate(episode_links, 1):
    print(f"[{j}] {provider}")
provider = int(input("Proveedor:")) - 1

# Reproducimos el video seleccionado
watch_video(title, episode_index, provider)
