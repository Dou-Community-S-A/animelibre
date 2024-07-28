from animeflv import AnimeFLV, EpisodeInfo, AnimeInfo

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

        for link in links:
            print(f"{link.server} - {link.url}")

    except Exception as e:
        print(e)       