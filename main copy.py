import subprocess
from animeflv import AnimeFLV, EpisodeInfo, AnimeInfo
from bs4 import BeautifulSoup  # Import BeautifulSoup for HTML parsing
import requests

with AnimeFLV() as api:
    try:
        anime_name = input("Anime: ")
        anime_list = api.search(anime_name)
        for i, anime in enumerate(anime_list):
            print(f"{i} - {anime.title}")

        select = int(input("Opción: "))
        selected_anime = anime_list[select]
        info = api.get_anime_info(selected_anime.id)
        info.episodes.reverse()

        for j, episode in enumerate(info.episodes):
            print(f"{j} - {episode.id}")

        ep = int(input("Opción de episodio: "))
        serie = selected_anime.id
        capitulo = info.episodes[ep].id
        links = api.get_links(serie, capitulo)

        for k, link in enumerate(links):
            print(f"{k} - {link.server} - {link.url}")

        server_option = int(input("Opción de servidor: "))
        selected_link = links[server_option].url

        # Obtener el enlace de la fuente del video:
        response = requests.get(selected_link)
        soup = BeautifulSoup(response.content, 'html.parser')

        video_wrapper = soup.find('div', class_='plyr__video-wrapper')
        video_element = video_wrapper.find('video')
        video_source = video_element['src']

        # Abrir el enlace de la fuente del video en VLC Media Player:
        player = 'vlc'
        subprocess.Popen([player, video_source])

    except Exception as e:
        print(e)


        